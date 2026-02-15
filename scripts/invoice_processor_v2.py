#!/usr/bin/env python3
"""
領収書自動処理 v2
- Gmail添付ファイル（PDF/画像）から領収書を抽出
- OpenAI Vision APIで情報を読み取り
- Google Spreadsheetの既存フォーマットに追記
"""

import json
import urllib.request
import urllib.parse
import base64
import hashlib
import sqlite3
import re
import io
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

# OpenAI API Key (環境変数から)
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


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


def get_invoice_emails(gmail_token: str, since_date: str = None) -> List[Dict]:
    """領収書メールを取得"""
    if not since_date:
        since_date = (datetime.now(JST) - timedelta(days=1)).strftime('%Y/%m/%d')
    
    # Anthropic, OpenAI等の領収書を検索
    queries = [
        f"from:Anthropic after:{since_date}",
        f"from:OpenAI after:{since_date}",
        f"from:Stripe after:{since_date}",
    ]
    
    emails = []
    for query in queries:
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=10&q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url)
        req.add_header('Authorization', f'Bearer {gmail_token}')
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read())
                for msg in data.get('messages', []):
                    email = get_email_with_attachments(gmail_token, msg['id'])
                    if email:
                        emails.append(email)
        except Exception as e:
            print(f"Error searching emails: {e}")
    
    return emails


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
    
    # 添付ファイルを探す
    attachments = []
    parts = detail['payload'].get('parts', [])
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


def extract_invoice_info_with_openai(image_data: bytes, mime_type: str) -> Optional[Dict]:
    """OpenAI Vision APIで領収書から情報を抽出"""
    if not OPENAI_API_KEY:
        print("⚠️ OPENAI_API_KEY not set")
        return None
    
    # 画像をbase64エンコード
    image_b64 = base64.b64encode(image_data).decode('utf-8')
    
    # OpenAI Vision APIリクエスト
    prompt = """この領収書から以下の情報を抽出してJSONで返してください:
{
  "date": "YYYY-MM-DD形式の日付",
  "recipient": "宛名",
  "issuer": "発行者の名前と住所",
  "amount": "金額（数字のみ）",
  "currency": "通貨（JPYまたはUSD）",
  "description": "内容・メモ"
}

日付が見つからない場合は今日の日付を使用してください。
金額はカンマを除いた数字のみで返してください。"""
    
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
        print(f"OpenAI API error: {e}")
    
    return None


def append_to_spreadsheet(drive_token: str, rows: List[List[str]]):
    """スプレッドシートに行を追記（既存フォーマット維持）"""
    # 既存データを読み込み
    url = f"https://www.googleapis.com/drive/v3/files/{SHEET_ID}/export?mimeType=text/csv"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {drive_token}')
    
    with urllib.request.urlopen(req) as response:
        existing_csv = response.read().decode('utf-8')
        existing_lines = existing_csv.strip().split('\n')
    
    # ヘッダー行を取得
    header = existing_lines[0] if existing_lines else ""
    
    # データ行のみ抽出（空行除去）
    data_lines = [line for line in existing_lines[1:] if line.strip() and not line.startswith(',,,,,,,,,FALSE')]
    
    # 新しい行を追加（フォーマット: 日付,宛名,カテゴリー分け,発行者,メモ,金額,通貨,URL,振り込み期日,振り込み,,,）
    for row in rows:
        # row = [date, recipient, category, issuer, memo, amount, currency, url]
        formatted_row = f'{row[0]},{row[1]},{row[2]},"{row[3]}",{row[4]},{row[5]},{row[6]},{row[7]},,FALSE,,,'
        data_lines.append(formatted_row)
    
    # 最終的なCSVを構築
    new_csv = header + '\n' + '\n'.join(data_lines) + '\n' + '\n'.join([',,,,,,,,,FALSE,,,'] * 100)
    
    # スプレッドシート更新
    boundary = '----WebKitFormBoundary'
    body_parts = []
    
    metadata = json.dumps({'mimeType': 'application/vnd.google-apps.spreadsheet'})
    body_parts.append(f'--{boundary}\r\n')
    body_parts.append('Content-Type: application/json; charset=UTF-8\r\n\r\n')
    body_parts.append(f'{metadata}\r\n')
    
    body_parts.append(f'--{boundary}\r\n')
    body_parts.append('Content-Type: text/csv\r\n\r\n')
    body_parts.append(f'{new_csv}\r\n')
    body_parts.append(f'--{boundary}--\r\n')
    
    body_data = ''.join(body_parts).encode('utf-8')
    
    url = f"https://www.googleapis.com/upload/drive/v3/files/{SHEET_ID}?uploadType=multipart"
    req = urllib.request.Request(url, data=body_data, method='PATCH')
    req.add_header('Authorization', f'Bearer {drive_token}')
    req.add_header('Content-Type', f'multipart/related; boundary={boundary}')
    
    with urllib.request.urlopen(req) as response:
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=1)
    args = parser.parse_args()
    
    print("=== 領収書自動処理 v2 ===\n")
    
    # トークン取得
    gmail_token, drive_token = get_tokens()
    print("✅ Tokens obtained")
    
    # 領収書メールを取得
    since_date = (datetime.now(JST) - timedelta(days=args.days)).strftime('%Y/%m/%d')
    emails = get_invoice_emails(gmail_token, since_date)
    print(f"Found {len(emails)} invoice emails")
    
    rows_to_add = []
    
    for email in emails:
        print(f"\n📧 {email['subject'][:50]}...")
        
        for attachment in email['attachments']:
            print(f"  📎 {attachment['filename']}")
            
            # 添付ファイルをダウンロード
            file_data = download_attachment(gmail_token, email['id'], attachment['attachment_id'])
            
            # OpenAI Vision APIで情報抽出
            info = extract_invoice_info_with_openai(file_data, attachment['mime_type'])
            
            if info:
                print(f"  ✅ Extracted: {info['amount']} {info['currency']}")
                
                # カテゴリ判定
                category = "AI/SaaS"
                if 'anthropic' in email['from'].lower():
                    category = "AI/SaaS"
                
                row = [
                    info.get('date', datetime.now(JST).strftime('%Y-%m-%d')),
                    info.get('recipient', '市岡直人'),
                    category,
                    info.get('issuer', ''),
                    info.get('description', email['subject']),
                    str(info.get('amount', '')),
                    info.get('currency', 'JPY'),
                    '',  # URL (後で手動で追加)
                ]
                rows_to_add.append(row)
    
    if rows_to_add:
        print(f"\n📝 Adding {len(rows_to_add)} rows to spreadsheet...")
        append_to_spreadsheet(drive_token, rows_to_add)
        print("✅ Done!")
    else:
        print("\nNo new invoices to add")


if __name__ == "__main__":
    main()
