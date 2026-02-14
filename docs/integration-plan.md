# 統合計画書：ichioka-vault + OpenClaw

## 📋 現状分析

### リポジトリ1: ichioka-vault（本番稼働中）
**場所**: https://github.com/ichiko5963/ichioka-vault

**機能**:
- Gmail同期（毎時、初回30日、以降1日）
- Calendar同期（毎時、初回30日、以降1日）
- Tasks同期（毎時）
- Drive文字起こし同期（毎時）
- Meet議事録自動生成
- LINE領収書Bot（OpenAI GPT-4V）
- Email領収書監視

**データ保存先**:
- `data/gmail/YYYY-MM-DD.json`
- `data/calendar/YYYY-MM-DD.json`
- `data/tasks/YYYY-MM-DD.json`
- `data/drive/transcriptions/*.json`

---

### リポジトリ2: OpenClaw（作りかけ）
**場所**: https://github.com/ichiko5963/OpenClaw

**機能**（READMEから）:
- Gmail同期
- Calendar同期
- Tasks同期
- Drive文字起こし同期
- **Notion同期**（未実装）
- **Slack同期**（未実装）
- **Sheets同期**（メタデータのみ）
- **Docs同期**（内容取得付き）
- **Slides同期**（メタデータのみ）

**重要な違い**:
1. Docs内容取得機能あり（更新検知付き）
2. Notion/Slack対応を想定
3. より詳細なメタデータ管理

---

## 🎯 統合方針

### 基本戦略
**OpenClawは「情報取得専用窓口」として独立させる**

```
[OpenClaw Repository]          [ichioka-vault Repository]
（情報収集専門）                （情報活用・処理）
       ↓                              ↓
  GitHub Actions                 GitHub Actions
       ↓                              ↓
  データ収集のみ                  処理・分析・自動化
       ↓                              ↓
   data/*.json           ← 同期 ←   処理結果
```

### 役割分担

#### OpenClaw（情報収集窓口）
- **Notion同期**（新規追加）
- **Slack同期**（新規追加）
- **Docs内容取得**（OpenClawから移行）
- **Sheets詳細取得**（OpenClawから移行）
- **Slides詳細取得**（OpenClawから移行）

#### ichioka-vault（情報活用）
- Gmail/Calendar/Tasks同期（既存）
- Drive文字起こし同期（既存）
- **Meet議事録自動生成**（既存）
- **LINE領収書Bot**（既存）
- **Email領収書監視**（既存）
- **OpenClawデータの取り込み**（新規）

---

## 🔧 実装計画

### Phase 1: OpenClaw拡張（Notion/Slack追加）

#### 1.1 Notion同期スクリプト
```python
# scripts/sync_notion.py
- Notionワークスペース内の全ページ取得
- データベース内容取得
- 更新検知（前回同期時刻）
- data/notion/YYYY-MM-DD.json に保存
```

#### 1.2 Slack同期スクリプト
```python
# scripts/sync_slack.py
- 参加チャンネルのメッセージ取得
- ダイレクトメッセージ取得
- ファイル添付取得
- data/slack/YYYY-MM-DD.json に保存
```

#### 1.3 GitHub Actions設定
```yaml
# .github/workflows/sync-all.yml
- cron: '0 * * * *'  # 毎時0分
- Gmail, Calendar, Tasks, Drive（既存）
- Notion, Slack（新規）
- Docs内容、Sheets詳細、Slides詳細（新規）
```

---

### Phase 2: ichioka-vault拡張（OpenClaw連携）

#### 2.1 OpenClawデータ取り込み
```python
# scripts/import_from_openclaw.py
- OpenClawリポジトリからデータ取得（GitHub API）
- data/notion/, data/slack/ を ichioka-vault にコピー
- 重複排除
- 1時間ごとに実行
```

#### 2.2 Notion/Slack処理機能
```python
# scripts/process_notion.py
- Notionページから重要情報抽出
- タスク/プロジェクト抽出
- Obsidianに反映

# scripts/process_slack.py
- Slackメンションチェック
- 重要メッセージ抽出
- 未読通知
```

---

### Phase 3: データフロー統合

