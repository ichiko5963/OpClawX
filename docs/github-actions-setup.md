# GitHub Actions セットアップ

## 必要なシークレット設定

GitHubリポジトリ: https://github.com/ichiko5963/ichioka-vault

### Settings → Secrets and variables → Actions → New repository secret

**GOOGLE_OAUTH_TOKENS** を作成：

```json
{
  "client_id": "90863020394-asb3rg4v1edka43crnde508j6d4agenc.apps.googleusercontent.com",
  "client_secret": "GOCSPX-...",
  "refresh_token": "1//0..."
}
```

⚠️ `/tmp/google_oauth_tokens.json` の内容をそのまま貼り付ける

---

## 実行確認

### 手動実行（テスト）

1. https://github.com/ichiko5963/ichioka-vault/actions にアクセス
2. 「Google Data Sync (Hourly)」を選択
3. 「Run workflow」をクリック
4. 「Run workflow」ボタン押下

### 自動実行

- **頻度**: 毎時0分
- **次回**: 4:00, 5:00, 6:00...

---

## 確認ポイント

1. ✅ データ取得成功
   - `data/gmail/YYYY-MM-DD.json`
   - `data/calendar/YYYY-MM-DD.json`
   - `data/tasks/YYYY-MM-DD.json`
   - `data/drive/transcriptions/*.json`

2. ✅ GitHubに自動コミット
   - Commit履歴に「🔄 Google Data Sync: ...」

3. ✅ Obsidianに反映
   - `bin/git-auto-sync.sh` が1時間ごとに実行
   - ローカルにpull

---

## トラブルシューティング

### シークレットが設定されていない

```
Error: GOOGLE_OAUTH_TOKENS secret not found
```

→ GitHubのSettings → Secrets で `GOOGLE_OAUTH_TOKENS` を追加

### OAuth token期限切れ

```
Error: invalid_grant
```

→ `/tmp/google_oauth_tokens.json` を再生成してGitHubシークレット更新

---

## 現在の状態（2026-02-15 03:10 実行済み）

✅ 初回同期完了:
- Gmail: 50件
- Calendar: 122件
- Tasks: 17件
- Transcriptions: 2件

✅ 以降は1日分ずつ取得
