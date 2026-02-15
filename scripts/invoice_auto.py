#!/usr/bin/env python3
"""
領収書自動処理 - 完全版
- 添付ファイルをGoogleドライブにアップロード
- 共有URLを発行
- 重複チェック強化
"""

import json
import urllib.request
import urllib.parse
import base64
import hashlib
import sqlite3
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
SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
PROCESSED_FILE = DATA_PATH / "processed_invoices.json"


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


def load_processed() -> Dict:
    """処理済み情報を読み込み（IDと金額+日付のハッシュ）"""
    if PROCESSED_FILE.exists():
        with open(PROCESSED_FILE) as f:
            data = json.load(f)
            if isinstance(data, list):
                # 旧形式（IDのみ）
                return {'ids': set(data), 'hashes': set()}
            return {'ids': set(data.get('ids', [])), 'hashes': set(data.get('hashes', []))}
    return {'ids': set(), 'hashes': set()}


def save_processed(processed: Dict):
    with open(PROCESSED_FILE, 'w') as f:
        json.dump({
            'ids': list(processed['ids']),
            'hashes': list(processed['hashes'])
        }, f)


def make_invoice_hash(date: str, amount: str, currency: str) -> str:
    """重複チェック用のハッシュ"""
    return hashlib.md5(f"{date}_{amount}_{currency}".encode()).hexdigest()


def search_invoice_emails(gmail_token: str, days: int = 1) -> List[str]:
    since_date = (datetime.now(JST) - timedelta(days=days)).strftime('%Y/%m/%d')
    
    queries = [
        f"from:Anthropic after:{since_date} (receipt OR invoice)",
        f"from:OpenAI after:{since_date} (receipt OR invoice)",
        f"from:Stripe after:{since_date} (receipt OR invoice)",
    ]
    
    message_ids = []
    for query in queries:
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=10&q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {gmail_token}')
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read())
                for msg in data.get('messages', []):
                    message_ids.append(msg['id'])
        except Exception as e:
            print(f"⚠️ Search error: {e}")
    
    return message_ids


def get_email_with_attachments(gmail_token: str, msg_id: str) -> Optional[Dict]:
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=full"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {gmail_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            detail = json.loads(response.read())
    except:
        return None
    
    headers = {h['name'].lower(): h['value'] for h in detail['payload'].get('headers', [])}
    body = extract_body(detail['payload'])
    
    # 添付ファイルを探す
    attachments = []
    def find_attachments(parts):
        for part in parts:
            filename = part.get('filename', '')
            if filename and filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                attachment_id = part['body'].get('attachmentId')
                if attachment_id:
                    attachments.append({
                        'filename': filename,
                        'attachment_id': attachment_id,
                        'mime_type': part.get('mimeType', '')
                    })
            if part.get('parts'):
                find_attachments(part['parts'])
    
    if detail['payload'].get('parts'):
        find_attachments(detail['payload']['parts'])
    
    return {
        'id': msg_id,
        'from': headers.get('from', ''),
        'subject': headers.get('subject', ''),
        'date': headers.get('date', ''),
        'body': body,
        'attachments': attachments,
    }


def extract_body(payload: Dict) -> str:
    body = ""
    
    if payload.get('body', {}).get('data'):
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    elif payload.get('parts'):
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                break
            elif part.get('parts'):
                body = extract_body(part)
                if body:
                    break
    
    body = re.sub(r'<[^>]+>', '', body)
    body = re.sub(r'\s+', ' ', body).strip()
    
    return body


def download_attachment(gmail_token: str, msg_id: str, attachment_id: str) -> bytes:
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}/attachments/{attachment_id}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {gmail_token}')
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        return base64.urlsafe_b64decode(data['data'])


