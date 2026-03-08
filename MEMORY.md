# Long-term Memory

## Principles
- 重要な決定 / 目的 / 連絡先 / 進行中タスクはここに残す

## User Preferences
- いちさん / 市岡直人 (AirCle代表)
- 長いタスクは「やるね」→「できたよ」で報告する
- 中学生にもわかるように説明する
- 品質優先、時間をかけてもいい

## 開発原則（2026-02-03 追加）
**「開発して」と言われたら:**
1. **最低30分以上稼働** - 急がない、じっくり作る
2. **自分でエラー修正** - 人間に頼らず自分で解決
3. **自分でブラウザ開いてテスト** - 実際に動かして確認
4. **完璧に動くまで繰り返す** - 中途半端で終わらない
5. **自律的に完成させる** - 途中で報告して待たない

**自動化の視点:**
- いちさんの仕事内容を見て「これ自動化できそう」を探す
- 見つけたら提案または実装

## メモリ整理の絶対ルール（2026-02-16 追加）
**メモリ整理・自動化実行時:**
1. **ファイルやフォルダは絶対に削除しない** - 並び替え・整理のみ
2. **要素を一つも削らない** - 追加・編集はOK、削除は絶対NG
3. **情報の整理 = 構造化・分類** であって、削除ではない
4. **アーカイブ化** も明示的な指示がない限りNG
5. **不確かな場合は何もしない** - 削除より放置の方がマシ

## Important Decisions
- 2026-02-02: セキュリティハードニング実施
  - groupPolicy: allowlist
  - gateway.bind: loopback
  - ~/.openclaw: 700
- 2026-02-02: Obsidian連携設定
  - memorySearch.extraPathsにObsidian Vault追加
- 2026-02-03: Context Curator運用開始
  - 役割: 文脈整備 > プロジェクト管理 > ブリーフィング
  - Read-only原則: メール送信/カレンダー追加は必ず確認
  - 7:00 Daily Brief (Telegram)
  - Hourly Pulse (毎時30分)

## Known Issues
- **2026-02-24: Google API認証エラー発生**
  - 全Googleサービス（Gmail, Calendar, Tasks, Drive）でHTTP 400 Bad Request
  - 影響スクリプト: email_manager.py, meeting_prep_reminder.py, task_reminder.py, overdue_tasks.py, expense_append.py
  - 対応: OAuth再設定が必要（gog CLIでも発生）
  - 2026-03-08: gog CLIで再認証完了（jiuhuot10@gmail.com）、しかしgogコマンドがタイムアウトする問題あり

## AI業界動向メモ（2026-03-09 更新）
- **米政府がAnthropic排除**: 自律型兵器・大規模監視への使用拒否が原因。OpenAI/Geminiに移行。
- **OpenAI Symphony**: Elixir製オープンソースエージェントフレームワーク（3/5）
- **GPT-5.4**: 100万トークンコンテキスト、ネイティブPC操作、幻覚33%減（3/5）
- **Cursor Automations**: イベント駆動AIエージェント、ARR $2B、評価額$29.3B（3/4）
- **Codex 0.111.0**: ローカルモデル対応（Ollama/LM Studio/MLX）

## Obsidian Integration
- Vault場所: `obsidian/Ichioka Obsidian/`
- 新構造 (2026-02-03):
  - `00_System/` - レジストリ、テンプレート、設定
  - `03_Projects/_Active/` - アクティブプロジェクト
  - `03_Projects/_Old/` - 完了・休止プロジェクト
  - `10_People/` - 人物情報
  - `11_Companies/` - 企業情報

## Active Projects (Top 5)
1. **AirCle** - いちさんが代表の大学生AI団体
   - チーム5名（いち、大山、さきくん、りょうせい、れある）
   - 自動化システム実装済み（請求書管理）
   - 構成: 議事録、運営チーム、イベント運営
   - 2/16: 806ファイル復元完了
   - 2/17: 人物・企業プロフィール6人+2社作成
2. **ClimbBeyond** - ポート株式会社、就活系プロジェクト
   - 最新: ずぼらくんプロフィール作成（2/15）
3. **SlideBox** - スライド関連プロジェクト
4. **ClientWork** - 外部案件（他社X投稿、マーケティング支援）
5. **Genspark** - 協業案件
   - 最新: ちぃたんゲーム、流行り音源×映像完了（2/15）

## Old Projects
- VideoPocket → Gensparkへ移行 (2026-02-03)

## プロジェクト整理履歴
- 2026-02-16: 月曜日メモリ自動整理実施
  - 04_Project/AirCle → 03_Projects/_Active/AirCle へ統合
  - 全プロジェクトにREADME.md、STATUS.md作成
  - プロジェクト構造の可視化（INDEX.md, STRUCTURE.md）
  - 議事録フォルダのテンプレート追加
  - **AirCle 806ファイル復元完了**（削除されていたファイルを復活）
