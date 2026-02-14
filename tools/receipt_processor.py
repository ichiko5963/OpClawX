#!/usr/bin/env python3
"""
領収書自動処理システム
- 入力: Telegram/メール/LINE公式からの領収書画像
- 処理: OCR → Googleドライブ保存 → スプレッドシート追記
"""

import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

SPREADSHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
DRIVE_FOLDER_NAME = "法人領収書まとめ"
GOG_ACCOUNT = "ichioka.naoto@aircle.jp"  # TODO: 実際のアカウントに変更

# スプレッドシートの列構造（A-G）
# A: 日付
# B: 宛名
# C: 発行者の住所
# D: メモ
# E: 金額
# F: 通貨（円）
# G: URL

def run_gog(args):
    """gog CLIを実行"""
    cmd = ["gog"] + args + ["--account", GOG_ACCOUNT, "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"gog failed: {result.stderr}")
    return json.loads(result.stdout) if result.stdout else None

def ocr_receipt(image_path):
    """
    領収書をOCR/AI解析
    TODO: Claude/Gemini Vision APIで解析
    返り値例: {
        "date": "2026-02-14",
        "recipient": "株式会社AirCle",
        "issuer_address": "東京都...",
        "amount": 10000,
        "currency": "円",
        "memo": "交通費"
    }
    """
    # Placeholder: 実際にはVision APIで解析
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "recipient": "",
        "issuer_address": "",
        "amount": 0,
        "currency": "円",
        "memo": "自動処理（要確認）"
    }

def upload_to_drive(image_path):
    """
    Googleドライブ「法人領収書まとめ」にアップロード
    TODO: gog drive upload実装
    """
    # Placeholder
    return "https://drive.google.com/file/d/PLACEHOLDER/view"

def append_to_sheet(data):
    """
    スプレッドシートに追記
    A: 日付, B: 宛名, C: 発行者住所, D: メモ, E: 金額, F: 通貨, G: URL
    """
    row = [
        data.get("date", ""),
        data.get("recipient", ""),
        data.get("issuer_address", ""),
        data.get("memo", ""),
        str(data.get("amount", "")),
        data.get("currency", "円"),
        data.get("url", "")
    ]
    
    values_json = json.dumps([row])
    
    # gog sheets append
    cmd = [
        "gog", "sheets", "append",
        SPREADSHEET_ID,
        "A:G",
        "--values-json", values_json,
        "--insert", "INSERT_ROWS",
        "--account", GOG_ACCOUNT
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to append to sheet: {result.stderr}")
    
    print(f"✓ スプレッドシートに追記: {data.get('date')} - {data.get('amount')}円")

def process_receipt(image_path):
    """領収書処理メインフロー"""
    print(f"Processing receipt: {image_path}")
    
    # 1. OCR解析
    print("1. OCR解析中...")
    receipt_data = ocr_receipt(image_path)
    
    # 2. Driveにアップロード
    print("2. Googleドライブにアップロード中...")
    drive_url = upload_to_drive(image_path)
    receipt_data["url"] = drive_url
    
    # 3. スプレッドシート追記
    print("3. スプレッドシートに追記中...")
    append_to_sheet(receipt_data)
    
    print("✓ 完了！")
    return receipt_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: receipt_processor.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    if not Path(image_path).exists():
        print(f"Error: File not found: {image_path}")
        sys.exit(1)
    
    process_receipt(image_path)
