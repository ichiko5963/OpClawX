#!/usr/bin/env python3
"""
経費領収書自動処理（改訂版）
- 一番上の空白行に挿入（A3固定ではない）
- 上から順番に詰める
"""
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")
SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
EXPENSE_SHEET_NAME = "2026年経費領収書"

# 固定DriveフォルダID（絶対に変えない）
DRIVE_FOLDER_ID = "1pzI8BkAGrio16HTGpVOyvB25rV8IOO_g"

def load_token():
    """OAuth token読み込み"""
    data = json.loads(TOKEN_FILE.read_text())
    
    url = "https://oauth2.googleapis.com/token"
    response = requests.post(url, data={
        'client_id': data['client_id'],
        'client_secret': data['client_secret'],
        'refresh_token': data['refresh_token'],
        'grant_type': 'refresh_token'
    })
    
    return response.json()['access_token']

def upload_to_drive(access_token, image_path, filename):
    """指定フォルダにアップロード"""
    print(f"\n=== Google Driveアップロード ===")
    
    metadata = {
        'name': filename,
        'parents': [DRIVE_FOLDER_ID]
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
    
    print(f"✓ アップロード完了: {file_url}")
    
    return file_url

def find_first_empty_row(access_token):
    """一番上の空白行を見つける（A2から検索）"""
    print(f"\n=== 空白行検索 ===")
    
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{EXPENSE_SHEET_NAME}!A:A"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    values = response.json().get('values', [])
    
    # A1はヘッダーなのでスキップ、A2から検索
    for i in range(1, len(values) + 1):
        if i >= len(values) or not values[i] or values[i][0] == '':
            row_num = i + 1  # 1-indexed
            print(f"✓ 空白行発見: A{row_num}")
            return row_num
    
    # 全て埋まっている場合は最後の次
    row_num = len(values) + 1
    print(f"✓ 最後尾に追加: A{row_num}")
    return row_num

def insert_at_first_empty(access_token, expense_data, drive_url):
    """一番上の空白行に挿入"""
    
    # 空白行を見つける
    row_num = find_first_empty_row(access_token)
    
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
    
    range_name = f"{EXPENSE_SHEET_NAME}!A{row_num}:G{row_num}"
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{range_name}"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    
    response = requests.put(url, params={'valueInputOption': 'RAW'}, headers=headers, json={'values': row})
    if response.status_code != 200:
        raise Exception(f"Write failed: {response.text}")
    
    print(f"✓ A{row_num}に書き込み完了")

def create_detailed_memo(expense_data):
    """詳細なメモを生成"""
    parts = []
    
    # 書類種類
    doc_type = expense_data.get('doc_type', '領収書')
    parts.append(doc_type)
    
    # 発行元
    issuer = expense_data.get('issuer', '')
    if issuer:
        parts.append(f"発行: {issuer}")
    
    # 対象月（請求書の場合）
    if '請求書' in doc_type:
        target_month = expense_data.get('target_month', '')
        if target_month:
            parts.append(f"{target_month}分")
    
    # 内容
    content = expense_data.get('content', '')
    if content:
        parts.append(content)
    
    return ' - '.join(parts) if parts else '領収書'

def main(image_path, expense_json):
    """メイン処理"""
    print("=== 経費領収書自動処理 ===")
    
    expense_data = json.loads(expense_json)
    
    # メモ詳細化
    expense_data['memo'] = create_detailed_memo(expense_data)
    
    print(f"日付: {expense_data.get('date')}")
    print(f"宛名: {expense_data.get('recipient')}")
    print(f"金額: {expense_data.get('amount')}{expense_data.get('currency', '円')}")
    print(f"メモ: {expense_data['memo']}")
    
    # 1. Access token取得
    access_token = load_token()
    
    # 2. Driveアップロード
    filename = f"expense_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    drive_url = upload_to_drive(access_token, image_path, filename)
    
    # 3. 一番上の空白行に挿入
    insert_at_first_empty(access_token, expense_data, drive_url)
    
    print("\n✅ 完了！")
    print(f"スプレッドシート: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=1248520565")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: expense_auto_v2.py <image_path> <expense_json>")
        sys.exit(1)
    
    try:
        main(sys.argv[1], sys.argv[2])
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
