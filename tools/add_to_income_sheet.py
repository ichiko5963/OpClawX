#!/usr/bin/env python3
"""
銀行明細 → 2026年収入シートの一番上から追加
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_api import SheetsAPI
import requests

SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"

# 銀行明細データ（日付順）
BANK_INCOMES = [
    ("2026-01-06", "外国非課税送金", 28522, "銀行明細"),
    ("2026-01-14", "メルカリ", 123600, "銀行明細"),
    ("2026-01-19", "Stripe", 112547, "銀行明細"),
    ("2026-01-19", "Stripe", 6423, "銀行明細"),
    ("2026-01-20", "Lily", 26400, "銀行明細"),
    ("2026-01-21", "九州大学", 12600, "銀行明細"),
    ("2026-01-21", "外国非課税送金", 163552, "銀行明細"),
    ("2026-01-23", "マシュマロエンタメ", 62853, "銀行明細"),
    ("2026-01-26", "Stripe", 61342, "銀行明細"),
    ("2026-01-30", "Port", 2750000, "銀行明細"),
    ("2026-01-30", "Note", 51734, "銀行明細"),
    ("2026-01-30", "Note", 87276, "銀行明細"),
    ("2026-01-30", "Note", 218294, "銀行明細"),
    ("2026-01-30", "Note", 11416, "銀行明細"),
    ("2026-01-30", "Note", 90918, "銀行明細"),
    ("2026-01-30", "Note", 19473, "銀行明細"),
    ("2026-01-30", "Note", 2865, "銀行明細"),
    ("2026-01-30", "Note", 4734, "銀行明細"),
    ("2026-01-30", "キャリアデザインセンター", 158400, "銀行明細"),
    ("2026-01-30", "みん就", 138600, "銀行明細"),
    ("2026-02-03", "外国非課税送金", 51876, "銀行明細"),
    ("2026-02-05", "福岡市保険年金課（還付）", 1600, "銀行明細"),
    ("2026-02-06", "九州大学", 150000, "銀行明細"),
    ("2026-02-09", "Stripe", 97955, "銀行明細"),
    ("2026-02-14", "利息", 6241, "銀行明細"),
]

def add_to_income_sheet():
    """2026年収入シートの一番上（A2以降）に追加"""
    print("=== 2026年収入シートに追加 ===")
    print(f"件数: {len(BANK_INCOMES)}件")
    print()
    
    api = SheetsAPI()
    
    # データ準備
    values = []
    total = 0
    for date, source, amount, memo in BANK_INCOMES:
        values.append([
            date,
            source,
            "",
            memo,
            str(amount),
            "円",
            ""
        ])
        total += amount
        print(f"{date} | {amount:>10,}円 | {source}")
    
    print()
    print(f"総入金額: {total:,}円")
    print()
    
    # 2026年収入シートのA2から追加（ヘッダー行の次）
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/2026年収入!A2:G:append"
    params = {
        'valueInputOption': 'USER_ENTERED',
        'insertDataOption': 'INSERT_ROWS'
    }
    headers = {
        'Authorization': f'Bearer {api.access_token}',
        'Content-Type': 'application/json'
    }
    body = {
        'values': values
    }
    
    response = requests.post(url, params=params, headers=headers, json=body)
    if response.status_code != 200:
        print(f"❌ エラー: {response.text}")
        sys.exit(1)
    
    result = response.json()
    updated_rows = result.get('updates', {}).get('updatedRows', 0)
    print(f"✓ {updated_rows}行追加成功")
    print()
    print("✅ 完了！")
    print("https://docs.google.com/spreadsheets/d/1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc/edit#gid=126020037")

if __name__ == "__main__":
    try:
        add_to_income_sheet()
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
