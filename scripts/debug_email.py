
import sys
import os
sys.path.append("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")

print("Importing email_manager...")
try:
    from email_manager import get_emails, get_access_token
    print("Import successful.")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

print("Getting access token...")
try:
    token = get_access_token()
    print(f"Token acquired: {token[:5]}...")
except Exception as e:
    print(f"Token acquisition failed: {e}")
    sys.exit(1)

print("Getting emails...")
try:
    emails = get_emails(max_results=5, unread_only=False)
    print(f"Emails count: {len(emails)}")
    for email in emails:
        print(f"Subject: {email['subject']}")
        if "広報_制作1on1" in email['subject']:
            print("FOUND TARGET EMAIL!")
            print(email['body'])
except Exception as e:
    print(f"Email fetch failed: {e}")
