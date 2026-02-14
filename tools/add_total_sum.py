#!/usr/bin/env python3
"""
H2に全体の合計金額を表示（1つだけ）
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_api import SheetsAPI
import requests

SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"

api = SheetsAPI()

print("=== H2に合計金額を表示 ===")

# 1. H2〜H26をクリア
clear_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/2026年収入!H2:H26:clear"
requests.post(
    clear_url,
    headers={'Authorization': f'Bearer {api.access_token}'}
)
print("✓ H2:H26をクリア")

# 2. H2に合計の計算式を追加
# =TEXT(SUM(E2:E26),"#,##0")&"円"
formula_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/2026年収入!H2"
response = requests.put(
    formula_url,
    params={'valueInputOption': 'USER_ENTERED'},
    headers={'Authorization': f'Bearer {api.access_token}', 'Content-Type': 'application/json'},
    json={'values': [['=TEXT(SUM(E2:E26),"#,##0")&"円"']]}
)

if response.status_code == 200:
    print("✓ H2に合計金額を追加")
    print("  計算式: =TEXT(SUM(E2:E26),\"#,##0\")&\"円\"")
else:
    print(f"❌ エラー: {response.text}")
    sys.exit(1)

print("\n✅ 完了！H2に合計が表示されます")
print("https://docs.google.com/spreadsheets/d/1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc/edit#gid=126020037")
