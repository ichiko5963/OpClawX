# 領収書OCRシステム - セットアップガイド

## 必要な準備

### 1. Google API Key取得

Gemini Vision APIを使うために必要。

1. https://aistudio.google.com/app/apikey にアクセス
2. 「Create API Key」をクリック
3. API Keyをコピー
4. 環境変数に設定：

```bash
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

または `.zshrc` / `.bashrc` に追加：

```bash
echo 'export GOOGLE_API_KEY="YOUR_API_KEY_HERE"' >> ~/.zshrc
source ~/.zshrc
```

### 2. OAuth認証

すでに完了済み（`/tmp/google_oauth_tokens.json`）

### 3. 必要なPythonパッケージ

```bash
cd ~/Documents/OpenClaw-Workspace
source venv/bin/activate
pip install requests
```

## 使い方

### 手動テスト

```bash
cd ~/Documents/OpenClaw-Workspace
source venv/bin/activate
python3 tools/receipt_ocr.py /path/to/receipt_image.jpg
```

### Telegram連携

Telegramに画像を送ると自動処理される（OpenClaw経由）

## 処理フロー

1. **Telegram画像受信**
2. **Gemini Vision API でOCR**
   - 日付、宛名、金額、通貨を抽出
3. **Google Drive保存**
   - フォルダ: 「法人領収書まとめ」
4. **スプレッドシート追記**
   - シート: 2026年収入
   - 列: 日付、宛名、住所、メモ、金額、通貨、URL

## トラブルシューティング

### GOOGLE_API_KEY not set

```bash
export GOOGLE_API_KEY="YOUR_KEY"
```

### Token file not found

OAuth再認証が必要：

```bash
cd /tmp
python3 get_google_token_extended.py
cp google_oauth_tokens_extended.json google_oauth_tokens.json
```

### Drive folder not found

スクリプトが自動で「法人領収書まとめ」フォルダを作成します。

## ファイル

- `tools/receipt_ocr.py` - メイン処理
- `tools/telegram_receipt_handler.py` - Telegram連携
- `tools/sheets_api.py` - Sheets API wrapper

## 次のステップ

- [ ] 銀行明細PDF処理
- [ ] メール監視（領収書自動検出）
- [ ] LINE公式アカウント連携
