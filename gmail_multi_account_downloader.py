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

# Search keywords for Keith King FCRA/Credit case
KEITH_CREDIT_KEYWORDS = [
    'FTC', 'identity theft', 'equifax', 'experian', 'transunion',
    'smartpay', 'smart pay', 'jefferson capital', 'trueaccord',
    'dispute', 'collection', 're-aged', 'FCRA', 'FDCPA',
    'credit report', 'credit denial', 'loan denial', 'fraud',
    'verizon', 'AT&T', 'capital one', 'credit union',
    'demand letter', 'cease and desist', 'collections agency',
    'equifax breach', 'data breach', 'sham investigation'
]

# Search keywords for Amanda Ross (housing/FHA case)
AMANDA_KEYWORDS = [
    'housing', 'HUD', 'MHRC', 'fair housing', 'discrimination',
    'brewer housing', 'bangor housing', 'bangor ha', 'charlotte perkins',
    'joseph bethony', 'joseph knox', 'housing authority',
    'denial letter', 'background check', 'credit pull',
    'federal court', 'right to sue', 'housing complaint'
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

    def search_emails(self, service, query, max_results=None):
        """Search for emails matching criteria (with pagination)"""
        all_messages = []
        page_token = None
        page_count = 0

        try:
            while True:
                page_count += 1
                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=100,
                    pageToken=page_token
                ).execute()

                messages = results.get('messages', [])
                all_messages.extend(messages)

                print(f"  📄 Page {page_count}: Found {len(messages)} messages (Total: {len(all_messages)})")

                # If no max_results specified, get ALL pages
                if max_results and len(all_messages) >= max_results:
                    return all_messages[:max_results]

                page_token = results.get('nextPageToken')
                if not page_token:
                    break

            return all_messages
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

    def download_account_emails(self, account_email, person_folder, keywords):
        """Download all emails from account for specified person"""
        print(f"\n{'='*80}")
        print(f"📧 Processing: {account_email}")
        print(f"   Saving to: {person_folder}/")
        print(f"{'='*80}")

        # Authenticate
        creds = self.authenticate_account(account_email)
        service = self.get_gmail_service(creds)

        # Build search query
        search_query = ' OR '.join([f'"{keyword}"' for keyword in keywords])

        print(f"\n🔍 Searching for ALL matching emails (paginating through all results)...")
        messages = self.search_emails(service, search_query)  # No max_results = get ALL

        if not messages:
            print("⚠ No emails found")
            return 0

        print(f"✓ Found {len(messages)} total matching emails\n")

        # Download each email
        download_count = 0
        for idx, message in enumerate(messages, 1):
            message_id = message['id']
            email_data = self.get_email_content(service, message_id)

            if not email_data:
                continue

            headers = email_data['payload']['headers']
            email_from = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            email_subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            email_date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')

            print(f"[{idx}/{len(messages)}] {email_subject[:60]}")
            print(f"    From: {email_from}")

            # Save email text to person-specific folder
            self.save_email_text(email_data, f"{person_folder}/{account_email}", email_from, email_subject, email_date)

            # Extract attachments to person-specific folder
            self.extract_attachments(service, email_data, f"{person_folder}/{account_email}", email_subject)

            download_count += 1

        print(f"\n✓ Downloaded {download_count} emails from {account_email}")
        return download_count

    def download_all_accounts(self, keith_accounts, amanda_accounts):
        """Download from multiple accounts, separated by person"""
        print("\n" + "="*80)
        print("📥 GMAIL DOWNLOADER - KEITH KING & AMANDA ROSS (SEPARATED)")
        print("="*80)
        print(f"\n👨 KEITH KING Accounts: {', '.join(keith_accounts)}")
        print(f"👩 AMANDA ROSS Accounts: {', '.join(amanda_accounts)}")
        print(f"\n📂 Output directory: {self.output_dir.absolute()}")
        print(f"🔑 Keith keywords: {len(KEITH_CREDIT_KEYWORDS)} terms")
        print(f"🔑 Amanda keywords: {len(AMANDA_KEYWORDS)} terms")

        keith_count = 0
        amanda_count = 0

        # Download Keith's credit case materials
        print("\n" + "="*80)
        print("👨 KEITH KING - FCRA/CREDIT CASE MATERIALS")
        print("="*80)
        for account in keith_accounts:
            keith_count += self.download_account_emails(account, "01_KEITH_KING_CREDIT_CASE", KEITH_CREDIT_KEYWORDS)

        # Download Amanda's housing/FHA case materials
        print("\n" + "="*80)
        print("👩 AMANDA ROSS - HOUSING/FHA CASE MATERIALS")
        print("="*80)
        for account in amanda_accounts:
            amanda_count += self.download_account_emails(account, "02_AMANDA_ROSS_HOUSING_CASE", AMANDA_KEYWORDS)

        print("\n" + "="*80)
        print("✅ DOWNLOAD COMPLETE")
        print("="*80)
        print(f"\n📂 Files saved to: {self.output_dir.absolute()}")
        print(f"👨 Keith King emails downloaded: {keith_count}")
        print(f"👩 Amanda Ross emails downloaded: {amanda_count}")
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

    # Gmail accounts - SEPARATED BY PERSON
    keith_accounts = [
        'keithandamanda123@gmail.com',      # Primary
        'keithandamanda2233@gmail.com',     # Secondary
        'keithaking2055@gmail.com'          # Tertiary
    ]

    amanda_accounts = [
        'keithfhacase2233@gmail.com'        # Amanda's FHA case account
        # Add more Amanda accounts if needed
    ]

    downloader = GmailDownloader(output_dir='gmail_downloads_separated')
    downloader.download_all_accounts(keith_accounts, amanda_accounts)

if __name__ == '__main__':
    main()
