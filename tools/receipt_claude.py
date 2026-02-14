#!/usr/bin/env python3
"""
領収書OCR（Claude直接読み取り版）
API不要 - OpenClawのimageツール経由でClaudeが読み取る
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# スプレッドシート設定
SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
SHEET_NAME = "2026年収入"
TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")

def analyze_receipt_with_claude(image_path):
    """
    Claude（私）に領収書を読み取らせる
    OpenClawのimageツール経由
    """
    print(f"=== 領収書画像分析（Claude） ===")
    print(f"画像: {image_path}")
    
    # OpenClaw経由でClaude（私）が画像を分析
    # imageツールのプロンプト
    prompt = """この領収書画像から以下の情報を抽出してJSON形式で回答してください：

{
  "date": "YYYY/MM/DD形式の日付",
  "recipient": "宛名（会社名・店名）",
  "address": "発行者の住所（あれば、なければ空文字）",
  "amount": "金額（数字のみ）",
  "currency": "通貨（円、ドル等）",
  "memo": "メモ（領収書の種類など、なければ「領収書」）"
}

情報がない項目は空文字""にしてください。
JSONのみを出力し、他の説明は不要です。"""
    
    # openclaw CLIでimage分析を実行
    # （実際にはこのスクリプトが呼ばれる前にOpenClawが画像を分析している想定）
    # ここではプレースホルダー
    print("  ※このスクリプトはOpenClaw経由で呼ばれることを想定")
    print("  ※画像分析結果をJSON形式で標準入力から受け取る")
    
    # 標準入力からJSON受け取り
    if not sys.stdin.isatty():
        receipt_data = json.load(sys.stdin)
    else:
        raise Exception("標準入力からJSONデータが必要です")
    
    print("✓ 領収書データ抽出完了:")
    print(f"  日付: {receipt_data.get('date')}")
    print(f"  宛名: {receipt_data.get('recipient')}")
    print(f"  金額: {receipt_data.get('amount')}{receipt_data.get('currency')}")
    
    return receipt_data

def upload_to_drive_simple(image_path):
    """Google Driveにアップロード（簡易版）"""
    print(f"\n=== Google Driveアップロード ===")
    
    # gogコマンドでアップロード
    folder_name = "法人領収書まとめ"
    
    try:
        # まずフォルダIDを取得
        result = subprocess.run(
            ['gog', 'drive', 'list', '--query', f'name="{folder_name}"', '--account', 'jiuhuot10@gmail.com'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # TODO: フォルダID抽出とアップロード実装
        # 今は簡易的にスキップ
        print("  ※Drive連携は後で実装（今はスキップ）")
        return ""
        
    except Exception as e:
        print(f"  警告: Drive連携エラー: {e}")
        return ""

def append_to_sheet_direct(receipt_data, drive_url=""):
    """スプレッドシートに直接追記"""
    print(f"\n=== スプレッドシート追記 ===")
    
    # sheets_api.pyを使う
    sys.path.insert(0, str(Path(__file__).parent))
    from sheets_api import SheetsAPI
    
    api = SheetsAPI()
    
    row = [[
        receipt_data.get('date', ''),
        receipt_data.get('recipient', ''),
        receipt_data.get('address', ''),
        receipt_data.get('memo', '領収書'),
        receipt_data.get('amount', ''),
        receipt_data.get('currency', '円'),
        drive_url
    ]]
    
    api.append_rows(SHEET_ID, row, SHEET_NAME)
    print("✓ 追記完了")

def main(image_path, receipt_json=None):
    """
    メイン処理
    receipt_json: Claudeが分析した結果（JSON文字列）
    """
    print("=== 領収書処理（Claude直接読み取り） ===")
    
    if receipt_json:
        # JSON文字列を受け取った場合
        receipt_data = json.loads(receipt_json)
    else:
        # 標準入力から受け取る
        receipt_data = analyze_receipt_with_claude(image_path)
    
    # Drive保存（オプション）
    drive_url = upload_to_drive_simple(image_path)
    
    # スプレッドシート追記
    append_to_sheet_direct(receipt_data, drive_url)
    
    print("\n✅ 処理完了！")
    print(f"スプレッドシート: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: receipt_claude.py <image_path> [receipt_json]")
        print("\n例:")
        print("  python3 receipt_claude.py receipt.jpg")
        print('  python3 receipt_claude.py receipt.jpg \'{"date":"2026/01/15","recipient":"店名","amount":"1000","currency":"円"}\'')
        sys.exit(1)
    
    image_path = sys.argv[1]
    receipt_json = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        main(image_path, receipt_json)
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
