#!/usr/bin/env python3
"""
銀行明細 → 領収書スプレッドシート（1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc）
収入も領収書も全て同じスプレッドシートに入れる
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_api import SheetsAPI, RECEIPT_SHEET_ID

# 銀行明細データ（2026/01/01-02/14）
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

def import_to_correct_sheet():
    """正しいスプレッドシート（領収書）に追加"""
    print("=== 銀行明細 → 領収書スプレッドシート ===")
    print(f"シートID: {RECEIPT_SHEET_ID}")
    print(f"期間: 2026/01/01 - 2026/02/14")
    print(f"件数: {len(BANK_INCOMES)}件")
    print()
    
    api = SheetsAPI()
    
    # スプレッドシート形式に変換
    values = []
    total = 0
    for date, source, amount, memo in BANK_INCOMES:
        values.append([
            date,  # A: 日付
            source,  # B: 宛名/収入元
            "",  # C: 発行者住所
            memo,  # D: メモ
            str(amount),  # E: 金額
            "円",  # F: 通貨
            ""  # G: URL
        ])
        total += amount
        print(f"{date} | {amount:>10,}円 | {source}")
    
    print()
    print(f"総入金額: {total:,}円")
    print()
    
    # 追加
    api.append_rows(RECEIPT_SHEET_ID, values)
    print()
    print("✅ 完了！スプレッドシートを確認してください")
    print("https://docs.google.com/spreadsheets/d/1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc/edit")

if __name__ == "__main__":
    try:
        import_to_correct_sheet()
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
