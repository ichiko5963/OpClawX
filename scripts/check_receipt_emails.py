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
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

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
        url = "https://oauth2.googleapis.com/token"
        data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'refresh_token': GOOGLE_REFRESH_TOKEN,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(url, data=data)
        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")
        
        return response.json()['access_token']
    
    def search_receipt_emails(self):
        """過去1時間の領収書メールを検索"""
        print("=== 領収書メール検索 ===")
        
        # 1時間前
        after_date = (datetime.now() - timedelta(hours=1)).strftime('%Y/%m/%d')
        
        # 検索クエリ: 添付ファイルあり + 領収書キーワード
        query = f'has:attachment after:{after_date} ('
        query += ' OR '.join([f'subject:{kw}' for kw in RECEIPT_KEYWORDS])
        query += ')'
        
        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
        params = {'q': query, 'maxResults': 50}
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Gmail search failed: {response.text}")
        
        messages = response.json().get('messages', [])
        print(f"✓ {len(messages)}件のメール発見")
        
        return messages
    
    def get_message_details(self, message_id):
        """メール詳細取得"""
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.get(url, headers=headers)
        return response.json()
    
    def download_attachments(self, message_id, message_data):
        """添付ファイル（画像）をダウンロード"""
        attachments = []
        
        for part in message_data.get('payload', {}).get('parts', []):
            filename = part.get('filename', '')
            
            # 画像ファイルのみ
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
                continue
            
            attachment_id = part.get('body', {}).get('attachmentId')
            if not attachment_id:
                continue
            
            # ダウンロード
            url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/attachments/{attachment_id}"
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                continue
            
            data = response.json().get('data', '')
            file_data = base64.urlsafe_b64decode(data)
            
            attachments.append({
                'filename': filename,
                'data': file_data
            })
        
        return attachments
    
    def upload_to_drive(self, filename, file_data):
        """Driveにアップロード"""
        metadata = {
            'name': filename,
            'parents': [DRIVE_FOLDER_ID]
        }
        
        files = {
            'data': ('metadata', json.dumps(metadata), 'application/json'),
            'file': (filename, file_data)
        }
        
        url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.post(url, headers=headers, files=files)
        if response.status_code != 200:
            raise Exception(f"Upload failed: {response.text}")
        
        file_id = response.json()['id']
        return f"https://drive.google.com/file/d/{file_id}/view"
    
    def save_to_queue(self, receipt_info):
        """処理キューに保存（OpenClawが後で処理）"""
        queue_dir = Path('data/receipt_queue')
        queue_dir.mkdir(parents=True, exist_ok=True)
        
        queue_file = queue_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        queue_file.write_text(json.dumps(receipt_info, ensure_ascii=False, indent=2))
        
        print(f"✓ キュー保存: {queue_file}")
    
    def process(self):
        """メイン処理"""
        print(f"=== 領収書メール監視開始 ({datetime.now()}) ===")
        
        # メール検索
        messages = self.search_receipt_emails()
        
        if not messages:
            print("新しい領収書メールなし")
            return
        
        processed = 0
        for msg in messages:
            try:
                # メール詳細取得
                message_data = self.get_message_details(msg['id'])
                subject = ''
                
                for header in message_data.get('payload', {}).get('headers', []):
                    if header['name'] == 'Subject':
                        subject = header['value']
                        break
                
                print(f"\n処理中: {subject}")
                
                # 添付ファイルダウンロード
                attachments = self.download_attachments(msg['id'], message_data)
                
                if not attachments:
                    print("  添付なし、スキップ")
                    continue
                
                # 各添付ファイルを処理
                for att in attachments:
                    print(f"  添付: {att['filename']}")
                    
                    # Driveアップロード
                    drive_url = self.upload_to_drive(att['filename'], att['data'])
                    print(f"  ✓ Drive: {drive_url}")
                    
                    # 処理キューに保存
                    self.save_to_queue({
                        'email_subject': subject,
                        'filename': att['filename'],
                        'drive_url': drive_url,
                        'received_at': datetime.now().isoformat(),
                        'message_id': msg['id']
                    })
                    
                    processed += 1
            
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                continue
        
        print(f"\n✅ 処理完了: {processed}件")

if __name__ == "__main__":
    try:
        monitor = ReceiptEmailMonitor()
        monitor.process()
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
