#!/usr/bin/env python3
"""
経費管理システム v2 - 高品質版
- メール本文から正確な金額抽出
- PDF添付ファイルをGoogle Driveにアップロード
- Google Spreadsheetに記録
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
DATA_PATH = WORKSPACE / "data/expenses"
DATA_PATH.mkdir(parents=True, exist_ok=True)

N8N_DB_PATH = Path("/tmp/n8n_db.sqlite")
N8N_ENCRYPTION_KEY = "effdc06a2c03977ec7f117f4e3f0841fb3f5817e18ba096b973b0fd6115c9ceb"
GMAIL_TOKEN_PATH = Path("/tmp/gmail_token.json")
DRIVE_TOKEN_PATH = Path("/tmp/google_drive_token.json")
SHEETS_TOKEN_PATH = Path("/tmp/google_sheets_token.json")

# Google Drive フォルダ名
DRIVE_FOLDER_NAME = "お金関係_経費管理"

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


def get_google_credentials(cred_type: str) -> dict:
    """n8nからGoogle認証情報を取得"""
    subprocess.run(
        ["docker", "cp", "n8n:/home/node/.n8n/database.sqlite", str(N8N_DB_PATH)],
        capture_output=True
    )
    
    conn = sqlite3.connect(N8N_DB_PATH)
    cursor = conn.cursor()
    
    if cred_type == "gmail":
        cursor.execute("SELECT data FROM credentials_entity WHERE type='gmailOAuth2'")
    elif cred_type == "drive":
        cursor.execute("SELECT data FROM credentials_entity WHERE type='googleDriveOAuth2Api'")
    elif cred_type == "sheets":
        # SheetsはDriveと同じtokenで使える場合が多い
        cursor.execute("SELECT data FROM credentials_entity WHERE type='googleDriveOAuth2Api'")
    elif cred_type == "calendar":
        cursor.execute("SELECT data FROM credentials_entity WHERE type='googleCalendarOAuth2Api'")
    elif cred_type == "tasks":
        cursor.execute("SELECT data FROM credentials_entity WHERE type='googleTasksOAuth2Api'")
    else:
        cursor.execute("SELECT data FROM credentials_entity WHERE type LIKE '%google%' LIMIT 1")
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise ValueError(f"{cred_type} credentials not found")
    
    return decrypt_n8n_credential(row[0], N8N_ENCRYPTION_KEY)


def refresh_token(creds: dict, token_cache_path: Path) -> str:
    """Access tokenをリフレッシュ"""
    # キャッシュ確認
    if token_cache_path.exists():
        with open(token_cache_path) as f:
            cache = json.load(f)
        refreshed_at = datetime.fromisoformat(cache.get('refreshed_at', '2000-01-01T00:00:00+09:00'))
        if datetime.now(JST) - refreshed_at < timedelta(minutes=30):
            return cache['access_token']
    
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
    with open(token_cache_path, 'w') as f:
        json.dump(cache, f)
    
    return token_response['access_token']


def get_gmail_token() -> str:
    creds = get_google_credentials("gmail")
    return refresh_token(creds, GMAIL_TOKEN_PATH)


def get_drive_token() -> str:
    # 専用のDrive token取得
    creds = get_google_credentials("drive")
    return refresh_token(creds, DRIVE_TOKEN_PATH)


def get_sheets_token() -> str:
    # DriveトークンでSheetsも使える
    creds = get_google_credentials("drive")
    return refresh_token(creds, SHEETS_TOKEN_PATH)


# ========== Gmail Functions ==========

def get_email_full_body(access_token: str, msg_id: str) -> Dict:
    """メールの完全な詳細を取得"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=full"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError:
        return None


def extract_email_parts(payload: Dict) -> Tuple[str, str, List[Dict]]:
    """メール本文（plain/html）と添付ファイルを抽出"""
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


