# 領収書・銀行明細 自動処理システム（Claude直接読み取り版）

## 🎯 コンセプト

**API不要！私（Claude）が直接読み取ります**

- Gemini APIなし
- Google API Keyなし
- OpenClawのimageツール経由で私が画像を分析

## 📸 領収書処理の流れ

### 1. Telegramに画像を送る
領収書の写真をTelegramで私に送ってください。

### 2. 私が読み取る
画像を受け取ったら：
1. imageツールで画像を分析
2. 日付・宛名・金額・通貨を抽出
3. Google Driveに保存（オプション）
4. スプレッドシートに自動追記

### 3. 完了通知
「✅ 領収書追加しといたよ！」と返信します。

## 📄 銀行明細PDF処理の流れ

### 1. TelegramにPDFを送る
銀行明細PDFをTelegramで送ってください。

### 2. 私が読み取る
1. PDFを開いて内容を確認
2. 入金取引のみを抽出（振込は除外）
3. スプレッドシートに自動追記

### 3. 完了通知
「✅ 25件の入金を追加しといたよ！総額4,439,221円」

## 🔧 技術的な仕組み

### 領収書
```
Telegram画像
  ↓
OpenClaw image tool
  ↓
Claude分析（私）
  ↓
JSON抽出 {"date":"2026/01/15", "amount":"1000", ...}
  ↓
tools/receipt_claude.py
  ↓
Google Sheets追記
```

### 銀行明細PDF
```
Telegram PDF
  ↓
Claude読み取り（私）
  ↓
入金判定（振込除外）
  ↓
tools/bank_claude.py
  ↓
Google Sheets追記
```

## 💡 メリット

1. **API Key不要** - すぐ使える
2. **セットアップ簡単** - OAuth認証のみ
3. **精度高い** - Claude（私）が直接読むので柔軟
4. **会話的** - 不明点は質問できる

## 🚀 使い方（手動テスト）

### 領収書
```bash
cd ~/Documents/OpenClaw-Workspace
source venv/bin/activate

# JSONを渡す方式
python3 tools/receipt_claude.py receipt.jpg '{"date":"2026/01/15","recipient":"コンビニ","amount":"1000","currency":"円"}'
```

### 銀行明細
Telegram経由で私に「この明細処理して」と送ってください。

## 📝 実装ファイル

- `tools/receipt_claude.py` - 領収書処理（Claude版）
- `tools/bank_claude.py` - 銀行明細処理（Claude版、未実装）
- `tools/sheets_api.py` - Google Sheets API wrapper

## 次のステップ

- [x] 領収書Claude読み取り実装
- [ ] 銀行明細Claude読み取り実装
- [ ] Telegram自動処理フロー
- [ ] Drive保存実装
