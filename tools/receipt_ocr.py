#!/usr/bin/env python3
"""
領収書OCR完全版
1. Telegram画像受信
2. Gemini Vision API でOCR（日付、金額、店名抽出）
3. Google Drive保存
4. スプレッドシート追記
"""

import sys
import os
import json
import base64
import requests
from pathlib import Path
from datetime import datetime

# 環境変数
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")

# スプレッドシート
SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
SHEET_NAME = "2026年収入"  # 収入も領収書もここ

# Drive folder
DRIVE_FOLDER_NAME = "法人領収書まとめ"

class ReceiptProcessor:
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
        
        # アクセストークン取得
        self.refresh_access_token()
    
    def refresh_access_token(self):
        """Refresh tokenからアクセストークン取得"""
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
    
    def ocr_with_gemini(self, image_path):
        """Gemini Vision APIでOCR"""
        if not GOOGLE_API_KEY:
            raise Exception("GOOGLE_API_KEY not set")
        
        print(f"\n=== Gemini Vision API でOCR ===")
        print(f"画像: {image_path}")
        
        # 画像をbase64エンコード
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        # Gemini API呼び出し
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}"
        
        prompt = """この領収書画像から以下の情報を抽出してください：

1. 日付（YYYY/MM/DD形式）
2. 宛名（会社名・店名）
3. 発行者の住所（あれば）
4. 金額（数字のみ）
5. 通貨（円、ドル等）

JSON形式で回答してください：
{
  "date": "2026/01/15",
  "recipient": "株式会社〇〇",
  "address": "東京都...",
  "amount": "10000",
  "currency": "円",
  "memo": "交通費"
}

情報がない場合は空文字""にしてください。"""
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_data
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
        
        # JSONを抽出（```json ... ```の中）
        import re
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            receipt_data = json.loads(json_match.group(1))
        else:
            # そのままJSONとしてパース試行
            receipt_data = json.loads(text)
        
        print("✓ OCR完了:")
        print(f"  日付: {receipt_data.get('date')}")
        print(f"  宛名: {receipt_data.get('recipient')}")
        print(f"  金額: {receipt_data.get('amount')}{receipt_data.get('currency')}")
        
        return receipt_data
    
    def upload_to_drive(self, image_path, filename):
        """Google Driveにアップロード"""
        print(f"\n=== Google Driveにアップロード ===")
        
        # フォルダID取得（「法人領収書まとめ」）
        folder_id = self.get_or_create_folder(DRIVE_FOLDER_NAME)
        
        # ファイルアップロード
        metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        files = {
            'data': ('metadata', json.dumps(metadata), 'application/json'),
            'file': open(image_path, 'rb')
        }
        
        url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.post(url, headers=headers, files=files)
        if response.status_code != 200:
            raise Exception(f"Drive upload failed: {response.text}")
        
        file_data = response.json()
        file_id = file_data['id']
        file_url = f"https://drive.google.com/file/d/{file_id}/view"
        
        print(f"✓ アップロード完了")
        print(f"  URL: {file_url}")
        
        return file_url
    
    def get_or_create_folder(self, folder_name):
        """フォルダを取得または作成"""
        # フォルダ検索
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            'q': f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            'fields': 'files(id, name)'
        }
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.get(url, params=params, headers=headers)
        files = response.json().get('files', [])
        
        if files:
            return files[0]['id']
        
        # フォルダ作成
        metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        response = requests.post(url, headers=headers, json=metadata)
        return response.json()['id']
    
    def append_to_sheet(self, receipt_data, drive_url):
        """スプレッドシートに追記"""
        print(f"\n=== スプレッドシートに追記 ===")
        
        row = [
            receipt_data.get('date', ''),
            receipt_data.get('recipient', ''),
            receipt_data.get('address', ''),
            receipt_data.get('memo', '領収書'),
            receipt_data.get('amount', ''),
            receipt_data.get('currency', '円'),
            drive_url
        ]
        
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{SHEET_NAME}!A:G:append"
        params = {
            'valueInputOption': 'RAW',
            'insertDataOption': 'INSERT_ROWS'
        }
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        body = {'values': [row]}
        
        response = requests.post(url, params=params, headers=headers, json=body)
        if response.status_code != 200:
            raise Exception(f"Sheet append failed: {response.text}")
        
        print("✓ スプレッドシート追記完了")
    
    def process_receipt(self, image_path):
        """領収書処理メイン"""
        print(f"=== 領収書処理開始 ===")
        print(f"画像: {image_path}")
        
        # 1. OCR
        receipt_data = self.ocr_with_gemini(image_path)
        
        # 2. Drive保存
        filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        drive_url = self.upload_to_drive(image_path, filename)
        
        # 3. スプレッドシート追記
        self.append_to_sheet(receipt_data, drive_url)
        
        print("\n✅ 領収書処理完了！")
        print(f"スプレッドシート: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: receipt_ocr.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        processor = ReceiptProcessor()
        processor.process_receipt(image_path)
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
