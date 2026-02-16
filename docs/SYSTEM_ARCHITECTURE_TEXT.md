# OpenClaw システムアーキテクチャ - 詳細説明

## 1. 全体構成

### 外部サービス層
OpenClawは以下の外部サービスと連携：
- **Gmail API** - メール取得・分析・ラベル付与
- **Google Calendar** - 予定管理・MTG準備リマインダー
- **Google Tasks** - タスク管理・リマインダー・期限通知
- **Google Drive** - 文字起こしファイル保存・文書管理
- **Telegram** - 主要通知チャネル（メール報告、タスクリマインダー等）
- **Discord** - セカンダリ通知（X投稿配信、完了報告等）

### データ収集層
**n8n Workflow（毎時10分実行）**
- Gmail、Google Calendar、Google Driveから新着データを毎時取得
- `/tmp/n8n_db.sqlite` に暗号化保存
- 重複排除機能（`cursors.json`で差分管理）

### データストレージ層
1. **Obsidian Vault** (`obsidian/Ichioka Obsidian/`)
   - 知識ベース・長期記憶
   - プロジェクト情報（`03_Projects/`）
   - 人物情報（`10_People/`）
   - 企業情報（`11_Companies/`）
   - システム状態（`00_System/01_State/`）

2. **State Files**
   - `events.jsonl` - n8nから収集した全イベント
   - `seen_emails.json` - 既読メールID管理
   - `cursors.json` - 各サービスの同期カーソル

### OpenClaw システム層
1. **OpenClaw Gateway**
   - メインセッション（直接会話）
   - Isolated セッション（バックグラウンドタスク実行）
   - Cron管理・スケジュール実行

2. **Cron Jobs**
   - 17個の定期実行ジョブ
   - systemEvent型（メインセッション）
   - agentTurn型（isolatedセッション）

3. **Python Scripts** (`scripts/`)
   - メール管理（`email_manager.py`, `email_classifier.py`）
   - タスク管理（`task_reminder.py`, `overdue_tasks.py`）
   - MTG準備（`meeting_prep_reminder.py`）
   - データ同期（`n8n_sync_to_vault.py`）
   - 経費管理（`expense_append.py`）
   - Git同期（`git-auto-sync.sh`）
   - メモリ整理（`memory_organizer.py`）

---

## 2. データフロー詳細

### メール処理フロー（毎時）

#### 10分: n8n同期
1. n8nがGmail APIから新着メール取得
2. `/tmp/n8n_db.sqlite` に保存
3. `cursors.json` で差分管理

#### 15分: 自動分類
1. OpenClaw Gatewayが `email_classifier.py` を実行
2. スクリプトがGmail APIから未分類メール取得（最大30件）
3. Obsidian Vault（`10_People/`, `11_Companies/`）から文脈検索
4. 送信者・件名から関係性を分析
5. Gmail APIでラベル付与（プロジェクト名、企業名、優先度）
6. Telegramに分類結果報告

#### 30分: 新着チェック・優先度判定
1. OpenClaw Gatewayが `email_manager.py` を実行（30秒タイムアウト付き）
2. スクリプトがGmail APIから新着確認
3. `seen_emails.json` で既読判定
4. Obsidian Vaultから文脈検索（送信者の関係性、過去のやり取り）
5. 優先度自動判定：
   - **P0**: 緊急（即対応必要）
   - **P1**: 重要（24時間以内）
   - **P2**: 通常（48時間以内）
   - **P3**: 低優先度
   - **ノイズ**: スキップ
6. 返信が必要なメールは返信案を生成
7. TelegramにP1/P2メールを報告

---

## 3. Cronスケジュール詳細

### 毎時実行（全17ジョブ中7ジョブ）

