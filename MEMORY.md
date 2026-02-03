# Long-term Memory

## Principles
- 重要な決定 / 目的 / 連絡先 / 進行中タスクはここに残す

## User Preferences
- いちさん / 市岡直人 (AirCle代表)
- 長いタスクは「やるね」→「できたよ」で報告する
- 中学生にもわかるように説明する
- 品質優先、時間をかけてもいい

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
