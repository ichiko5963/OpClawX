
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
    "*@speed-ma.com",
    "*@sendenkaigi.com",
    "*@*.sendenkaigi.com",
    "*@*.mynavi.jp",
    "*@*.asoview.com",
    "*@chat-work.com",
    "*@*.chatwork.com",
    "OfferBox-plus@i-plug.co.jp"
]

def create_filter(criteria, action):
    try:
        token = get_access_token()
    except Exception as e:
        print(f"Error getting token: {e}")
        return

    url = "https://gmail.googleapis.com/gmail/v1/users/me/settings/filters"
    
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
            print(f"Filter created for {criteria}: ID {result.get('id')}")
    except Exception as e:
        print(f"Error creating filter for {criteria}: {e}")

def block_emails():
    print("Creating Gmail filters to block (trash) emails...")
    
    # 1つのフィルタにまとめる（OR条件）
    # criteriaのfromはスペース区切りのOR検索には対応していない場合があるが、
    # フィルタAPIでは query 文字列を使うのが確実かも。
    # しかし、settings/filters APIの criteria オブジェクトは field ごとに指定する。
    # 複数ドメインを一度に指定するには from に "A OR B" のように書けるか？ -> 書ける。
    
    from_query = " OR ".join(BLOCK_LIST)
    
    criteria = {
        "from": from_query
    }
    
    action = {
        "addLabelIds": ["TRASH"], # ゴミ箱へ
        "removeLabelIds": ["INBOX"] # 受信トレイから削除
    }
    
    print(f"Blocking: {from_query}")
    create_filter(criteria, action)

if __name__ == "__main__":
    block_emails()