```
[外部サービス]
    ↓
[OpenClaw Repository]
    ↓ (GitHub Actions 毎時)
Notion/Slack/Docs等を収集
    ↓
data/*.json に保存
    ↓ (GitHub commit & push)
GitHub上のデータ更新
    ↓
[ichioka-vault Repository]
    ↓ (GitHub Actions 毎時10分)
OpenClawから最新データ取得
    ↓
処理・分析
    ↓
- Meet議事録生成
- TODO抽出 → Google Tasks
- 次回MTG → Calendar
- Telegram通知
```

---

## 📁 ディレクトリ構造（統合後）

### OpenClaw Repository
```
OpenClaw/
├── .github/workflows/
│   └── sync-all.yml         # 毎時0分実行
├── scripts/
│   ├── sync_notion.py       # 新規
│   ├── sync_slack.py        # 新規
│   ├── sync_docs_content.py # 移行
│   ├── sync_sheets.py       # 拡張
│   └── sync_slides.py       # 拡張
├── data/
│   ├── notion/
│   ├── slack/
│   ├── docs/content/
│   ├── sheets/
│   └── slides/
└── README.md
```

### ichioka-vault Repository
```
ichioka-vault/
├── .github/workflows/
│   ├── sync-google-data.yml      # 既存
│   ├── email-receipt-monitor.yml # 既存
│   └── import-openclaw.yml       # 新規
├── scripts/
│   ├── sync_google_data.py       # 既存
│   ├── process_meet_transcripts.py # 既存
│   ├── import_from_openclaw.py   # 新規
│   ├── process_notion.py         # 新規
│   └── process_slack.py          # 新規
├── data/
│   ├── gmail/
│   ├── calendar/
│   ├── tasks/
│   ├── drive/transcriptions/
│   ├── notion/         # OpenClawから
│   ├── slack/          # OpenClawから
│   ├── docs/           # OpenClawから
│   ├── sheets/         # OpenClawから
│   └── slides/         # OpenClawから
└── obsidian/
    └── Ichioka Obsidian/
```

---

## 🔐 シークレット管理

### OpenClaw
```
GOOGLE_OAUTH_TOKENS  # 既存
NOTION_TOKEN         # 新規
SLACK_TOKEN          # 新規
```

### ichioka-vault
```
GOOGLE_OAUTH_TOKENS   # 既存
OPENAI_API_KEY        # 既存
OPENCLAW_GITHUB_TOKEN # 新規（OpenClawアクセス用）
```

---

## ⏱️ スケジュール

### OpenClaw（情報収集）
- **毎時0分**: Notion/Slack/Docs/Sheets/Slides同期
- データをGitHubにcommit & push

### ichioka-vault（情報活用）
- **毎時10分**: OpenClawから最新データ取得
- **毎時15分**: Notion/Slack処理
- **毎時30分**: Meet議事録処理（既存）

---

## 🚀 実装ステップ

### ステップ1: OpenClaw拡張（2-3時間）
1. Notion API統合
2. Slack API統合
3. GitHub Actions設定
4. テスト実行

### ステップ2: ichioka-vault連携（1-2時間）
1. OpenClawデータ取り込みスクリプト
2. GitHub Actions設定
3. テスト実行

### ステップ3: 処理機能追加（1-2時間）
1. Notion処理（タスク抽出等）
2. Slack処理（メンション通知等）
3. Obsidian連携

### ステップ4: テスト・検証（1時間）
1. 全体フロー確認
2. エラーハンドリング
3. ドキュメント整備

---

## 💡 バッティング回避策

### データ重複防止
- OpenClaw: 生データのみ（メタデータ中心）
- ichioka-vault: 処理済みデータ（分析結果）

### 実行タイミング分離
- OpenClaw: 毎時0分
- ichioka-vault: 毎時10分（OpenClawの後）

### スコープ分離
- OpenClaw: 収集専門（書き込みなし）
- ichioka-vault: 処理専門（Tasks追加、Calendar追加等）

---

## ✅ 完成後のメリット

1. **情報の一元管理**: Notion/Slack含む全サービス
2. **処理の分離**: 収集と活用を明確に分担
3. **保守性向上**: 各リポジトリの役割が明確
4. **拡張性**: 新しいサービス追加が容易

---

**この設計でいい？実装開始する？🚀**
