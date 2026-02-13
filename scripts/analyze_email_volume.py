
import sys
import re
from collections import Counter
from datetime import datetime, timezone, timedelta

# パスを追加
sys.path.append("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")

# email_managerをインポート
try:
    from email_manager import get_emails
except ImportError:
    print("Error: Could not import email_manager.py")
    sys.exit(1)

def analyze_senders():
    print("Fetching emails for sender analysis (max 500)...")
    # 多めに取得して傾向分析
    emails = get_emails(max_results=500, unread_only=False)
    
    sender_counts = Counter()
    
    ignore_domains = ["gmail.com", "google.com"] # 一般的なドメインは除外してもいいかもだが、企業ドメインを見たいので一旦そのまま
    
    print(f"Analyzing {len(emails)} emails...")
    
    for email in emails:
        sender_email = email.get('from', '')
        # emailアドレス抽出
        match = re.search(r'<(.+?)>', sender_email)
        if match:
            email_addr = match.group(1)
        else:
            email_addr = sender_email
            
        # ドメイン抽出
        if '@' in email_addr:
            domain = email_addr.split('@')[-1]
            sender_counts[f"{email_addr} ({domain})"] += 1
        else:
             sender_counts[sender_email] += 1

    print("\nTop 20 Frequent Senders:")
    for sender, count in sender_counts.most_common(20):
        print(f"{count}通: {sender}")

if __name__ == "__main__":
    analyze_senders()
