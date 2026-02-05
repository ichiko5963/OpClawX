#!/usr/bin/env python3
"""
請求書・経費管理システム v1
- メールから請求書/領収書を検出
- 添付ファイルをOCR
- Google Spreadsheetに保存
- 確定申告用の集計
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import base64
import hashlib
import sqlite3
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
from Crypto.Cipher import AES

# 設定
JST = timezone(timedelta(hours=9))
SCRIPTS_PATH = Path(__file__).parent
WORKSPACE = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared")
OBSIDIAN_PATH = WORKSPACE / "obsidian/Ichioka Obsidian"
PROJECTS_PATH = OBSIDIAN_PATH / "03_Projects/_Active"
STATE_PATH = OBSIDIAN_PATH / "00_System/01_State"
EXPENSES_PATH = WORKSPACE / "data/expenses"

N8N_DB_PATH = Path("/tmp/n8n_db.sqlite")
N8N_ENCRYPTION_KEY = "effdc06a2c03977ec7f117f4e3f0841fb3f5817e18ba096b973b0fd6115c9ceb"
TOKEN_CACHE_PATH = Path("/tmp/gmail_token.json")

# 請求書/領収書を示すキーワード
INVOICE_KEYWORDS = [
    r"請求書",
    r"領収書",
    r"receipt",
    r"invoice",
    r"お支払い",
    r"ご利用明細",
    r"決済完了",
    r"payment",
    r"ご請求",
    r"お振込",
    r"クレジットカード.*明細",
    r"カード.*利用",
]

# プロジェクトマッピング
PROJECT_MAPPING = {
    "aircle": "AirCle",
    "air-cle": "AirCle",
    "クライム": "ClimbBeyond",
    "climb": "ClimbBeyond",
    "beyond": "ClimbBeyond",
    "ポート": "ClimbBeyond",
    "port": "ClimbBeyond",
    "genspark": "Genspark",
    "slidebox": "SlideBox",
    "skywork": "ClientWork",
    "外部案件": "ClientWork",
}

# 経費カテゴリ
EXPENSE_CATEGORIES = {
    "openai": "AI/SaaS",
    "anthropic": "AI/SaaS",
    "claude": "AI/SaaS",
    "gpt": "AI/SaaS",
    "vercel": "AI/SaaS",
    "stripe": "決済手数料",
    "aws": "サーバー",
    "google cloud": "サーバー",
    "adobe": "ソフトウェア",
    "figma": "ソフトウェア",
    "notion": "ソフトウェア",
    "zoom": "通信費",
    "交通": "交通費",
    "タクシー": "交通費",
    "uber": "交通費",
    "ホテル": "宿泊費",
    "飲食": "会議費",
    "amazon": "消耗品",
}


def get_access_token() -> str:
    """有効なaccess tokenを取得"""
    if TOKEN_CACHE_PATH.exists():
        with open(TOKEN_CACHE_PATH) as f:
            cache = json.load(f)
        refreshed_at = datetime.fromisoformat(cache.get('refreshed_at', '2000-01-01T00:00:00+09:00'))
        if datetime.now(JST) - refreshed_at < timedelta(minutes=30):
            return cache['access_token']
    
    # 新規取得（email_manager.pyと同じロジック）
    from email_manager import get_gmail_credentials
    
    creds = get_gmail_credentials()
    
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'client_id': creds['clientId'],
        'client_secret': creds['clientSecret'],
        'refresh_token': creds['oauthTokenData']['refresh_token'],
        'grant_type': 'refresh_token'
    }).encode()
    
    req = urllib.request.Request(token_url, data=data)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    with urllib.request.urlopen(req) as response:
        token_response = json.loads(response.read())
    
    cache = {
        'access_token': token_response['access_token'],
        'refreshed_at': datetime.now(JST).isoformat()
    }
    with open(TOKEN_CACHE_PATH, 'w') as f:
        json.dump(cache, f)
    
    return token_response['access_token']


def get_all_emails_since(start_date: str, max_results: int = 2000) -> List[Dict]:
    """指定日以降の全メールを取得"""
    access_token = get_access_token()
    
    query = f"after:{start_date}"
    messages = []
    next_page = None
    
    while True:
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=500&q={urllib.parse.quote(query)}"
        if next_page:
            url += f"&pageToken={next_page}"
        
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {access_token}')
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            messages.extend(data.get('messages', []))
            next_page = data.get('nextPageToken')
            
            if not next_page or len(messages) >= max_results:
                break
    
    return messages[:max_results]


def get_email_full(access_token: str, msg_id: str) -> Optional[Dict]:
    """メールの全詳細を取得"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=full"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError:
        return None


