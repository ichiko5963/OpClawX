#!/usr/bin/env python3
"""
Google Sheets API wrapper（既存のOAuth token使用）
"""

import json
import sys
import requests
from pathlib import Path
from datetime import datetime

# 既存のOAuth情報
TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")

# スプレッドシートID
RECEIPT_SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
INCOME_SHEET_ID = "1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990"

class SheetsAPI:
    def __init__(self):
        self.access_token = None
        self.load_credentials()
    
    def load_credentials(self):
        """既存のOAuth情報を読み込み"""
        if not TOKEN_FILE.exists():
            raise Exception(f"Token file not found: {TOKEN_FILE}")
        
        data = json.loads(TOKEN_FILE.read_text())
        self.client_id = data['client_id']
        self.client_secret = data['client_secret']
        self.refresh_token = data['refresh_token']
        
        # アクセストークン取得
        self.refresh_access_token()
    
    def refresh_access_token(self):
        """Refresh tokenからアクセストークンを取得"""
        url = "https://oauth2.googleapis.com/token"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")
        
        self.access_token = response.json()['access_token']
        print("✓ Access token取得成功")
    
    def append_rows(self, sheet_id, values, sheet_name=None):
        """行を追加"""
        range_spec = f"{sheet_name}!A:G" if sheet_name else "A:G"
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{range_spec}:append"
        params = {
            'valueInputOption': 'RAW',  # RAWで送信（日付の自動変換を防ぐ）
            'insertDataOption': 'INSERT_ROWS'
        }
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        body = {
            'values': values
        }
        
        response = requests.post(url, params=params, headers=headers, json=body)
        if response.status_code != 200:
            raise Exception(f"Failed to append: {response.text}")
        
        result = response.json()
        updated_rows = result.get('updates', {}).get('updatedRows', 0)
        print(f"✓ {updated_rows}行追加成功")
        return True

def test_income():
    """収入追記テスト"""
    print("=== 収入スプレッドシートテスト ===")
    
    api = SheetsAPI()
    values = [[
        datetime.now().strftime("%Y-%m-%d"),
        "Stripe（テスト）",
        "",
        "API直接テスト",
        "1000",
        "円",
        ""
    ]]
    
    api.append_rows(INCOME_SHEET_ID, values)

def test_receipt():
    """領収書追記テスト"""
    print("=== 領収書スプレッドシートテスト ===")
    
    api = SheetsAPI()
    values = [[
        datetime.now().strftime("%Y-%m-%d"),
        "株式会社テスト",
        "東京都...",
        "交通費",
        "5000",
        "円",
        "https://drive.google.com/..."
    ]]
    
    api.append_rows(RECEIPT_SHEET_ID, values)

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == "income":
                test_income()
            elif sys.argv[1] == "receipt":
                test_receipt()
            else:
                print("Usage: sheets_api.py [income|receipt]")
        else:
            test_income()
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)
