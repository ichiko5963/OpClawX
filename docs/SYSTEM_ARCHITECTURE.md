# システム全体アーキテクチャ

## 全体構成図

```mermaid
graph TB
    subgraph "外部サービス"
        Gmail[Gmail API]
        Calendar[Google Calendar]
        Tasks[Google Tasks]
        Drive[Google Drive]
        Telegram[Telegram]
        Discord[Discord]
    end
    
    subgraph "データ収集層"
        n8n[n8n Workflow<br/>毎時同期]
        n8n --> Gmail
        n8n --> Calendar
        n8n --> Drive
    end
    
    subgraph "データストレージ"
        Vault[Obsidian Vault<br/>知識ベース]
        StateDB[(State Files<br/>JSON/SQLite)]
    end
    
    subgraph "OpenClaw システム"
        Gateway[OpenClaw Gateway<br/>メインセッション]
        Cron[Cron Jobs<br/>定期実行]
        Scripts[Python Scripts<br/>自動化ツール]
        
        Gateway --> Cron
        Cron --> Scripts
    end
    
    subgraph "処理フロー"
        EmailMgr[email_manager.py<br/>メール分析]
        EmailClass[email_classifier.py<br/>自動分類]
        TaskReminder[task_reminder.py<br/>リマインダー]
        MeetingPrep[meeting_prep_reminder.py<br/>MTG準備]
        N8NSync[n8n_sync_to_vault.py<br/>Vault保存]
        ExpenseAppend[expense_append.py<br/>経費記録]
        GitSync[git-auto-sync.sh<br/>Git同期]
    end
    
    n8n --> StateDB
    Scripts --> Vault
    Scripts --> StateDB
    Scripts --> Tasks
    Scripts --> Calendar
    
    EmailMgr --> Gmail
    EmailClass --> Gmail
    
    Gateway --> Telegram
    Gateway --> Discord
    
    Scripts --> EmailMgr
    Scripts --> EmailClass
    Scripts --> TaskReminder
    Scripts --> MeetingPrep
    Scripts --> N8NSync
    Scripts --> ExpenseAppend
    Scripts --> GitSync
    
    N8NSync --> Vault
    GitSync --> Vault

    style Gateway fill:#4CAF50
    style Vault fill:#2196F3
    style n8n fill:#FF9800
    style Scripts fill:#9C27B0
```

## データフロー詳細

```mermaid
sequenceDiagram
    participant Gmail
    participant n8n
    participant Vault
    participant Scripts
    participant Gateway
    participant Telegram
    
    Note over n8n: 毎時10分
    n8n->>Gmail: 新着メール取得
    n8n->>Vault: events.jsonl に保存
    
    Note over Scripts: 毎時15分
    Gateway->>Scripts: email_classifier.py 実行
    Scripts->>Gmail: 未分類メール取得
    Scripts->>Vault: 文脈検索（10_People/, 11_Companies/）
    Scripts->>Gmail: ラベル付与
    Scripts->>Telegram: 分類結果報告
    
    Note over Scripts: 毎時30分
    Gateway->>Scripts: email_manager.py 実行
    Scripts->>Gmail: 新着確認
    Scripts->>Vault: 文脈検索
    Scripts->>Telegram: P1/P2メール報告
```

## Cron スケジュール

```mermaid
gantt
    title 定期実行スケジュール
    dateFormat HH:mm
    axisFormat %H:%M
    
    section 毎時
    n8n Vault保存        :10:00, 1h
    メール分析            :15:00, 1h
    メール自動分類        :15:00, 1h
    メールチェック        :30:00, 1h
    BACKLOG確認          :30:00, 1h
    MTG準備リマインダー   :00:00, 30m
    Git自動同期          :14:00, 1h
    
    section 1日4回
    タスクリマインダー    :09:00, 12h
    タスクリマインダー    :12:00, 12h
    タスクリマインダー    :18:00, 12h
    タスクリマインダー    :21:00, 12h
    
    section 毎日1回
    深夜開発セッション    :01:00, 5h
    メモリ自動整理        :04:10, 3h
    X投稿作成            :06:00, 1h
    朝のブリーフィング    :07:00, 1h
    効率化提案           :12:00, 1h
    期限超えタスク通知    :15:00, 8h
    Daily Digest         :23:00, 1h
    経費スキャン         :23:00, 1h
```

## ファイル構成