| 時刻 | ジョブ名 | 処理内容 |
|-----|---------|---------|
| 毎時10分 | n8n-vault-sync | n8nイベントをVaultに保存 |
| 毎時15分 | email-analysis | メール分析（analyze_emails.py） |
| 毎時15分 | email-auto-classifier | メール自動分類（最大30件） |
| 毎時30分 | email-hourly-check | 新着メールチェック・優先度判定 |
| 毎時30分 | backlog-check | BACKLOG.md未完了タスク確認 |
| 毎30分 | meeting-prep-reminder | 2時間以内のMTG準備リスト送信 |
| 毎時（14分） | git-auto-sync | Git自動同期（push/pull） |

### 1日4回実行

| 時刻 | ジョブ名 | 処理内容 |
|-----|---------|---------|
| 9:00, 12:00, 18:00, 21:00 | task-reminder-check | タスク期限リマインダー（3日前/1日前/12時間前） |

### 毎日1回実行

| 時刻 | ジョブ名 | 処理内容 | セッション |
|-----|---------|---------|----------|
| 01:00 | nightly-dev-session | 深夜開発セッション（5時間稼働） | Isolated |
| 04:10 | daily-memory-organizer | メモリ自動整理（曜日別テーマ） | Isolated |
| 06:00 | morning-task-report | X投稿作成（3アカウント×20投稿） | Isolated |
| 07:00 | morning-briefing-telegram | 朝のブリーフィング（Digest + 予定） | Main |
| 12:00 | daily-efficiency-suggestions | 効率化提案（音声アシスタント） | Isolated |
| 15:00 | overdue-tasks-nag | 期限超えタスク通知（煽りモード） | Main |
| 23:00 | daily-memory-cleanup | Daily Digest生成 | Main |
| 23:00 | expense-daily-append | 領収書スキャン→スプレッドシート追記 | Isolated |

### 曜日別メモリ整理テーマ（毎日4:10）
- **月曜**: プロジェクト情報
- **火曜**: 人物情報
- **水曜**: 企業情報
- **木曜**: タスク・TODO
- **金曜**: 知識・メモ
- **土曜**: 全体見直し
- **日曜**: アーカイブ整理

---

## 4. ファイル構成詳細

```
OpenClaw-Workspace/
├── scripts/                          # 自動化スクリプト
│   ├── email_manager.py             # メール分析・優先度判定（30秒タイムアウト）
│   ├── email_classifier.py          # メール自動分類・ラベル付与
│   ├── task_reminder.py             # タスク期限リマインダー
│   ├── meeting_prep_reminder.py     # MTG準備リマインダー
│   ├── overdue_tasks.py             # 期限超えタスク通知
│   ├── n8n_sync_to_vault.py         # n8nイベントをVaultに保存
│   ├── expense_append.py            # 領収書スキャン・経費記録
│   ├── daily_digest.py              # Executive Summary生成
│   ├── memory_organizer.py          # メモリ自動整理
│   └── analyze_emails.py            # メール分析（旧版）
│
├── bin/                              # シェルスクリプト
│   └── git-auto-sync.sh             # Git自動同期
│
├── obsidian/Ichioka Obsidian/        # Obsidian Vault（知識ベース）
│   ├── 00_System/                    # システムファイル
│   │   ├── 01_State/                 # 状態管理
│   │   │   ├── events.jsonl          # 全イベント履歴
│   │   │   ├── seen_emails.json      # 既読メール管理
│   │   │   └── cursors.json          # 同期カーソル
│   │   ├── 02_Templates/             # テンプレート
│   │   └── 03_Registry/              # レジストリ
│   │
│   ├── 03_Projects/                  # プロジェクト情報
│   │   ├── _Active/                  # アクティブプロジェクト
│   │   │   ├── AirCle/
│   │   │   ├── ClimbBeyond/
│   │   │   ├── SlideBox/
│   │   │   ├── ClientWork/
│   │   │   └── Genspark/
│   │   └── _Old/                     # 完了・休止プロジェクト
│   │
│   ├── 10_People/                    # 人物情報
│   │   └── [人物名]/
│   │       └── PROFILE.md            # 関係性、やり取り履歴
│   │
│   └── 11_Companies/                 # 企業情報
│       └── [企業名]/
│           └── PROFILE.md            # 関係性、契約情報
│
├── memory/                           # 日次メモリ
│   └── YYYY-MM-DD.md                 # 日次ログ
│
├── data/                             # 一時データ
│   └── drive/transcriptions/         # Google Meet文字起こし
│
├── public/                           # 公開ファイル（Vercel）
│   ├── system-architecture.html      # システム図解
│   └── daily-posts/                  # X投稿HTML
│
├── MEMORY.md                         # 長期記憶
├── AGENTS.md                         # エージェント設定
├── SOUL.md                           # パーソナリティ
├── USER.md                           # ユーザー情報
├── IDENTITY.md                       # AI識別情報
├── TOOLS.md                          # ツール設定
├── HEARTBEAT.md                      # ハートビート設定
└── BACKLOG.md                        # 後回しタスク
```

