#!/usr/bin/env python3
"""
Invoice Creator - urllibで直接Google APIアクセス
n8nの認証情報を復号化して使用
"""

import json
import base64
import hashlib
import sqlite3
import urllib.request
import urllib.parse
from datetime import datetime

N8N_DB_PATH = "/tmp/n8n_db.sqlite"
encryption_key = "effdc06a2c03977ec7f117f4e3f0841fb3f5817e18ba096b973b0fd6115c9ceb"
SHEET_ID = "1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990"
FOLDER_ID = "1oLO6kGT31AV780TzymtC6puZ9vM8xqMH"

def decrypt_n8n_credential(encrypted_data):
    from Crypto.Cipher import AES
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
    return json.loads(decrypted.rstrip(b' \x0b').decode('utf-8'))

def get_drive_token():
    conn = sqlite3.connect(N8N_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM credentials_entity WHERE name = 'Google Drive account'")
    row = cursor.fetchone()
    conn.close()
    creds = decrypt_n8n_credential(row[0])
    return creds['oauthTokenData']['access_token'], creds['oauthTokenData']['refresh_token'], creds['clientId'], creds['clientSecret']

def refresh_token(refresh_token, client_id, client_secret):
    url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode()
    
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def create_doc(token, title):
    """Google Docs作成"""
    url = "https://docs.googleapis.com/v1/documents"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    data = json.dumps({'title': title}).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def insert_text(token, doc_id, text):
    """ドキュメントにテキスト插入"""
    url = f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    data = json.dumps({
        'requests': [{
            'insertText': {
                'location': {'index': 1},
                'text': text
            }
        }]
    }).encode()
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    urllib.request.urlopen(req)

def add_to_folder(token, file_id, folder_id):
    """Driveでフォルダに追加"""
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}/parents"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    data = json.dumps({'id': folder_id}).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    urllib.request.urlopen(req)

def share_file(token, file_id):
    """共有設定"""
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    data = json.dumps({'type': 'anyone', 'role': 'reader'}).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    urllib.request.urlopen(req)

def get_link(token, file_id):
    """公開リンク取得"""
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=webViewLink"
    headers = {'Authorization': f'Bearer {token}'}
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())['webViewLink']

def append_sheet(token, values):
    """スプレッドシートに追加"""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/A:F:append?valueInputOption=USER_ENTERED"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    data = json.dumps({'values': [values]}).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    urllib.request.urlopen(req)

def get_last_invoice(token):
    """最後の請求書番号取得"""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/A:A"
    headers = {'Authorization': f'Bearer {token}'}
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        values = json.loads(response.read()).get('values', [])
        if len(values) > 1:
            return values[-1][0]
        return None

def main():
    print("=== 請求書作成 start ===")
    
    # 認証情報取得
    print("1. Getting credentials...")
    access_token, refresh_t, client_id, client_secret = get_drive_token()
    token = access_token
    
    # 請求書番号
    print("2. Getting invoice number...")
    last = get_last_invoice(token)
    if last:
        year, num = last.split('-')
        invoice_no = f"{year}-{int(num)+1:04d}"
    else:
        invoice_no = "2026-0027"
    print(f"   Invoice No: {invoice_no}")
    
    # 内容
    content = f"""請求書

請求番号: {invoice_no}
請求日: 2026年2月21日

宛先: ポート株式会社
件名: Xプレミアム2月分

--------------------------------------------------------------------------------
品名                    数量    単価        金額
--------------------------------------------------------------------------------
Xプレミアム(999円)       1       ¥999        ¥999
Xプレミアム(499円)       1       ¥499        ¥499

                                          小計:    ¥1,498
                                          消費税:  ¥150
                                          合計:    ¥1,648
                                          
================================================================================
支払期限: 2026年3月21日
================================================================================
"""
    
    # ドキュメント作成
    print("3. Creating document...")
    doc = create_doc(token, invoice_no)
    doc_id = doc['documentId']
    print(f"   Doc ID: {doc_id}")
    
    # テキスト插入
    print("4. Inserting content...")
    insert_text(token, doc_id, content)
    
    # フォルダに追加
    print("5. Adding to folder...")
    add_to_folder(token, doc_id, FOLDER_ID)
    
    # 共有設定
    print("6. Sharing...")
    share_file(token, doc_id)
    
    # リンク取得
    print("7. Getting link...")
    link = get_link(token, doc_id)
    
    # スプレッドシートに記録
    print("8. Recording to spreadsheet...")
    append_sheet(token, [invoice_no, 'ポート株式会社', '¥1,648', '2026年2月21日', '作成済み', link])
    
    print("")
    print("=== 完了! ===")
    print(f"請求書番号: {invoice_no}")
    print(f"リンク: {link}")

if __name__ == '__main__':
    main()
