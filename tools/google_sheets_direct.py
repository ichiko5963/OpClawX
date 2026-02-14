#!/usr/bin/env python3
"""
Google Sheets直接操作（OAuth token使用）
gogが動かないので直接API叩く
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Google OAuth token location (from gog)
TOKEN_PATH = Path.home() / "Library/Application Support/gogcli/tokens/jiuhuot10@gmail.com.json"

# スプレッドシートID
RECEIPT_SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
INCOME_SHEET_ID = "1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990"

def append_to_sheet(sheet_id, values):
    """
    Google Sheets APIで行を追記
    valuesは [[col1, col2, ...]] の形式
    """
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        # tokenファイル読み込み
        if not TOKEN_PATH.exists():
            print(f"❌ Token not found: {TOKEN_PATH}")
            return False
        
        token_data = json.loads(TOKEN_PATH.read_text())
        
        creds = Credentials(
            token=token_data.get('access_token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=creds)
        
        body = {
            'values': values
        }
        
        result = service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range='A:G',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        print(f"✓ {result.get('updates').get('updatedRows')}行追加")
        return True
        
    except ImportError:
        print("❌ google-api-python-client未インストール")
        print("実行: pip3 install google-api-python-client google-auth")
        return False
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def test_append_income():
    """収入追記テスト"""
    values = [[
        datetime.now().strftime("%Y-%m-%d"),  # A: 日付
        "テスト入金（Stripe）",  # B: 宛名
        "",  # C: 発行者住所
        "Python API直接テスト",  # D: メモ
        "1000",  # E: 金額
        "円",  # F: 通貨
        ""  # G: URL
    ]]
    
    print("=== 収入スプレッドシートテスト ===")
    return append_to_sheet(INCOME_SHEET_ID, values)

def test_append_receipt():
    """領収書追記テスト"""
    values = [[
        datetime.now().strftime("%Y-%m-%d"),
        "株式会社テスト",
        "東京都...",
        "交通費",
        "5000",
        "円",
        "https://drive.google.com/..."
    ]]
    
    print("=== 領収書スプレッドシートテスト ===")
    return append_to_sheet(RECEIPT_SHEET_ID, values)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "income":
            test_append_income()
        elif sys.argv[1] == "receipt":
            test_append_receipt()
        else:
            print("Usage: google_sheets_direct.py [income|receipt]")
    else:
        print("収入テスト...")
        test_append_income()
