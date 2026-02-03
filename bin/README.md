# 🛠️ OpenClaw-Shared ツール集

このディレクトリには、日常業務を効率化するためのスクリプトが含まれています。

---

## 📋 タスク・プロジェクト管理

### `extract-tasks.sh`
Obsidian Vaultから未完了タスクを抽出します。

```bash
# 全プロジェクトのタスクを表示
./extract-tasks.sh

# 特定プロジェクトのタスクを表示
./extract-tasks.sh AirCle
```

### `project-status.sh`
プロジェクトの進捗状況をダッシュボード形式で表示します。

```bash
./project-status.sh
```

### `create-daily.sh`
Obsidianのデイリーノートを作成します。

```bash
# 今日のノートを作成
./create-daily.sh

# 指定日のノートを作成
./create-daily.sh 2026-02-10
```

### `weekly-summary.sh`
週次サマリーを自動生成します。

```bash
./weekly-summary.sh
```

---

## 📝 ノート・メモ管理

### `quick-note.sh`
素早くノートを作成します。

```bash
./quick-note.sh "タイトル" "内容" [フォルダ]
```

### `meeting-notes.sh`
会議メモのテンプレートを生成します。

```bash
./meeting-notes.sh "会議名" "参加者1, 参加者2" "プロジェクト名"
```

### `obsidian-search.sh`
Obsidian Vault内を検索します。

```bash
./obsidian-search.sh "検索ワード"
./obsidian-search.sh "検索ワード" "03_Projects"
```

---

## 🐦 X (Twitter) 投稿管理

### `x-drafts.sh`
X投稿の下書きを管理します。

```bash
# 下書き追加
./x-drafts.sh add "投稿内容" "カテゴリ"

# 一覧表示
./x-drafts.sh list

# 削除
./x-drafts.sh delete 1

# CSVエクスポート
./x-drafts.sh export
```

### `x-post-analyzer.js`
X投稿を分析し、改善提案を行います。

```bash
node x-post-analyzer.js "投稿内容"
```

---

## 🔄 同期・自動化

### `git-auto-sync.sh`
変更を自動でコミット・プッシュします（cronで定期実行用）。

```bash
./git-auto-sync.sh
```

### `smart-commit.sh`
変更内容を分析し、適切なコミットメッセージを生成します。

```bash
./smart-commit.sh
```

---

## 🔍 分析・レポート

### `health-check.sh`
ワークスペースの健全性をチェックします。

```bash
./health-check.sh
```

### `daily-report.sh`
日次レポートを生成します。

```bash
./daily-report.sh
```

### `link-checker.js`
ドキュメント内のリンク切れをチェックします。

```bash
node link-checker.js
```

---

## 💡 アイデア・リマインダー

### `idea-capture.js`
アイデアを素早くキャプチャして保存します。

```bash
node idea-capture.js "素晴らしいアイデア"
```

### `smart-reminder.js`
スマートリマインダーを設定します。

```bash
node smart-reminder.js
```

---

## 🔧 セットアップスクリプト

### `setup-slack.sh`
Slack連携の設定を行います。

### `setup-google.sh`
Google連携（Gmail, Calendar）の設定を行います。

### `setup-chatwork.sh`
Chatwork連携の設定を行います。

### `transcribe-meeting.sh`
会議音声を文字起こしします（要: Whisper API）。

---

## 💡 使い方のヒント

1. **パスを通す**: 
   ```bash
   export PATH="$PATH:$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/bin"
   ```

2. **エイリアスを設定**: 
   ```bash
   alias tasks="./extract-tasks.sh"
   ```

3. **cronで自動化**: 
   ```bash
   0 * * * * /path/to/git-auto-sync.sh
   ```

---

## 📁 ファイル構成

```
bin/
├── README.md              # このファイル
├── create-daily.sh        # デイリーノート作成
├── daily-report.sh        # 日次レポート生成
├── extract-tasks.sh       # タスク抽出
├── git-auto-sync.sh       # Git自動同期
├── health-check.sh        # ヘルスチェック
├── idea-capture.js        # アイデアキャプチャ
├── link-checker.js        # リンクチェッカー
├── meeting-notes.sh       # 会議メモテンプレート
├── obsidian-search.sh     # Obsidian検索
├── project-status.sh      # プロジェクト状況
├── quick-note.sh          # クイックノート
├── setup-chatwork.sh      # Chatwork設定
├── setup-google.sh        # Google設定
├── setup-slack.sh         # Slack設定
├── smart-commit.sh        # スマートコミット
├── smart-reminder.js      # スマートリマインダー
├── transcribe-meeting.sh  # 文字起こし
├── weekly-summary.sh      # 週次サマリー
├── x-drafts.sh            # X投稿下書き管理
└── x-post-analyzer.js     # X投稿分析
```

---

## 🔗 関連

Python版ツールは `tools/` ディレクトリにもあります：
- `tools/x_scheduler.py` - X投稿スケジューラー
- `tools/workspace_health.py` - ワークスペースヘルスチェッカー
- `tools/viral_analyzer.py` - バイラル度分析
- `tools/morning_brief.py` - モーニングブリーフィング

---

*最終更新: 2026-02-04*
