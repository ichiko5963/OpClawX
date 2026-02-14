
import sys
import re
from collections import Counter

# パスを追加
sys.path.append("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")

# email_managerをインポート
try:
    from email_manager import get_emails
except ImportError:
    print("Error: Could not import email_manager.py")
    sys.exit(1)

def analyze_senders():
    print("Fetching emails...")
    # さらに件数を減らす
    emails = get_emails(max_results=30, unread_only=False)
    
    sender_counts = Counter()
    domain_counts = Counter()
    
    for email in emails:
        sender_full = email.get('from', '')
        
        match = re.search(r'[\w\.-]+@[\w\.-]+', sender_full)
        if match:
            email_addr = match.group(0)
            sender_counts[email_addr] += 1
            domain = email_addr.split('@')[-1]
            if domain not in ["gmail.com", "google.com"]:
                 domain_counts[domain] += 1
        else:
            sender_counts[sender_full[:30]] += 1

    print("\n--- Top Senders ---")
    for sender, count in sender_counts.most_common(15):
        print(f"{count}通: {sender}")

    print("\n--- Top Domains (Exclude Gmail/Google) ---")
    for domain, count in domain_counts.most_common(15):
        print(f"{count}通: {domain}")

if __name__ == "__main__":
    analyze_senders()
