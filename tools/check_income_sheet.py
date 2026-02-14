#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_api import SheetsAPI
import requests

SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"

api = SheetsAPI()

# 2026年収入シートの内容取得
url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/2026年収入!A1:G30"
headers = {'Authorization': f'Bearer {api.access_token}'}

response = requests.get(url, headers=headers)
data = response.json()
values = data.get('values', [])

print("=== 2026年収入シート確認 ===")
print(f"総行数: {len(values)}行")
print()
print("最初の10行:")
for i, row in enumerate(values[:10], 1):
    print(f"{i}. {row}")
