#!/usr/bin/env python3
"""
銀行明細 → 収入スプレッドシート自動追記（完全版）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_api import SheetsAPI, INCOME_SHEET_ID

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

def import_bank_incomes():
    """銀行明細の入金データを一括インポート"""
    print("=== 銀行明細 → 収入スプレッドシート ===")
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
            source,  # B: 収入元
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
    
    # 一括追加
    confirm = input("スプレッドシートに追加しますか？ (y/n): ")
    if confirm.lower() == 'y':
        api.append_rows(INCOME_SHEET_ID, values)
        print()
        print("✅ 完了！スプレッドシートを確認してください")
        print("https://docs.google.com/spreadsheets/d/1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990/edit")
    else:
        print("キャンセルしました")

if __name__ == "__main__":
    try:
        import_bank_incomes()
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)
