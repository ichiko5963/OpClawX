#!/usr/bin/env python3
"""
LINE公式アカウント使い方マニュアル（Google Docs版）- 修正版
既存ドキュメントに追記
"""

import os
import sys
import json
from pathlib import Path
import requests

OAUTH_TOKEN_FILE = Path("/tmp/google_oauth_tokens.json")

def get_access_token():
    """OAuth access token取得"""
    data = json.loads(OAUTH_TOKEN_FILE.read_text())
    url = "https://oauth2.googleapis.com/token"
    response = requests.post(url, data={
        'client_id': data['client_id'],
        'client_secret': data['client_secret'],
        'refresh_token': data['refresh_token'],
        'grant_type': 'refresh_token'
    })
    return response.json()['access_token']

def main():
    """メイン処理"""
    doc_id = "1ayqUFwQfSV_NNy_fQsPG3JjUkZfJOi6slsOwYRquQm0"
    
    access_token = get_access_token()
    
    url = f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # タイトル
    requests_list = [{
        'insertText': {
            'location': {'index': 1},
            'text': 'PLai領収書管理 使い方マニュアル\n\n'
        }
    }]
    
    # タイトルスタイル
    requests_list.append({
        'updateParagraphStyle': {
            'range': {'startIndex': 1, 'endIndex': 23},
            'paragraphStyle': {
                'namedStyleType': 'HEADING_1',
                'alignment': 'CENTER'
            },
            'fields': 'namedStyleType,alignment'
        }
    })
    
    # 本文
    main_text = """このLINE公式アカウントに領収書・請求書の画像を送るだけで、自動的にGoogleスプレッドシートに登録されます。

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 基本的な使い方
━━━━━━━━━━━━━━━━━━━━━━━━━━

1. このアカウントに領収書・請求書の写真を送信
2. 数秒待つ
3. 自動的に内容を読み取ってスプレッドシートに保存
4. 確認メッセージが届く

たったこれだけ！📸

━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 確認メッセージについて
━━━━━━━━━━━━━━━━━━━━━━━━━━

画像を送信すると、以下のような確認メッセージが届きます：

✅ 処理完了しました！

📋 登録内容:
━━━━━━━━━━━━━━━
1. 日付: 2026/02/10
2. 宛名: 市岡直人様
3. カテゴリー: 従業員請求書
4. 発行者: ハタ コウタ
5. メモ: 売却報酬
6. 金額: 269370円
7. 振込期日: 2026/03/01
━━━━━━━━━━━━━━━

間違いがあればメッセージで教えてください！
例: 「カテゴリーは交通費」「金額は5000円」

Drive: https://drive.google.com/...

━━━━━━━━━━━━━━━━━━━━━━━━━━
✏️ 修正方法（超簡単！）
━━━━━━━━━━━━━━━━━━━━━━━━━━

確認メッセージを見て、もし間違いがあれば、そのままメッセージで教えてください。
AI（GPT-4）が理解して、自動的にスプレッドシートを修正します！

【修正例】

❌ 間違い: カテゴリーが「その他経費」になっている
✅ 送信: 「カテゴリーは交通費」

❌ 間違い: 金額が違う
✅ 送信: 「金額は5000円」

❌ 間違い: 振込期日が抜けている
✅ 送信: 「期日は2026/03/15」

→ すぐに「✅ 修正しました」と返信が来て、スプレッドシートも更新されます！

━━━━━━━━━━━━━━━━━━━━━━━━━━
🏷️ カテゴリーについて
━━━━━━━━━━━━━━━━━━━━━━━━━━

AIが自動的に以下のカテゴリーに分類します：

【自動判定されるカテゴリー】
• 従業員請求書（個人名からの請求）
• 交通費（電車・バス・タクシー）
• 消耗品費（文房具等）
• 通信費（携帯・ネット）
• 広告宣伝費（広告・SNS）
• 外注費（フリーランスへの支払い）
• 会議費（会議用飲食）
• 接待交際費（接待用飲食）
• 備品購入（家具・機器）
• 書籍・資料費
• その他経費

特に、発行者が個人名（山田太郎、佐藤花子など）の場合は、
自動的に「従業員請求書」に分類されます。

もし違うカテゴリーにしたい場合は、修正メッセージを送ってください。

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 スプレッドシートの列構成
━━━━━━━━━━━━━━━━━━━━━━━━━━

以下の9項目が自動的に入力されます：

1. 日付
2. 宛名
3. カテゴリー
4. 発行者の名前と住所
5. メモ
6. 金額
7. 通貨
8. URL（Drive保存先）
9. 振り込み期日

━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 ポイント
━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 写真は明るいところで撮影してください
✅ 文字がはっきり見えるように撮影してください
✅ 複数枚ある場合は、1枚ずつ送信してください
✅ 間違いがあればすぐに修正メッセージを送れます
✅ 修正は何度でもできます

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 セキュリティ
━━━━━━━━━━━━━━━━━━━━━━━━━━

• 画像はGoogle Driveの専用フォルダに保存されます
• スプレッドシートは指定されたシートのみにアクセス
• 送信された画像は安全に管理されます

━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ よくある質問
━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: 手書きの領収書でも大丈夫？
A: はい！できるだけ読めるように撮影してください。

Q: 修正は何回でもできる？
A: はい！何度でも修正できます。

Q: PDFは送れる？
A: 現在は画像（写真）のみ対応しています。
   PDFの場合はスクリーンショットを撮って送ってください。

Q: 処理に時間がかかるのはなぜ？
A: AI（GPT-4）が画像を分析しているためです。
   通常5〜10秒程度で完了します。

━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 お問い合わせ
━━━━━━━━━━━━━━━━━━━━━━━━━━

不明点があれば、このアカウントにメッセージを送ってください。

最終更新: 2026年2月15日
バージョン: 2.0（修正機能対応版）
"""
    
    requests_list.append({
        'insertText': {
            'location': {'index': 24},
            'text': main_text
        }
    })
    
    response = requests.post(url, headers=headers, json={'requests': requests_list})
    
    if response.status_code == 200:
        print("✅ マニュアル更新完了！")
        print(f"📄 URL: https://docs.google.com/document/d/{doc_id}/edit")
    else:
        print(f"❌ エラー: {response.text}")

if __name__ == "__main__":
    main()
