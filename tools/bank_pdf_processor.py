#!/usr/bin/env python3
"""
銀行明細PDF自動処理
1. PDFからテキスト抽出（Gemini Vision API）
2. 入金抽出
3. スプレッドシート追記
"""

import sys
import os
import json
import base64
import requests
from pathlib import Path

# 環境変数
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")

# スプレッドシート
SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
SHEET_NAME = "2026年収入"

# 入金判定キーワード
INCOME_KEYWORDS = [
    'ｶﾞｲｺｸﾋｼﾑｹｿｳｷﾝ', 'ﾋﾟ-ﾃｨﾂｸｽｼﾞﾔﾊﾟﾝ', 'ｽﾄﾗｲﾌﾟｼﾞﾔﾊﾟﾝ',
    'ﾉ-ﾄ', 'ﾎﾟ-ﾄ', 'ﾒﾙﾍﾟｲ', 'ｷﾕｳｼﾕｳﾀﾞｲｶﾞｸ',
    'ﾏｼﾕﾏﾛｴﾝﾀﾒ', 'ｷﾔﾘｱﾃﾞｻﾞｲﾝｾﾝﾀ-', 'ﾐﾝｼﾕｳ',
    'ﾘﾘ', 'ﾌｸｵｶｼﾎｹﾝﾈﾝｷﾝｶ', 'ｵﾘｿｸ'
]

EXPENSE_KEYWORDS = [
    'ﾌﾘｺﾐｼｷﾝ', 'ﾌﾘｺﾐﾃｽｳﾘﾖｳ', 'RS ﾍﾟｲﾍﾟｲ',
    'ATMｼﾊﾗｲ', 'ATMﾃｽｳﾘﾖｳ', 'ﾐﾂｲｽﾐﾄﾓｶ-ﾄﾞ',
    'ﾗｸﾃﾝｶ-ﾄﾞｻ-ﾋﾞｽ', 'ﾗｲﾌｶ-ﾄﾞ'
]

class BankStatementProcessor:
    def __init__(self):
        self.load_credentials()
    
    def load_credentials(self):
        """OAuth情報読み込み"""
        if not TOKEN_FILE.exists():
            raise Exception(f"Token file not found: {TOKEN_FILE}")
        
        data = json.loads(TOKEN_FILE.read_text())
        self.client_id = data['client_id']
        self.client_secret = data['client_secret']
        self.refresh_token = data['refresh_token']
        
        self.refresh_access_token()
    
    def refresh_access_token(self):
        """アクセストークン取得"""
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
    
    def extract_transactions_with_gemini(self, pdf_path):
        """Gemini Vision APIでPDFから取引抽出"""
        if not GOOGLE_API_KEY:
            raise Exception("GOOGLE_API_KEY not set")
        
        print(f"\n=== Gemini Vision API でPDF解析 ===")
        print(f"PDF: {pdf_path}")
        
        # PDFをbase64エンコード
        with open(pdf_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode()
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}"
        
        prompt = """この銀行明細PDFから入金取引のみを抽出してください。

以下の条件で判定：
- 入金: 外国非課税送金、Stripe、Note、Port、メルカリ、九州大学、利息等
- 支出（除外）: 振込、ATM、クレカ支払い等

JSON配列で回答：
[
  {
    "date": "2026/01/06",
    "source": "外国非課税送金",
    "amount": "28522"
  },
  ...
]"""
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "application/pdf",
                                "data": pdf_data
                            }
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.text}")
        
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        
        # JSONを抽出
        import re
        json_match = re.search(r'```json\s*(\[.*?\])\s*```', text, re.DOTALL)
        if json_match:
            transactions = json.loads(json_match.group(1))
        else:
            transactions = json.loads(text)
        
        print(f"✓ {len(transactions)}件の入金を抽出")
        return transactions
    
    def append_to_sheet(self, transactions):
        """スプレッドシートに追記"""
        print(f"\n=== スプレッドシートに追記 ===")
        
        values = []
        for txn in transactions:
            values.append([
                txn.get('date', ''),
                txn.get('source', ''),
                '',  # 住所
                '銀行明細',  # メモ
                txn.get('amount', ''),
                '円',
                ''  # URL
            ])
        
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{SHEET_NAME}!A:G:append"
        params = {
            'valueInputOption': 'RAW',
            'insertDataOption': 'INSERT_ROWS'
        }
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        body = {'values': values}
        
        response = requests.post(url, params=params, headers=headers, json=body)
        if response.status_code != 200:
            raise Exception(f"Sheet append failed: {response.text}")
        
        print(f"✓ {len(values)}件追加完了")
    
    def process_pdf(self, pdf_path):
        """銀行明細PDF処理メイン"""
        print(f"=== 銀行明細PDF処理開始 ===")
        print(f"PDF: {pdf_path}")
        
        # 1. PDF解析（入金抽出）
        transactions = self.extract_transactions_with_gemini(pdf_path)
        
        if not transactions:
            print("入金が見つかりませんでした")
            return
        
        # 2. スプレッドシート追記
        self.append_to_sheet(transactions)
        
        # 3. サマリー表示
        total = sum(int(t.get('amount', 0)) for t in transactions)
        print(f"\n✅ 処理完了！")
        print(f"件数: {len(transactions)}件")
        print(f"総入金額: {total:,}円")
        print(f"スプレッドシート: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: bank_pdf_processor.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    try:
        processor = BankStatementProcessor()
        processor.process_pdf(pdf_path)
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
