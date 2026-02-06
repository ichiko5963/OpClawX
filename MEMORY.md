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

## Obsidian Integration
- Vault場所: `obsidian/Ichioka Obsidian/`
- 新構造 (2026-02-03):
  - `00_System/` - レジストリ、テンプレート、設定
  - `03_Projects/_Active/` - アクティブプロジェクト
  - `03_Projects/_Old/` - 完了・休止プロジェクト
  - `10_People/` - 人物情報
  - `11_Companies/` - 企業情報

## Active Projects (Top 5)
1. AirCle - いちさんが代表の大学生AI団体
2. ClimbBeyond
3. SlideBox
4. ClientWork - 外部案件
5. Genspark - 協業案件

## Old Projects
- VideoPocket → Gensparkへ移行 (2026-02-03)

## Cron Jobs
- context-curator-daily-brief: 毎日7:00 JST - Context Curatorブリーフ (Telegram)
- context-curator-hourly-pulse: 毎時30分 - 軽量スキャン
- morning-task-report: 毎日6:00 JST - 深夜セッション報告 (Discord)
- morning-x-post-selection: 毎日7:00 JST - X投稿作成 (Discord)
- nightly-dev-session: 毎日1:00 JST - 深夜開発セッション
- git-auto-sync: 毎時 - Git自動同期
- daily-efficiency-suggestions: 毎日12:00 JST - 効率化提案

## External Integrations (TODO)
- Slack: AirCle｜大学生AI団体 (未接続)
- Google: Gmail/Calendar/Drive (未接続)
- 接続方法: MCP or n8n or Zapier で検討中

## 経費管理システム (2026-02-05 追加)
- **経費スプレッドシート**: https://docs.google.com/spreadsheets/d/1NLiR89wGRWoFDppU1PpYzdk4YMIrMsjIfLbsdhKMe2s/edit
- **収入スプレッドシート**: https://docs.google.com/spreadsheets/d/1R6dEPRTHfjnCXu1VWMh0lwfea0OqMTYjhzIVL_NA990/edit
- **Driveフォルダ**: https://drive.google.com/drive/folders/1oLO6kGT31AV780TzymtC6puZ9vM8xqMH
- 毎日23:00に `expense_append.py` で自動追記
- 収入判定: 「お支払いがありました」= Stripe入金、案件受注

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