---

## 5. 主要スクリプト機能詳細

### email_manager.py（メール分析・優先度判定）
**実行頻度**: 毎時30分  
**タイムアウト**: 30秒  
**機能**:
1. Gmail APIから新着メール取得（最大50件）
2. `seen_emails.json` で既読判定
3. Obsidian Vault（`10_People/`, `11_Companies/`）から送信者の文脈検索
4. 優先度自動判定：
   - 重要な送信者パターンマッチング（ポート、Genspark、AirCle等）
   - 無視パターン除外（noreply、newsletter等）
   - 返信必要キーワード検出
5. P1/P2メールのみTelegramに報告
6. 返信が必要なメールは返信案を自動生成
7. `seen_emails.json` 更新

**依存**: Gmail API, Obsidian Vault  
**出力**: Telegram通知、seen_emails.json更新

---

### email_classifier.py（自動分類）
**実行頻度**: 毎時15分  
**処理上限**: 30件/回  
**機能**:
1. Gmail APIから未分類メール取得
2. Obsidian Vaultから文脈検索
3. 送信者・件名から関係性分析
4. ラベル付与：
   - プロジェクト名（AirCle、ClimbBeyond等）
   - 企業名（ポート、Genspark等）
   - 優先度（要返信、案件、重要等）
5. Gmail APIでラベル適用
6. 分類結果をTelegramに報告

**依存**: Gmail API, Obsidian Vault  
**出力**: Gmailラベル、Telegram通知

---

### task_reminder.py（タスクリマインダー）
**実行頻度**: 9:00, 12:00, 18:00, 21:00  
**機能**:
1. Google Tasksから全タスク取得
2. 期限チェック：
   - 3日前
   - 1日前
   - 12時間前
3. リマインド対象があればTelegramに送信
4. なければ `NO_REMINDER`

**依存**: Google Tasks  
**出力**: Telegram通知

---

### meeting_prep_reminder.py（MTG準備リマインダー）
**実行頻度**: 毎30分  
**機能**:
1. Google Calendarから今後2時間以内のMTG取得
2. MTG準備リスト生成：
   - MTGタイトル
   - 開始時間
   - 参加者
   - 議題（あれば）
   - 関連資料（Vaultから検索）
3. TelegramにMTG準備リスト送信
4. なければ `NO_REPLY`

**依存**: Google Calendar, Obsidian Vault  
**出力**: Telegram通知

---

### n8n_sync_to_vault.py（n8nイベント同期）
**実行頻度**: 毎時10分  
**機能**:
1. `/tmp/n8n_db.sqlite` からn8nイベント取得
2. 重複排除（`events.jsonl`と照合）
3. 新規イベントを `events.jsonl` に追記
4. Google Tasks同期（タスク数カウント）
5. 結果サマリー出力

**依存**: n8n DB  
**出力**: events.jsonl更新、サマリー出力

---

### expense_append.py（経費記録）
**実行頻度**: 毎日23:00  
**機能**:
1. Gmailから過去24時間の領収書メール検索
   - Anthropic, OpenAI, Stripe等
