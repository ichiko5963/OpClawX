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

## Tools (2026-02-04 追加)
Pythonワークフローツール `tools/`:
- x_scheduler.py - X投稿スケジューラー
- workspace_health.py - ヘルスチェック
- viral_analyzer.py - バイラル度分析
- past_tweets_analysis.py - 過去投稿分析
- x_analysis_report.py - 詳細レポート生成
- morning_brief.py - モーニングブリーフィング

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
