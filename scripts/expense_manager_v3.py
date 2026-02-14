#!/usr/bin/env python3
"""
経費管理システム v3 - シンプル版
- メール本文から正確な金額抽出
- PDF添付ファイルをGoogle Driveにアップロード
- CSVでエクスポート→Driveにアップロード
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
import csv
import io
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
from Crypto.Cipher import AES

# 設定
JST = timezone(timedelta(hours=9))
SCRIPTS_PATH = Path(__file__).parent
WORKSPACE = Path("/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared")
DATA_PATH = WORKSPACE / "data/expenses"
DATA_PATH.mkdir(parents=True, exist_ok=True)

N8N_DB_PATH = Path("/tmp/n8n_db.sqlite")
N8N_ENCRYPTION_KEY = "effdc06a2c03977ec7f117f4e3f0841fb3f5817e18ba096b973b0fd6115c9ceb"

# Drive folder/sheet IDs (from previous creation)
DRIVE_FOLDER_ID = "1oLO6kGT31AV780TzymtC6puZ9vM8xqMH"
DRIVE_FOLDER_URL = f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}"

# 請求書キーワード
INVOICE_KEYWORDS = [
    "請求書", "領収書", "receipt", "invoice", "お支払い",
    "ご利用明細", "決済完了", "payment", "ご請求", "お振込",
    "購入", "注文確認", "order confirmation", "billing"
]


def decrypt_n8n_credential(encrypted_data: str, encryption_key: str) -> dict:
    """n8nのcredentialを復号"""
    data = base64.b64decode(encrypted_data)
    if data[:8] != b'Salted__':
        raise ValueError("Invalid format")
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
    decrypted = decrypted[:-padding_len]
    
    return json.loads(decrypted.decode('utf-8'))


def get_tokens() -> Tuple[str, str]:
    """Gmail and Drive tokens"""
    subprocess.run(
        ["docker", "cp", "n8n:/home/node/.n8n/database.sqlite", str(N8N_DB_PATH)],
        capture_output=True
    )
    
    conn = sqlite3.connect(N8N_DB_PATH)
    cursor = conn.cursor()
    
    # Gmail
    cursor.execute("SELECT data FROM credentials_entity WHERE type='gmailOAuth2'")
    gmail_creds = decrypt_n8n_credential(cursor.fetchone()[0], N8N_ENCRYPTION_KEY)
    
    # Drive
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


def get_email_full(gmail_token: str, msg_id: str) -> Optional[Dict]:
    """メール全文を取得"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=full"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {gmail_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except:
        return None


def extract_email_parts(payload: Dict) -> Tuple[str, str, List[Dict]]:
    """メール本文と添付ファイルを抽出"""
    text_body = ""
    html_body = ""
    attachments = []
    
    def process_part(part):
        nonlocal text_body, html_body, attachments
        
        mime_type = part.get('mimeType', '')
        filename = part.get('filename', '')
        body = part.get('body', {})
        
        if filename and body.get('attachmentId'):
            attachments.append({
                'filename': filename,
                'mimeType': mime_type,
                'attachmentId': body['attachmentId'],
                'size': body.get('size', 0)
            })
        elif mime_type == 'text/plain' and body.get('data'):
            text_body = base64.urlsafe_b64decode(body['data']).decode('utf-8', errors='ignore')
        elif mime_type == 'text/html' and body.get('data'):
            html_body = base64.urlsafe_b64decode(body['data']).decode('utf-8', errors='ignore')
        
        for subpart in part.get('parts', []):
            process_part(subpart)
    
    process_part(payload)
    
    return text_body, html_body, attachments


def get_attachment(gmail_token: str, msg_id: str, attachment_id: str) -> bytes:
    """添付ファイルをダウンロード"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}/attachments/{attachment_id}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {gmail_token}')
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        return base64.urlsafe_b64decode(data['data'])


def upload_to_drive(drive_token: str, file_data: bytes, filename: str, mime_type: str) -> str:
    """ファイルをDriveにアップロード"""
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    metadata = {
        'name': filename,
        'parents': [DRIVE_FOLDER_ID]
    }
    
    body = io.BytesIO()
    body.write(f'--{boundary}\r\n'.encode())
    body.write(b'Content-Type: application/json; charset=UTF-8\r\n\r\n')
    body.write(json.dumps(metadata).encode())
    body.write(f'\r\n--{boundary}\r\n'.encode())
    body.write(f'Content-Type: {mime_type}\r\n\r\n'.encode())
    body.write(file_data)
    body.write(f'\r\n--{boundary}--\r\n'.encode())
    
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,webViewLink"
    req = urllib.request.Request(url, data=body.getvalue(), method='POST')
    req.add_header('Authorization', f'Bearer {drive_token}')
    req.add_header('Content-Type', f'multipart/related; boundary={boundary}')
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        return result.get('webViewLink', '')


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
        (r'(?:Total|Amount)[：:\s]*\$?\s*([\d,]+\.?\d*)', 'USD'),
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


def process_invoices():
    """請求書を処理"""
    print("=== 経費管理システム v3 ===\n")
    
    # トークン取得
    print("Getting tokens...")
    gmail_token, drive_token = get_tokens()
    print("✅ Tokens obtained\n")
    
    # 以前のスキャン結果を読み込み
    scan_result_path = DATA_PATH / "invoices_scan_result.json"
    if not scan_result_path.exists():
        print("No scan result found. Run invoice scanner first.")
        return
    
    with open(scan_result_path) as f:
        scan_data = json.load(f)
    
    invoices = scan_data.get('invoices', [])
    print(f"Processing {len(invoices)} invoices...\n")
    
    # 処理済みID
    processed_path = DATA_PATH / "processed_v3.json"
    if processed_path.exists():
        with open(processed_path) as f:
            processed = set(json.load(f))
    else:
        processed = set()
    
    results = []
    
    for i, inv in enumerate(invoices, 1):
        msg_id = inv['id']
        
        if msg_id in processed:
            continue
        
        print(f"[{i}/{len(invoices)}] {inv['subject'][:50]}...")
        
        email = get_email_full(gmail_token, msg_id)
        if not email:
            continue
        
        headers = {h['name'].lower(): h['value'] for h in email['payload'].get('headers', [])}
        subject = headers.get('subject', '')
        from_addr = headers.get('from', '')
        date_header = headers.get('date', '')
        
        # 本文と添付
        text_body, html_body, attachments = extract_email_parts(email['payload'])
        full_text = html_body or text_body or email.get('snippet', '')
        
        # 金額抽出
        amount_info = extract_amount(full_text)
        
        # 日付
        invoice_date = datetime.now(JST).strftime('%Y-%m-%d')
        try:
            for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%d %b %Y %H:%M:%S %z']:
                try:
                    dt = datetime.strptime(date_header.split(' (')[0].strip(), fmt)
                    invoice_date = dt.strftime('%Y-%m-%d')
                    break
                except:
                    continue
        except:
            pass
        
        # PDF添付をアップロード
        drive_urls = []
        for att in attachments:
            if 'pdf' in att['mimeType'].lower() or att['filename'].lower().endswith('.pdf'):
                try:
                    file_data = get_attachment(gmail_token, msg_id, att['attachmentId'])
                    safe_filename = f"{invoice_date}_{re.sub(r'[^\\w\\-\\.\\s]', '_', att['filename'])}"
                    url = upload_to_drive(drive_token, file_data, safe_filename, att['mimeType'])
                    if url:
                        drive_urls.append(url)
                        print(f"  📎 Uploaded: {safe_filename}")
                except Exception as e:
                    print(f"  ❌ Failed: {att['filename']}")
        
        results.append({
            'date': invoice_date,
            'from': from_addr[:80],
            'subject': subject[:150],
            'amount': amount_info[0] if amount_info else None,
            'currency': amount_info[1] if amount_info else None,
            'attachments': ', '.join(a['filename'] for a in attachments),
            'drive_urls': '\n'.join(drive_urls),
            'msg_id': msg_id,
        })
        
        processed.add(msg_id)
    
    # 処理済み保存
    with open(processed_path, 'w') as f:
        json.dump(list(processed), f)
    
    # CSV出力
    if results:
        csv_path = DATA_PATH / f"expenses_{datetime.now(JST).strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'from', 'subject', 'amount', 'currency', 'attachments', 'drive_urls', 'msg_id'])
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\n✅ CSV saved: {csv_path}")
        
        # CSVをDriveにアップロード
        with open(csv_path, 'rb') as f:
            csv_data = f.read()
        csv_url = upload_to_drive(drive_token, csv_data, csv_path.name, 'text/csv')
        print(f"✅ CSV uploaded to Drive: {csv_url}")
    
    # サマリー
    print(f"\n=== Summary ===")
    print(f"Processed: {len(results)} new invoices")
    total_jpy = sum(r['amount'] for r in results if r['amount'] and r.get('currency') == 'JPY')
    total_usd = sum(r['amount'] for r in results if r['amount'] and r.get('currency') == 'USD')
    print(f"Total JPY: ¥{total_jpy:,}")
    print(f"Total USD: ${total_usd:,}")
    print(f"\n📁 Drive Folder: {DRIVE_FOLDER_URL}")


if __name__ == "__main__":
    process_invoices()
