#!/usr/bin/env python3
"""
経費自動追記システム
- 新しい請求書メールをスキャン
- Google Spreadsheetに追記（Drive API経由でCSVインポート）
"""

import json
import io
import urllib.request
import urllib.parse
import urllib.error
import base64
import hashlib
import sqlite3
import csv
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
from Crypto.Cipher import AES

# 設定
JST = timezone(timedelta(hours=9))
WORKSPACE = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared")
DATA_PATH = WORKSPACE / "data/expenses"
DATA_PATH.mkdir(parents=True, exist_ok=True)

N8N_DB_PATH = Path("/tmp/n8n_db.sqlite")
N8N_ENCRYPTION_KEY = "effdc06a2c03977ec7f117f4e3f0841fb3f5817e18ba096b973b0fd6115c9ceb"

# スプレッドシートID
SHEET_IDS_PATH = DATA_PATH / "sheet_ids.json"

# 請求書キーワード
INVOICE_KEYWORDS = [
    "請求書", "領収書", "receipt", "invoice", "お支払い",
    "ご利用明細", "決済完了", "payment", "ご請求", "お振込",
    "購入", "注文確認", "order confirmation", "billing"
]


def decrypt_n8n_credential(encrypted_data: str, encryption_key: str) -> dict:
    data = base64.b64decode(encrypted_data)
    salt = data[8:16]
    ciphertext = data[16:]
    key_iv = b''
    prev = b''
    while len(key_iv) < 48:
        prev = hashlib.md5(prev + encryption_key.encode() + salt).digest()
        key_iv += prev
    key = key_iv[:32]
    iv = key_iv[32:48]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    padding_len = decrypted[-1]
    return json.loads(decrypted[:-padding_len].decode('utf-8'))


