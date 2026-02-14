#!/usr/bin/env python3
"""
日付を正しいフォーマットで修正
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_api import SheetsAPI
import requests

SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"

# 正しい日付データ
CORRECT_DATES = [
    "2026/01/06",
    "2026/01/14",
    "2026/01/19",
    "2026/01/19",
    "2026/01/20",
    "2026/01/21",
    "2026/01/21",
    "2026/01/23",
    "2026/01/26",
    "2026/01/30",
    "2026/01/30",
    "2026/01/30",
    "2026/01/30",
    "2026/01/30",
    "2026/01/30",
    "2026/01/30",
    "2026/01/30",
    "2026/01/30",
    "2026/01/30",
    "2026/01/30",
    "2026/02/03",
    "2026/02/05",
    "2026/02/06",
    "2026/02/09",
    "2026/02/14",
]

api = SheetsAPI()

# A2からA26まで日付を更新
values = [[date] for date in CORRECT_DATES]

url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/2026年収入!A2:A26"
params = {
    'valueInputOption': 'RAW'  # RAWで送信（自動変換しない）
}
headers = {
    'Authorization': f'Bearer {api.access_token}',
    'Content-Type': 'application/json'
}
body = {
    'values': values
}

response = requests.put(url, params=params, headers=headers, json=body)
if response.status_code != 200:
    print(f"❌ エラー: {response.text}")
    sys.exit(1)

print("✓ 日付を修正しました")
print()
print("確認:")
print("https://docs.google.com/spreadsheets/d/1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc/edit#gid=126020037")
