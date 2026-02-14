#!/usr/bin/env python3
"""
領収書・収入自動処理システム v2
- Google Sheets API直接利用（gogではなく）
- 領収書: 1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc
- 収入: 1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990
"""

import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# スプレッドシートID
RECEIPT_SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
INCOME_SHEET_ID = "1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990"
GOG_ACCOUNT = "jiuhuot10@gmail.com"

# スプレッドシートの列構造
# 領収書（A-G）: 日付, 宛名, 発行者住所, メモ, 金額, 通貨, URL
# 収入（要確認）: TBD

def append_receipt(date, recipient, issuer_address, memo, amount, currency, url):
    """領収書スプレッドシートに追記"""
    row = [date, recipient, issuer_address, memo, str(amount), currency, url]
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
        raise Exception(f"Failed to append receipt: {result.stderr}")
    
    print(f"✓ 領収書追記: {date} - {amount}{currency} - {memo}")
    return True

def append_income(date, source, amount, memo, url=""):
    """収入スプレッドシートに追記（列構造は後で確認）"""
    # TODO: 収入シートの構造確認後に実装
    print(f"TODO: 収入追記 - {date} - {source} - {amount}円")
    pass

def process_receipt_from_telegram(message):
    """
    Telegramメッセージから領収書処理
    - 画像添付の場合: OCR → Drive → Sheet
    - テキストの場合: パース → Sheet
    """
    # TODO: Telegram画像ダウンロード、OCR実装
    print("TODO: Telegram領収書処理")

def process_income_from_email(email_body):
    """
    メールから収入検出
    - 「お支払いがありました」（Stripe）
    - 案件受注メール
    """
    # TODO: メール解析、収入抽出
    print("TODO: メール収入検出")

def check_recurring_income():
    """
    定期収入チェック（Google Meet文字起こし、契約情報から）
    - 毎月の振込予定を検出
    - 振込日に自動追記
    """
    # TODO: Meet文字起こし解析、契約情報DB構築
    print("TODO: 定期収入チェック")

if __name__ == "__main__":
    # テスト: 領収書追記
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        append_receipt(
            date="2026-02-14",
            recipient="株式会社AirCle",
            issuer_address="",
            memo="テスト領収書",
            amount=1000,
            currency="円",
            url="https://example.com"
        )
    else:
        print("Usage: receipt_income_processor.py test")