def get_tokens() -> Tuple[str, str]:
    """Gmail and Drive tokens"""
    import subprocess
    subprocess.run(
        ["docker", "cp", "n8n:/home/node/.n8n/database.sqlite", str(N8N_DB_PATH)],
        capture_output=True
    )
    
    conn = sqlite3.connect(N8N_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT data FROM credentials_entity WHERE type='gmailOAuth2'")
    gmail_creds = decrypt_n8n_credential(cursor.fetchone()[0], N8N_ENCRYPTION_KEY)
    
    cursor.execute("SELECT data FROM credentials_entity WHERE type='googleDriveOAuth2Api'")
    drive_creds = decrypt_n8n_credential(cursor.fetchone()[0], N8N_ENCRYPTION_KEY)
    
    conn.close()
    
    def refresh(creds):
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
            return json.loads(response.read())['access_token']
    
    return refresh(gmail_creds), refresh(drive_creds)


def download_spreadsheet_as_csv(drive_token: str, file_id: str) -> Tuple[List[Dict], List[str]]:
    """スプレッドシートをCSVとしてダウンロード（ヘッダー含む）"""
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType=text/csv"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {drive_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            csv_content = response.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(csv_content))
            return list(reader), reader.fieldnames or []
    except Exception as e:
        print(f"Failed to download spreadsheet: {e}")
        return [], []


def get_spreadsheet_headers(drive_token: str, file_id: str) -> List[str]:
    """スプレッドシートのヘッダー（列名）を取得"""
    data, headers = download_spreadsheet_as_csv(drive_token, file_id)
    return headers


def update_spreadsheet(drive_token: str, file_id: str, rows: List[Dict]):
    """スプレッドシートを更新（全体を置き換え）"""
    if not rows:
        return True
    
    # 既存のヘッダーを取得
    headers = get_spreadsheet_headers(drive_token, file_id)
    if not headers:
        # デフォルトヘッダー
        headers = ['日付', '件名', '金額', '通貨', 'カテゴリ', 'プロジェクト', 'Drive URL', 'メールID']
    
    # CSVを生成
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
    
    csv_bytes = csv_buffer.getvalue().encode('utf-8')
    
    # 既存ファイルを更新（PATCH）
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    body = io.BytesIO()
    body.write(f'--{boundary}\r\n'.encode())
    body.write(b'Content-Type: text/csv\r\n\r\n')
    body.write(csv_bytes)
    body.write(f'\r\n--{boundary}--\r\n'.encode())
    
    url = f"https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=multipart"
    req = urllib.request.Request(url, data=body.getvalue(), method='PATCH')
    req.add_header('Authorization', f'Bearer {drive_token}')
    req.add_header('Content-Type', f'multipart/related; boundary={boundary}')
    
    try:
        with urllib.request.urlopen(req) as response:
            return True
    except Exception as e:
        print(f"Failed to update spreadsheet: {e}")
        return False


def classify_email(subject: str, from_addr: str, snippet: str) -> Tuple[str, str, str]:
    """メールを分類（type, category, project）"""
    from_lower = from_addr.lower()
    
    # 収入判定
    if 'お支払いがありました' in subject:
        return 'income', 'Stripe入金', ''
    if 'Readdy AI動画作成' in subject:
        return 'income', '案件受注', 'ClientWork'
    if 'ClimbBeyonの適格請求書' in subject:
        return 'income', '案件受注', 'ClimbBeyond'
    
    # ノイズ判定
    if '失敗' in subject:
        return 'noise', '', ''
    if any(w in subject for w in ['融資', 'ピンチ', 'おすすめ', 'ログイン状態', '銀行口座を登録']):
        return 'noise', '', ''
    if '署名・合意' in subject:
        return 'noise', '', ''
    
    # 経費カテゴリ分類
    category = 'その他'
    project = ''
    
    if 'trip.com' in from_lower:
        category, project = '交通費', '移動'
    elif 'x receipt' in subject.lower() or 'from x' in subject.lower():
        category, project = 'X広告', 'AirCle/マーケ'
    elif 'canva' in subject.lower():
        category, project = 'AI/SaaS', 'AirCle'
    elif 'studio veco' in subject.lower():
        category, project = 'AI/SaaS', 'AirCle'
    elif 'aqua voice' in subject.lower():
        category, project = 'AI/SaaS', 'AirCle'
    elif 'imobie' in subject.lower() or 'mainfunc' in subject.lower():
        category, project = 'AI/SaaS', ''
    elif '西日本シティ銀行' in subject:
        category, project = '振込手数料', ''
    elif 'バーチャルオフィス' in subject:
        category, project = '事務所', 'AirCle'
    elif 'apple' in from_lower:
        category, project = 'その他', ''
    
    return 'expense', category, project


def extract_amount(text: str) -> Optional[Tuple[int, str]]:
    """金額抽出"""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    patterns = [
        (r'(?:合計|総額|請求金額|お支払い金額|ご利用金額)[：:\s]*[¥￥]?\s*([\d,]+)', 'JPY'),
        (r'[¥￥]\s*([\d,]+)', 'JPY'),
        (r'(\d{1,3}(?:,\d{3})+)\s*円', 'JPY'),
        (r'(\d+)\s*円', 'JPY'),
        (r'\$\s*([\d,]+\.?\d*)', 'USD'),
        (r'USD\s*([\d,]+\.?\d*)', 'USD'),
    ]
    
    for pattern, currency in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                amount = int(float(amount_str))
                if 1 <= amount <= 100000000:
                    return amount, currency
            except:
                continue
    
    return None


def scan_new_invoices(gmail_token: str, since_date: str = None) -> List[Dict]:
    """新しい請求書メールをスキャン"""
    if not since_date:
        since_date = (datetime.now(JST) - timedelta(days=1)).strftime('%Y/%m/%d')
    
    query = f"after:{since_date}"
    messages = []
    
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=100&q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {gmail_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            messages = data.get('messages', [])
    except:
        return []
    
    invoices = []
    
    for msg in messages:
        msg_id = msg['id']
        
        # メタデータ取得
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {gmail_token}')
        
        try:
            with urllib.request.urlopen(req) as response:
                detail = json.loads(response.read())
        except:
            continue
        
        headers = {h['name'].lower(): h['value'] for h in detail['payload'].get('headers', [])}
        subject = headers.get('subject', '')
        from_addr = headers.get('from', '')
        snippet = detail.get('snippet', '')
        
        # 請求書かどうか判定
        full_text = f"{subject} {snippet}"
        is_invoice = any(kw in full_text for kw in INVOICE_KEYWORDS)
        
        if is_invoice:
            # 分類
            email_type, category, project = classify_email(subject, from_addr, snippet)
            
            if email_type == 'noise':
                continue
            
            # 金額抽出
            amount_info = extract_amount(full_text)
            
            # 日付
            invoice_date = datetime.now(JST).strftime('%Y-%m-%d')
            try:
                date_header = headers.get('date', '')
                for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%d %b %Y %H:%M:%S %z']:
                    try:
                        dt = datetime.strptime(date_header.split(' (')[0].strip(), fmt)
                        invoice_date = dt.strftime('%Y-%m-%d')
                        break
                    except:
                        continue
            except:
                pass
            
            invoices.append({
                'type': email_type,
                'date': invoice_date,
                'subject': subject[:80],
                'from': from_addr[:50],
                'amount': amount_info[0] if amount_info else None,
                'currency': amount_info[1] if amount_info else None,
                'category': category,
                'project': project,
                'msg_id': msg_id,
            })
    
    return invoices


def append_to_spreadsheets(drive_token: str, new_items: List[Dict]):
    """スプレッドシートに追記"""
    if not SHEET_IDS_PATH.exists():
        print("Sheet IDs not found")
        return
    
    with open(SHEET_IDS_PATH) as f:
        sheet_ids = json.load(f)
    
    # 処理済みIDを取得
    processed_path = DATA_PATH / "processed_msg_ids.json"
    if processed_path.exists():
        with open(processed_path) as f:
            processed = set(json.load(f))
    else:
        processed = set()
    
    # 新規のみフィルタ
    new_items = [i for i in new_items if i['msg_id'] not in processed]
    
    if not new_items:
        print("No new items to add")
        return
    
    # 経費を追記
    expenses = [i for i in new_items if i['type'] == 'expense' and i['amount']]
    if expenses:
        existing, existing_headers = download_spreadsheet_as_csv(drive_token, sheet_ids['expense_sheet_id'])
        
        for e in expenses:
            row = {
                '日付': e['date'],
                '件名': e['subject'],
                '金額': str(e['amount']),
                '通貨': e['currency'],
                'カテゴリ': e['category'],
                'プロジェクト': e.get('project', ''),
                'Drive URL': '',
                'メールID': e['msg_id'],
            }
            # 既存のヘッダーに合わせてフィルタリング
            filtered_row = {}
            for k in existing_headers:
                if k in row:
                    filtered_row[k] = row[k]
                elif existing and k in existing[0]:
                    filtered_row[k] = existing[0].get(k, '')
                else:
                    filtered_row[k] = ''
            existing.append(filtered_row)
        
        if update_spreadsheet(drive_token, sheet_ids['expense_sheet_id'], existing):
            print(f"✅ {len(expenses)} expenses added to spreadsheet")
    
    # 収入を追記
    income = [i for i in new_items if i['type'] == 'income' and i['amount']]
    if income:
        existing, existing_headers = download_spreadsheet_as_csv(drive_token, sheet_ids['income_sheet_id'])
        
        for i in income:
            row = {
                '日付': i['date'],
                '件名': i['subject'],
                '金額': str(i['amount']),
                '通貨': i['currency'],
                'カテゴリ': i['category'],
                '詳細': '',
                'メールID': i['msg_id'],
            }
            # 既存のヘッダーに合わせてフィルタリング
            filtered_row = {}
            for k in existing_headers:
                if k in row:
                    filtered_row[k] = row[k]
                elif existing and k in existing[0]:
                    filtered_row[k] = existing[0].get(k, '')
                else:
                    filtered_row[k] = ''
            existing.append(filtered_row)
        
        if update_spreadsheet(drive_token, sheet_ids['income_sheet_id'], existing):
            print(f"✅ {len(income)} income items added to spreadsheet")
    
    # 処理済みに追加
    for item in new_items:
        if item['amount']:
            processed.add(item['msg_id'])
    
    with open(processed_path, 'w') as f:
        json.dump(list(processed), f)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=1, help='Days to look back')
    args = parser.parse_args()
    
    print(f"=== 経費自動追記 ===")
    print(f"Looking back {args.days} days\n")
    
    # トークン取得
    gmail_token, drive_token = get_tokens()
    print("✅ Tokens obtained")
    
    # 新しい請求書をスキャン
    since_date = (datetime.now(JST) - timedelta(days=args.days)).strftime('%Y/%m/%d')
    new_items = scan_new_invoices(gmail_token, since_date)
    print(f"Found {len(new_items)} invoice-related emails")
    
    if new_items:
        # スプレッドシートに追記
        append_to_spreadsheets(drive_token, new_items)
    
    print("\n✅ Done")


if __name__ == "__main__":
    main()
