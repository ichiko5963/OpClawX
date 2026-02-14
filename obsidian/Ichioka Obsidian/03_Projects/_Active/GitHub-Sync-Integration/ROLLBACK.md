# GitHub情報一元管理システム - ロールバック計画

## 🔙 ロールバック戦略

もし新システムに問題が発生した場合、既存のn8nシステムに戻す手順。

---

## 前提条件

- [ ] n8nコンテナは削除しない（停止のみ）
- [ ] n8n DBバックアップを取る
- [ ] OpenClaw設定の変更前にバックアップ

---

## バックアップ手順

### 1. n8n DB バックアップ

```bash
# 実行日時: [実行前に記入]
cp /tmp/n8n_db.sqlite /tmp/n8n_db.sqlite.backup.$(date +%Y%m%d)
```

### 2. OpenClaw設定バックアップ

```bash
# cron設定
openclaw cron list > ~/openclaw_cron_backup_$(date +%Y%m%d).json

# config
openclaw config.get > ~/openclaw_config_backup_$(date +%Y%m%d).json
```

### 3. Obsidian設定バックアップ

```bash
# Git plugin設定
cp "obsidian/Ichioka Obsidian/.obsidian/plugins/obsidian-git" \
   ~/obsidian_git_backup_$(date +%Y%m%d) -r
```

---

## ロールバック手順

### Phase 1: GitHub Actions停止（即時）

1. GitHubリポジトリ → Settings → Actions
2. "Disable actions for this repository"
3. 実行中のワークフローをキャンセル

### Phase 2: OpenClaw cronジョブ無効化（5分）

```bash
# 新しく追加したcronジョブを無効化
openclaw cron update meeting-transcription-processor --enabled=false

# 既存cronジョブを無効化（元々無効だったもの）
openclaw cron update meeting-prep-reminder --enabled=false
openclaw cron update email-hourly-check --enabled=false
# ... (全て)
```

### Phase 3: n8n復活（10分）

```bash
# n8nコンテナ起動
docker start n8n

# n8n管理画面でGoogle OAuth再認証
# http://localhost:5678
# Credentials → Google Calendar/Gmail/Drive/Tasks → Reconnect → Save
```

### Phase 4: 元のcronジョブ復活（5分）

元々動いていたcronジョブ（n8n依存）を再有効化:

```bash
openclaw cron update expense-daily-append --enabled=true
openclaw cron update morning-task-report --enabled=true
openclaw cron update nightly-dev-session --enabled=true
openclaw cron update daily-efficiency-suggestions --enabled=true
```

### Phase 5: Obsidian設定戻す（5分）

1. Obsidian Git Pluginを無効化
2. サブモジュール削除:
   ```bash
   cd "obsidian/Ichioka Obsidian/00_System/"
   git submodule deinit External
   git rm External
   git commit -m "Remove GitHub sync submodule"
   ```

### Phase 6: 検証（10分）

- [ ] n8nワークフローが動作するか
- [ ] cronジョブが動作するか
- [ ] メール・カレンダー・タスクが取得できるか

---

## データ保全

### ロールバック中もデータは保持

- GitHubリポジトリは削除しない（Actionsだけ無効化）
- 既に収集されたデータは残る
- いつでも再開可能

---

## 緊急連絡先

- いち: Telegram @ichikodayo
- OpenClaw Discord: https://discord.com/invite/clawd
- GitHub Support: https://support.github.com

---

## ロールバック判断基準

以下の場合はロールバックを検討:

- [ ] GitHub Actionsが24時間以上失敗し続ける
- [ ] データ損失が発生
- [ ] Obsidianが重くなりすぎる
- [ ] OpenClawの処理が追いつかない
- [ ] いちの業務に支障が出る

---

## 部分ロールバック

全体ではなく、一部だけ戻すことも可能:

| 戻す対象 | 手順 |
|---------|------|
| Gmail同期のみ | `gmail-sync.yml`だけ無効化 + n8nのGmail同期を有効化 |
| 文字起こし処理のみ | `meeting-transcription-processor` cronだけ無効化 + 手動処理に戻す |
| Obsidian同期のみ | Git Pluginを無効化 + 手動でgit pull |

---

## 最終確認

ロールバック実行前に確認:

- [ ] いちの承認を得た
- [ ] バックアップを取得済み
- [ ] ロールバック手順を理解した
- [ ] 元の状態に戻せることを確認した

---

**重要**: ロールバックは最終手段。まずは問題の修正を試みる。
