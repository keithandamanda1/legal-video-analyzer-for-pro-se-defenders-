# Gmail Multi-Account Email Downloader - Setup Guide

## What This Does
Downloads ALL credit/FCRA case emails + attachments from multiple Gmail accounts:
- ✅ Searches all 3+ Gmail accounts in parallel
- ✅ Downloads full email content (with attachments)
- ✅ Extracts all attachments (PDFs, images, documents)
- ✅ Organizes by account and category
- ✅ Saves as searchable text files

## 📋 Prerequisites

### 1. Install Required Libraries
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Get Gmail API Credentials

**Step 1: Go to Google Cloud Console**
- Visit: https://console.cloud.google.com/

**Step 2: Create a Project**
- Click "Select a Project" (top left)
- Click "New Project"
- Name it: "Keith King Credit Case"
- Click "Create"

**Step 3: Enable Gmail API**
- Search for "Gmail API" in the search bar
- Click "Gmail API"
- Click "Enable"

**Step 4: Create OAuth Credentials**
- Click "Create Credentials" (blue button)
- Choose: Application type = "Desktop app"
- Choose: User data
- Click "Create OAuth client ID"
- For "Authorized redirect URIs" add: `http://localhost`
- Click "Create"

**Step 5: Download Credentials**
- A dialog will appear with your client ID
- Click "Download JSON" (right side)
- Save as `credentials.json` in the SAME directory as this script

**Step 6: Place credentials.json**
```
legal-video-analyzer-for-pro-se-defenders-/
├── gmail_multi_account_downloader.py
├── credentials.json  ← Put it here
└── GMAIL_SETUP_INSTRUCTIONS.md
```

## ▶️ Running the Script

### Option 1: From Terminal/Command Prompt
```bash
cd /path/to/legal-video-analyzer-for-pro-se-defenders-/
python3 gmail_multi_account_downloader.py
```

### Option 2: First Run Authentication
When you run the script for the first time:
1. A browser window will open
2. Select the first Gmail account (keithandamanda123@gmail.com)
3. Click "Allow" to authorize access
4. Do the same for each additional account
5. Tokens are saved so you only auth ONCE per account

### Step-by-Step Walkthrough

```
1. Script starts
   ↓
2. Browser opens → Authenticate first account
   ↓
3. Browser opens → Authenticate second account
   ↓
4. Browser opens → Authenticate third account
   ↓
5. Script searches all accounts for credit keywords
   ↓
6. Downloads 500+ emails + all attachments
   ↓
7. Saves to: credit_case_emails/ folder
   ↓
8. Creates summary report
```

## 📁 Output Structure

After running, you'll have:
```
credit_case_emails/
├── keithandamanda123@gmail.com/
│   ├── emails/
│   │   ├── 20260515_123456_Equifax_Dispute_Results.txt
│   │   ├── 20260514_123455_SmartPay_Demand_Letter.txt
│   │   └── [more emails...]
│   └── attachments/
│       ├── Equifax_Dispute_Results_Equifax_Dispute_Results.pdf
│       ├── SmartPay_Demand_FCRA_VIOLATION.pdf
│       └── [more attachments...]
│
├── keithandamanda2233@gmail.com/
│   ├── emails/
│   └── attachments/
│
└── keithaking2055@gmail.com/
    ├── emails/
    └── attachments/
```

## 🔍 What It Searches For

**23 Search Keywords:**
- FTC, identity theft, equifax, experian, transunion
- smartpay, jefferson capital, trueaccord
- dispute, collection, re-aged, FCRA, FDCPA
- credit report, credit denial, loan denial, fraud
- verizon, AT&T, capital one, credit union
- demand letter, cease and desist, collections agency

**Result:** Finds ALL emails mentioning ANY of these terms

## ⚙️ Customizing Accounts

To search different accounts, edit this section in the script:

```python
accounts = [
    'keithandamanda123@gmail.com',
    'keithandamanda2233@gmail.com',
    'keithaking2055@gmail.com',
    'your-other-account@gmail.com'  # Add more here
]
```

## 🔐 Security Notes

- **Credentials.json is LOCAL ONLY** - never uploaded anywhere
- **Tokens saved as `token_[email].pickle`** - only in your directory
- **No data sent to third parties**
- You can delete token files anytime to re-authenticate
- Script only reads emails, never modifies anything

## ❓ Troubleshooting

### "credentials.json not found"
→ Make sure you downloaded the file and it's in the same directory as the script

### "HttpError 401: Invalid Credentials"
→ Delete `token_*.pickle` files and run again to re-authenticate

### "Gmail API not enabled"
→ Go back to Google Cloud Console and make sure you enabled the Gmail API

### Script runs but finds no emails
→ Check Gmail account actually has the emails
→ Verify email isn't in "All Mail" filter only
→ Try searching Gmail web interface manually first

## 📧 After Download

1. All emails + attachments will be in `credit_case_emails/` folder
2. Ready to:
   - Upload to Proton Drive
   - Organize into attorney package
   - Archive as backup
   - Extract specific documents

## ✅ Ready to Go!

Once you have `credentials.json` in place:
```bash
python3 gmail_multi_account_downloader.py
```

The script will handle everything else automatically! ✨
