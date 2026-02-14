
import sys
import re
from pathlib import Path
from datetime import datetime

# パスを追加
sys.path.append("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")

# email_managerをインポート
try:
    from email_manager import get_emails
except ImportError:
    print("Error: Could not import email_manager.py")
    sys.exit(1)

SUBSCRIPTIONS_FILE = Path("SUBSCRIPTIONS.md")

# サービス名の候補
SERVICES = [
    "Netflix", "Spotify", "Amazon", "Prime", "Apple", "iCloud", "Adobe", "Google", "YouTube",
    "Zoom", "Slack", "Notion", "Figma", "Canva", "OpenAI", "ChatGPT", "Claude", "Cursor",
    "Vercel", "Heroku", "AWS", "X Premium", "Twitter", "Midjourney", "DeepL", "Grammarly",
    "1Password", "NordVPN", "ExpressVPN", "Dropbox", "Evernote", "Microsoft", "Office",
    "Nintendo", "PlayStation", "Hulu", "Disney", "DAZN", "U-NEXT", "Abema", "Niconico",
    "Kindle", "Audible", "Pixiv", "Fanbox", "Patreon"
]

def scan_subscriptions():
    print("Fetching emails...")
    # NOTE: max_results を減らして高速化
    emails = get_emails(max_results=30, unread_only=False)
    
    found_subs = {}
    
    # 既存のSUBSCRIPTIONS.mdを読み込む
    if SUBSCRIPTIONS_FILE.exists():
        current_content = SUBSCRIPTIONS_FILE.read_text(encoding='utf-8')
    else:
        current_content = "# Subscriptions\n\n## Active Subscriptions\n"
        SUBSCRIPTIONS_FILE.write_text(current_content, encoding='utf-8')

    for email in emails:
        # 日付フィルタ (簡易)
        if "2026" not in email['date']:
            continue
            
        subject = email['subject']
        sender = email['from']
        body = email['body'][:500]
        
        full_text = f"{subject} {sender} {body}"
        
        # サービス名を検出
        detected_service = None
        for service in SERVICES:
            if re.search(service, full_text, re.IGNORECASE):
                # 文脈チェック
                if re.search(r"領収書|請求書|お支払い|ご請求|receipt|invoice|payment|renew|subscription|定期購読|月額|年額|更新|membership|メンバーシップ|课金|plan|プラン", full_text, re.IGNORECASE):
                    detected_service = service
                    break
        
        if detected_service:
            if detected_service not in found_subs:
                found_subs[detected_service] = []
            
            found_subs[detected_service].append({
                "date": email['date'],
                "subject": subject,
                "sender": sender
            })

    # 結果を追記
    new_entries = []
    print("\nFound Potential Subscriptions:")
    
    for service, items in found_subs.items():
        latest = items[0]
        date_str = latest['date']
        
        entry = f"- {service}: {date_str} (Source: {latest['subject']})"
        
        # 重複チェック（簡易）
        if f"- {service}:" not in current_content:
            new_entries.append(entry)
            print(f"  [NEW] {service}")
        else:
            print(f"  [SKIP] {service} (Already exists)")

    if new_entries:
        with open(SUBSCRIPTIONS_FILE, "a", encoding='utf-8') as f:
            for entry in new_entries:
                f.write(f"{entry}\n")
        print(f"\nAdded {len(new_entries)} new subscriptions to SUBSCRIPTIONS.md")
    else:
        print("\nNo new subscriptions to add.")

if __name__ == "__main__":
    scan_subscriptions()
