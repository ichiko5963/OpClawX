#!/usr/bin/env python3
"""
Gmail自動分類 + ラベル付与
- 受信メールを自動分類
- 優先度ラベル付与
- 返信必要フラグ
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

# 既存のGmail関数をインポート
SCRIPTS_PATH = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_PATH))

from email_manager import (
    get_access_token, 
    IMPORTANT_SENDERS,
    IGNORE_PATTERNS
)

def make_gmail_request(token: str, endpoint: str, method: str = "GET", body: dict = None):
    """Gmail APIリクエスト"""
    import urllib.request
    import urllib.error
    
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/{endpoint}"
    
    if method == "GET":
        req = urllib.request.Request(url)
    else:
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
    
    req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read())

def get_gmail_token():
    """Gmail トークンを取得"""
    return get_access_token()

# 設定
JST = timezone(timedelta(hours=9))

# ラベル定義
LABELS = {
    "要返信": {"color": {"backgroundColor": "#fb4c2f", "textColor": "#ffffff"}},  # 赤
    "案件": {"color": {"backgroundColor": "#16a765", "textColor": "#ffffff"}},     # 緑
    "請求/経費": {"color": {"backgroundColor": "#ffad47", "textColor": "#ffffff"}}, # オレンジ
    "ミーティング": {"color": {"backgroundColor": "#4986e7", "textColor": "#ffffff"}}, # 青
    "確認済み": {"color": {"backgroundColor": "#a4c2f4", "textColor": "#000000"}},  # 薄青
    "後で対応": {"color": {"backgroundColor": "#b99aff", "textColor": "#ffffff"}}, # 紫
}

# 除外パターン（営業・プロモーション）
PROMOTIONAL_PATTERNS = [
    r"セミナー",
    r"ウェビナー",
    r"キャンペーン",
    r"プレゼント",
    r"資料.*ダウンロード",
    r"無料.*公開",
    r"限定.*公開",
    r"解説",
    r"ポイント.*解説",
    r"導入.*ポイント",
    r"ご紹介",
    r"お知らせ",
    r"ニュースレター",
    r"メールマガジン",
    r"登録.*ありがとう",
]

# 分類ルール
CLASSIFICATION_RULES = {
    "要返信": {
        "subject_patterns": [
            r"確認.*お願い",
            r"ご確認ください",
            r"返信.*お願い",
            r"お返事",
            r"ご回答",
            r"質問",
            r"相談",
            r"依頼",
            r"\?|？",
        ],
        "body_patterns": [
            r"ご返信.*お願い",
            r"お返事.*いただけ",
            r"ご確認の上.*ご連絡",
            r"いかがでしょうか",
            r"ご都合.*いかが",
        ],
        "sender_patterns": IMPORTANT_SENDERS,
        "exclude_patterns": PROMOTIONAL_PATTERNS,  # プロモーション除外
    },
    "案件": {
        "subject_patterns": [
            r"見積.*依頼",
            r"見積.*お願い",
            r"契約.*締結",
            r"契約.*お願い",
            r"発注",
            r"納品.*予定",
            r"納品.*日程",
            r"業務委託.*依頼",
            r"業務委託.*お願い",
        ],
        "body_patterns": [
            r"お見積.*お願い",
            r"お見積.*いただけ",
            r"ご契約.*お願い",
            r"業務委託.*検討",
            r"報酬.*ご提示",
            r"案件.*ご相談",
        ],
        "exclude_patterns": PROMOTIONAL_PATTERNS,  # プロモーション除外
    },
    "請求/経費": {
        "subject_patterns": [
            r"請求書",
            r"領収書",
            r"Invoice",
            r"支払",
            r"決済",
            r"振込",
            r"ご入金",
        ],
        "body_patterns": [
            r"請求金額",
            r"お支払い",
            r"振込先",
            r"経費",
        ],
    },
    "ミーティング": {
        "subject_patterns": [
            r"MTG",
            r"ミーティング",
            r"打ち合わせ",
            r"会議",
            r"面談",
            r"Zoom|Google Meet|Teams",
            r"日程調整",
            r"スケジュール",
        ],
        "body_patterns": [
            r"zoom\.us",
            r"meet\.google",
            r"teams\.microsoft",
            r"日程.*候補",
        ],
    },
}

def get_or_create_label(token: str, label_name: str) -> Optional[str]:
    """ラベルを取得または作成"""
    # 既存ラベル一覧取得
    try:
        result = make_gmail_request(token, "labels", method="GET")
        labels = result.get('labels', [])
        
        for label in labels:
            if label['name'] == label_name:
                return label['id']
        
        # ラベル作成
        label_config = LABELS.get(label_name, {})
        body = {
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
        if 'color' in label_config:
            body['color'] = label_config['color']
        
        result = make_gmail_request(
            token, "labels",
            method="POST",
            body=body
        )
        return result.get('id')
        
    except Exception as e:
        print(f"Label error: {e}")
        return None

def classify_email(subject: str, body: str, sender: str) -> List[str]:
    """メールを分類してラベルリストを返す"""
    labels = []
    
    # 無視パターンチェック
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, sender, re.IGNORECASE) or re.search(pattern, subject, re.IGNORECASE):
            return []  # 無視
    
    # 各分類ルールをチェック
    for label_name, rules in CLASSIFICATION_RULES.items():
        matched = False
        
        # プロモーション除外チェック（要返信・案件のみ）
        if label_name in ["要返信", "案件"]:
            is_promotional = False
            for pattern in rules.get('exclude_patterns', []):
                if re.search(pattern, subject, re.IGNORECASE) or re.search(pattern, body[:2000], re.IGNORECASE):
                    is_promotional = True
                    break
            if is_promotional:
                continue  # このラベルはスキップ
        
        # 件名パターン
        for pattern in rules.get('subject_patterns', []):
            if re.search(pattern, subject, re.IGNORECASE):
                matched = True
                break
        
        # 本文パターン
        if not matched:
            for pattern in rules.get('body_patterns', []):
                if re.search(pattern, body[:2000], re.IGNORECASE):
                    matched = True
                    break
        
        # 送信者パターン（要返信のみ）
        if label_name == "要返信" and not matched:
            for pattern in rules.get('sender_patterns', []):
                if re.search(pattern, sender, re.IGNORECASE):
                    matched = True
                    break
        
        if matched:
            labels.append(label_name)
    
    return labels

def apply_labels_to_message(token: str, message_id: str, label_names: List[str]) -> bool:
    """メッセージにラベルを付与"""
    if not label_names:
        return True
    
    label_ids = []
    for name in label_names:
        label_id = get_or_create_label(token, name)
        if label_id:
            label_ids.append(label_id)
    
    if not label_ids:
        return False
    
    try:
        make_gmail_request(
            token,
            f"messages/{message_id}/modify",
            method="POST",
            body={"addLabelIds": label_ids}
        )
        return True
    except Exception as e:
        print(f"Apply label error: {e}")
        return False

def process_unread_emails(max_results: int = 20, dry_run: bool = False) -> Dict:
    """未読メールを処理して分類"""
    token = get_gmail_token()
    if not token:
        return {"status": "error", "message": "Gmail token not available"}
    
    # 未読メール取得
    try:
        result = make_gmail_request(
            token,
            f"messages?q=is:unread&maxResults={max_results}",
            method="GET"
        )
        messages = result.get('messages', [])
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    if not messages:
        return {"status": "no_emails", "message": "未読メールがありません"}
    
    processed = []
    for msg in messages:
        msg_id = msg['id']
        
        # メール詳細取得
        try:
            detail = make_gmail_request(token, f"messages/{msg_id}", method="GET")
            
            headers = {h['name']: h['value'] for h in detail.get('payload', {}).get('headers', [])}
            subject = headers.get('Subject', '(件名なし)')
            sender = headers.get('From', '')
            
            # 本文取得（簡易）
            body = detail.get('snippet', '')
            
            # 分類
            labels = classify_email(subject, body, sender)
            
            if labels:
                if not dry_run:
                    apply_labels_to_message(token, msg_id, labels)
                
                processed.append({
                    'subject': subject[:50],
                    'sender': sender[:30],
                    'labels': labels
                })
        except Exception as e:
            print(f"Process error for {msg_id}: {e}")
            continue
    
    return {
        "status": "success",
        "total": len(messages),
        "labeled": len(processed),
        "emails": processed
    }

def ensure_all_labels_exist() -> Dict:
    """全てのラベルを事前に作成"""
    token = get_gmail_token()
    if not token:
        return {"status": "error", "message": "Gmail token not available"}
    
    created = []
    for label_name in LABELS.keys():
        label_id = get_or_create_label(token, label_name)
        if label_id:
            created.append(label_name)
    
    return {
        "status": "success",
        "labels": created
    }

def format_result_for_telegram(result: Dict) -> str:
    """結果をTelegram用にフォーマット"""
    if result['status'] == 'error':
        return f"❌ エラー: {result['message']}"
    
    if result['status'] == 'no_emails':
        return "📧 未読メールがありません"
    
    lines = [f"📧 **{result['labeled']}件のメールを分類しました**\n"]
    
    for email in result.get('emails', [])[:10]:
        labels_str = " ".join([f"`{l}`" for l in email['labels']])
        lines.append(f"• {email['subject'][:30]}...\n  → {labels_str}")
    
    if result['labeled'] > 10:
        lines.append(f"\n...他 {result['labeled'] - 10}件")
    
    return "\n".join(lines)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail自動分類')
    parser.add_argument('--setup', action='store_true', help='ラベルを事前作成')
    parser.add_argument('--process', action='store_true', help='未読メールを処理')
    parser.add_argument('--dry-run', action='store_true', help='ラベル付与せずに確認のみ')
    parser.add_argument('--max', type=int, default=20, help='処理する最大件数')
    
    args = parser.parse_args()
    
    if args.setup:
        result = ensure_all_labels_exist()
        print("ラベル作成完了:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.process:
        result = process_unread_emails(max_results=args.max, dry_run=args.dry_run)
        print("\n" + "="*50)
        print(format_result_for_telegram(result))
        print("="*50)
        print("\nJSON:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()
