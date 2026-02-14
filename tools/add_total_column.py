#!/usr/bin/env python3
"""
H列に合計金額を追加（計算式）+ 赤い塗りつぶし削除
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_api import SheetsAPI
import requests

SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
INCOME_SHEET_GID = 126020037

api = SheetsAPI()

# 1. H1にヘッダー追加
print("=== H列に合計金額を追加 ===")

# ヘッダー
header_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/2026年収入!H1"
requests.put(
    header_url,
    params={'valueInputOption': 'RAW'},
    headers={'Authorization': f'Bearer {api.access_token}', 'Content-Type': 'application/json'},
    json={'values': [['合計金額']]}
)
print("✓ H1にヘッダー追加")

# 2. H2:H26に計算式追加（E列の金額をそのまま表示）
formulas = []
for i in range(2, 27):  # 2行目から26行目
    formulas.append([f'=E{i}'])

formula_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/2026年収入!H2:H26"
requests.put(
    formula_url,
    params={'valueInputOption': 'USER_ENTERED'},  # 計算式として送信
    headers={'Authorization': f'Bearer {api.access_token}', 'Content-Type': 'application/json'},
    json={'values': formulas}
)
print("✓ H2:H26に計算式追加")

# 3. 赤い塗りつぶし削除（背景色をクリア）
print("\n=== 赤い塗りつぶし削除 ===")

batch_url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}:batchUpdate"
requests.post(
    batch_url,
    headers={'Authorization': f'Bearer {api.access_token}', 'Content-Type': 'application/json'},
    json={
        'requests': [
            {
                'updateCells': {
                    'range': {
                        'sheetId': INCOME_SHEET_GID,
                        'startRowIndex': 0,
                        'endRowIndex': 100
                    },
                    'fields': 'userEnteredFormat.backgroundColor'
                }
            }
        ]
    }
)
print("✓ 背景色クリア完了")

print("\n✅ 完了！")
print("https://docs.google.com/spreadsheets/d/1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc/edit#gid=126020037")
