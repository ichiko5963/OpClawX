# OpClawX 🚀

<p align="center">
  <img src="./assets/logo.png" alt="OpClawX Logo" width="400">
</p>

<p align="center">
  <strong>毎朝7時、15のバズ型 × 最新トレンド = あなたの投稿案15個がURLで届く</strong><br>
  <strong>Every morning: 15 viral patterns × latest trends = 15 post ideas delivered via URL</strong><br>
  <strong>每天早上：15种爆款模式 × 最新趋势 = 15个帖子创意URL送达</strong>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://nodejs.org"><img src="https://img.shields.io/badge/Node-%3E%3D16-brightgreen.svg" alt="Node.js"></a>
  <img src="https://img.shields.io/badge/Languages-5-orange.svg" alt="5 Languages">
  <img src="https://img.shields.io/badge/Patterns-15%2B-blue.svg" alt="15+ Patterns">
</p>

---

## 📱 What You Get Every Morning

```
🌅 7:00 AM — Your Daily 15 Viral Posts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

① 【速報型】Breaking News     → Claude最新アップデート
② 【保存版型】Save for Later   → AIツール完全まとめ📌  
③ 【海外バズ型】Global Trend  → ChatGPT海外の反応🌎
④ 【結論型】Conclusion First  → AIはこう使うと効果的
⑤ 【正直型】Honest Opinion   → 本音で言うと...
⑥ 【比較型】VS Battle        → GPT-4 vs Claude⚔️
⑦ 【体験記型】First Impression→ 使ってみたレビュー
⑧ 【数字強調型】By Numbers   → 驚きのデータ3選📊
⑨ 【洞察型】Insight          → 実はみんな勘違いしてる
⑩ 【配布型】Free Resource    → 無料テンプレート🎁
⑪ 【裏技型】Pro Tips        → 知ってると差がつく💎
⑫ 【警告型】Warning          → ⚠️ これやめた方がいい
⑬ 【ストーリー型】Storytelling→ 3年前の私は...
⑭ 【完全解説型】Complete Guide→ 徹底解説📚
⑮ 【予測型】Future Forecast  → 3年後、こうなる...

🔗 https://your-domain.com/daily.html
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**One URL. 15 viral post ideas. Ready to copy-paste into ChatGPT/Claude.**

---

## 🇯🇵 日本語

### これは何？

**OpClawX**は、毎朝15個のバズる投稿案を自動生成し、URLで届けるシステムです。

X Premiumの分析データや過去の投稿データを学習し、**あなたのフォロワーが実際に反応するパターン**を特定。最新のAIニュースを踏まえて、15のバズ型で投稿案を生成します。

### 🚀 クイックスタート

```bash
# 1. インストール
git clone https://github.com/ichiko5963/OpClawX.git
cd OpClawX
npm install

# 2. 環境変数設定
cp .env.example .env
# .envを編集

# 3. X Premiumデータを分析
node cli.js analyze ./x-premium-export.csv

# 4. テスト実行（15投稿生成）
node scheduler/daily-15.js --lang ja

# 5. Cron設定（毎日自動実行）
crontab -e
# 追加: 0 7 * * * cd /path/to/OpClawX && node scheduler/daily-15.js --lang ja
```

### 📁 対応データ形式

| 形式 | 説明 | コマンド |
|-----|------|---------|
| **CSV** | X Premiumエクスポート | `analyze ./data.csv` |
| **Numbers** | Mac Numbersファイル (.numbers) | `analyze ./data.numbers` |
| **JSON** | カスタムJSON形式 | `analyze ./data.json` |

---

## 🇺🇸 English

### What is OpClawX?

**OpClawX** automatically generates 15 viral post ideas every morning and delivers them via URL.

It learns from your X Premium analytics and past posts to identify **which patterns actually work for YOUR audience**.

### 🚀 Quick Start

```bash
git clone https://github.com/ichiko5963/OpClawX.git
cd OpClawX
npm install
cp .env.example .env

# Analyze your X Premium data
node cli.js analyze ./x-premium-export.csv

# Generate daily 15 posts
node scheduler/daily-15.js --lang en

# Setup daily cron
crontab -e
# Add: 0 7 * * * cd /path/to/OpClawX && node scheduler/daily-15.js --lang en
```

---

## 🇨🇳 中文 — 专为中国市场优化

### 小红书 · 微博 · 抖音风格适配

```bash
# 小红书种草风格
node scheduler/daily-15.js --lang cn --topics "种草,测评,必入,yyds"
```

---

## 📦 Installation

### Requirements
- Node.js >= 16
- macOS/Linux/Windows

```bash
git clone https://github.com/ichiko5963/OpClawX.git
cd OpClawX
npm install
cp .env.example .env
```

---

## 📊 X Premium Analytics

Export your data from X Premium:
1. X Premium → Analytics → Export Data
2. Save as CSV (includes impressions, engagements, bookmarks)
3. Run: `node cli.js analyze ./export.csv`

---

## 📄 License

MIT — free for personal and commercial use.
