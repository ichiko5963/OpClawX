# ichioka-vault 現在の構成図

## 🏗️ 全体像

```
┌─────────────────────────────────────────────────────────────┐
│                    外部サービス                              │
├─────────────────────────────────────────────────────────────┤
│  Gmail  │  Calendar  │  Tasks  │  Drive  │  LINE  │ Telegram│
└────┬─────────┬──────────┬────────┬─────────┬──────────┬─────┘
     │         │          │        │         │          │
     └─────────┴──────────┴────────┴─────────┘          │
                    ↓                                    │
     ┌──────────────────────────────┐                   │
     │   GitHub Actions（毎時0分）   │                   │
     │  - sync-google-data.yml      │                   │
     │  - email-receipt-monitor.yml │                   │
     └──────────────┬───────────────┘                   │
                    ↓                                    │
     ┌──────────────────────────────┐                   │
     │  GitHub Repository           │                   │
     │  ichioka-vault               │                   │
     │                              │                   │
     │  data/                       │                   │
     │  ├── gmail/*.json            │                   │
     │  ├── calendar/*.json         │                   │
     │  ├── tasks/*.json            │                   │
     │  └── drive/transcriptions/   │                   │
     └──────────────┬───────────────┘                   │
                    ↓                                    │
     ┌──────────────────────────────┐                   │
     │  Mac mini                    │                   │
     │  (OpenClaw実行環境)           │                   │
     │                              │                   │
     │  1. git-auto-sync (毎時)     │◄──────────────────┘
     │     GitHub → ローカル同期     │   Telegram/LINE
     │                              │   からのメッセージ
     │  2. cronジョブ (16個稼働中)   │
     │     - Meet議事録処理          │
     │     - メール分析              │
     │     - タスクリマインダー      │
     │     - X投稿生成              │
     │     - etc...                 │
     │                              │
     │  3. LINE Webhook Server      │
     │     (ポート5001, ngrok)      │
     │     - 領収書画像受信          │
     │     - GPT-4V分析             │
     │     - Drive保存              │
     │     - Sheet追記              │
     └──────────────┬───────────────┘
                    ↓
     ┌──────────────────────────────┐
     │  処理結果                    │
     ├──────────────────────────────┤
     │  • Google Tasks追加          │
     │  • Googleカレンダー追加      │
     │  • Googleスプレッドシート更新│
     │  • Telegram通知              │
     │  • Discord投稿               │
     └──────────────────────────────┘
```

---

## 📁 データフロー

### 1. Google同期（毎時0分）

```
GitHub Actions
     ↓
[Gmail取得] → data/gmail/2026-02-15.json
[Calendar取得] → data/calendar/2026-02-15.json
[Tasks取得] → data/tasks/2026-02-15.json
[Drive文字起こし] → data/drive/transcriptions/*.json
     ↓
GitHubにcommit & push
```

### 2. ローカル同期（毎時）

```
Mac mini
     ↓
git pull (GitHub → ローカル)
     ↓
~/Documents/OpenClaw-Workspace/data/
     ↓
Obsidian反映
```

### 3. 自動処理（cronジョブ）

```
Meet文字起こし検出 (毎時0分)
     ↓
Claude分析
     ↓
- 議事録生成
- いちさんのTODO抽出 → Google Tasks追加
- 次回MTG日程 → Googleカレンダー追加
     ↓
Telegram通知
```

### 4. LINE領収書Bot（リアルタイム）

```
LINE画像送信
     ↓
LINE Webhook Server (Mac mini)
     ↓
GPT-4V分析
     ↓
- 日付、宛名、金額、カテゴリー抽出
- Drive保存
- スプレッドシート追記
     ↓
LINE返信（全9列表示）
     ↓
修正指示あれば → Sheet更新
```

---

## 🔧 稼働中のシステム

### GitHub Actions（2個）
1. **sync-google-data.yml** (毎時0分)
   - Gmail, Calendar, Tasks, Drive同期
   
2. **email-receipt-monitor.yml** (毎時0分)
   - 領収書メール検出
   - 添付ファイル → Drive保存

### cronジョブ（16個）
1. git-auto-sync (毎時)
2. meet-transcript-processor (毎時0分)
3. email-hourly-check (30分)
4. email-analysis (15分)
5. email-auto-classifier (15分)
6. meeting-prep-reminder (30分ごと)
7. task-reminder-check (9,12,18,21時)
8. overdue-tasks-nag (15時)
9. morning-briefing-telegram (7時)
10. morning-task-report (6時) - X投稿3アカウント分
11. nightly-dev-session (1時) - 深夜セッション
12. daily-efficiency-suggestions (12時)
13. expense-daily-append (23時)
14. daily-memory-cleanup (23時)
15. n8n-vault-sync (毎時10分)
16. backlog-check (30分ごと)

### LINE Webhook Server
- ポート: 5001 (ngrok)
- リアルタイム処理
- GPT-4V使用

---

## 📊 データ保存先

```
~/Documents/OpenClaw-Workspace/
├── data/
│   ├── gmail/
│   │   └── 2026-02-15.json (2.8MB, 50件)
│   ├── calendar/
│   │   └── 2026-02-15.json (144KB, 122件)
│   ├── tasks/
│   │   └── 2026-02-15.json (13KB, 17件)
│   ├── drive/
│   │   └── transcriptions/
│   │       ├── pnp-gqnf-isz...Transcript.json (2件)
│   │       └── ...
│   └── sync_state.json
│
├── obsidian/
│   └── Ichioka Obsidian/
│       ├── 00_System/
│       ├── 03_Projects/
│       ├── 10_People/
│       └── 11_Companies/
│
└── memory/
    ├── 2026-02-14.md
    ├── 2026-02-15.md
    └── MEMORY.md
```

---

## 🔄 同期頻度

| システム | 頻度 | タイミング |
|---------|------|-----------|
| Google同期 | 毎時 | 0分 |
| 領収書メール | 毎時 | 0分 |
| git同期 | 毎時 | 随時 |
| Meet議事録 | 毎時 | 0分 |
| メール分析 | 毎時 | 15分・30分 |
| LINE領収書 | リアルタイム | 随時 |

---

**こんな感じ！👍**
