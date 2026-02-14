# OpenClaw徹底解説：AIが24時間働く仕組みを全公開｜大学生AI団体代表の運用術

---

## はじめに：AIが「秘書」から「相棒」になった瞬間

「AIに仕事を任せたい」

そう思っている人は多いはず。でも、ChatGPTやClaudeに質問して終わり…という使い方で止まっていませんか？

僕は大学生AI団体「AirCle」の代表をしながら、複数のプロジェクトを同時進行しています。正直、人間1人では回らない。

そこで出会ったのが**OpenClaw**というツール。

今では：
- **毎朝6時に自動でX投稿用コンテンツが届く**
- **メールが自動で分類・優先度付けされる**
- **会議の2時間前に準備リストが届く**
- **深夜1時から6時まで自律的に開発作業をする**
- **経費を自動でスプレッドシートに記録する**

全部、AIが勝手にやってくれる。

この記事では、僕がOpenClawをどう設定して、どう運用しているかを**徹底公開**します。

---

## OpenClawとは？

OpenClawは、AIエージェントを**常駐させる**ためのフレームワーク。

普通のAIチャット（ChatGPT、Claude）は「聞かれたら答える」だけ。
OpenClawは違う。

- **24時間動き続ける**
- **定期的にタスクを実行する（cron）**
- **ファイルを読み書きできる**
- **コマンドを実行できる**
- **メッセージを送受信できる（Discord、Telegram、Slack）**

つまり、**AIに「仕事」を任せられる**。

---

## 全体構成：僕の運用システム

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                         │
│  （Mac mini M4で24時間稼働）                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Discord   │  │  Telegram   │  │   Google    │         │
│  │  チャンネル  │  │    Bot      │  │  連携       │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│                    ┌─────▼─────┐                            │
│                    │   Agent   │                            │
│                    │  (Claude) │                            │
│                    └─────┬─────┘                            │
│                          │                                  │
│    ┌─────────────────────┼─────────────────────┐            │
│    │                     │                     │            │
│    ▼                     ▼                     ▼            │
│ ┌──────┐           ┌──────────┐         ┌──────────┐       │
│ │Memory│           │  Cron    │         │ Scripts  │       │
│ │ .md  │           │  Jobs    │         │ (.py)    │       │
│ └──────┘           └──────────┘         └──────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Part 1: メモリシステム

AIは毎回のセッションで「記憶をリセット」される。でも、僕のOpenClawは**記憶を持っている**。

### ファイル構成

```
OpenClaw-Shared/
├── MEMORY.md          # 長期記憶（重要な決定、ルール）
├── AGENTS.md          # エージェントの行動ルール
├── SOUL.md            # パーソナリティ
├── USER.md            # ユーザー情報
└── memory/
    └── YYYY-MM-DD.md  # 日次ログ
```

### MEMORY.md：長期記憶

ここには「忘れてほしくないこと」を書く。

```markdown
# Long-term Memory

## User Preferences
- いちさん / 市岡直人 (AirCle代表)
- 長いタスクは「やるね」→「できたよ」で報告する
- 中学生にもわかるように説明する
- 品質優先、時間をかけてもいい

## 開発原則
**「開発して」と言われたら:**
1. 最低30分以上稼働 - 急がない、じっくり作る
2. 自分でエラー修正 - 人間に頼らず自分で解決
3. 自分でブラウザ開いてテスト - 実際に動かして確認
4. 完璧に動くまで繰り返す - 中途半端で終わらない
5. 自律的に完成させる - 途中で報告して待たない

## Active Projects
1. AirCle - 大学生AI団体
2. ClimbBeyond
3. SlideBox
4. ClientWork - 外部案件
5. Genspark - 協業案件
```

AIはセッション開始時にこのファイルを読む。だから、僕のことを「覚えている」。

### AGENTS.md：行動ルール

エージェントがどう振る舞うかのルール。

```markdown
# AGENTS.md - Your Workspace

## Every Session
1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` for recent context
4. If in MAIN SESSION: Also read `MEMORY.md`

## Safety
- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm` (recoverable beats gone forever)

## 文字起こし → 議事録 自動化
文字起こしを受け取ったら：
1. 参加者を照合
2. 判断可能 → 自動で議事録化
3. 保存先を適切に選択
```

---

## Part 2: Cronジョブ（定期実行）

これが**本当の自動化**。決まった時間に、AIが勝手に動く。

### 現在稼働中のCronジョブ

