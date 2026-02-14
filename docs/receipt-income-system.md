# 領収書・収入自動処理システム - 実装ガイド

## 📋 システム概要

領収書と収入を自動的に処理し、Googleスプレッドシートに記録するシステム。

### 入力
1. **銀行明細PDF** - Telegramで送信
2. **領収書画像** - Telegram/メール/LINE
3. **Google Meet文字起こし** - 定期収入検出

### 出力
1. **収入スプレッドシート**: `1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990`
2. **領収書スプレッドシート**: `1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc`

## 📊 スプレッドシート構造（A-G列）

| 列 | 項目 | 例 |
|----|------|-----|
| A | 日付 | 2026-02-14 |
| B | 宛名/収入元 | Stripe、株式会社〇〇 |
| C | 発行者住所 | 東京都... |
| D | メモ | 交通費、案件受注 |
| E | 金額 | 10000 |
| F | 通貨 | 円 |
| G | URL | Drive URL |

## 🔍 入金/支出判定ロジック

### 収入（スプレッドシートに追記）
- `ｶﾞｲｺｸﾋｼﾑｹｿｳｷﾝ` - 外国非課税送金
- `ｽﾄﾗｲﾌﾟｼﾞﾔﾊﾟﾝ` / `ﾋﾟ-ﾃｨﾂｸｽｼﾞﾔﾊﾟﾝ` - Stripe
- `ﾉ-ﾄ` - Note
- `ﾎﾟ-ﾄ` - Port
- `ﾒﾙﾍﾟｲ` - メルカリ
- `ｷﾕｳｼﾕｳﾀﾞｲｶﾞｸ` - 九州大学
- `ﾏｼﾕﾏﾛｴﾝﾀﾒ` - マシュマロエンタメ
- `ｷﾔﾘｱﾃﾞｻﾞｲﾝｾﾝﾀ-` - キャリアデザインセンター
- `ﾐﾝｼﾕｳ` - みん就
- `ｵﾘｿｸ` - 利息
- `ﾌｸｵｶｼﾎｹﾝﾈﾝｷﾝｶ` - 還付金

### 支出（除外）
- `ﾌﾘｺﾐｼｷﾝ` - 振込支払
- `ﾌﾘｺﾐﾃｽｳﾘﾖｳ` - 振込手数料
- `RS ﾍﾟｲﾍﾟｲ` - PayPay
- `ATMｼﾊﾗｲ` - ATM引き出し
- `ﾐﾂｲｽﾐﾄﾓｶ-ﾄﾞ` - クレカ支払い
- `ﾗｸﾃﾝｶ-ﾄﾞｻ-ﾋﾞｽ` - 楽天カード

## 🚀 使い方

### 1. 銀行明細PDF処理
```bash
# PDFをTelegramで送信
# → 自動処理 → 収入スプレッドシートに追記
```

### 2. 領収書処理
```bash
# 画像をTelegramで送信
# → OCR → Drive保存 → 領収書スプレッドシートに追記
```

### 3. 手動テスト
```bash
cd ~/Documents/OpenClaw-Workspace
python3 tools/receipt_income_complete.py test
```

## 🔧 実装状況

### ✅ 完了
- 入金/支出判定ロジック
- スプレッドシート構造定義
- 基本スクリプト作成

### 🚧 TODO
- [ ] PDF処理（pdftotext or Gemini Vision）
- [ ] OCR実装（Gemini Vision API）
- [ ] Googleドライブ連携
- [ ] Google OAuth認証修正（gog sheets が応答しない問題）
- [ ] LINE公式アカウント作成
- [ ] Webhook実装
- [ ] メール監視cron
- [ ] Telegram監視cron
- [ ] 定期収入検出（Meet文字起こし）

## 📝 次のステップ

1. **Google OAuth認証修正** - gog sheetsが動作するように
2. **PDF処理実装** - 銀行明細からテキスト抽出
3. **OCR実装** - 領収書画像から情報抽出
4. **Drive連携** - ファイルアップロード
5. **自動化** - cron設定

## 🔗 関連ファイル

- メインスクリプト: `tools/receipt_income_complete.py`
- 銀行明細パーサー: `tools/bank_income_parser.py`
- セットアップガイド: `docs/receipt-system-setup.md`