def extract_body_and_attachments(payload: Dict) -> Tuple[str, List[Dict]]:
    """メール本文と添付ファイルを抽出"""
    body = ""
    attachments = []
    
    def process_part(part):
        nonlocal body, attachments
        
        mime_type = part.get('mimeType', '')
        
        if part.get('filename') and part.get('body', {}).get('attachmentId'):
            attachments.append({
                'filename': part['filename'],
                'mimeType': mime_type,
                'attachmentId': part['body']['attachmentId'],
                'size': part['body'].get('size', 0)
            })
        elif mime_type == 'text/plain' and part.get('body', {}).get('data'):
            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
        elif part.get('parts'):
            for subpart in part['parts']:
                process_part(subpart)
    
    if payload.get('body', {}).get('data'):
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    
    if payload.get('parts'):
        for part in payload['parts']:
            process_part(part)
    
    # HTMLタグを除去
    body = re.sub(r'<[^>]+>', '', body)
    body = re.sub(r'\s+', ' ', body).strip()
    
    return body, attachments


def is_invoice_email(subject: str, body: str, from_addr: str) -> bool:
    """請求書/領収書メールかどうか判定"""
    full_text = f"{subject} {body} {from_addr}"
    return any(re.search(p, full_text, re.I) for p in INVOICE_KEYWORDS)


