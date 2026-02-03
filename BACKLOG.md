# 後回しタスク (Backlog)

> このファイルは毎時チェックされます。未完了タスクがあれば、Piから確認が来ます。

## 📋 未完了タスク

### 優先度: 高

- [x] **dedupe.sqlite 実装** - 重複防止用DBを作成 ✅ 2026-02-03
- [x] **cursors.json 差分同期** - 差分取得を実現 ✅ 2026-02-03
- [x] **共通イベントスキーマ** - 正規化イベント形式 ✅ 2026-02-03
- [x] **ActionQueue システム** - pending/processed + メール分析 ✅ 2026-02-03
- [x] **承認フロー** - 承認→実行の仕組み ✅ 2026-02-03

### 優先度: 中

- [x] **Daily Digest 強化** - Executive Summary、P0/P1分類、要返信一覧 ✅ 2026-02-03
- [x] **Google Tasks 連携** - n8n連携、毎時同期、タスク管理 ✅ 2026-02-03
- [ ] **Google Drive 連携** - ワークフローに組み込み、ファイル変更検知
- [ ] **音声議事録 自動文字起こし** - Drive特定フォルダ投入→Whisper API→Vault保存

### 優先度: 低

- [x] **Logs構造化** - JSON Lines形式、レベル対応、ローテーション ✅ 2026-02-03
- [x] **routing_rules.yaml 拡充** - プロジェクト/人/企業/優先度ルール ✅ 2026-02-03
- [x] **sensitivity.yaml 実装** - 機密判定・PII検出・マスキング ✅ 2026-02-03

---

## ✅ 完了タスク

- [x] n8n セットアップ（Docker）
- [x] Gmail 接続
- [x] Slack 接続（Bot + User Token）
- [x] Google Calendar 接続
- [x] Google Drive 認証（n8nに登録済み）
- [x] 毎時同期ワークフロー（Gmail/Slack/Calendar）
- [x] 毎時Vault保存（cron: n8n-vault-sync）
- [x] Daily Memory Cleanup スクリプト
- [x] Daily Digest 生成
- [x] プロジェクト別MEMORY.md自動更新
- [x] Vault構造 00_System 初期化

---

## 📅 最終更新

- 更新日時: 2026-02-03 20:47 JST
- 更新者: Pi (自動)
