# GitHub情報一元管理システム - 全タスクリスト

## 📋 タスク進捗

**開始日**: 2026-02-14
**担当**: Pi (OpenClaw)
**レビュー**: いち

---

## Phase 1: GitHub基盤構築（30分）

### 1.1 GitHubリポジトリ作成
- [ ] GitHub.comでログイン
- [ ] New Repository作成
  - Name: `ichioka-vault`
  - Private: ✅
  - Initialize with README: ✅
- [ ] リポジトリURL確認: `https://github.com/[username]/ichioka-vault`
- [ ] ローカルにclone: `git clone git@github.com:[username]/ichioka-vault.git`

### 1.2 ディレクトリ構造作成
- [ ] `.github/workflows/` ディレクトリ作成
- [ ] `scripts/` ディレクトリ作成
- [ ] `data/` ディレクトリ作成（gmail, calendar, tasks, drive, notion, slack）
- [ ] `README.md` 更新（プロジェクト説明）
- [ ] commit & push

### 1.3 GitHub Secrets設定
- [ ] Google OAuth Client ID/Secret取得
- [ ] Google Refresh Token取得（手動認証1回）
- [ ] Notion Integration Token取得
- [ ] Slack Bot/User Token取得
- [ ] GitHub Settings → Secrets → 全て登録
  - [ ] `GOOGLE_CLIENT_ID`
  - [ ] `GOOGLE_CLIENT_SECRET`
  - [ ] `GOOGLE_REFRESH_TOKEN`
  - [ ] `NOTION_TOKEN`
  - [ ] `SLACK_BOT_TOKEN`
  - [ ] `SLACK_USER_TOKEN`
  - [ ] `ANTHROPIC_API_KEY` (議事録生成用)

---

## Phase 2: データ同期スクリプト作成（1.5時間）

### 2.1 Gmail同期
- [ ] `scripts/sync_gmail.py` 作成
- [ ] OAuth認証ロジック実装
- [ ] 差分取得（History API使用）
- [ ] JSON保存（`data/gmail/YYYY-MM-DD.json`）
- [ ] metadata.json管理（last_history_id）
- [ ] テスト実行（ローカル）

### 2.2 Calendar同期
- [ ] `scripts/sync_calendar.py` 作成
- [ ] 今後30日のイベント取得
- [ ] JSON保存（`data/calendar/YYYY-MM.json`）
- [ ] metadata.json管理
- [ ] テスト実行

### 2.3 Tasks同期
- [ ] `scripts/sync_tasks.py` 作成
- [ ] 全タスクリスト取得
- [ ] 各リストのタスク取得
- [ ] JSON保存（`data/tasks/YYYY-MM-DD.json`）
- [ ] metadata.json管理
- [ ] テスト実行

### 2.4 Drive同期（文字起こし検出）
- [ ] `scripts/sync_drive.py` 作成
- [ ] `mimeType='text/plain' and 'Recordings' in parents` クエリ
- [ ] 文字起こしファイル検出
- [ ] 生テキストをそのまま保存（`data/drive/transcriptions/YYYY-MM-DD_HH-MM.txt`）
- [ ] ファイル変更履歴も取得（Changes API）
- [ ] metadata.json管理
- [ ] テスト実行

### 2.5 Notion同期
- [ ] `scripts/sync_notion.py` 作成
- [ ] Database query
- [ ] Pages取得
- [ ] JSON保存（`data/notion/YYYY-MM-DD.json`）
- [ ] metadata.json管理
- [ ] テスト実行

### 2.6 Slack同期
- [ ] `scripts/sync_slack.py` 作成
- [ ] conversations.history取得
- [ ] JSON保存（`data/slack/YYYY-MM-DD.json`）
- [ ] metadata.json管理
- [ ] テスト実行

### 2.7 統合スクリプト
- [ ] `scripts/sync_all.py` 作成（全サービスを順次実行）
- [ ] エラーハンドリング追加
- [ ] ログ出力
- [ ] テスト実行

---

## Phase 3: GitHub Actions設定（30分）

### 3.1 統合ワークフロー作成
- [ ] `.github/workflows/sync-all.yml` 作成
- [ ] schedule設定（`0 * * * *` 毎時）
- [ ] workflow_dispatch設定（手動実行可能）
- [ ] Python 3.11セットアップ
- [ ] 依存関係インストール
- [ ] `scripts/sync_all.py` 実行
- [ ] commit & push設定
- [ ] push

### 3.2 ワークフロー初回実行
- [ ] GitHub Actions画面で手動実行
- [ ] 実行ログ確認
- [ ] データが`data/`に保存されているか確認
- [ ] commitが作成されているか確認

### 3.3 エラー対応
- [ ] エラーログ確認
- [ ] 認証エラーの修正
- [ ] スクリプトのデバッグ
- [ ] 再実行

---

## Phase 4: Obsidian統合（15分）

### 4.1 Obsidian Git Plugin設定
- [ ] Obsidian → Settings → Community plugins → Browse
- [ ] 「Obsidian Git」インストール
- [ ] 設定:
  - [ ] Vault backup interval: 60 minutes
  - [ ] Auto pull interval: 60 minutes
  - [ ] Commit message: `vault backup: {{date}}`