```mermaid
graph LR
    subgraph "Workspace Root"
        Scripts[scripts/]
        Obsidian[obsidian/]
        Data[data/]
        Bin[bin/]
        Memory[memory/]
    end
    
    subgraph "scripts/"
        EmailMgr[email_manager.py]
        EmailClass[email_classifier.py]
        TaskRem[task_reminder.py]
        MeetPrep[meeting_prep_reminder.py]
        N8NSync[n8n_sync_to_vault.py]
        Expense[expense_append.py]
    end
    
    subgraph "obsidian/Ichioka Obsidian/"
        System[00_System/]
        Projects[03_Projects/]
        People[10_People/]
        Companies[11_Companies/]
    end
    
    subgraph "00_System/"
        State[01_State/]
        Templates[02_Templates/]
        Registry[03_Registry/]
    end
    
    subgraph "01_State/"
        Events[events.jsonl]
        SeenEmails[seen_emails.json]
        Cursors[cursors.json]
    end
    
    Scripts --> EmailMgr
    Scripts --> EmailClass
    Scripts --> TaskRem
    Scripts --> MeetPrep
    Scripts --> N8NSync
    Scripts --> Expense
    
    Obsidian --> System
    Obsidian --> Projects
    Obsidian --> People
    Obsidian --> Companies
    
    System --> State
    System --> Templates
    System --> Registry
    
    State --> Events
    State --> SeenEmails
    State --> Cursors
```

## 主要スクリプト機能

| スクリプト | 実行頻度 | 機能 | 依存サービス |
|-----------|---------|------|-------------|
| `email_manager.py` | 毎時30分 | 新着メール分析・優先度判定・返信案生成 | Gmail API, Vault |
| `email_classifier.py` | 毎時15分 | メール自動ラベル付与（最大30件） | Gmail API, Vault |
| `n8n_sync_to_vault.py` | 毎時10分 | n8nイベントをVaultに保存 | n8n DB |
| `task_reminder.py` | 9/12/18/21時 | タスク期限リマインダー（3日前/1日前/12時間前） | Google Tasks |
| `meeting_prep_reminder.py` | 毎30分 | 2時間以内のMTG準備リスト送信 | Google Calendar |
| `expense_append.py` | 毎日23時 | 領収書スキャン→スプレッドシート追記 | Gmail, Google Sheets |
| `daily_digest.py` | 毎日23時 | Executive Summary生成 | Vault |
| `memory_organizer.py` | 毎日4:10 | メモリ自動整理（曜日別テーマ） | Vault |
| `git-auto-sync.sh` | 毎時 | Git自動同期（push/pull） | GitHub |

## 通知フロー

```mermaid
graph LR
    subgraph "情報源"
        Gmail
        Calendar
        Tasks
        Scripts
    end
    
    subgraph "OpenClaw Gateway"
        MainSession[メインセッション]
        IsolatedSession[Isolated セッション]
    end
    
    subgraph "通知先"
        Telegram
        Discord
    end
    
    Gmail --> Scripts
    Calendar --> Scripts
    Tasks --> Scripts
    
    Scripts --> MainSession
    Scripts --> IsolatedSession
    
    MainSession --> Telegram
    IsolatedSession --> Telegram
    IsolatedSession --> Discord
    
    MainSession -->|重要通知| Telegram
    IsolatedSession -->|完了報告| Discord
```

## セキュリティ層

```mermaid
graph TB
    subgraph "認証"
        GmailToken[Gmail OAuth Token<br/>n8n管理]
        GCalToken[Google Calendar Token<br/>gog skill]
        TasksToken[Google Tasks Token<br/>gog skill]
    end
    
    subgraph "暗号化"
        n8nEnc[n8n DB 暗号化<br/>AES-256-CBC]
        TokenCache[Token Cache<br/>/tmp/gmail_token.json]
    end
    
    subgraph "アクセス制限"
        LoopbackOnly[Gateway: loopback only]
        AllowList[groupPolicy: allowlist]
        FilePerms[~/.openclaw: 700]
    end
    
    GmailToken --> n8nEnc
    n8nEnc --> TokenCache
    
    style n8nEnc fill:#f44336
    style LoopbackOnly fill:#ff9800
    style AllowList fill:#ff9800
```

---

## 更新履歴

- 2026-02-16: 初版作成（タイムアウト機能追加後）
