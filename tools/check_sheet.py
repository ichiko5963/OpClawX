#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_api import SheetsAPI
import requests
import json

SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"

api = SheetsAPI()

# 最新10行を取得
url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/A:G"
headers = {'Authorization': f'Bearer {api.access_token}'}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"❌ エラー: {response.text}")
    sys.exit(1)

data = response.json()
values = data.get('values', [])

print(f"=== スプレッドシート内容確認 ===")
print(f"シートID: {SHEET_ID}")
print(f"総行数: {len(values)}行")
print()
print("最新10行:")
for row in values[-10:]:
    print(row)
