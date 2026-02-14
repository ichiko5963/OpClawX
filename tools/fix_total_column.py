#!/usr/bin/env python3
"""
H列に「金額+通貨」を見やすくまとめて表示
例: 28,522円
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_api import SheetsAPI
import requests

SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"

api = SheetsAPI()

print("=== H列に合計金額（金額+通貨）を表示 ===")

# H2:H26に計算式追加
# =TEXT(E2,"#,##0")&F2 で「28,522円」形式
formulas = []
for i in range(2, 27):  # 2行目から26行目
    formulas.append([f'=TEXT(E{i},"#,##0")&F{i}'])

formula_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/2026年収入!H2:H26"
response = requests.put(
    formula_url,
    params={'valueInputOption': 'USER_ENTERED'},
    headers={'Authorization': f'Bearer {api.access_token}', 'Content-Type': 'application/json'},
    json={'values': formulas}
)

if response.status_code == 200:
    print("✓ H2:H26に計算式追加完了")
    print("  形式: 28,522円")
else:
    print(f"❌ エラー: {response.text}")
    sys.exit(1)

print("\n✅ 完了！")
print("https://docs.google.com/spreadsheets/d/1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc/edit#gid=126020037")
