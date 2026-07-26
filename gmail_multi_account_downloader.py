#!/usr/bin/env python3
"""
Multi-Account Gmail Downloader - FCRA/Credit Case Materials
Downloads emails + attachments from multiple Gmail accounts
Searches for: FTC, disputes, Equifax, SmartPay, Jefferson, TransUnion, Experian, loan denials
"""

import os
import json
import base64
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core.exceptions import HttpError
from googleapiclient.discovery import build
from datetime import datetime

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Search keywords for credit case
CREDIT_KEYWORDS = [
    'FTC', 'identity theft', 'equifax', 'experian', 'transunion',
    'smartpay', 'smart pay', 'jefferson capital', 'trueaccord',
    'dispute', 'collection', 're-aged', 'FCRA', 'FDCPA',
    'credit report', 'credit denial', 'loan denial', 'fraud',
    'verizon', 'AT&T', 'capital one', 'credit union',
    'demand letter', 'cease and desist', 'collections agency'
]

class GmailDownloader:
    def __init__(self, output_dir='gmail_downloads'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.accounts = {}

    def authenticate_account(self, account_email):
        """Authenticate a single Gmail account"""
        creds = None
        token_file = f'token_{account_email}.pickle'

        # Load existing token
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or create new auth
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif not creds or not creds.valid:
            print(f"\n🔐 Authenticating {account_email}...")
            print("A browser window will open. Please authenticate and authorize access.")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

            # Save token
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def get_gmail_service(self, creds):
        """Build Gmail API service"""
        return build('gmail', 'v1', credentials=creds)

    def search_emails(self, service, query, max_results=100):
        """Search for emails matching criteria"""
        try:
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            return results.get('messages', [])
        except HttpError as error:
            print(f"❌ Search error: {error}")
            return []

    def get_email_content(self, service, message_id):
        """Download full email content"""
        try:
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            return message
        except HttpError as error:
            print(f"❌ Get message error: {error}")
            return None

    def extract_attachments(self, service, message, account_email, email_subject):
        """Extract and save attachments"""
        attachments = []

        if 'parts' not in message['payload']:
            return attachments

        for part in message['payload']['parts']:
            if part['filename']:
                filename = part['filename']
                attachment_id = part['body'].get('attachmentId')

                if attachment_id:
                    try:
                        attachment = service.users().messages().attachments().get(
                            userId='me',
                            messageId=message_id,
                            id=attachment_id
                        ).execute()

                        data = attachment['data']
                        file_data = base64.urlsafe_b64decode(data)

                        # Create safe filename
                        safe_subject = "".join(c for c in email_subject if c.isalnum() or c in ' -_')[:50]
                        filepath = self.output_dir / account_email / 'attachments' / f"{safe_subject}_{filename}"
                        filepath.parent.mkdir(parents=True, exist_ok=True)

                        with open(filepath, 'wb') as f:
                            f.write(file_data)

                        attachments.append(str(filepath))
                        print(f"✓ Downloaded: {filename}")
                    except Exception as e:
                        print(f"⚠ Failed to download {filename}: {e}")

        return attachments

    def save_email_text(self, message, account_email, email_from, email_subject, email_date):
        """Save email as text file"""
        try:
            # Extract body
            payload = message['payload']
            body = ''

            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            else:
                if 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

            # Save to file
            safe_subject = "".join(c for c in email_subject if c.isalnum() or c in ' -_')[:50]
            timestamp = email_date.replace(':', '').replace(' ', '_')

            filepath = self.output_dir / account_email / 'emails' / f"{timestamp}_{safe_subject}.txt"
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"FROM: {email_from}\n")
                f.write(f"SUBJECT: {email_subject}\n")
                f.write(f"DATE: {email_date}\n")
                f.write("=" * 80 + "\n\n")
                f.write(body)

            return str(filepath)
        except Exception as e:
            print(f"⚠ Error saving email: {e}")
            return None

    def download_account_emails(self, account_email):
        """Download all credit-related emails from account"""
        print(f"\n{'='*80}")
        print(f"📧 Processing: {account_email}")
        print(f"{'='*80}")

        # Authenticate
        creds = self.authenticate_account(account_email)
        service = self.get_gmail_service(creds)

        # Build search query
        search_query = ' OR '.join([f'"{keyword}"' for keyword in CREDIT_KEYWORDS])

        print(f"\n🔍 Searching for credit-related emails...")
        messages = self.search_emails(service, search_query, max_results=500)

        if not messages:
            print("⚠ No emails found")
            return

        print(f"✓ Found {len(messages)} matching emails\n")

        # Download each email
        for idx, message in enumerate(messages, 1):
            message_id = message['id']
            email_data = self.get_email_content(service, message_id)

            if not email_data:
                continue

            headers = email_data['payload']['headers']
            email_from = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            email_subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            email_date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')

            print(f"\n[{idx}/{len(messages)}] {email_subject}")
            print(f"    From: {email_from}")
            print(f"    Date: {email_date}")

            # Save email text
            self.save_email_text(email_data, account_email, email_from, email_subject, email_date)

            # Extract attachments
            self.extract_attachments(service, email_data, account_email, email_subject)

        print(f"\n✓ Completed {account_email}")

    def download_all_accounts(self, account_emails):
        """Download from multiple accounts"""
        print("\n" + "="*80)
        print("📥 GMAIL MULTI-ACCOUNT CREDIT CASE DOWNLOADER")
        print("="*80)
        print(f"\nAccounts to process: {', '.join(account_emails)}")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Search keywords: {len(CREDIT_KEYWORDS)} terms")

        for account in account_emails:
            self.download_account_emails(account)

        print("\n" + "="*80)
        print("✅ DOWNLOAD COMPLETE")
        print("="*80)
        print(f"\n📂 Files saved to: {self.output_dir.absolute()}")
        self.print_summary()

    def print_summary(self):
        """Print summary of downloaded files"""
        total_emails = 0
        total_attachments = 0

        for account_dir in self.output_dir.iterdir():
            if account_dir.is_dir():
                emails = list((account_dir / 'emails').glob('*.txt')) if (account_dir / 'emails').exists() else []
                attachments = list((account_dir / 'attachments').glob('*')) if (account_dir / 'attachments').exists() else []

                total_emails += len(emails)
                total_attachments += len(attachments)

                print(f"\n{account_dir.name}:")
                print(f"  📧 Emails: {len(emails)}")
                print(f"  📎 Attachments: {len(attachments)}")

def main():
    # Check for credentials file
    if not os.path.exists('credentials.json'):
        print("\n❌ ERROR: credentials.json not found")
        print("\n📋 SETUP INSTRUCTIONS:")
        print("1. Go to: https://developers.google.com/gmail/api/quickstart/python")
        print("2. Click 'Enable the Gmail API'")
        print("3. Choose 'Desktop app' when creating OAuth consent screen")
        print("4. Download credentials as JSON")
        print("5. Save as 'credentials.json' in this directory")
        print("6. Run this script again")
        return

    # Gmail accounts to search
    accounts = [
        'keithandamanda123@gmail.com',
        'keithandamanda2233@gmail.com',
        'keithaking2055@gmail.com'
    ]

    downloader = GmailDownloader(output_dir='credit_case_emails')
    downloader.download_all_accounts(accounts)

if __name__ == '__main__':
    main()
