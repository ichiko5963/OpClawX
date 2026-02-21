---
name: invoice-generator
description: 請求書を自動作成し、Vercelにデプロイして一覧で管理するスキル。
---

# Invoice Generator

HTML形式で請求書を自動作成し、Vercelにデプロイして一覧で管理する。

## 請求書URL

**一覧:** https://invoices-henna.vercel.app

**個別:** https://invoices-henna.vercel.app/01.html etc.

## 請求書フォーマット（完全版）

### 入力フィールド

| フィールド | 必須 | 説明 | 例 |
|-----------|------|------|-----|
| `company_name` | ✅ | 請求先企業名 | ポート株式会社 |
| `title` | ✅ | 件名 | Xプレミアム2月分 |
| `items` | ✅ | 明細リスト | [{name, quantity, unit_price, amount}, ...] |
| `date` | ✅ | 請求日 | 2026年2月21日 |
| `invoice_no` | ✅ | 請求番号 | 01, 02, 03... |

### 税率
- 税率: 10%（内税）
- 消費税计算: 小計 × 0.1

### itemsの形式（複数行OK）
```python
items = [
    {'name': 'Xプレミアム(999円)', 'quantity': '1', 'unit_price': '999', 'amount': '999'},
    {'name': 'Xプレミアム(499円)', 'quantity': '1', 'unit_price': '499', 'amount': '499'},
]
```

## 作業フロー

### 1. 請求書番号採番
- 形式: 01, 02, 03...（ゼロ埋め2桁）
- 現在の最大番号+1
- ファイル: `invoices/index.html` の列表から取得

### 2. HTML生成
- 一覧: `invoices/index.html`
- 個別: `invoices/{invoice_no}.html`

### 3. Vercelデプロイ
```bash
cd invoices && npx vercel --prod --yes
```

### 4. URL提供
- 一覧URL: https://invoices-henna.vercel.app
- 個別URL: https://invoices-henna.vercel.app/{invoice_no}.html

## テンプレートファイル

- 一一覧: `invoices/index.html`
- 請求書: `invoices/{no}.html`（個別ページ）

## スキルを使うタイミング

- 「請求書作って」「invoice作成して」
- 「請求書をPDFで」「PDF請求書作成して」
- 「Gensparkに請求書」「ポートに請求書出して」
- 「X代の請求書出して」

## 銀行口座情報（市岡さん用）

- 銀行: 西日本シティ銀行 周船寺支行
- 口座: 普通 3124131
- 名義: イチオカナオト

## 金額オプション

- 999円+499円のような複数アイテムOK
- 自動計算: 小計 = 全itemsのamount合計
- 消費税 = 小計 × 0.1
- 合計 = 小計 + 消費税