2. 件名・本文から金額・日付抽出
3. Google Spreadsheetsに追記：
   - 経費シート: https://docs.google.com/spreadsheets/d/1NLiR89wGRWoFDppU1PpYzdk4YMIrMsjIfLbsdhKMe2s
   - 収入シート: https://docs.google.com/spreadsheets/d/1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990
4. 処理結果をTelegramに報告

**依存**: Gmail API, Google Sheets API  
**出力**: スプレッドシート更新、Telegram通知

---

### memory_organizer.py（メモリ自動整理）
**実行頻度**: 毎日4:10  
**稼働時間**: 30分  
**機能**:
1. 曜日別テーマで整理実行：
   - 月: プロジェクト情報
   - 火: 人物情報
   - 水: 企業情報
   - 木: タスク・TODO
   - 金: 知識・メモ
   - 土: 全体見直し
   - 日: アーカイブ整理
2. `memory/YYYY-MM-DD.md` から重要情報抽出
3. Obsidian Vaultの該当セクション更新
4. 古い情報のアーカイブ化
5. 結果をTelegramに報告

**依存**: Obsidian Vault  
**出力**: Vault更新、Telegram通知

---

### git-auto-sync.sh（Git自動同期）
**実行頻度**: 毎時  
**機能**:
1. `git pull --rebase` でリモート変更取得
2. ローカル変更を自動コミット
3. `git push` でリモートに同期
4. コンフリクトがあれば通知
5. 結果をDiscordに報告

**依存**: GitHub  
**出力**: Discord通知

---

## 6. 通知フロー詳細

### Telegram通知（メイン通知チャネル）
**主な通知内容**:
- P1/P2メール報告（毎時30分）
- メール分類結果（毎時15分）
- タスクリマインダー（9/12/18/21時）
- MTG準備リスト（2時間前）
- 期限超えタスク（毎日15時）
- 朝のブリーフィング（毎日7時）
- 経費スキャン結果（毎日23時）
- メモリ整理結果（毎日4時）

**送信元**:
- メインセッション（直接会話の延長）
- Isolated セッション（agentTurn完了報告）

---

### Discord通知（セカンダリ）
**主な通知内容**:
- X投稿配信（毎日6時） → #aircle
- Git同期結果（毎時）
- 深夜開発セッション報告（毎日6時） → #aircle

**送信先チャネル**:
- `#aircle` (1468094860987863060)

---

## 7. セキュリティ層詳細

### 認証管理
1. **Gmail OAuth Token**
   - n8nで管理
   - `/tmp/n8n_db.sqlite` に暗号化保存（AES-256-CBC）
   - スクリプト実行時に復号化して `/tmp/gmail_token.json` にキャッシュ

2. **Google Calendar/Tasks Token**
   - `gog` skill経由で管理
   - OAuth認証フロー

### 暗号化
- **n8n DB暗号化**: AES-256-CBC
- **暗号化キー**: 環境変数（ハードコード回避）

### アクセス制限
1. **OpenClaw Gateway**
   - `gateway.bind: loopback` - ローカルホストのみ
   - `groupPolicy: allowlist` - 許可リストのみ実行

2. **ファイルパーミッション**
   - `~/.openclaw: 700` - 所有者のみアクセス可能

3. **トークンキャッシュ**
   - `/tmp/gmail_token.json` - 一時ファイル（再起動で消去）

---

## 8. エラーハンドリング

### タイムアウト保護
- `email_manager.py`: 30秒タイムアウト（signal.alarm）
- ハング時は自動終了（exit code 124）

### リトライ戦略
- Gmail API: 3回リトライ（指数バックオフ）
- Google Tasks: 2回リトライ
- n8n DB接続: 1回リトライ

### エラー通知
- 連続エラー時はTelegramに通知
- Cronジョブの `consecutiveErrors` カウント

---

## 更新履歴
- 2026-02-16 13:10 JST: 初版作成（全図解を文字化）