- 2026-02-17: 火曜日メモリ自動整理実施
  - 人物プロフィール3件作成（大山竜輝、折井英人、大前綾香）
  - 企業プロフィール2件作成（ポート株式会社、Genspark）
  - INDEX.md、ORGANIZATION.md作成
  - Codex CLI導入、モデル設定修正

## Cron Jobs
- context-curator-daily-brief: 毎日7:00 JST - Context Curatorブリーフ (Telegram)
- context-curator-hourly-pulse: 毎時30分 - 軽量スキャン
- morning-task-report: 毎日6:00 JST - 深夜セッション報告 (Discord)
- morning-x-post-selection: 毎日7:00 JST - X投稿作成 (Discord)
- nightly-dev-session: 毎日1:00 JST - 深夜開発セッション
- git-auto-sync: 毎時 - Git自動同期
- daily-efficiency-suggestions: 毎日12:00 JST - 効率化提案

## Skills構造 (2026-02-22)
```
skills/
├── browser-skills/     - ブラウザ操作スキル
│   └── youtube-live-scheduler/
├── slides-generator/   - スライド自動生成
└── invoice-generator/  - 請求書自動生成→PDF→Drive
```

## Tools (2026-03-09 更新)
```
tools/
├── weekly_report_generator.py  - 週次レポート自動生成（NEW 3/9）
├── x_post_freshness_checker.py - 投稿ネタ鮮度チェック（NEW 3/9）
├── daily_memory_digest.py     - メモリダイジェスト自動生成（3/6）
├── x_post_diversity_checker.py - 投稿多様性・重複チェック（3/6）
├── content_calendar.py        - コンテンツカレンダー管理（3/5）
├── engagement_optimizer.py    - エンゲージメント最適化（3/5）
├── post_performance_predictor.py - 投稿パフォーマンス予測（3/4）
├── trend_tracker.py           - トレンド追跡・ネタ鮮度管理（3/4）
├── news_digest_generator.py   - ニュースダイジェスト生成（3/3）
├── session_progress.py        - セッション進捗トラッキング（3/3）
├── post_dedup_checker.py      - 投稿重複チェック（3/3）
├── session_tracker.py         - 深夜セッション進捗トラッカー（3/1）
├── x_post_validator.py        - X投稿バリデーター（3/1）
├── x_post_quality_checker.py  - X投稿品質スコアリング
├── memory_organizer.py        - メモリ整理分析ツール
├── x_scheduler.py             - X投稿スケジューラー
├── viral_analyzer.py          - バイラル度分析
├── past_tweets_analysis.py    - 過去投稿分析
├── x_analysis_report.py       - 詳細レポート生成
├── morning_brief.py           - モーニングブリーフィング
├── workspace_health.py        - ヘルスチェック
├── efficiency_suggestions.py  - 効率化提案
├── daily_summary.py           - デイリーサマリー
├── project_status.py          - プロジェクト状況
├── session_analysis.py        - セッション分析
├── md_to_html.py              - MD→HTML変換
├── project_dashboard.py       - プロジェクトダッシュボード
├── session_reporter.py        - セッションレポーター
├── x_export.py                - X投稿エクスポート
├── x_pattern_analysis.py      - 投稿パターン分析
├── x_posts_generator.py       - 投稿生成ツール
└── x_quality_scorer.py        - 品質スコアラー
```

## External Integrations (TODO)
- Slack: AirCle｜大学生AI団体 (未接続)
- Google: Gmail/Calendar/Drive (Connected via gog skill)

## 経費管理システム (2026-02-05 追加)
- **経費スプレッドシート**: https://docs.google.com/spreadsheets/d/1NLiR89wGRWoFDppU1PpYzdk4YMIrMsjIfLbsdhKMe2s/edit
- **収入スプレッドシート**: https://docs.google.com/spreadsheets/d/1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990/edit
- **Driveフォルダ**: https://drive.google.com/drive/folders/1oLO6kGT31AV780TzymtC6puZ9vM8xqMH
- 毎日23:00に `expense_append.py` で自動追記
- 収入判定: 「お支払いがありました」= Stripe入金、案件受注
- **領収書メールは返信不要**（2026-02-16 追加）

## Pi Voice (2026-02-05 追加)
- URL: https://pi-voice.vercel.app
- 音声対話アシスタント（ブラウザTTS）
- 12時の自動化提案はTelegramに変更

## Tools (2026-02-04 追加)
Pythonワークフローツール `tools/`:
- x_scheduler.py - X投稿スケジューラー
- workspace_health.py - ヘルスチェック
- viral_analyzer.py - バイラル度分析
- past_tweets_analysis.py - 過去投稿分析
- x_analysis_report.py - 詳細レポート生成
- morning_brief.py - モーニングブリーフィング