def upload_to_drive(drive_token: str, file_data: bytes, filename: str, mime_type: str) -> Optional[str]:
    """Googleドライブにアップロードして共有URLを返す"""
    boundary = '----WebKitFormBoundary'
    
    metadata = json.dumps({'name': filename, 'mimeType': mime_type})
    
    body_parts = []
    body_parts.append(f'--{boundary}\r\n')
    body_parts.append('Content-Type: application/json; charset=UTF-8\r\n\r\n')
    body_parts.append(f'{metadata}\r\n')
    body_parts.append(f'--{boundary}\r\n')
    body_parts.append(f'Content-Type: {mime_type}\r\n\r\n')
    
    body_data = ''.join(body_parts).encode('utf-8') + file_data + f'\r\n--{boundary}--\r\n'.encode('utf-8')
    
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
    req = urllib.request.Request(url, data=body_data, method='POST')
    req.add_header('Authorization', f'Bearer {drive_token}')
    req.add_header('Content-Type', f'multipart/related; boundary={boundary}')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            file_id = result['id']
    except Exception as e:
        print(f"  ⚠️ Upload failed: {e}")
        return None
    
    # 共有設定
    permission_body = json.dumps({'type': 'anyone', 'role': 'reader'}).encode('utf-8')
    
    permission_url = f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions"
    req = urllib.request.Request(permission_url, data=permission_body, method='POST')
    req.add_header('Authorization', f'Bearer {drive_token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            pass
    except Exception as e:
        print(f"  ⚠️ Permission failed: {e}")
    
    return f"https://drive.google.com/file/d/{file_id}/view"


def extract_invoice_info(email: Dict) -> Optional[Dict]:
    from_addr = email['from'].lower()
    body = email['body']
    
    # Anthropic
    if 'anthropic' in from_addr:
        amount_match = re.search(r'\$\s*([0-9,]+\.?\d*)', body)
        if not amount_match:
            return None
        
        amount_str = amount_match.group(1).replace(',', '')
        amount = int(float(amount_str))
        
        try:
            from email.utils import parsedate_to_datetime
            date_obj = parsedate_to_datetime(email['date'])
            date_str = date_obj.astimezone(JST).strftime('%Y/%m/%d')
        except:
            date_str = datetime.now(JST).strftime('%Y/%m/%d')
        
        return {
            'date': date_str,
            'recipient': '市岡直人',
            'category': 'AI/SaaS',
            'issuer': 'Anthropic, PBC',
            'memo': 'Anthropic API利用料',
            'amount': str(amount),
            'currency': 'USD'
        }
    
    # OpenAI
    elif 'openai' in from_addr:
        amount_match = re.search(r'\$\s*([0-9,]+\.?\d*)', body)
        if not amount_match:
            return None
        
        amount_str = amount_match.group(1).replace(',', '')
        amount = int(float(amount_str))
        
        try:
            from email.utils import parsedate_to_datetime
            date_obj = parsedate_to_datetime(email['date'])
            date_str = date_obj.astimezone(JST).strftime('%Y/%m/%d')
        except:
            date_str = datetime.now(JST).strftime('%Y/%m/%d')
        
        return {
            'date': date_str,
            'recipient': '市岡直人',
            'category': 'AI/SaaS',
            'issuer': 'OpenAI',
            'memo': 'OpenAI API利用料',
            'amount': str(amount),
            'currency': 'USD'
        }
    
    return None


def get_last_row_number(token: str) -> int:
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/A:M"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            values = data.get('values', [])
            
            for i in range(len(values) - 1, 0, -1):
                row = values[i]
                if any(cell.strip() for cell in row[:5] if cell):
                    return i + 1
            
            return 1
    except Exception as e:
        print(f"⚠️ Error getting last row: {e}")
        return 1


def append_rows_to_sheet(token: str, rows: List[List[str]]):
    last_row = get_last_row_number(token)
    next_row = last_row + 1
    
    print(f"\n📝 Last data row: {last_row}, inserting at row {next_row}")
    
    formatted_rows = []
    for row in rows:
        formatted_rows.append([
            row[0],  # 日付
            row[1],  # 宛名
            row[2],  # カテゴリー分け
            row[3],  # 発行者
            row[4],  # メモ
            row[5],  # 金額
            row[6],  # 通貨
            row[7],  # URL（Googleドライブ）
            '',      # 振り込み期日
            'FALSE',
            '', '', ''
        ])
    
    range_name = f"A{next_row}:M{next_row + len(formatted_rows) - 1}"
    body = json.dumps({'values': formatted_rows}).encode('utf-8')
    
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{range_name}?valueInputOption=RAW"
    req = urllib.request.Request(url, data=body, method='PUT')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            print(f"✅ Added {result['updatedRows']} rows to spreadsheet")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ Failed: {e.read().decode()}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=1)
    args = parser.parse_args()
    
    print(f"=== 領収書自動処理 ===")
    print(f"Looking back {args.days} days\n")
    
    gmail_token, drive_token = get_tokens()
    print("✅ Tokens obtained")
    
    processed = load_processed()
    
    message_ids = search_invoice_emails(gmail_token, args.days)
    print(f"Found {len(message_ids)} invoice emails")
    
    new_message_ids = [mid for mid in message_ids if mid not in processed['ids']]
    print(f"New emails: {len(new_message_ids)}\n")
    
    rows_to_add = []
    
    for msg_id in new_message_ids:
        email = get_email_with_attachments(gmail_token, msg_id)
        if not email:
            continue
        
        print(f"📧 {email['subject'][:50]}...")
        
        info = extract_invoice_info(email)
        if not info:
            print(f"  ⚠️ Could not extract invoice info")
            continue
        
        # 重複チェック（金額+日付）
        invoice_hash = make_invoice_hash(info['date'], info['amount'], info['currency'])
        if invoice_hash in processed['hashes']:
            print(f"  ⏭️ Skip: Duplicate (same date+amount)")
            processed['ids'].add(msg_id)
            continue
        
        print(f"  ✅ {info['amount']} {info['currency']} - {info['issuer']}")
        
        # 添付ファイルをDriveにアップロード
        drive_url = ''
        if email['attachments']:
            attachment = email['attachments'][0]  # 最初の添付ファイルを使用
            print(f"  📎 {attachment['filename']}")
            
            file_data = download_attachment(gmail_token, msg_id, attachment['attachment_id'])
            drive_url = upload_to_drive(drive_token, file_data, attachment['filename'], attachment['mime_type'])
            
            if drive_url:
                print(f"  📁 Uploaded: {drive_url}")
        
        row = [
            info['date'],
            info['recipient'],
            info['category'],
            info['issuer'],
            info['memo'],
            info['amount'],
            info['currency'],
            drive_url
        ]
        rows_to_add.append(row)
        processed['ids'].add(msg_id)
        processed['hashes'].add(invoice_hash)
    
    if rows_to_add:
        success = append_rows_to_sheet(drive_token, rows_to_add)
        if success:
            save_processed(processed)
            print("\n✅ Done!")
    else:
        save_processed(processed)  # IDは保存
        print("\n💤 No new invoices to add")


if __name__ == "__main__":
    main()
