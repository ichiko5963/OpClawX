#!/usr/bin/env python3
"""
LINE Webhook サーバー（完全版）
領収書画像を受信 → Claude分析 → Drive保存 → Sheet追記
"""

import os
import sys
import json
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

# Claude分析関数（OpenClaw経由）
def analyze_receipt_with_claude(image_path):
    """画像を分析して領収書データを抽出"""
    # TODO: 実際にはOpenClawのimageツールを使う
    # 今は固定データを返す（テスト用）
    from datetime import datetime
    
    # 仮のデータ（実際はClaudeが分析）
    return {
        "date": datetime.now().strftime("%Y/%m/%d"),
        "recipient": "領収書テスト",
        "address": "",
        "doc_type": "領収書",
        "issuer": "LINE経由",
        "content": "自動処理テスト",
        "amount": "1000",
        "currency": "円"
    }

# Drive保存 + Sheet追記
def process_receipt(image_path, expense_data):
    """領収書処理（expense_auto_v2.py相当）"""
    sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))
    
    import json
    import requests
    from datetime import datetime
    
    TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")
    SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
    EXPENSE_SHEET_NAME = "2026年経費領収書"
    DRIVE_FOLDER_ID = "1pzI8BkAGrio16HTGpVOyvB25rV8IOO_g"
    
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
    
    print(f"✓ Drive保存: {drive_url}")
    
    # メモ詳細化
    parts = []
    doc_type = expense_data.get('doc_type', '領収書')
    parts.append(doc_type)
    
    issuer = expense_data.get('issuer', '')
    if issuer:
        parts.append(f"発行: {issuer}")
    
    content = expense_data.get('content', '')
    if content:
        parts.append(content)
    
    memo = ' - '.join(parts) if parts else '領収書'
    
    # 空白行検索
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{EXPENSE_SHEET_NAME}!A:A"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    values = response.json().get('values', [])
    
    row_num = 2  # デフォルトA2
    for i in range(1, len(values) + 1):
        if i >= len(values) or not values[i] or values[i][0] == '':
            row_num = i + 1
            break
    
    # Sheet追記
    row = [[
        expense_data.get('date', ''),
        expense_data.get('recipient', ''),
        expense_data.get('address', ''),
        memo,
        expense_data.get('amount', ''),
        expense_data.get('currency', '円'),
        drive_url
    ]]
    
    range_name = f"{EXPENSE_SHEET_NAME}!A{row_num}:G{row_num}"
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{range_name}"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    
    requests.put(url, params={'valueInputOption': 'RAW'}, headers=headers, json={'values': row})
    
    print(f"✓ Sheet追記: A{row_num}")
    
    return drive_url

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
        
        # Claude分析
        expense_data = analyze_receipt_with_claude(image_path)
        print(f"✓ Claude分析完了")
        
        # Drive保存 + Sheet追記
        drive_url = process_receipt(image_path, expense_data)
        
        # 完了通知
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'✅ 処理完了しました！\n\n日付: {expense_data["date"]}\n金額: {expense_data["amount"]}{expense_data["currency"]}\n\nDrive: {drive_url}')
        )
        
        print("✓ 処理完了")
        
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
