#!/usr/bin/env python3
"""
LINE Webhook サーバー（Anthropic Claude Vision）
画像受信 → Claude分析 → Drive保存 → Sheet追記 → 完了通知
"""

import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, ImageMessage, TextSendMessage
import requests

# 環境変数
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

app = Flask(__name__)

if CHANNEL_ACCESS_TOKEN and CHANNEL_SECRET:
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(CHANNEL_SECRET)
else:
    line_bot_api = None
    handler = None
    print("⚠️  LINE credentials not set")

DRIVE_FOLDER_ID = "1pzI8BkAGrio16HTGpVOyvB25rV8IOO_g"
SHEET_ID = "1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
EXPENSE_SHEET_NAME = "2026年経費領収書"

def analyze_receipt_with_claude(image_path):
    """Claude Vision APIで領収書分析"""
    if not ANTHROPIC_API_KEY:
        raise Exception("ANTHROPIC_API_KEY not set")
    
    print("  Claude分析中...")
    
    # 画像をbase64エンコード
    with open(image_path, 'rb') as f:
        image_data = base64.standard_b64encode(f.read()).decode()
    
    # Claude API呼び出し
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    prompt = """この領収書・請求書の画像から以下の情報を抽出してJSON形式で回答してください：

{
  "date": "YYYY/MM/DD形式の日付",
  "recipient": "宛名（会社名・店名）",
  "address": "発行者の住所（あれば、なければ空文字）",
  "doc_type": "領収書 or 請求書",
  "issuer": "発行元（会社名・個人名）",
  "content": "内容・品目（例：交通費、売却報酬等）",
  "amount": "金額（数字のみ、カンマなし）",
  "currency": "円"
}

JSONのみを出力してください。"""
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1024,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Claude API error: {response.text}")
    
    result = response.json()
    text = result['content'][0]['text']
    
    # JSONを抽出
    import re
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        expense_data = json.loads(json_match.group(0))
    else:
        expense_data = json.loads(text)
    
    print(f"  ✓ Claude分析完了")
    print(f"    日付: {expense_data.get('date')}")
    print(f"    宛名: {expense_data.get('recipient')}")
    print(f"    金額: {expense_data.get('amount')}{expense_data.get('currency')}")
    
    return expense_data

def upload_to_drive(image_path):
    """Driveにアップロード"""
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
    
    print(f"  ✓ Drive保存: {drive_url}")
    
    return drive_url

def append_to_sheet(expense_data, drive_url):
    """スプレッドシートに追記"""
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
    
    # メモ詳細化
    parts = []
    doc_type = expense_data.get('doc_type', '領収書')
    parts.append(doc_type)
    
    issuer = expense_data.get('issuer', '')
    if issuer:
        parts.append(f"発行: {issuer}")
    
    if '請求書' in doc_type:
        target_month = expense_data.get('target_month', '')
        if target_month:
            parts.append(f"{target_month}分")
    
    content = expense_data.get('content', '')
    if content:
        parts.append(content)
    
    memo = ' - '.join(parts) if parts else '領収書'
    
    # 空白行検索
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{EXPENSE_SHEET_NAME}!A:A"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    values = response.json().get('values', [])
    
    row_num = 2
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
    
    print(f"  ✓ Sheet追記: A{row_num}")

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
        
        print(f"  ✓ 画像保存")
        
        # Claude分析
        expense_data = analyze_receipt_with_claude(image_path)
        
        # Driveアップロード
        drive_url = upload_to_drive(image_path)
        
        # Sheet追記
        append_to_sheet(expense_data, drive_url)
        
        # 完了通知
        message = f"""✅ 処理完了しました！

日付: {expense_data.get('date')}
宛名: {expense_data.get('recipient')}
金額: {expense_data.get('amount')}{expense_data.get('currency')}
内容: {expense_data.get('content')}

Drive: {drive_url}"""
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )
        
        print("✓ 処理完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'❌ エラーが発生しました:\n{str(e)}')
        )

@app.route("/health", methods=['GET'])
def health():
    """ヘルスチェック"""
    return {'status': 'ok', 'line_configured': bool(handler), 'anthropic_configured': bool(ANTHROPIC_API_KEY)}

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5001))
    print(f"Starting LINE Webhook server on port {port}")
    print(f"Anthropic API: {'✓' if ANTHROPIC_API_KEY else '❌'}")
    app.run(host='0.0.0.0', port=port, debug=True)