| ジョブ名 | 実行時間 | 内容 |
|---------|---------|------|
| morning-task-report | 毎日6:00 | X投稿コンテンツをDiscordに配信 |
| nightly-dev-session | 毎日1:00 | 深夜5時間の自律開発セッション |
| email-hourly-check | 毎時30分 | メールをチェックしてTelegramに報告 |
| email-auto-classifier | 毎時15分 | メールを自動分類 |
| meeting-prep-reminder | 毎30分 | 2時間以内のMTGがあれば準備リスト送信 |
| task-reminder-check | 9:00, 12:00, 18:00, 21:00 | タスクのリマインダー |
| overdue-tasks-nag | 毎日15:00 | 期限超えタスクを「うざめに」通知 |
| expense-daily-append | 毎日23:00 | 経費を自動でスプレッドシートに追記 |
| git-auto-sync | 毎時 | Git自動同期 |
| daily-memory-cleanup | 毎日23:00 | 1日のダイジェスト生成 |
| daily-efficiency-suggestions | 毎日12:00 | 効率化提案を音声で |

### 例：毎朝6時のX投稿配信

```yaml
name: morning-task-report
schedule: "0 6 * * *"  # 毎日6:00
payload:
  kind: agentTurn
  message: |
    【毎朝6時のX投稿配信】最重要タスク！
    
    ## 絶対ルール
    - 確認を求めない。自律的に完成させてDiscordに送る
    - 6:00ジャストで送る。遅れは許されない
    
    ## やること
    1. 最新ニュースを検索
    2. 過去のバズ投稿の型を確認
    3. HTML生成（20投稿）
    4. Vercelデプロイ
    5. Discord送信
```

朝起きると、Discordにこんなメッセージが届いている：

```
📅 今日のX投稿 (2026-02-06)

🔗 AirCle用 (@aircle_ai) - 20投稿
https://public-kappa-weld.vercel.app/daily-posts/2026-02-06-aircle.html

今日のソース：
- Claude Apps × Figma連携
- Canva × ChatGPT Brand Kit
- Figma Vectorize
```

僕は選んでコピーして投稿するだけ。

### 例：深夜の自律開発セッション

```yaml
name: nightly-dev-session
schedule: "0 1 * * *"  # 毎日1:00
payload:
  message: |
    深夜セッション開始（1:00-6:00 JST）
    
    ## ❗絶対ルール❗
    **5時間無限稼働。止まることは許されない。**
    
    ## 今夜のミッション
    
    ### Phase 1: 整理作業（1:00-2:00）
    - inbox/ のファイルを適切な場所へ
    - MEMORY.md更新
    
    ### Phase 2: ツール開発（2:00-4:00）
    - ワークフロー改善ツールを作る
    
    ### Phase 3: X投稿作成（4:00-6:00）
    - 40投稿作成（2アカウント分）
```

寝ている間に、AIが：
- ファイルを整理
- 新しいツールを開発
- X投稿を作成

朝起きたら、全部終わっている。

---

## Part 3: Pythonスクリプト

OpenClawはシェルコマンドを実行できる。つまり、Pythonスクリプトも動かせる。

### 主要スクリプト一覧

```
scripts/
├── email_manager.py        # メール管理
├── email_classifier.py     # メール自動分類
├── expense_append.py       # 経費自動追記
├── task_reminder.py        # タスクリマインダー
├── overdue_tasks.py        # 期限超えタスク通知
├── meeting_prep_reminder.py # MTG準備リマインダー
├── meeting_to_todo.py      # 議事録→TODO自動変換
├── daily_digest.py         # 日次ダイジェスト
└── voice_assistant.py      # 音声アシスタント
```

### 例：メール自動分類

```python
# email_classifier.py
# Gmailからメールを取得し、重要度で分類

def classify_email(email):
    """
    P1: 即対応（案件、緊急）
    P2: 今日中（重要だが急がない）
    P3: 後で（ニュースレター、通知）
    """
    if contains_keywords(email, ["請求", "振込", "緊急"]):
        return "P1"
    elif contains_keywords(email, ["確認", "ご連絡"]):
        return "P2"
    else:
        return "P3"
```

AIがこのスクリプトを実行して、結果をTelegramで報告：

```
📧 メール分類完了

P1（即対応）: 2件
- 〇〇株式会社: 請求書の件
- △△さん: 緊急の確認事項

P2（今日中）: 5件
P3（後で）: 12件
```

### 例：経費自動追記

```python
# expense_append.py
# Gmailから請求書・領収書を検出してスプレッドシートに追記

def process_expense_email(email):
    """
    1. 件名・本文から金額を抽出
    2. カテゴリを推定
    3. Google Sheetsに追記
    """
    amount = extract_amount(email.body)
    category = classify_expense(email.subject)
    append_to_sheet(date, amount, category, email.subject)
```

