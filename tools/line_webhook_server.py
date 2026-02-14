#!/usr/bin/env python3
"""
LINE Webhook サーバー（OpenAI GPT-4 Vision + 修正対応）
画像受信 → GPT-4V分析 → Drive保存 → Sheet追記 → 完了通知
テキスト受信 → 修正内容解析 → Sheet更新
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
from linebot.models import MessageEvent, ImageMessage, TextMessage, TextSendMessage
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

# セッション管理（最後の処理情報を保存）
CACHE_DIR = Path("/tmp/line_sessions")
CACHE_DIR.mkdir(exist_ok=True)

def save_last_receipt(user_id, row_num, expense_data):
    """最後の処理情報を保存"""
    cache_file = CACHE_DIR / f"{user_id}.json"
    cache_data = {
        'row_num': row_num,
        'expense_data': expense_data,
        'timestamp': datetime.now().isoformat()
    }
    cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2))

def get_last_receipt(user_id):
    """最後の処理情報を取得"""
    cache_file = CACHE_DIR / f"{user_id}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    return None

def analyze_receipt_with_gpt4v(image_path):
    """GPT-4 Vision APIで領収書分析"""
    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY not set")
    
    print("  GPT-4V分析中...")
    
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
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
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
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
    
    import re
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        expense_data = json.loads(json_match.group(0))
    else:
        expense_data = json.loads(text)
    
    print(f"  ✓ GPT-4V分析完了")
    
    return expense_data

def upload_to_drive(image_path):
    """Driveにアップロード"""
    TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")
    
    data = json.loads(TOKEN_FILE.read_text())
    url = "https://oauth2.googleapis.com/token"
    response = requests.post(url, data={
        'client_id': data['client_id'],
        'client_secret': data['client_secret'],
        'refresh_token': data['refresh_token'],
        'grant_type': 'refresh_token'
    })
    access_token = response.json()['access_token']
    
    filename = f"line_receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    metadata = {'name': filename, 'parents': [DRIVE_FOLDER_ID]}
    
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
        expense_data.get('date', ''),
        expense_data.get('recipient', ''),
        expense_data.get('category', 'その他経費'),
        expense_data.get('issuer_name_address', ''),
        expense_data.get('memo', ''),
        expense_data.get('amount', ''),
        expense_data.get('currency', '円'),
        drive_url,
        expense_data.get('payment_due', '')
    ]]
    
    range_name = f"{EXPENSE_SHEET_NAME}!A{row_num}:I{row_num}"
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{range_name}"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    
    requests.put(url, params={'valueInputOption': 'RAW'}, headers=headers, json={'values': row})
    
    print(f"  ✓ Sheet追記: A{row_num}")
    
    return row_num

def update_sheet_row(row_num, updates):
    """スプレッドシートの特定行を更新"""
    TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")
    
    data = json.loads(TOKEN_FILE.read_text())
    url = "https://oauth2.googleapis.com/token"
    response = requests.post(url, data={
        'client_id': data['client_id'],
        'client_secret': data['client_secret'],
        'refresh_token': data['refresh_token'],
        'grant_type': 'refresh_token'
    })
    access_token = response.json()['access_token']
    
    # 列マッピング
    col_map = {
        '日付': 'A', 'date': 'A',
        '宛名': 'B', 'recipient': 'B',
        'カテゴリー': 'C', 'category': 'C',
        '発行者': 'D', '発行者の名前と住所': 'D', 'issuer_name_address': 'D',
        'メモ': 'E', 'memo': 'E',
        '金額': 'F', 'amount': 'F',
        '通貨': 'G', 'currency': 'G',
        'URL': 'H',
        '振り込み期日': 'I', '期日': 'I', 'payment_due': 'I'
    }
    
    for field, value in updates.items():
        if field in col_map:
            col = col_map[field]
            range_name = f"{EXPENSE_SHEET_NAME}!{col}{row_num}"
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{range_name}"
            headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
            
            requests.put(url, params={'valueInputOption': 'RAW'}, headers=headers, json={'values': [[value]]})
            print(f"  ✓ {field} → {value}")

def parse_correction(text):
    """修正指示を解析"""
    if not OPENAI_API_KEY:
        return {}
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""以下のユーザーメッセージから、領収書データの修正内容を抽出してJSON形式で回答してください：

ユーザーメッセージ: "{text}"

抽出するフィールド:
- date (日付)
- recipient (宛名)
- category (カテゴリー)
- issuer_name_address (発行者の名前と住所)
- memo (メモ)
- amount (金額)
- currency (通貨)
- payment_due (振り込み期日)

例:
"カテゴリーは交通費に変更" → {{"category": "交通費"}}
"金額は5000円" → {{"amount": "5000"}}
"期日は2026/03/01" → {{"payment_due": "2026/03/01"}}

JSONのみを出力してください。修正がない場合は {{}} を返してください。"""
    
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return {}
    
    result = response.json()
    text_result = result['choices'][0]['message']['content']
    
    import re
    json_match = re.search(r'\{.*\}', text_result, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(0))
    return {}

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
    
    try:
        message_content = line_bot_api.get_message_content(event.message.id)
        
        temp_dir = Path("/tmp/line_receipts")
        temp_dir.mkdir(exist_ok=True)
        
        image_path = temp_dir / f"receipt_{event.message.id}.jpg"
        with open(image_path, 'wb') as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
        
        expense_data = analyze_receipt_with_gpt4v(image_path)
        drive_url = upload_to_drive(image_path)
        row_num = append_to_sheet(expense_data, drive_url)
        
        # セッション保存
        save_last_receipt(event.source.user_id, row_num, expense_data)
        
        # 全情報表示 + 修正促し
        message = f"""✅ 処理完了しました！

📋 登録内容:
━━━━━━━━━━━━━━━
1. 日付: {expense_data.get('date')}
2. 宛名: {expense_data.get('recipient')}
3. カテゴリー: {expense_data.get('category')}
4. 発行者: {expense_data.get('issuer_name_address', '').split(chr(10))[0] if expense_data.get('issuer_name_address') else ''}
5. メモ: {expense_data.get('memo')}
6. 金額: {expense_data.get('amount')}{expense_data.get('currency')}
7. 振込期日: {expense_data.get('payment_due') or 'なし'}
━━━━━━━━━━━━━━━

間違いがあればメッセージで教えてください！
例: 「カテゴリーは交通費」「金額は5000円」

Drive: {drive_url}"""
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        print("✓ 処理完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'❌ エラーが発生しました:\n{str(e)}')
        )

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """テキストメッセージ処理（修正指示）"""
    print(f"=== LINEテキスト受信 ===")
    
    try:
        user_id = event.source.user_id
        text = event.message.text
        
        # 最後の処理情報取得
        last_receipt = get_last_receipt(user_id)
        
        if not last_receipt:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='直前の領収書情報が見つかりません。先に領収書画像を送信してください。')
            )
            return
        
        # 修正内容解析
        updates = parse_correction(text)
        
        if not updates:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='修正内容が理解できませんでした。もう一度具体的に教えてください。\n例: 「カテゴリーは交通費」')
            )
            return
        
        # スプレッドシート更新
        row_num = last_receipt['row_num']
        update_sheet_row(row_num, updates)
        
        # 確認メッセージ
        updates_text = '\n'.join([f'• {k} → {v}' for k, v in updates.items()])
        message = f"""✅ 修正しました！

{updates_text}

スプレッドシートを確認してください。"""
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        print(f"✓ 修正完了: {updates}")
        
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