## @ichiaimarketer 投稿テーマ (2026-02-06 追加)
1. **個人開発成功事例** - Pieter Levels、Danny Postma、Marc Louなど（TypingMind型の戦略分析）
2. **デザイン系AIツールの最新ニュース** - Figma、Canva、Claude連携などのリリース・アップデート
3. **X運用、UI/UXトレンド** - アルゴリズム攻略、投稿時間帯、デザイントレンド

## X投稿 毎朝自律送信ルール (2026-02-06 更新)
**毎朝6:00ジャストにDiscord #aircleへ自分から送信する（聞かれる前に）**

1. 最新ニュースをweb_searchで検索
2. **過去のバズ投稿の型**でHTMLページ生成 → Vercelデプロイ
3. **6:00ジャスト**にDiscordでリンク送信（遅れ厳禁）

### バズる型（必ず使う）
1. 速報型「【速報】〜が〜を公開」
2. 海外バズ型「【海外で大バズ】【海外で話題】」
3. 結論型「【結論から言います】」
4. 公式型「【公式が答えを出してしまった】」
5. 正直型「正直、〜」で始める
6. 配布型「〇〇欲しい人いますか？」

### 絵文字ルール
- ✅ 使っていい：🔥👇😳（控えめに）
- ❌ 禁止：📱📅🔗📰🚨などの情報的な絵文字

### 構成ルール
- 「これ、何を意味するか👇」で箇条書きに繋げる
- 最後に「〜すべき」「〜の時代」で締める
- 番号リスト（①②③）は多用しない

### HTMLフォーマット要件
- 参考URLへのリンク付き
- 日本語訳（ソース概要）
- 投稿文（**長め**に書く）
- コピーボタン付き
- ダークUI

### 投稿数
- AirCle用 (@aircle_ai): 20投稿

### 送信先
- Discord #aircle (1468094860987863060)

### 重要な注意点
- Markdownファイルで送らない（HTML必須）
- 自分から送る（聞かれてからでは遅い）
- 最新ニュースを必ず検索してから作成
- 過去のバズ投稿の型を絶対に守る

## X投稿分析結果 (2026-02-04)
820件の過去投稿を分析:
- 結論型: 平均306.7いいね（最強）
- 速報型: 平均173.2いいね
- 配布型: 平均35.1RT
- 最適時間: 16:00, 0:00, 8:00

## AirCle運営チーム (2026-02-03)
- いち（代表）
- 大山（マーケ担当）
- さきくん
- りょうせい（動画編集・サムネ）
- れある（X運用・2/27〜）

## 会議招待・カレンダー連携ルール (2026-02-07 追加)
**会議招待・日程調整メールが届いたら:**
1. **確認不要でGoogleカレンダーに即時追加**する（勝手に追加してOK）。
2. 追加後、「〇〇の予定をカレンダーに追加しといたよ」と事後報告する。
3. **絶対厳守**。

## 議事録 → TODO作成ルール (2026-02-05 追加)
MTG文字起こしから議事録を作成したら:
1. **いちさんの立場を理解**した上でTODOを整理（いちさんがやるべきことだけ抽出）
2. 「このTODOでいい？良ければGoogleのTODOに連携して追加しとこうか？」と聞く
3. 「おけ」と言われたらGoogle TODOに追加
4. **時間かけてもいいから品質優先**
5. **締め切りを必ず聞く**：「いつまでに終わらせる？」と確認してから期限を設定
6. **「次回ミーティングまで」と言われたら**：Googleカレンダーから該当プロジェクトの次回定例を探して、**ミーティング開始時間**を期限に設定
7. **期限は必ず1時間単位で設定**（例: 12:00, 20:00）

### 次回予定の汎用検索 (2026-02-05 追加)
「次回の〇〇まで」と言われたら:
1. Googleカレンダーから「〇〇」に該当する予定を検索
2. 見つかったらその開始時間を期限に設定
3. 見つからなければ「カレンダーに〇〇が見つからないけど、いつ？」と確認

### 議事録から予定追加 (2026-02-05 追加)
議事録の中で次回ミーティングや予定が決まったら:
1. 「この予定をGoogleカレンダーに追加していい？」と確認
2. 「おけ」と言われたらカレンダーに追加
3. 追加内容: 日時、タイトル、参加者（わかれば）

### タスクリストのルーティング
- **AirCle関連** → Aircleリスト
- **ClimbBeyond関連**（ポート株式会社、就活系）→ ClimbBeyondリスト
- **外部案件**（他社とのX投稿、マーケティング支援）→ 外部案件リスト
- **その他** → マイタスク

### タスクリマインダー (2026-02-05 追加)
期限付きタスクで完了していないものをリマインド:
- **3日前**
- **1日前**
- **12時間前**
チェック時間: 9:00, 12:00, 18:00, 21:00 JST
**デフォルト期限時間: 20:00**（具体的な時間指定がなければ）

### 期限超えタスク通知 (2026-02-05 追加)
- **毎日15:00**に期限超えタスクをうざめに通知
- 超過日数に応じて煽り度UP（1日→😤、3日→😡、それ以上→💀）
