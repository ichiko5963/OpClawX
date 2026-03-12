# BACKLOG.md - Task Backlog

## 未完了タスク

### 高優先度

- [ ] **Google API認証再設定**
  - 説明: Gmail/Calendar/DriveのOAuth認証が2/24から切れている
  - 対応: `gog auth add your-email@gmail.com --services gmail,calendar,drive,contacts,docs,sheets`
  - 状態: 18日間継続中

- [ ] **Cronジョブ用スクリプト作成**
  - 説明: 以下のスクリプトがないためcronジョブが機能していない
    - `scripts/analyze_emails.py`
    - `scripts/email_manager.py`
    - `scripts/email_classifier.py`
    - `scripts/task_reminder.py`
    - `scripts/overdue_tasks.py`
    - `scripts/daily_digest.py`
    - `scripts/n8n_sync_to_vault.py`

### 中優先度

- [ ] **Viral Posts GeneratorのDiscord配信設定**
  - 説明: `viral-posts-daily-generator`の`delivery.to`が"x-analyticsチャンネルID"のまま
  - 対応: 実際のDiscordチャンネルIDに変更

- [ ] **Git自動同期スクリプト作成**
  - 説明: `bin/git-auto-sync.sh`が存在しない（直接Gitコマンドで代替中）

### 完了タスク

- [x] Discord配信設定修正 (git-auto-sync, email-auto-classifier)
- [x] meeting_prep_reminder.pyの作成

##メモ

基本的に、Google API認証が解決されれば大半の自動化機能が復活します。
