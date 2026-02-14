#!/usr/bin/env python3
"""
LINE Webhook サーバー（OpenAI GPT-4 Vision）
画像受信 → GPT-4V分析 → Drive保存 → Sheet追記 → 完了通知
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
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

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

def analyze_receipt_with_gpt4v(image_path):
    """GPT-4 Vision APIで領収書分析"""
    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY not set")
    
    print("  GPT-4V分析中...")
    
    # 画像をbase64エンコード
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    # OpenAI API呼び出し
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = """この領収書・請求書の画像から以下の情報を抽出してJSON形式で回答してください：

{
  "date": "YYYY/MM/DD形式の日付",
  "recipient": "宛名（会社名・店名）",
  "category": "カテゴリー（以下から選択または新規提案）: 従業員請求書, 交通費, 消耗品費, 通信費, 広告宣伝費, 外注費, 会議費, 接待交際費, 備品購入, 書籍・資料費, その他経費",
  "issuer_name_address": "発行者の名前と住所（改行区切りで両方、例: 山田太郎\\n東京都...）",
  "memo": "メモ・詳細内容",
  "amount": "金額（数字のみ、カンマなし）",
  "currency": "円",
  "payment_due": "振り込み期日（YYYY/MM/DD形式、なければ空文字）"
}

カテゴリー判定ルール:
- 個人名からの請求書 → 従業員請求書
- 電車・バス・タクシー → 交通費
- 文房具・消耗品 → 消耗品費
- 携帯・通信サービス → 通信費
- 広告・SNS広告 → 広告宣伝費
- フリーランスへの支払い → 外注費
- 飲食（会議用） → 会議費
- 飲食（接待） → 接待交際費
- 家具・機器 → 備品購入
- 書籍・教材 → 書籍・資料費

JSONのみを出力してください。"""
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"OpenAI API error: {response.text}")
    
    result = response.json()
    text = result['choices'][0]['message']['content']
    
    # JSONを抽出
    import re
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        expense_data = json.loads(json_match.group(0))
    else:
        expense_data = json.loads(text)
    
    print(f"  ✓ GPT-4V分析完了")
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
    """スプレッドシートに追記（新列構造: 9列）"""
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
    
    # Sheet追記（新列構造）
    row = [[
        expense_data.get('date', ''),                      # A: 日付
        expense_data.get('recipient', ''),                 # B: 宛名
        expense_data.get('category', 'その他経費'),        # C: カテゴリー
        expense_data.get('issuer_name_address', ''),       # D: 発行者の名前と住所
        expense_data.get('memo', ''),                      # E: メモ
        expense_data.get('amount', ''),                    # F: 金額
        expense_data.get('currency', '円'),                # G: 通貨
        drive_url,                                         # H: URL
        expense_data.get('payment_due', '')                # I: 振り込み期日
    ]]
    
    range_name = f"{EXPENSE_SHEET_NAME}!A{row_num}:I{row_num}"
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{range_name}"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    
    requests.put(url, params={'valueInputOption': 'RAW'}, headers=headers, json={'values': row})
    
    print(f"  ✓ Sheet追記: A{row_num}")
    print(f"    カテゴリー: {expense_data.get('category')}")

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
        
        # GPT-4V分析
        expense_data = analyze_receipt_with_gpt4v(image_path)
        
        # Driveアップロード
        drive_url = upload_to_drive(image_path)
        
        # Sheet追記
        append_to_sheet(expense_data, drive_url)
        
        # 完了通知
        message = f"""✅ 処理完了しました！

日付: {expense_data.get('date')}
宛名: {expense_data.get('recipient')}
カテゴリー: {expense_data.get('category')}
金額: {expense_data.get('amount')}{expense_data.get('currency')}
振込期日: {expense_data.get('payment_due') or 'なし'}

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
    return {'status': 'ok', 'line_configured': bool(handler), 'openai_configured': bool(OPENAI_API_KEY)}

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5001))
    print(f"Starting LINE Webhook server on port {port}")
    print(f"OpenAI API: {'✓' if OPENAI_API_KEY else '❌'}")
    app.run(host='0.0.0.0', port=port, debug=True)