- [ ] テスト（手動でCommit/Pull）

### 4.2 GitHubリポジトリをサブモジュールとして追加
- [ ] ターミナルで実行:
  ```bash
  cd "obsidian/Ichioka Obsidian/00_System/"
  git submodule add git@github.com:[username]/ichioka-vault.git External
  git commit -m "Add ichioka-vault as submodule"
  git push
  ```
- [ ] Obsidianで`00_System/External/`が見えることを確認
- [ ] データが同期されていることを確認

### 4.3 memorySearch設定更新
- [ ] `MEMORY.md`に追記:
  ```markdown
  ## GitHub同期データ
  - 場所: `obsidian/Ichioka Obsidian/00_System/External/data/`
  - 更新頻度: 1時間ごと
  - memorySearchで検索可能
  ```

---

## Phase 5: OpenClaw cronジョブ追加（30分）

### 5.1 文字起こし処理cronジョブ
- [ ] cronジョブ定義作成:
  - name: `meeting-transcription-processor`
  - schedule: `*/30 * * * *` (30分ごと)
  - sessionTarget: `isolated`
  - payload: 議事録生成タスク
- [ ] cronジョブ追加コマンド実行
- [ ] 初回手動実行でテスト
- [ ] ログ確認

### 5.2 議事録生成スクリプト
- [ ] `scripts/process_transcriptions.py` 作成
- [ ] 未処理の文字起こしファイル検出
- [ ] Claude Sonnetで議事録生成
  - [ ] 参加者特定
  - [ ] 要約
  - [ ] 決定事項
  - [ ] TODO抽出（いちのTODOのみ）
  - [ ] 次回予定
- [ ] プロジェクト判定ロジック
  - [ ] Obsidian 10_People/, 11_Companies/ 参照
  - [ ] ClimbBeyond, AirCle等の判定
- [ ] 議事録保存
  - [ ] `03_Projects/_Active/[project]/MTG/YYYY-MM-DD_[title].md`
  - [ ] `10_People/[name]/MTG/YYYY-MM-DD_[title].md`
- [ ] テスト実行

### 5.3 Google Tasks連携
- [ ] TODO抽出ロジック実装
- [ ] Google Tasks API呼び出し
- [ ] タスクリスト振り分け
  - [ ] AirCle → Aircleリスト
  - [ ] ClimbBeyond → ClimbBeyondリスト
  - [ ] 外部案件 → 外部案件リスト
  - [ ] その他 → マイタスク
- [ ] 期限設定ロジック
  - [ ] 「次回MTGまで」→ カレンダー検索
  - [ ] 具体的日時 → パース
  - [ ] デフォルト: 20:00
- [ ] テスト実行

### 5.4 既存cronジョブ復活
- [ ] 無効化していたcronジョブを再有効化:
  - [ ] meeting-prep-reminder
  - [ ] email-hourly-check
  - [ ] email-analysis
  - [ ] task-reminder-check
  - [ ] overdue-tasks-nag
  - [ ] morning-briefing-telegram
  - [ ] daily-memory-cleanup
  - [ ] backlog-check
- [ ] 各ジョブのテスト実行
- [ ] エラーがないか確認

---

## Phase 6: テスト＆検証（30分）

### 6.1 エンドツーエンドテスト
- [ ] Google MeetでテストMTG実施（録画 + 文字起こし）
- [ ] 1時間待つ（GitHub Actions実行）
- [ ] Obsidian Gitが同期したか確認
- [ ] 文字起こしが`External/data/drive/transcriptions/`に存在するか確認
- [ ] 30分待つ（OpenClaw cronジョブ実行）
- [ ] 議事録が生成されたか確認
- [ ] TODOがGoogle Tasksに追加されたか確認

### 6.2 既存機能テスト
- [ ] メールチェックcronジョブが動作するか
- [ ] カレンダー確認が動作するか
- [ ] タスクリマインダーが動作するか
- [ ] 期限超えタスク通知が動作するか

### 6.3 パフォーマンス確認
- [ ] GitHub Actionsの実行時間（1時間以内に完了するか）
- [ ] OpenClaw cronジョブの実行時間
- [ ] Obsidian同期の負荷

---

## Phase 7: ドキュメント整備（15分）

### 7.1 README更新
- [ ] `ichioka-vault/README.md` にシステム説明追加
- [ ] データ構造の説明
- [ ] 各スクリプトの説明
- [ ] トラブルシューティング

### 7.2 運用マニュアル作成
- [ ] 日常運用手順
- [ ] エラー対応手順
- [ ] メンテナンス手順
- [ ] Obsidianに保存

### 7.3 MEMORY.md更新
- [ ] GitHub同期システムの記録
- [ ] 重要な設定の記録
- [ ] cronジョブ一覧の更新

---

## 完了条件

- [x] 全Phase完了
- [x] エンドツーエンドテストが成功
- [x] 24時間の安定稼働確認
- [x] いちからのOK

---

## 次のアクション

**最初のタスク**: Phase 1.1 - GitHubリポジトリ作成

いち、準備できたら「開始」って言って。順番に進めていく。
