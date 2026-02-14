# LINE Bot Webhook 完全セットアップガイド

## ✅ 取得済み情報

- **Channel ID**: 2009132576
- **Channel Secret**: 59c8cb272d41d5a849adb7b08764f83e
- **Channel Access Token**: (設定済み)

---

## 🚀 セットアップ手順

### ステップ1: Webhookサーバー起動

```bash
cd ~/Documents/OpenClaw-Workspace
bash bin/start-line-webhook.sh
```

サーバーが起動したら **このターミナルはそのまま** にしておく。

---

### ステップ2: ngrokでトンネル作成

**新しいターミナルを開いて**：

```bash
ngrok http 5000
```

表示される情報から **Forwarding URL** をコピー：
```
Forwarding    https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:5000
```

この `https://xxxx-xxxx-xxxx.ngrok-free.app` をコピー

---

### ステップ3: LINE Developers で Webhook 設定

1. https://developers.line.biz/console/ を開く
2. 「PLai領収書管理」チャネルを選択
3. 「Messaging API」タブをクリック
4. **Webhook settings** セクション:
   - Webhook URL: `https://xxxx-xxxx-xxxx.ngrok-free.app/webhook/line` （ngrok URLに `/webhook/line` を追加）
   - 「Update」をクリック
   - 「Verify」をクリック → Success が出ればOK

5. **Webhook の利用** を「ON」にする

6. **応答メッセージ** を「OFF」にする
   - 「Messaging API」タブの下の方
   - 「応答メッセージ」→「編集」→「OFF」

---

### ステップ4: 友だち追加

1. 同じページの「Messaging API」タブ
2. **QRコード** が表示されている
3. LINEアプリでQRコードをスキャン
4. 友だち追加

---

### ステップ5: テスト

1. 追加したBotに **領収書画像を送信**
2. 「✅ 領収書を受け付けました！」と返信が来ればOK
3. Google Drive と スプレッドシートを確認

---

## 🔧 トラブルシューティング

### Webhook Verify が失敗する
- ngrok のURLが正しいか確認
- `/webhook/line` を忘れずに
- Webhookサーバーが起動しているか確認

### 画像を送っても反応しない
- Webhook が「ON」になっているか
- 応答メッセージが「OFF」になっているか
- サーバーのログを確認

---

## 📝 本番運用時

ngrokは開発用。本番では：
1. Vercel/Railway にデプロイ
2. または固定IPでポート開放
3. HTTPS必須

---

## 🎯 次のステップ

1. ✅ Webhookサーバー起動
2. ✅ ngrok起動
3. ✅ LINE設定
4. ✅ テスト
5. ⬜ Claude分析統合
6. ⬜ 本番デプロイ
