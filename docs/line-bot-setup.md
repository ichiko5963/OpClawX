# LINE公式アカウント - 領収書受信システム

## 🎯 目的
LINE公式アカウントで領収書画像を受信 → 自動処理

## 📋 セットアップ手順

### 1. LINE Developers アカウント作成
1. https://developers.line.biz/ にアクセス
2. ログイン（LINEアカウント）
3. 新規プロバイダー作成

### 2. Messaging API チャネル作成
1. プロバイダーを選択
2. 「Messaging APIチャネルを作成」
3. 設定:
   - チャネル名: 領収書受付Bot（仮）
   - チャネル説明: 領収書自動処理
   - 大業種/小業種: 適当に選択
   - メールアドレス: jiuhuot10@gmail.com

### 3. 必要な情報を取得
- **Channel ID**
- **Channel Secret**
- **Channel Access Token** (長期)

### 4. Webhook設定
1. Webhook URLを設定: `https://your-server.com/webhook`
2. Webhook利用: ON
3. 応答メッセージ: OFF
4. Greeting message: OFF

---

## 🔧 実装

### Webhook サーバー
OpenClawのHTTPエンドポイントまたは外部サーバー

```python
# LINE Messaging API
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, ImageMessage

line_bot_api = LineBotApi('CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('CHANNEL_SECRET')

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # 画像ダウンロード
    message_content = line_bot_api.get_message_content(event.message.id)
    
    # 画像保存
    image_path = f"/tmp/receipt_{event.message.id}.jpg"
    with open(image_path, 'wb') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
    
    # Claude分析 → Drive保存 → Sheet追加
    # tools/expense_auto_v2.py を呼び出し
    
    # 返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='✅ 領収書を受け付けました！')
    )
```

---

## 📝 必要な作業

### すぐやること
1. ✅ LINE Developers アカウント作成
2. ✅ Messaging API チャネル作成
3. ✅ Channel Access Token取得
4. ⬜ Webhook サーバー実装
5. ⬜ OpenClawとの連携

### Webhook実装オプション

#### オプション1: OpenClaw組み込み
- OpenClawにHTTPエンドポイント追加
- `/webhook/line` でLINEからのリクエスト受信

#### オプション2: 外部サーバー（Vercel/Railway等）
- 軽量Webhookサーバーをデプロイ
- OpenClawのツールを呼び出し

#### オプション3: ngrok経由（開発用）
- ローカルでWebhookサーバー起動
- ngrokでトンネル作成
- LINE Webhookに設定

---

## 🚀 次のステップ

1. **今すぐ**: LINE Developers で設定開始
2. **Webhook実装**: オプション選択して実装
3. **テスト**: 画像送信 → 自動処理確認

---

## 🔗 参考リンク
- LINE Developers: https://developers.line.biz/
- Messaging API ドキュメント: https://developers.line.biz/ja/docs/messaging-api/
- Python SDK: https://github.com/line/line-bot-sdk-python

---

## 📌 メモ
- Telegramと同じフロー
- 画像受信 → Claude分析 → Drive → Sheet
- 違いはWebhook受信部分だけ
