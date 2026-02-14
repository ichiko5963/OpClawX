#!/usr/bin/env python3
"""
LINE Webhook サーバー（キュー方式）
画像受信 → Drive保存 → キューに追加
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, ImageMessage, TextSendMessage

# 環境変数
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')

app = Flask(__name__)

if CHANNEL_ACCESS_TOKEN and CHANNEL_SECRET:
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(CHANNEL_SECRET)
else:
    line_bot_api = None
    handler = None
    print("⚠️  LINE credentials not set")

QUEUE_DIR = Path.home() / "Documents/OpenClaw-Workspace/data/line_queue"
DRIVE_FOLDER_ID = "1pzI8BkAGrio16HTGpVOyvB25rV8IOO_g"

def upload_to_drive(image_path):
    """Driveにアップロード"""
    import json
    import requests
    
    TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")
    
    # OAuth token取得
    data = json.loads(TOKEN_FILE.read_text())
    url = "https://oauth2.googleapis.com/token"
    response = requests.post(url, data={
        'client_id': data['client_id'],
        'client_secret': data['client_secret'],
        'refresh_token': data['refresh_token'],
        'grant_type': 'refresh_token'
    })
    access_token = response.json()['access_token']
    
    # Driveアップロード
    filename = f"line_receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    metadata = {
        'name': filename,
        'parents': [DRIVE_FOLDER_ID]
    }
    
    files = {
        'data': ('metadata', json.dumps(metadata), 'application/json'),
        'file': open(image_path, 'rb')
    }
    
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.post(url, headers=headers, files=files)
    file_id = response.json()['id']
    drive_url = f"https://drive.google.com/file/d/{file_id}/view"
    
    return file_id, drive_url

@app.route("/webhook/line", methods=['POST'])
def webhook():
    """LINE Webhook エンドポイント"""
    if not handler:
        abort(500)
    
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """画像メッセージ処理"""
    print(f"=== LINE画像受信 ===")
    print(f"Message ID: {event.message.id}")
    
    try:
        # 画像ダウンロード
        message_content = line_bot_api.get_message_content(event.message.id)
        
        temp_dir = Path("/tmp/line_receipts")
        temp_dir.mkdir(exist_ok=True)
        
        image_path = temp_dir / f"receipt_{event.message.id}.jpg"
        with open(image_path, 'wb') as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
        
        print(f"✓ 画像保存: {image_path}")
        
        # Driveアップロード
        file_id, drive_url = upload_to_drive(image_path)
        print(f"✓ Drive保存: {drive_url}")
        
        # キューに保存
        QUEUE_DIR.mkdir(parents=True, exist_ok=True)
        queue_file = QUEUE_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{event.message.id}.json"
        
        queue_data = {
            'message_id': event.message.id,
            'user_id': event.source.user_id,
            'reply_token': event.reply_token,
            'image_path': str(image_path),
            'drive_file_id': file_id,
            'drive_url': drive_url,
            'received_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        queue_file.write_text(json.dumps(queue_data, ensure_ascii=False, indent=2))
        print(f"✓ キュー保存: {queue_file}")
        
        # 即座に返信
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='✅ 領収書を受け付けました！\n\nGoogle Driveに保存しました。\n画像を分析中です...\n\n処理完了したら通知します（10分以内）')
        )
        
        print("✓ 返信送信完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='❌ エラーが発生しました。再度お試しください。')
        )

@app.route("/health", methods=['GET'])
def health():
    """ヘルスチェック"""
    return {'status': 'ok', 'line_configured': bool(handler)}

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5001))
    print(f"Starting LINE Webhook server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
