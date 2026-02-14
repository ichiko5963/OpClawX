
import sys
import os
# パスを通す
sys.path.append("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")
from email_manager import get_emails

def find_email():
    emails = get_emails(max_results=50, unread_only=False)
    for email in emails:
        if "広報_制作1on1" in email['subject']:
            print(f"Subject: {email['subject']}")
            print(f"Date: {email['date']}")
            print("Body:")
            print(email['body'])
            return
    print("Email not found.")

if __name__ == "__main__":
    find_email()
