# CFO ナレッジベース

ルール詳細: `00-rules/cfo.md`

## スキルマップ

| スキル | パス | ステータス |
|--------|------|-----------|
| 領収書管理 | — | 未作成 |
| 売上トラッキング | — | 未作成 |
| Gmail→スプシ連携 | — | 未作成 |
| 月次レポート作成 | — | 未作成 |

## knowledge/ の内容

- `monthly/YYYY-MM.md` — 月次経費・売上まとめ
- （今後追加: revenue-overview.md, expense-categories.md, tax-relevant.md）

## 自動化の前提

Google API認証が必要（現在切れている: 2/24〜）。
復旧後、以下のスクリプトが利用可能:
- `scripts/analyze_emails.py`
- `scripts/email_manager.py`
- `scripts/email_classifier.py`
- `scripts/expense_append.py`