def get_attachment(access_token: str, msg_id: str, attachment_id: str) -> bytes:
    """添付ファイルをダウンロード"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}/attachments/{attachment_id}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        return base64.urlsafe_b64decode(data['data'])


def extract_amount_from_text(text: str) -> Optional[Tuple[int, str]]:
    """テキストから金額を抽出（通貨も検出）"""
    # HTMLタグを除去
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    # 金額パターン（優先度順）
    patterns = [
        # 日本円
        (r'(?:合計|総額|請求金額|お支払い金額|ご利用金額)[：:\s]*[¥￥]?\s*([\d,]+)\s*円?', 'JPY'),
        (r'[¥￥]\s*([\d,]+)', 'JPY'),
        (r'(\d{1,3}(?:,\d{3})+)\s*円', 'JPY'),
        (r'(\d+)\s*円', 'JPY'),
        # USD
        (r'\$\s*([\d,]+\.?\d*)', 'USD'),
        (r'USD\s*([\d,]+\.?\d*)', 'USD'),
        # 汎用
        (r'(?:Total|Amount|Subtotal)[：:\s]*\$?\s*([\d,]+\.?\d*)', 'USD'),
    ]
    
    for pattern, currency in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                if '.' in amount_str:
                    amount = int(float(amount_str))
                else:
                    amount = int(amount_str)
                
                # 金額が妥当な範囲か確認
                if 1 <= amount <= 100000000:  # 1円〜1億円
                    return amount, currency
            except ValueError:
                continue
    
    return None


def extract_date_from_text(text: str) -> Optional[str]:
    """テキストから日付を抽出"""
    patterns = [
        r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})',
        r'(\d{1,2})[月/](\d{1,2})[日/](\d{4})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups[0]) == 4:
                return f"{groups[0]}-{int(groups[1]):02d}-{int(groups[2]):02d}"
            else:
                return f"{groups[2]}-{int(groups[0]):02d}-{int(groups[1]):02d}"
    
    return None


# ========== Google Drive Functions ==========

def find_or_create_folder(access_token: str, folder_name: str, parent_id: str = None) -> str:
    """フォルダを検索、なければ作成"""
    # 検索
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        if data.get('files'):
            return data['files'][0]['id']
    
    # 作成
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        metadata['parents'] = [parent_id]
    
    url = "https://www.googleapis.com/drive/v3/files"
    req = urllib.request.Request(url, data=json.dumps(metadata).encode(), method='POST')
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        return data['id']


def upload_file_to_drive(access_token: str, file_data: bytes, filename: str, folder_id: str, mime_type: str) -> Dict:
    """ファイルをDriveにアップロード"""
    import io
    
    metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    
    # multipart upload
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
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
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', f'multipart/related; boundary={boundary}')
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())


# ========== Google Sheets Functions ==========

def find_or_create_spreadsheet(access_token: str, title: str, folder_id: str = None) -> str:
    """スプレッドシートを検索、なければ作成"""
    # 検索
    query = f"name='{title}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
    url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        if data.get('files'):
            return data['files'][0]['id']
    
    # Sheets APIで作成
    spreadsheet = {
        'properties': {'title': title},
        'sheets': [{
            'properties': {'title': '経費一覧'},
            'data': [{
                'startRow': 0,
                'startColumn': 0,
                'rowData': [{
                    'values': [
                        {'userEnteredValue': {'stringValue': '日付'}},
                        {'userEnteredValue': {'stringValue': '送信者'}},
                        {'userEnteredValue': {'stringValue': '件名'}},
                        {'userEnteredValue': {'stringValue': '金額'}},
                        {'userEnteredValue': {'stringValue': '通貨'}},
                        {'userEnteredValue': {'stringValue': 'カテゴリ'}},
                        {'userEnteredValue': {'stringValue': 'プロジェクト'}},
                        {'userEnteredValue': {'stringValue': '添付ファイル'}},
                        {'userEnteredValue': {'stringValue': 'Drive URL'}},
                        {'userEnteredValue': {'stringValue': 'メールID'}},
                    ]
                }]
            }]
        }]
    }
    
    url = "https://sheets.googleapis.com/v4/spreadsheets"
    req = urllib.request.Request(url, data=json.dumps(spreadsheet).encode(), method='POST')
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        sheet_id = data['spreadsheetId']
    
    # フォルダに移動
    if folder_id:
        url = f"https://www.googleapis.com/drive/v3/files/{sheet_id}?addParents={folder_id}"
        req = urllib.request.Request(url, method='PATCH')
        req.add_header('Authorization', f'Bearer {access_token}')
        try:
            with urllib.request.urlopen(req) as response:
                pass
        except:
            pass
    
    return sheet_id


def append_to_sheet(access_token: str, spreadsheet_id: str, row_data: List) -> bool:
    """スプレッドシートに行を追加"""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/経費一覧!A:J:append?valueInputOption=USER_ENTERED"
    
    body = {
        'values': [row_data]
    }
    
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method='POST')
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            return True
    except Exception as e:
        print(f"Error appending to sheet: {e}")
        return False


# ========== Main Processing ==========

def process_invoice_email(gmail_token: str, drive_token: str, msg_id: str, folder_id: str) -> Optional[Dict]:
    """1つの請求書メールを処理"""
    email = get_email_full_body(gmail_token, msg_id)
    if not email:
        return None
    
    headers = {h['name'].lower(): h['value'] for h in email['payload'].get('headers', [])}
    subject = headers.get('subject', '')
    from_addr = headers.get('from', '')
    date_header = headers.get('date', '')
    
    # 本文と添付ファイルを抽出
    text_body, html_body, attachments = extract_email_parts(email['payload'])
    
    # 金額抽出（HTML優先、なければテキスト）
    amount_info = None
    full_text = html_body or text_body or email.get('snippet', '')
    amount_info = extract_amount_from_text(full_text)
    
    # 日付抽出
    invoice_date = extract_date_from_text(full_text)
    if not invoice_date:
        # メールヘッダーから
        try:
            for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%d %b %Y %H:%M:%S %z']:
                try:
                    dt = datetime.strptime(date_header.split(' (')[0].strip(), fmt)
                    invoice_date = dt.strftime('%Y-%m-%d')
                    break
                except:
                    continue
        except:
            invoice_date = datetime.now(JST).strftime('%Y-%m-%d')
    
    if not invoice_date:
        invoice_date = datetime.now(JST).strftime('%Y-%m-%d')
    
    # PDF添付ファイルをDriveにアップロード
    drive_urls = []
    for att in attachments:
        if att['mimeType'] == 'application/pdf' or att['filename'].lower().endswith('.pdf'):
            try:
                file_data = get_attachment(gmail_token, msg_id, att['attachmentId'])
                
                # ファイル名を日付付きに
                safe_filename = f"{invoice_date}_{att['filename']}"
                safe_filename = re.sub(r'[^\w\-\.\s]', '_', safe_filename)
                
                result = upload_file_to_drive(drive_token, file_data, safe_filename, folder_id, att['mimeType'])
                if result.get('webViewLink'):
                    drive_urls.append(result['webViewLink'])
                    print(f"  📎 Uploaded: {safe_filename}")
            except Exception as e:
                print(f"  ❌ Failed to upload {att['filename']}: {e}")
    
    return {
        'msg_id': msg_id,
        'date': invoice_date,
        'from': from_addr[:100],
        'subject': subject[:200],
        'amount': amount_info[0] if amount_info else None,
        'currency': amount_info[1] if amount_info else None,
        'attachments': [a['filename'] for a in attachments],
        'drive_urls': drive_urls,
    }


def main():
    print("=== 経費管理システム v2 ===\n")
    
    # トークン取得
    print("Getting tokens...")
    gmail_token = get_gmail_token()
    drive_token = get_drive_token()
    sheets_token = get_sheets_token()
    
    # Driveフォルダ作成
    print(f"Creating Drive folder: {DRIVE_FOLDER_NAME}")
    folder_id = find_or_create_folder(drive_token, DRIVE_FOLDER_NAME)
    folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
    print(f"  Folder URL: {folder_url}")
    
    # スプレッドシート作成
    print("Creating spreadsheet...")
    sheet_id = find_or_create_spreadsheet(sheets_token, "経費管理_2026", folder_id)
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
    print(f"  Spreadsheet URL: {sheet_url}")
    
    # 以前のスキャン結果を読み込み
    scan_result_path = DATA_PATH / "invoices_scan_result.json"
    if not scan_result_path.exists():
        print("No previous scan result found. Run invoice scanner first.")
        return
    
    with open(scan_result_path) as f:
        scan_data = json.load(f)
    
    invoices = scan_data.get('invoices', [])
    print(f"\nProcessing {len(invoices)} invoices...\n")
    
    # 処理済みIDを追跡
    processed_path = DATA_PATH / "processed_invoices_v2.json"
    if processed_path.exists():
        with open(processed_path) as f:
            processed = set(json.load(f))
    else:
        processed = set()
    
    results = []
    for i, inv in enumerate(invoices, 1):
        msg_id = inv['id']
        
        if msg_id in processed:
            print(f"[{i}/{len(invoices)}] Already processed: {inv['subject'][:40]}...")
            continue
        
        print(f"[{i}/{len(invoices)}] Processing: {inv['subject'][:40]}...")
        
        result = process_invoice_email(gmail_token, drive_token, msg_id, folder_id)
        if result:
            results.append(result)
            
            # スプレッドシートに追加
            row = [
                result['date'],
                result['from'],
                result['subject'],
                result['amount'] or '',
                result['currency'] or '',
                '',  # カテゴリ（後で手動設定）
                '',  # プロジェクト（後で手動設定）
                ', '.join(result['attachments']),
                '\n'.join(result['drive_urls']) if result['drive_urls'] else '',
                result['msg_id'],
            ]
            
            if append_to_sheet(sheets_token, sheet_id, row):
                print(f"  ✅ Added to sheet")
                processed.add(msg_id)
            else:
                print(f"  ❌ Failed to add to sheet")
    
    # 処理済みを保存
    with open(processed_path, 'w') as f:
        json.dump(list(processed), f)
    
    # サマリー
    print(f"\n=== Summary ===")
    print(f"Processed: {len(results)} invoices")
    total_jpy = sum(r['amount'] for r in results if r['amount'] and r.get('currency') == 'JPY')
    total_usd = sum(r['amount'] for r in results if r['amount'] and r.get('currency') == 'USD')
    print(f"Total JPY: ¥{total_jpy:,}")
    print(f"Total USD: ${total_usd:,}")
    print(f"\n📁 Drive Folder: {folder_url}")
    print(f"📊 Spreadsheet: {sheet_url}")


if __name__ == "__main__":
    main()
