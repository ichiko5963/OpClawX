#!/usr/bin/env python3
"""
Invoice Creator using n8n credentials
"""

import json
import base64
import hashlib
import sqlite3
from Crypto.Cipher import AES
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# n8n DBから認証情報を取得
N8N_DB_PATH = "/tmp/n8n_db.sqlite"
encryption_key = "effdc06a2c03977ec7f117f4e3f0841fb3f5817e18ba096b973b0fd6115c9ceb"

def decrypt_n8n_credential(encrypted_data):
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
    return decrypted.rstrip(b' \x0b')

def get_n8n_credentials(cred_name):
    conn = sqlite3.connect(N8N_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM credentials_entity WHERE name = ?", (cred_name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(decrypt_n8n_credential(row[0]))
    return None

def create_invoice(company_name, items, title, due_date, invoice_date=None):
    """請求書作成"""
    # 認証取得
    creds_data = get_n8n_credentials("Google Drive account")
    if not creds_data:
        raise Exception("Google Drive credentials not found")
    
    # Credentials作成
    oauth_data = creds_data['oauthTokenData']
    creds = Credentials(
        token=oauth_data['access_token'],
        refresh_token=oauth_data['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=creds_data['clientId'],
        client_secret=creds_data['clientSecret'],
        scopes=oauth_data['scope'].split()
    )
    
    # APIサービス作成
    drive = build('drive', 'v3', credentials=creds)
    docs = build('docs', 'v1', credentials=creds)
    sheets = build('sheets', 'v4', credentials=creds)
    
    # 請求書番号取得
    SPREADSHEET_ID = '1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990'
    result = sheets.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='A:A').execute()
    values = result.get('values', [])
    if len(values) > 1:
        last = values[-1][0]
        year, num = last.split('-')
        invoice_no = f'{year}-{int(num)+1:04d}'
    else:
        invoice_no = '2026-0001'
    
    if invoice_date is None:
        invoice_date = datetime.now().strftime('%Y年%m月%d日')
    
    # 計算
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax = int(subtotal * 0.10)
    total = subtotal + tax
    
    print(f"請求書番号: {invoice_no}")
    
    # ドキュメント作成
    doc = docs.documents().create(body={'title': invoice_no}).execute()
    doc_id = doc['documentId']
    
    # 内容作成
    items_text = ""
    for item in items:
        items_text += f"{item['name']:<20} {item['quantity']:>3}    ¥{item['unit_price']:,}    ¥{item['quantity']*item['unit_price']:,}\n"
    
    content = f"""請求書

請求番号: {invoice_no}
請求日: {invoice_date}

宛先: {company_name}
件名: {title}

--------------------------------------------------------------------------------
品名                    数量    単価        金額
--------------------------------------------------------------------------------
{items_text}
                                          小計:    ¥{subtotal:,}
                                          消費税:  ¥{tax:,}
                                          合計:    ¥{total:,}
                                          
================================================================================
支払期限: {due_date}
================================================================================
"""
    
    # ドキュメントに挿入
    docs.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': [{
            'insertText': {'location': {'index': 1}, 'text': content}
        }]}
    ).execute()
    
    # Driveフォルダに移動
    DRIVE_FOLDER_ID = '1oLO6kGT31AV780TzymtC6puZ9vM8xqMH'
    drive.files().update(fileId=doc_id, addParents=DRIVE_FOLDER_ID).execute()
    
    # 共有設定
    drive.permissions().create(fileId=doc_id, body={'type': 'anyone', 'role': 'reader'}).execute()
    
    # リンク取得
    link = drive.files().get(fileId=doc_id, fields='webViewLink').execute()['webViewLink']
    
    # スプレッドシートに記録
    sheets.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range='A:F',
        valueInputOption='USER_ENTERED',
        body={'values': [[invoice_no, company_name, f'¥{total:,}', invoice_date, '作成済み', link]]}
    ).execute()
    
    return {'invoice_no': invoice_no, 'link': link, 'total': total}

if __name__ == '__main__':
    import sys
    
    # デフォルト値（ポート株式会社 Xプレミアム）
    company = "ポート株式会社"
    title = "Xプレミアム2月分"
    due_date = "2026年3月21日"
    items = [
        {'name': 'Xプレミアム(999円)', 'quantity': 1, 'unit_price': 999},
        {'name': 'Xプレミアム(499円)', 'quantity': 1, 'unit_price': 499},
    ]
    
    result = create_invoice(company, items, title, due_date)
    print("=" * 40)
    print("✅ 請求書作成完了!")
    print(f"請求書番号: {result['invoice_no']}")
    print(f"合計: ¥{result['total']:,}")
    print(f"リンク: {result['link']}")
