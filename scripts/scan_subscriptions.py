
import sys
import re
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# パスを追加
sys.path.append("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")

try:
    from email_manager import get_emails
except ImportError:
    print("Error: Could not import email_manager.py")
    sys.exit(1)

SUBSCRIPTIONS_FILE = Path("SUBSCRIPTIONS.md")

# サブスクっぽい件名・本文のキーワード
SUB_KEYWORDS = [
    r"領収書",
    r"請求書",
    r"お支払い",
    r"ご請求",
    r"receipt",
    r"invoice",
    r"payment",
    r"renew",
    r"subscription",
    r"定期購読",
    r"月額",
    r"年額",
    r"更新",
    r"membership",
    r"メンバーシップ",
    r"課金",
    r"plan",
    r"プラン",
]

# サービス名の候補
SERVICES = [
    "Netflix", "Spotify", "Amazon", "Prime", "Apple", "iCloud", "Adobe", "Google", "YouTube",
    "Zoom", "Slack", "Notion", "Figma", "Canva", "OpenAI", "ChatGPT", "Claude", "Cursor",
    "Vercel", "Heroku", "AWS", "X Premium", "Twitter", "Midjourney", "DeepL", "Grammarly",
    "1Password", "NordVPN", "ExpressVPN", "Dropbox", "Evernote", "Microsoft", "Office",
    "Nintendo", "PlayStation", "Hulu", "Disney", "DAZN", "U-NEXT", "Abema", "Niconico",
    "Kindle", "Audible", "Pixiv", "Fanbox", "Patreon"
]

def analyze_subscriptions():
    print("Fetching emails from Jan 1, 2026...")
    # NOTE: email_manager.get_emails は max_results 指定なので、多めに取ってフィルタする簡易実装
    # 本来は日付指定クエリを使うべきだが、既存関数を流用
    emails = get_emails(max_results=200, unread_only=False)
    
    found_subs = {}
    
    for email in emails:
        # 日付フィルタ (簡易)
        # email['date'] は "Fri, 07 Feb 2026 15:30:00 +0900" のような形式
        # ここでは厳密なパースを省略し、文字列検索で "2026" を含むか確認
        if "2026" not in email['date']:
            continue
            
        subject = email['subject']
        body = email['body']
        sender = email['from']
        
        full_text = f"{subject} {body} {sender}"
        
        is_sub = any(re.search(k, full_text, re.I) for k in SUB_KEYWORDS)
        
        if is_sub:
            # サービス名特定
            detected_service = None
            for service in SERVICES:
                if re.search(service, full_text, re.I):
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

    # 結果をSUBSCRIPTIONS.mdに追記
    if not SUBSCRIPTIONS_FILE.exists():
        SUBSCRIPTIONS_FILE.write_text("# Subscriptions\n\n## Active Subscriptions\n", encoding='utf-8')
    
    current_content = SUBSCRIPTIONS_FILE.read_text(encoding='utf-8')
    
    new_entries = []
    print("\nFound Potential Subscriptions:")
    for service, items in found_subs.items():
        print(f"- {service}: {len(items)} emails")
        # 最新の日付を取得
        latest = items[0] # get_emailsは新しい順と仮定
        entry = f"- {service}: {latest['date']} (Source: {latest['subject']})"
        if service not in current_content:
            new_entries.append(entry)
    
    if new_entries:
        with open(SUBSCRIPTIONS_FILE, "a", encoding='utf-8') as f:
            for entry in new_entries:
                f.write(f"{entry}\n")
        print("\nUpdated SUBSCRIPTIONS.md")
    else:
        print("\nNo new subscriptions found to add.")

if __name__ == "__main__":
    analyze_subscriptions()