毎日23時に実行。請求書が来たら自動で経費シートに記録される。

---

## Part 4: Obsidian連携

OpenClawは僕のObsidian Vaultにアクセスできる。

### フォルダ構成

```
obsidian/Ichioka Obsidian/
├── 00_System/         # レジストリ、テンプレート
├── 03_Projects/       # プロジェクト
│   ├── _Active/       # アクティブ
│   └── _Old/          # 完了・休止
├── 10_People/         # 人物情報
└── 11_Companies/      # 企業情報
```

### 議事録の自動処理

Zoomで会議→文字起こし→OpenClawに送信

すると：
1. 参加者をObsidianの人物情報と照合
2. 議事録を自動生成
3. 適切なフォルダに保存
4. TODOを抽出してGoogle Tasksに追加

```markdown
# 2026-02-06 〇〇株式会社 定例MTG

## 参加者
- いち（AirCle代表）
- 田中さん（〇〇株式会社 マーケ部長）

## 要約
X運用の進捗確認と次月の施策について議論。

## 決定事項
- 来月からショート動画を週3本に増加
- インフルエンサーコラボを1件実施

## TODO
- [ ] いち: インフルエンサーリスト作成（2/10まで）
- [ ] 田中: 予算確認（2/8まで）

## 次回
2026-02-13 15:00
```

---

## Part 5: メッセージング連携

### Discord

AirCleのDiscordサーバーにBotとして参加。

- #aircle チャンネルでメンションされたら応答
- 毎朝6時にX投稿を配信
- 深夜開発の成果を報告

### Telegram

プライベートな通知用。

- メールの重要アラート
- タスクリマインダー
- MTG準備リマインダー
- 効率化提案

### 使い分け

| 用途 | チャンネル |
|-----|---------|
| X投稿配信 | Discord |
| チーム共有 | Discord |
| 個人への通知 | Telegram |
| 緊急アラート | Telegram |

---

## Part 6: セキュリティ

AIに色々任せる以上、セキュリティは重要。

### 実施している対策

```yaml
# セキュリティ設定
groupPolicy: allowlist      # 許可したグループのみ
gateway.bind: loopback      # ローカルのみ
~/.openclaw: 700            # パーミッション制限
```

### 行動ルール

```markdown
## Safety（AGENTS.mdより）

- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm`
- When in doubt, ask.

## 外部アクション

**勝手にやっていい:**
- ファイル読み書き
- Web検索
- カレンダー確認

**確認が必要:**
- メール送信
- SNS投稿
- 外部API呼び出し
```

---

## Part 7: 実際の1日の流れ

### 深夜1:00

```
🌙 深夜セッション開始
- inbox/ の整理中...
- 新しいスクリプト開発中...
- X投稿を作成中...
```

（寝ている）

### 朝6:00

```
📅 今日のX投稿 (2026-02-06)
🔗 https://...
（20投稿が届く）
```

### 朝7:00

```
📧 メールチェック完了
P1: 2件あります
- 〇〇株式会社: 請求書確認依頼
```

### 昼12:00

```
💡 効率化提案の時間！
今日自動化できそうなこと：
1. 〇〇の定型作業
2. △△のレポート生成
...
```

### 午後15:00

```
😤 期限超えタスクがあるよ！
- 「資料作成」が1日超過してます
やりましょう！
```

### 夜23:00

```
📊 今日のダイジェスト
- 処理したメール: 45件
- 完了したタスク: 8件
- 経費記録: 2件（合計¥12,500）
```

---

## まとめ：AIと「一緒に働く」という感覚

OpenClawを使い始めて変わったこと：

### Before
- メールを手動でチェック
- タスクを忘れる
- 深夜まで作業
- X投稿を考える時間がない

### After
- メールは分類済みで届く
- タスクは勝手にリマインドされる
- 寝ている間にAIが作業
- X投稿は選ぶだけ

正直、「人を雇う」より先に「AIを雇う」方がコスパがいい。

OpenClawは無料で使える。設定は少し大変だけど、一度組めば**24時間365日働いてくれる相棒**になる。

---

## 次のステップ

興味を持った人へ：

1. **OpenClaw公式**: https://github.com/openclaw/openclaw
2. **ドキュメント**: https://docs.openclaw.ai
3. **Discord**: https://discord.com/invite/clawd

質問があればAirCleのDiscordでも聞いてください！

---

*この記事はOpenClawのAIエージェントと一緒に作成しました。*
