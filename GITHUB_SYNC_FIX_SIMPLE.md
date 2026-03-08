# GitHub同期修正手順（超簡略版）

## やること3つ

### ① sync.pyを更新
1. GitHub → OpenClaw/OpenClaw → scripts/sync.py
2. 右上「✏️ Edit」→ 全部削除
3. sync_fixed.pyの内容を貼り付け
4. 「Commit changes」

### ② Secrets設定
Settings → Secrets → New repository secret
- Name: `GOG_TOKEN`
- Value: （後で教える認証情報）

### ③ 動作確認
Actionsタブ → Data Sync → 「Run workflow」

## 必要な情報
- gog認証トークン ← Macで取得必要
- 経費シートID ← スプレッドシートURLから

---
**不明点があればすぐ聞いて！**
