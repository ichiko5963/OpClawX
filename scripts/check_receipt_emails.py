#!/usr/bin/env python3
"""
Gmail領収書メール監視
1時間ごとにGitHub Actionsから実行
領収書添付を検出 → Drive保存 → 処理キューに追加
"""

import os
import json
import base64
import requests
from datetime import datetime, timedelta
from pathlib import Path

# 環境変数
OAUTH_TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")
SHEET_ID = os.getenv("SHEET_ID")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
STATE_FILE = Path("data/email_receipt_state.json")

# 領収書検出キーワード
RECEIPT_KEYWORDS = [
    '領収書', 'レシート', '請求書', '明細',
    '領収証', 'receipt', 'invoice'
]

class ReceiptEmailMonitor:
    def __init__(self):
        self.access_token = self.get_access_token()
    
    def get_access_token(self):
        """Access token取得"""
        if not OAUTH_TOKEN_FILE.exists():
            raise Exception("OAuth token file not found")
        
        data = json.loads(OAUTH_TOKEN_FILE.read_text())
        
        url = "https://oauth2.googleapis.com/token"
        response = requests.post(url, data={
            'client_id': data['client_id'],
            'client_secret': data['client_secret'],
            'refresh_token': data['refresh_token'],
            'grant_type': 'refresh_token'
        })
        
        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")
        
        return response.json()['access_token']
    
    def get_state(self):
        """同期状態取得"""
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text())
        return {
            'last_check': None,
            'initial_sync_done': False
        }
    
    def update_state(self, state):
        """同期状態更新"""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2))
    
    def search_receipt_emails(self, days_back=1):
        """領収書メールを検索"""
        print(f"=== 領収書メール検索（過去{days_back}日）===")
        
        # 日付計算
        after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
        
        # キーワードクエリ
        keywords_query = ' OR '.join([f'subject:{kw}' for kw in RECEIPT_KEYWORDS])
        query = f'has:attachment ({keywords_query}) after:{after_date}'
        
        print(f"Query: {query}")
        
        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {
            'q': query,
            'maxResults': 100
        }
        
        response = requests.get(url, headers=headers, params=params)
        messages = response.json().get('messages', [])
        
        print(f"✓ {len(messages)}件検出")
        
        return messages
    
    def get_message_detail(self, message_id):
        """メール詳細取得"""
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.get(url, headers=headers)
        return response.json()
    
    def download_attachment(self, message_id, attachment_id, filename):
        """添付ファイルダウンロード"""
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/attachments/{attachment_id}"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.get(url, headers=headers)
        data = response.json()['data']
        
        # Base64デコード
        file_data = base64.urlsafe_b64decode(data)
        
        # 保存
        temp_dir = Path("/tmp/receipts")
        temp_dir.mkdir(exist_ok=True)
        
        file_path = temp_dir / filename
        file_path.write_bytes(file_data)
        
        return file_path
    
    def upload_to_drive(self, file_path):
        """Google Driveにアップロード"""
        url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        metadata = {
            'name': file_path.name,
            'parents': [DRIVE_FOLDER_ID]
        }
        
        files = {
            'data': ('metadata', json.dumps(metadata), 'application/json'),
            'file': open(file_path, 'rb')
        }
        
        response = requests.post(url, headers=headers, files=files)
        file_id = response.json()['id']
        drive_url = f"https://drive.google.com/file/d/{file_id}/view"
        
        return drive_url
    
    def process_receipts(self):
        """領収書処理メイン"""
        state = self.get_state()
        
        # 初回同期チェック
        if not state['initial_sync_done']:
            print("✨ 初回同期モード（過去30日）")
            days_back = 30
        else:
            print("📅 通常モード（過去1日）")
            days_back = 1
        
        # メール検索
        messages = self.search_receipt_emails(days_back)
        
        if not messages:
            print("✓ 新しい領収書メールなし")
            return
        
        processed = 0
        for msg in messages[:10]:  # 最大10件
            try:
                detail = self.get_message_detail(msg['id'])
                
                # 件名取得
                headers = detail.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                
                print(f"\n📧 {subject}")
                
                # 添付ファイル処理
                parts = detail.get('payload', {}).get('parts', [])
                for part in parts:
                    if part.get('filename'):
                        filename = part['filename']
                        attachment_id = part['body'].get('attachmentId')
                        
                        if attachment_id:
                            print(f"  📎 {filename}")
                            
                            # ダウンロード
                            file_path = self.download_attachment(msg['id'], attachment_id, filename)
                            
                            # Driveアップロード
                            drive_url = self.upload_to_drive(file_path)
                            print(f"  ✓ Drive: {drive_url}")
                            
                            processed += 1
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                continue
        
        # 状態更新
        state['last_check'] = datetime.now().isoformat()
        state['initial_sync_done'] = True
        state['last_processed'] = processed
        self.update_state(state)
        
        print(f"\n✅ 処理完了: {processed}件")

def main():
    try:
        monitor = ReceiptEmailMonitor()
        monitor.process_receipts()
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
