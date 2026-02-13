
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
    print("Fetching emails (max 100) for faster analysis...")
    # タイムアウトしないように件数を減らす
    emails = get_emails(max_results=100, unread_only=False)
    
    domain_counts = Counter()
    sender_counts = Counter()
    
    print(f"Analyzing {len(emails)} emails...")
    
    for email in emails:
        sender_full = email.get('from', '')
        
        # emailアドレス抽出
        match = re.search(r'<(.+?)>', sender_full)
        if match:
            email_addr = match.group(1)
        else:
            email_addr = sender_full.strip()
            
        sender_counts[f"{email_addr}"] += 1
        
        # ドメイン抽出
        if '@' in email_addr:
            domain = email_addr.split('@')[-1]
            domain_counts[domain] += 1

    print("\n--- Top Senders (送信元アドレス) ---")
    for sender, count in sender_counts.most_common(15):
        print(f"{count}通: {sender}")

    print("\n--- Top Domains (企業ドメイン) ---")
    for domain, count in domain_counts.most_common(10):
        # フリーメールは除外して表示
        if domain not in ["gmail.com", "google.com"]:
            print(f"{count}通: {domain}")

if __name__ == "__main__":
    analyze_senders()
