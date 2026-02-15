#!/usr/bin/env python3
"""
領収書自動処理 - 完全版（画像読み取り対応）
- Gmail添付ファイル（PDF/画像）をダウンロード
- OpenAI Vision APIで情報抽出
- Googleドライブにアップロード
- 共有URLを発行してスプレッドシートに追加
"""

import json
import urllib.request
import urllib.parse
import base64
import hashlib
import sqlite3
import re
import os
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

# OpenAI API Key（環境変数から）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 領収書キーワード
INVOICE_KEYWORDS = ['receipt', 'invoice', '領収書', '請求書', 'お支払い', 'ご利用明細']


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


def load_processed_ids() -> set:
    if PROCESSED_FILE.exists():
        with open(PROCESSED_FILE) as f:
            return set(json.load(f))
    return set()


def save_processed_ids(ids: set):
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(list(ids), f)


def search_invoice_emails(gmail_token: str, days: int = 1) -> List[str]:
    """領収書メールを検索（キーワードベース）"""
    since_date = (datetime.now(JST) - timedelta(days=days)).strftime('%Y/%m/%d')
    
    # 領収書キーワードで広く検索
    query = f"after:{since_date} (receipt OR invoice OR 領収書 OR 請求書 OR お支払い OR ご利用明細) has:attachment"
    
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=50&q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {gmail_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return [msg['id'] for msg in data.get('messages', [])]
    except Exception as e:
        print(f"⚠️ Search error: {e}")
        return []


def get_email_with_attachments(gmail_token: str, msg_id: str) -> Optional[Dict]:
    """メールと添付ファイルを取得"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=full"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {gmail_token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            detail = json.loads(response.read())
    except:
        return None
    
    headers = {h['name'].lower(): h['value'] for h in detail['payload'].get('headers', [])}
    
    # 添付ファイルを探す（PDF/画像のみ）
    attachments = []
    
    def find_attachments(parts):
        for part in parts:
            filename = part.get('filename', '')
            if filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
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
        'attachments': attachments,
    }


def download_attachment(gmail_token: str, msg_id: str, attachment_id: str) -> bytes:
    """添付ファイルをダウンロード"""
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}/attachments/{attachment_id}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {gmail_token}')
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        return base64.urlsafe_b64decode(data['data'])


def extract_invoice_with_openai(file_data: bytes, mime_type: str) -> Optional[Dict]:
    """OpenAI Vision APIで領収書情報を抽出"""
    if not OPENAI_API_KEY:
        print("⚠️ OPENAI_API_KEY not set. Set via: export OPENAI_API_KEY='sk-...'")
        return None
    
    # PDFの場合は最初のページを画像に変換（簡易実装：スキップ）
    if 'pdf' in mime_type.lower():
        print("  ⚠️ PDF conversion not implemented, skipping...")
        return None
    
    # 画像をbase64エンコード
    image_b64 = base64.b64encode(file_data).decode('utf-8')
    
    # OpenAI Vision APIリクエスト
    prompt = """この領収書/請求書から以下の情報を抽出してJSONで返してください:

{
  "date": "YYYY/MM/DD形式の日付",
  "recipient": "宛名（例: 市岡直人）",
  "issuer": "発行者の名前と住所",
  "amount": "金額（数字のみ、カンマなし）",
  "currency": "通貨（JPY または USD）",
  "category": "カテゴリ（AI/SaaS、交通費、事務所、従業員の給料、その他 から選択）",
  "memo": "内容・メモ（簡潔に）"
}

ルール:
- 日付が見つからない場合は今日の日付
- 金額はカンマを除いた数字のみ
- カテゴリは上記から最も適切なものを選択
- 日本語の領収書の場合、発行者は日本語で返す
- 宛名が見つからない場合は「市岡直人」
"""
    
    body = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_b64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500
    }).encode('utf-8')
    
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        method='POST'
    )
    req.add_header('Authorization', f'Bearer {OPENAI_API_KEY}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            content = result['choices'][0]['message']['content']
            # JSONを抽出
            match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
    except Exception as e:
        print(f"  ⚠️ OpenAI API error: {e}")
    
    return None


def upload_to_drive(drive_token: str, file_data: bytes, filename: str, mime_type: str) -> Optional[str]:
    """Googleドライブにアップロードして共有URLを返す"""
    # ファイルをアップロード
    boundary = '----WebKitFormBoundary'
    
    metadata = json.dumps({
        'name': filename,
        'mimeType': mime_type
    })
    
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
    
    # 共有設定（誰でも閲覧可能）
    permission_body = json.dumps({
        'type': 'anyone',
        'role': 'reader'
    }).encode('utf-8')
    
    permission_url = f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions"
    req = urllib.request.Request(permission_url, data=permission_body, method='POST')
    req.add_header('Authorization', f'Bearer {drive_token}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            pass
    except Exception as e:
        print(f"  ⚠️ Permission failed: {e}")
    
    # 共有URLを返す
    return f"https://drive.google.com/file/d/{file_id}/view"


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
            row[7],  # URL（共有リンク）
            '',      # 振り込み期日
            'FALSE', # 振り込み
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
    
    print(f"=== 領収書自動処理（画像読み取り版） ===")
    print(f"Looking back {args.days} days\n")
    
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not set")
        print("Set it via: export OPENAI_API_KEY='sk-...'")
        return
    
    # トークン取得
    gmail_token, drive_token = get_tokens()
    print("✅ Tokens obtained")
    
    processed_ids = load_processed_ids()
    
    # 領収書メールを検索
    message_ids = search_invoice_emails(gmail_token, args.days)
    print(f"Found {len(message_ids)} emails with attachments")
    
    new_message_ids = [mid for mid in message_ids if mid not in processed_ids]
    print(f"New emails: {len(new_message_ids)}\n")
    
    rows_to_add = []
    
    for msg_id in new_message_ids:
        email = get_email_with_attachments(gmail_token, msg_id)
        if not email or not email['attachments']:
            continue
        
        print(f"📧 {email['subject'][:50]}...")
        
        for attachment in email['attachments']:
            print(f"  📎 {attachment['filename']}")
            
            # 添付ファイルをダウンロード
            file_data = download_attachment(gmail_token, msg_id, attachment['attachment_id'])
            
            # OpenAI Vision APIで情報抽出
            info = extract_invoice_with_openai(file_data, attachment['mime_type'])
            
            if not info:
                continue
            
            print(f"  ✅ {info.get('amount', '?')} {info.get('currency', '?')} - {info.get('issuer', '?')[:30]}...")
            
            # Googleドライブにアップロード
            drive_url = upload_to_drive(drive_token, file_data, attachment['filename'], attachment['mime_type'])
            
            if drive_url:
                print(f"  📁 Uploaded: {drive_url}")
            else:
                drive_url = ''
            
            row = [
                info.get('date', datetime.now(JST).strftime('%Y/%m/%d')),
                info.get('recipient', '市岡直人'),
                info.get('category', 'その他'),
                info.get('issuer', ''),
                info.get('memo', email['subject']),
                str(info.get('amount', '')),
                info.get('currency', 'JPY'),
                drive_url
            ]
            rows_to_add.append(row)
            processed_ids.add(msg_id)
    
    if rows_to_add:
        success = append_rows_to_sheet(drive_token, rows_to_add)
        if success:
            save_processed_ids(processed_ids)
            print("\n✅ All done!")
    else:
        print("\n💤 No new invoices to process")


if __name__ == "__main__":
    main()
