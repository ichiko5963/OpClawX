# メール領収書自動監視システム

## 📧 仕組み

### 1. GitHub Actionsで1時間ごとにチェック
- 過去1時間のメールを検索
- 件名に「領収書」「請求書」「レシート」等
- 添付ファイル（画像・PDF）あり

### 2. 自動処理
1. 添付ファイルダウンロード
2. Google Driveに保存（`1pzI8BkAGrio16HTGpVOyvB25rV8IOO_g`）
3. 処理キューに保存（`data/receipt_queue/`）

### 3. OpenClawで処理
- 定期的にキューをチェック
- Claudeで画像分析
- 2026年経費領収書シートに追加

---

## 🚀 セットアップ

### GitHub Secrets設定（既存）
以下は既に設定済み：
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`

### ワークフロー有効化
`.github/workflows/email-receipt-monitor.yml` が自動で実行されます。

---

## 📋 処理フロー

```
Gmail受信
  ↓
GitHub Actions (1時間ごと)
  ↓
領収書キーワード検索
  ↓
添付ファイルダウンロード
  ↓
Google Drive保存
  ↓
data/receipt_queue/*.json 保存
  ↓
OpenClaw cron (定期実行)
  ↓
Claude画像分析
  ↓
2026年経費領収書シートに追加
```

---

## 🔍 検出キーワード

件名に以下が含まれるメール：
- 領収書
- レシート
- 請求書
- 明細
- 領収証
- receipt
- invoice

---

## 📝 キューファイル形式

`data/receipt_queue/YYYYMMDD_HHMMSS.json`:
```json
{
  "email_subject": "領収書の送付",
  "filename": "receipt.jpg",
  "drive_url": "https://drive.google.com/file/d/...",
  "received_at": "2026-02-15T00:30:00",
  "message_id": "..."
}
```

---

## 🔧 手動実行

### GitHub Actionsから
1. GitHubリポジトリを開く
2. Actions → Email Receipt Monitor
3. Run workflow

### ローカルテスト
```bash
cd ~/Documents/OpenClaw-Workspace
export GOOGLE_CLIENT_ID="..."
export GOOGLE_CLIENT_SECRET="..."
export GOOGLE_REFRESH_TOKEN="..."
export SHEET_ID="1FH_CZkEkn621MNvFioUHgT3_4UU_TL1POu-Bhpz7KCc"
export DRIVE_FOLDER_ID="1pzI8BkAGrio16HTGpVOyvB25rV8IOO_g"

python3 scripts/check_receipt_emails.py
```

---

## ⚠️ 注意点

- **重複処理**: 同じメールを2回処理しないように、処理済みは`processed/`に移動
- **エラー処理**: 失敗しても他のメールは処理継続
- **手動確認**: 自動追加後は必ずスプレッドシート確認

---

## 次のステップ

- [ ] OpenClawでキュー処理自動化（cron設定）
- [ ] Claude画像分析統合
- [ ] エラー通知（Telegram）
