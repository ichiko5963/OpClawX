
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

# パスを追加
sys.path.append("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/scripts")

# email_managerをインポート
try:
    from email_manager import get_access_token
except ImportError:
    print("Error: Could not import email_manager.py")
    sys.exit(1)

# ブロック対象のドメイン・アドレスリスト
BLOCK_LIST = [
    "speed-ma.com",
    "sendenkaigi.com",
    "mynavi.jp",
    "asoview.com",
    "chat-work.com",
    "chatwork.com",
    "OfferBox-plus@i-plug.co.jp"
]

def create_filter(sender_domain):
    try:
        token = get_access_token()
    except Exception as e:
        print(f"Error getting token: {e}")
        return

    url = "https://gmail.googleapis.com/gmail/v1/users/me/settings/filters"
    
    # フィルタ条件: 送信元が特定ドメインの場合
    criteria = {
        "from": sender_domain
    }
    
    # アクション: ゴミ箱へ移動（TRASHラベル追加 + 受信トレイから削除）
    action = {
        "addLabelIds": ["TRASH"],
        "removeLabelIds": ["INBOX"]
    }
    
    data = {
        "criteria": criteria,
        "action": action
    }
    
    json_data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=json_data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as res:
            result = json.loads(res.read())
            print(f"Filter created for {sender_domain}: ID {result.get('id')}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error creating filter for {sender_domain}: {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Error creating filter for {sender_domain}: {e}")

def block_emails():
    print("Creating Gmail filters individually...")
    for domain in BLOCK_LIST:
        print(f"Blocking: {domain}")
        create_filter(domain)

if __name__ == "__main__":
    block_emails()