def extract_amount(text: str) -> Optional[int]:
    """金額を抽出"""
    patterns = [
        r'¥\s*([\d,]+)',
        r'(\d{1,3}(?:,\d{3})+)\s*円',
        r'(\d+)\s*円',
        r'\$\s*([\d,]+\.?\d*)',
        r'合計[：:]\s*([\d,]+)',
        r'請求金額[：:]\s*([\d,]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount_str = match.group(1).replace(',', '').replace('.', '')
            try:
                return int(amount_str)
            except ValueError:
                continue
    
    return None


def detect_project(text: str) -> Optional[str]:
    """プロジェクトを検出"""
    text_lower = text.lower()
    for keyword, project in PROJECT_MAPPING.items():
        if keyword in text_lower:
            return project
    return None


def detect_category(text: str) -> str:
    """経費カテゴリを検出"""
    text_lower = text.lower()
    for keyword, category in EXPENSE_CATEGORIES.items():
        if keyword in text_lower:
            return category
    return "その他"


def load_processed_invoices() -> set:
    """処理済み請求書IDを読み込み"""
    processed_path = STATE_PATH / "processed_invoices.json"
    if processed_path.exists():
        with open(processed_path) as f:
            return set(json.load(f))
    return set()


def save_processed_invoices(processed: set):
    """処理済み請求書IDを保存"""
    STATE_PATH.mkdir(parents=True, exist_ok=True)
    processed_path = STATE_PATH / "processed_invoices.json"
    with open(processed_path, 'w') as f:
        json.dump(list(processed), f)


def save_expense_record(record: Dict):
    """経費レコードを保存"""
    EXPENSES_PATH.mkdir(parents=True, exist_ok=True)
    
    # 月別ファイルに保存
    date = record.get('date', datetime.now(JST).strftime('%Y-%m-%d'))
    month = date[:7]  # YYYY-MM
    
    filepath = EXPENSES_PATH / f"expenses_{month}.jsonl"
    
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    return filepath


def process_invoices(start_date: str = "2026/01/01") -> Dict:
    """請求書メールを処理"""
    access_token = get_access_token()
    messages = get_all_emails_since(start_date)
    processed = load_processed_invoices()
    
    results = {
        'total_emails': len(messages),
        'invoices_found': 0,
        'new_invoices': 0,
        'total_amount': 0,
        'by_category': {},
        'by_project': {},
        'by_month': {},
        'records': [],
    }
    
    print(f"Processing {len(messages)} emails since {start_date}...")
    
    for i, msg in enumerate(messages):
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(messages)}")
        
        msg_id = msg['id']
        
        # 既に処理済みならスキップ
        if msg_id in processed:
            continue
        
        # メール詳細を取得
        email = get_email_full(access_token, msg_id)
        if not email:
            continue
        
        headers = {h['name'].lower(): h['value'] for h in email['payload'].get('headers', [])}
        subject = headers.get('subject', '')
        from_addr = headers.get('from', '')
        date = headers.get('date', '')
        
        body, attachments = extract_body_and_attachments(email['payload'])
        
        # 請求書かどうか判定
        if not is_invoice_email(subject, body, from_addr):
            continue
        
        results['invoices_found'] += 1
        
        # 金額抽出
        amount = extract_amount(f"{subject} {body}")
        
        # プロジェクト・カテゴリ検出
        project = detect_project(f"{subject} {body} {from_addr}")
        category = detect_category(f"{subject} {body} {from_addr}")
        
        # 日付をパース
        try:
            # 様々な日付形式に対応
            date_parsed = None
            for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S %Z', '%d %b %Y %H:%M:%S %z']:
                try:
                    date_parsed = datetime.strptime(date.split(' (')[0].strip(), fmt)
                    break
                except:
                    continue
            
            if date_parsed:
                date_str = date_parsed.strftime('%Y-%m-%d')
            else:
                date_str = datetime.now(JST).strftime('%Y-%m-%d')
        except:
            date_str = datetime.now(JST).strftime('%Y-%m-%d')
        
        record = {
            'id': msg_id,
            'date': date_str,
            'from': from_addr[:100],
            'subject': subject[:200],
            'amount': amount,
            'category': category,
            'project': project,
            'has_attachment': len(attachments) > 0,
            'attachment_names': [a['filename'] for a in attachments],
            'processed_at': datetime.now(JST).isoformat(),
        }
        
        results['records'].append(record)
        results['new_invoices'] += 1
        
        if amount:
            results['total_amount'] += amount
            results['by_category'][category] = results['by_category'].get(category, 0) + amount
            if project:
                results['by_project'][project] = results['by_project'].get(project, 0) + amount
            
            month = date_str[:7]
            results['by_month'][month] = results['by_month'].get(month, 0) + amount
        
        # レコード保存
        save_expense_record(record)
        processed.add(msg_id)
    
    save_processed_invoices(processed)
    
    return results


def format_report(results: Dict) -> str:
    """レポートを生成"""
    lines = []
    
    lines.append("📊 **請求書・経費レポート**\n")
    lines.append(f"処理メール: {results['total_emails']}件")
    lines.append(f"請求書検出: {results['invoices_found']}件")
    lines.append(f"新規処理: {results['new_invoices']}件")
    lines.append(f"合計金額: ¥{results['total_amount']:,}\n")
    
    if results['by_category']:
        lines.append("**カテゴリ別**")
        for cat, amount in sorted(results['by_category'].items(), key=lambda x: -x[1]):
            lines.append(f"  • {cat}: ¥{amount:,}")
        lines.append("")
    
    if results['by_project']:
        lines.append("**プロジェクト別**")
        for proj, amount in sorted(results['by_project'].items(), key=lambda x: -x[1]):
            lines.append(f"  • {proj}: ¥{amount:,}")
        lines.append("")
    
    if results['by_month']:
        lines.append("**月別**")
        for month, amount in sorted(results['by_month'].items()):
            lines.append(f"  • {month}: ¥{amount:,}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Invoice Manager")
    parser.add_argument("--scan", action="store_true", help="Scan emails for invoices")
    parser.add_argument("--since", type=str, default="2026/01/01", help="Start date (YYYY/MM/DD)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--reset", action="store_true", help="Reset processed invoices")
    args = parser.parse_args()
    
    if args.reset:
        processed_path = STATE_PATH / "processed_invoices.json"
        if processed_path.exists():
            processed_path.unlink()
        print("Processed invoices reset")
        exit(0)
    
    if args.scan:
        results = process_invoices(args.since)
        
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(format_report(results))
