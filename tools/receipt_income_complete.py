#!/usr/bin/env python3
"""
領収書・収入自動処理システム（完全版）
- 銀行明細PDF処理（入金/支出判定）
- 領収書OCR → Drive → Sheet
- 収入自動追記
"""

import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

# スプレッドシートID
RECEIPT_SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
INCOME_SHEET_ID = "1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990"
GOG_ACCOUNT = "jiuhuot10@gmail.com"

# スプレッドシート列構造（A-G）
# A: 日付
# B: 宛名（収入元）
# C: 発行者の住所（空でOK）
# D: メモ
# E: 金額
# F: 通貨（円）
# G: URL（Drive URLまたは空）

# 入金判定キーワード（これらは収入）
INCOME_KEYWORDS = [
    'ｶﾞｲｺｸﾋｼﾑｹｿｳｷﾝ',  # 外国非課税送金
    'ﾋﾟ-ﾃｨﾂｸｽｼﾞﾔﾊﾟﾝ',  # Stripe
    'ｽﾄﾗｲﾌﾟｼﾞﾔﾊﾟﾝ',  # Stripe
    'ﾉ-ﾄ',  # Note
    'ﾎﾟ-ﾄ',  # Port
    'ﾒﾙﾍﾟｲ',  # メルカリ
    'ｷﾕｳｼﾕｳﾀﾞｲｶﾞｸ',  # 九州大学
    'ﾏｼﾕﾏﾛｴﾝﾀﾒ',  # マシュマロエンタメ
    'ｷﾔﾘｱﾃﾞｻﾞｲﾝｾﾝﾀ-',  # キャリアデザインセンター
    'ﾐﾝｼﾕｳ',  # みん就
    'ﾘﾘ',  # Lily
    'ﾌｸｵｶｼﾎｹﾝﾈﾝｷﾝｶ',  # 福岡市保険年金課（還付）
    'ｵﾘｿｸ',  # 利息
]

# 支出判定キーワード（これらは除外）
EXPENSE_KEYWORDS = [
    'ﾌﾘｺﾐｼｷﾝ',  # 振込支払
    'ﾌﾘｺﾐﾃｽｳﾘﾖｳ',  # 振込手数料
    'RS ﾍﾟｲﾍﾟｲ',  # PayPay支払い
    'ATMｼﾊﾗｲ',  # ATM支払い
    'ATMﾃｽｳﾘﾖｳ',  # ATM手数料
    'ﾐﾂｲｽﾐﾄﾓｶ-ﾄﾞ',  # クレカ支払い
    'ﾗｸﾃﾝｶ-ﾄﾞｻ-ﾋﾞｽ',  # 楽天カード
    'ﾗｲﾌｶ-ﾄﾞ',  # ライフカード
]

def is_income(description):
    """入金かどうかを判定"""
    desc_upper = description.upper()
    
    # 支出キーワードが含まれていたら除外
    for keyword in EXPENSE_KEYWORDS:
        if keyword in description:
            return False
    
    # 入金キーワードが含まれていたら収入
    for keyword in INCOME_KEYWORDS:
        if keyword in description:
            return True
    
    return False

def parse_bank_statement_pdf(pdf_path):
    """
    銀行明細PDFから入金を抽出
    TODO: pdftotext or Gemini Vision API
    """
    # Placeholder: 実際にはPDF解析実装
    print(f"TODO: PDF解析 {pdf_path}")
    return []

def append_income_to_sheet(date, source, amount, memo="", url=""):
    """収入スプレッドシートに追記"""
    row = [
        date,  # A: 日付
        source,  # B: 宛名（収入元）
        "",  # C: 発行者住所（空）
        memo,  # D: メモ
        str(amount),  # E: 金額
        "円",  # F: 通貨
        url  # G: URL
    ]
    
    values_json = json.dumps([row])
    
    cmd = [
        "gog", "sheets", "append",
        INCOME_SHEET_ID,
        "A:G",
        "--values-json", values_json,
        "--insert", "INSERT_ROWS",
        "--account", GOG_ACCOUNT
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to append to sheet: {result.stderr}")
    
    print(f"✓ 収入追記: {date} - {source} - {amount:,}円")

def append_receipt_to_sheet(date, recipient, issuer_address, memo, amount, currency, url):
    """領収書スプレッドシートに追記"""
    row = [
        date,  # A: 日付
        recipient,  # B: 宛名
        issuer_address,  # C: 発行者住所
        memo,  # D: メモ
        str(amount),  # E: 金額
        currency,  # F: 通貨
        url  # G: URL
    ]
    
    values_json = json.dumps([row])
    
    cmd = [
        "gog", "sheets", "append",
        RECEIPT_SHEET_ID,
        "A:G",
        "--values-json", values_json,
        "--insert", "INSERT_ROWS",
        "--account", GOG_ACCOUNT
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to append to sheet: {result.stderr}")
    
    print(f"✓ 領収書追記: {date} - {amount}{currency} - {memo}")

def test_income_append():
    """収入追記テスト"""
    print("=== 収入追記テスト ===")
    
    # テストデータ
    test_incomes = [
        {
            "date": "2026-02-14",
            "source": "Stripe（テスト）",
            "amount": 1000,
            "memo": "テスト入金",
            "url": ""
        }
    ]
    
    for income in test_incomes:
        append_income_to_sheet(
            income["date"],
            income["source"],
            income["amount"],
            income["memo"],
            income["url"]
        )
    
    print("\n✓ テスト完了")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_income_append()
    else:
        print("Usage: receipt_income_complete.py test")
        print("\nTODO:")
        print("- PDF処理実装")
        print("- OCR実装")
        print("- Drive連携")
        print("- LINE Webhook")
        print("- メール監視cron")
