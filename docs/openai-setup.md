# OpenAI API セットアップガイド

## 🔑 OpenAI API Key取得方法（5分）

### ステップ1: OpenAI アカウント作成
1. https://platform.openai.com/ にアクセス
2. 「Sign up」または既存アカウントでログイン

### ステップ2: API Key作成
1. https://platform.openai.com/api-keys にアクセス
2. 「Create new secret key」をクリック
3. 名前を入力（例: LINE領収書Bot）
4. 「Create secret key」をクリック
5. **表示されたキーをコピー**（一度しか表示されない！）

---

## 💳 料金について

### GPT-4o（Vision対応）
- **入力**: $2.50 / 1M tokens
- **画像**: 約 $0.01 / 1枚
- **月1000枚処理**: 約 $10

### 無料クレジット
- 新規アカウント: $5 無料クレジット（3ヶ月有効）
- テスト十分できる

---

## ⚙️ 設定方法

### 方法1: 環境変数（永続）

Mac miniのターミナルで：

```bash
echo 'export OPENAI_API_KEY="sk-proj-..."' >> ~/.zshrc
source ~/.zshrc
```

### 方法2: 一時的に設定

```bash
export OPENAI_API_KEY="sk-proj-..."
```

---

## 🚀 サーバー起動

```bash
cd ~/Documents/OpenClaw-Workspace

# 環境変数確認
echo $OPENAI_API_KEY

# サーバー起動
source venv/bin/activate
LINE_CHANNEL_ACCESS_TOKEN="McPVn4sc9LKdm2jc5e5g2EG1DUX6hqIHlrvTpKsKAtmp3xmlXoH0W1T8yQhdtvwUiy5cE2UmX+mm+1CWZtTq3nztSUqU03RoH5MF1XjvHMm/RcdjqKOha+i+gBmcV29rXWpT9QpCnpRSWBSBkIHthwdB04t89/1O/w1cDnyilFU=" \
LINE_CHANNEL_SECRET="59c8cb272d41d5a849adb7b08764f83e" \
PORT=5001 python3 tools/line_webhook_server.py
```

起動時に「OpenAI API: ✓」と表示されればOK

---

## 🧪 テスト

1. LINEで領収書画像を送信
2. 数秒待つ
3. 「✅ 処理完了しました！」と返信が来る
4. スプレッドシート確認

---

## 🔧 トラブルシューティング

### API Keyエラー
```
OpenAI API error: 401 Unauthorized
```
→ API Keyが正しく設定されているか確認

### クレジット不足
```
OpenAI API error: insufficient_quota
```
→ https://platform.openai.com/account/billing でクレジット追加

### モデルエラー
```
model: gpt-4o not found
```
→ GPT-4oへのアクセスがまだない場合、gpt-4-vision-previewに変更

---

## 📊 使用量確認

https://platform.openai.com/usage
- リアルタイムで使用量確認
- コスト監視

---

## 次のステップ

1. ✅ API Key取得
2. ✅ 環境変数設定
3. ✅ サーバー起動
4. ✅ テスト送信
5. ⬜ 本番運用
