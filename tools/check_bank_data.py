#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_api import SheetsAPI
import requests

SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"

api = SheetsAPI()

url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/A:G"
headers = {'Authorization': f'Bearer {api.access_token}'}

response = requests.get(url, headers=headers)
data = response.json()
values = data.get('values', [])

print(f"=== 銀行明細データ確認 ===")
print(f"総行数: {len(values)}行")
print()

# 「銀行明細」を含む行を抽出
bank_rows = [row for row in values if len(row) > 3 and '銀行明細' in row[3]]

print(f"銀行明細データ: {len(bank_rows)}行")
print()

# 日付でソート
bank_rows.sort(key=lambda x: x[0] if len(x) > 0 else '')

for row in bank_rows:
    date = row[0] if len(row) > 0 else ''
    source = row[1] if len(row) > 1 else ''
    amount = row[4] if len(row) > 4 else ''
    print(f"{date} | {amount:>10}円 | {source}")

# 合計金額
total = sum(int(row[4]) for row in bank_rows if len(row) > 4 and row[4].isdigit())
print()
print(f"総入金額: {total:,}円")
