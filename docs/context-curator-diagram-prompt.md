# Context Curator システム図解プロンプト

## 画像生成プロンプト（ナノバナナ / Midjourney用）

---

### 日本語版

```
16:9のシステムアーキテクチャ図を作成してください。

【全体構成】
左から右へのデータフローを示す、モダンでクリーンなテック系インフォグラフィック。
背景は深いダークブルー(#0a1628)、アクセントカラーは電気ブルー(#00d4ff)とパープル(#8b5cf6)。
各要素は角丸の白/半透明カードで表現。接続線は発光するネオンライン。

【左側: データソース】(5つの入力)
1. Gmail - 赤いエンベロープアイコン、Googleの「M」ロゴスタイル
2. Google Calendar - 青/緑/黄/赤の4色カレンダーアイコン
3. Google Tasks - 青いチェックマーク付きリストアイコン
4. Slack - 4色のハッシュタグ風ロゴ(#E01E5A, #36C5F0, #2EB67D, #ECB22E)
5. Telegram - 紙飛行機アイコン(水色)

【中央上: 自動化エンジン】
n8nのロゴ風(オレンジ/コーラル色の「n8n」テキスト)
「Hourly Sync Workflow」のラベル
矢印で全データソースから集約

【中央: OpenClaw / Pi 処理】
大きな六角形のハブ、中央に「🤖 Pi」
周囲に6つの処理モジュール(小さな六角形):
- 📥 Ingest (データ取込)
- 🏷️ Routing (振り分け)
- 🔒 Sensitivity (機密判定)
- 📊 Analysis (分析)
- ✅ Approval (承認)
- 📝 Digest (要約)

【中央下: Obsidian Vault】
紫色の宝石アイコン(Obsidianロゴ風)
フォルダ構造を示す:
- 00_System (設定・状態・ログ)
- 03_Projects (プロジェクト)
- 07-To Do (タスク)
- 10_People (人物)
- 11_Companies (企業)

【右側: 出力・通知】
3つの出力チャンネル:
1. Telegram (紙飛行機) → 「朝7時ブリーフィング」「毎時レポート」
2. Discord (ゲームコントローラー風ロゴ) → 「開発レポート」
3. Google Tasks (逆方向矢印) → 「タスク追加」

【下部: スケジュールタイムライン】
24時間の時計風タイムライン:
- 1:00 🌙 深夜開発セッション
- 6:00 📋 朝タスクレポート  
- 7:00 ☀️ 朝ブリーフィング
- 毎時30分 ⏰ 統合レポート
- 23:00 📊 日次ダイジェスト

【右上: 統計カード】
小さなダッシュボード風:
- 「228件/日 収集」
- 「P0: 0 / P1: 16」
- 「5件 Google Tasks」

スタイル: フラットデザイン、テック系、SaaS風ダッシュボード、グラデーション発光、ミニマルアイコン
```

---

### English Version (for Midjourney)

```
Create a 16:9 system architecture diagram.

STYLE: Modern tech infographic, dark blue background (#0a1628), electric blue (#00d4ff) and purple (#8b5cf6) accents, rounded white/translucent cards, glowing neon connection lines, flat design, SaaS dashboard aesthetic, minimal icons with gradient glow.

LEFT SIDE - DATA SOURCES (5 inputs in vertical stack):
1. Gmail icon - red envelope with Google "M" style logo
2. Google Calendar icon - blue/green/yellow/red 4-color calendar
3. Google Tasks icon - blue checklist with checkmark
4. Slack icon - 4-color hashtag logo (#E01E5A, #36C5F0, #2EB67D, #ECB22E)
5. Telegram icon - light blue paper plane

CENTER TOP - AUTOMATION ENGINE:
n8n logo style (orange/coral "n8n" text)
Label: "Hourly Sync Workflow"
Arrows converging from all data sources

CENTER - MAIN PROCESSING HUB:
Large hexagon hub with "🤖 Pi" in center
6 smaller hexagon modules around it:
- 📥 Ingest
- 🏷️ Routing  
- 🔒 Sensitivity
- 📊 Analysis
- ✅ Approval
- 📝 Digest

CENTER BOTTOM - STORAGE:
Purple gem icon (Obsidian logo style)
Folder tree showing:
- 00_System (Config/State/Logs)
- 03_Projects
- 07-To Do
- 10_People
- 11_Companies

RIGHT SIDE - OUTPUTS (3 channels):
1. Telegram (paper plane) → "7AM Briefing" "Hourly Report"
2. Discord (game controller style logo) → "Dev Reports"
3. Google Tasks (reverse arrow) → "Add Tasks"

BOTTOM - SCHEDULE TIMELINE:
24-hour clock style timeline showing:
- 1:00 🌙 Nightly Dev Session
- 6:00 📋 Morning Task Report
- 7:00 ☀️ Morning Briefing
- Every :30 ⏰ Hourly Report
- 23:00 📊 Daily Digest

TOP RIGHT - STATS CARD:
Small dashboard showing:
- "228/day collected"
- "P0: 0 / P1: 16"
- "5 Google Tasks"

--ar 16:9 --v 6
```

---

## 文字数

- 日本語版: 約1,200文字
- 英語版: 約1,100文字

---

## 含まれる全要素

### データソース (5)
- [x] Gmail
- [x] Google Calendar
- [x] Google Tasks
- [x] Slack
- [x] Telegram (入力として)

### 処理 (6)
- [x] n8n ワークフロー
- [x] データ取込 (Ingest)
- [x] ルーティング (Routing)
- [x] 機密判定 (Sensitivity)
- [x] 分析 (Analysis)
- [x] 承認フロー (Approval)
- [x] ダイジェスト生成 (Digest)

### ストレージ (5)
- [x] 00_System
- [x] 03_Projects
- [x] 07-To Do
- [x] 10_People
- [x] 11_Companies

### 出力 (3)
- [x] Telegram通知
- [x] Discord通知
- [x] Google Tasks追加

### スケジュール (5)
- [x] 1:00 深夜開発
- [x] 6:00 朝レポート
- [x] 7:00 ブリーフィング
- [x] 毎時30分 統合レポート
- [x] 23:00 日次ダイジェスト

### 統計 (3)
- [x] 日次収集件数
- [x] P0/P1カウント
- [x] Google Tasksカウント
