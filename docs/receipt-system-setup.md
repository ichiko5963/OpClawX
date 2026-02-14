# 領収書自動処理システム - セットアップガイド

## 📋 概要

領収書をLINE/Telegram/メールで送ると自動的に：
1. OCR/AIで内容を解析
2. Googleドライブ「法人領収書まとめ」に保存
3. スプレッドシートに追記

## 🔧 セットアップ手順

### 1. Google OAuth認証設定

```bash
# gog CLIの認証（初回のみ）
gog auth credentials ~/path/to/client_secret.json
gog auth add ichioka.naoto@aircle.jp --services gmail,calendar,drive,sheets

# 確認
gog auth list
```

### 2. LINE公式アカウント設定

1. [LINE Developers](https://developers.line.biz/)でMessaging API作成
2. Webhook URL設定: `https://your-server.com/webhook/line`
3. トークン取得してOpenClaw設定に追加

### 3. 自動処理cron設定

```bash
# Telegramからの領収書を自動処理
cron add receipt-telegram-handler \
  --schedule '*/5 * * * *' \
  --session isolated \
  --payload agentTurn \
  --message "Telegramの未処理領収書をチェックして、あれば tools/receipt_processor.py で処理"
```

## 📊 スプレッドシート構造

| 列 | 項目 | 例 |
|----|------|-----|
| A | 日付 | 2026-02-14 |
| B | 宛名 | 株式会社AirCle |
| C | 発行者の住所 | 東京都渋谷区... |
| D | メモ | 交通費 |
| E | 金額 | 10000 |
| F | 通貨 | 円 |
| G | URL | https://drive.google.com/... |

## 🚀 使い方

### Telegramで送信
```
領収書の画像を送る → 自動処理される
```

### 手動実行
```bash
python3 tools/receipt_processor.py /path/to/receipt.jpg
```

## 📝 TODO

- [ ] Google OAuth認証完了
- [ ] Vision API連携（OCR）
- [ ] Drive API連携（アップロード）
- [ ] LINE公式アカウント作成
- [ ] Webhook設定
- [ ] メール監視cron作成
- [ ] Telegram監視cron作成

## 🔗 リンク

- スプレッドシート: https://docs.google.com/spreadsheets/d/1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc/edit
- Googleドライブフォルダ: 「法人領収書まとめ」（要作成）
