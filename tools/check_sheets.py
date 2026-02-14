#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_api import SheetsAPI
import requests

SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"

api = SheetsAPI()

# スプレッドシートのメタデータ取得
url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
headers = {'Authorization': f'Bearer {api.access_token}'}

response = requests.get(url, headers=headers)
data = response.json()

print("=== スプレッドシート内のシート一覧 ===")
for sheet in data.get('sheets', []):
    props = sheet.get('properties', {})
    print(f"- {props.get('title')} (ID: {props.get('sheetId')})")
