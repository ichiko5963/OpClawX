#!/usr/bin/env python3
"""
経費領収書を処理
1. Google Driveアップロード
2. 経費領収書シートのA3（上から3番目）に挿入
"""
import sys
import json
import requests
from pathlib import Path

TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")
SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
EXPENSE_SHEET_NAME = "2026年経費領収書"
DRIVE_FOLDER_NAME = "法人領収書まとめ"

def load_token():
    """OAuth token読み込み"""
    data = json.loads(TOKEN_FILE.read_text())
    
    # Access token取得
    url = "https://oauth2.googleapis.com/token"
    response = requests.post(url, data={
        'client_id': data['client_id'],
        'client_secret': data['client_secret'],
        'refresh_token': data['refresh_token'],
        'grant_type': 'refresh_token'
    })
    
    return response.json()['access_token']

def get_or_create_folder(access_token, folder_name):
    """フォルダ取得または作成"""
    # 検索
    url = "https://www.googleapis.com/drive/v3/files"
    params = {
        'q': f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        'fields': 'files(id, name)'
    }
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, params=params, headers=headers)
    files = response.json().get('files', [])
    
    if files:
        print(f"✓ フォルダ発見: {folder_name}")
        return files[0]['id']
    
    # 作成
    print(f"✓ フォルダ作成: {folder_name}")
    response = requests.post(url, headers=headers, json={
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    })
    return response.json()['id']

def upload_to_drive(access_token, image_path, filename):
    """Driveにアップロード"""
    print(f"\n=== Google Driveアップロード ===")
    
    folder_id = get_or_create_folder(access_token, DRIVE_FOLDER_NAME)
    
    metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    
    files = {
        'data': ('metadata', json.dumps(metadata), 'application/json'),
        'file': open(image_path, 'rb')
    }
    
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.post(url, headers=headers, files=files)
    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.text}")
    
    file_id = response.json()['id']
    file_url = f"https://drive.google.com/file/d/{file_id}/view"
    
    print(f"✓ アップロード完了")
    print(f"  URL: {file_url}")
    
    return file_url

def insert_at_row3(access_token, expense_data, drive_url):
    """A3（上から3番目）に挿入"""
    print(f"\n=== 経費領収書シートA3に挿入 ===")
    
    # シートID取得
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    
    expense_sheet_id = None
    for sheet in response.json().get('sheets', []):
        if sheet['properties']['title'] == EXPENSE_SHEET_NAME:
            expense_sheet_id = sheet['properties']['sheetId']
            break
    
    if not expense_sheet_id:
        raise Exception(f"シートが見つかりません: {EXPENSE_SHEET_NAME}")
    
    # A3に行を挿入
    batch_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}:batchUpdate"
    requests.post(batch_url, headers=headers, json={
        'requests': [{
            'insertDimension': {
                'range': {
                    'sheetId': expense_sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': 2,  # 0-indexed（3行目）
                    'endIndex': 3
                },
                'inheritFromBefore': False
            }
        }]
    })
    
    # データ書き込み
    row = [[
        expense_data.get('date', ''),
        expense_data.get('recipient', ''),
        expense_data.get('address', ''),
        expense_data.get('memo', ''),
        expense_data.get('amount', ''),
        expense_data.get('currency', '円'),
        drive_url
    ]]
    
    values_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{EXPENSE_SHEET_NAME}!A3:G3"
    requests.put(values_url, params={'valueInputOption': 'RAW'}, headers=headers, json={'values': row})
    
    print("✓ A3に挿入完了")

def main(image_path, expense_json):
    """メイン処理"""
    print("=== 経費領収書処理 ===")
    
    expense_data = json.loads(expense_json)
    
    # 1. Access token取得
    access_token = load_token()
    print("✓ Access token取得")
    
    # 2. Driveアップロード
    from datetime import datetime
    filename = f"expense_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    drive_url = upload_to_drive(access_token, image_path, filename)
    
    # 3. A3に挿入
    insert_at_row3(access_token, expense_data, drive_url)
    
    print("\n✅ 完了！")
    print(f"スプレッドシート: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=1248520565")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: upload_and_add_expense.py <image_path> <expense_json>")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2])
