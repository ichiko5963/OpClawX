#!/usr/bin/env python3
"""
LINE Webhook サーバー（簡易版）
領収書画像を受信 → 自動処理
"""

import os
import sys
from pathlib import Path
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

@app.route("/webhook/line", methods=['POST'])
def webhook():
    """LINE Webhook エンドポイント"""
    if not handler:
        abort(500)
    
    # 署名検証
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
        
        # 一時保存
        temp_dir = Path("/tmp/line_receipts")
        temp_dir.mkdir(exist_ok=True)
        
        image_path = temp_dir / f"receipt_{event.message.id}.jpg"
        with open(image_path, 'wb') as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
        
        print(f"✓ 画像保存: {image_path}")
        
        # TODO: Claude分析 → Drive → Sheet
        # tools/expense_auto_v2.py を呼び出し
        
        # 返信
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='✅ 領収書を受け付けました！処理中...')
        )
        
        print("✓ 返信送信完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='❌ エラーが発生しました')
        )

@app.route("/health", methods=['GET'])
def health():
    """ヘルスチェック"""
    return {'status': 'ok', 'line_configured': bool(handler)}

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print(f"Starting LINE Webhook server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
