# OpClawX 🚀 — Viral Post Automation for OpenClaw

> **X/Twitterデータ → AI分析 → 毎朝URLで届くバズ投稿案**  
> **X/Twitter Data → AI Analysis → Daily Viral Post Suggestions via URL**  
> **X/Twitter数据 → AI分析 → 每日病毒式帖子建议直达URL**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![Node](https://img.shields.io/badge/Node-%3E%3D14-brightgreen)](https://nodejs.org)
[![Languages](https://img.shields.io/badge/Languages-EN%20%7C%20JP%20%7C%20CN%20%7C%20KR%20%7C%20ES-orange)](./i18n)

**🇺🇸 English** | **🇯🇵 日本語** | **🇨🇳 中文** | **🇰🇷 한국어** | **🇪🇸 Español**

---

## 🎯 For OpenClaw Users

```bash
# Install as OpenClaw skill
openclaw skills install https://github.com/ichiko5963/OpClawX.git

# Analyze your X Premium export
openclaw run OpClawX --analyze ./x-premium-analytics.csv --lang ja

# Generate today's viral post
openclaw run OpClawX --generate --topic "AI最新情報" --pattern auto

# Set up daily morning delivery to Discord
openclaw run OpClawX --schedule --time 07:00 --webhook https://discord.com/api/webhooks/...
```

---

<a id="english"></a>
## 🇺🇸 English

### Why This Exists

Every viral post follows psychological patterns. This system **learns YOUR audience's response patterns** from your X Premium analytics (or any CSV export) and generates daily post suggestions that match what actually works for *your* followers.

### The Flow

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  X Premium CSV  │────▶│ Pattern AI   │────▶│  Generator  │────▶│  Discord/    │
│  or Past Posts  │     │  Analysis    │     │  (15 types) │     │  Slack URL   │
└─────────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
       ↓
   Custom patterns
   (your knowledge)
```

### Quick Start

```bash
git clone https://github.com/ichiko5963/OpClawX.git && cd OpClawX
npm install

# 1. Analyze your data (supports X Premium analytics export)
node cli.js analyze ./x-premium-data.csv --lang en

# 2. Generate post with best pattern auto-selected
node cli.js generate --topic "AI tools changing everything" --lang en

# 3. Daily automation
node cli.js schedule --time "07:00" --webhook https://hooks.slack.com/...
```

### X Premium Analytics Support

Export your X Premium analytics:
1. X Premium → Analytics → Export Data
2. Save as CSV (posts with impressions, engagements, etc.)
3. Feed directly into OpClawX

The system reads: `text`, `impressions`, `engagements`, `likes`, `retweets`, `replies`, `bookmarks`

### Customizable Patterns (Your Knowledge Matters!)

**The 15 built-in patterns are just a starting point.** Create your own:

```bash
# Edit config/patterns.json
cp config/patterns.example.json config/patterns.json
```

```json
{
  "my-pattern-id": {
    "name": { "en": "My Custom Type", "ja": "自分の型" },
    "indicators": ["🔥","独家"],
    "keywords": { "en": ["exclusive","breaking"], "cn": ["独家","首发"] },
    "structure": "Hook → Twist → CTA",
    "weight": 2.0
  }
}
```

Your custom patterns work alongside (or replace) the defaults.

---

<a id="日本語"></a>
## 🇯🇵 日本語

### なぜ作ったか

バズる投稿には必ず心理パターンがある。このシステムは**あなたのXプレミアム分析データ（または過去投稿CSV）から、あなたのフォロワーが実際に反応するパターンを学習**し、毎日それに最適化された投稿案を生成する。

### OpenClaw連携（推奨）

```bash
# OpenClawスキルとしてインストール
openclaw skills install https://github.com/ichiko5963/OpClawX.git

# Xプレミアムの分析データを読み込み
openclaw run OpClawX --analyze ~/Downloads/x-premium-analytics.csv --lang ja

# 毎朝7時にDiscordへ自動配信
openclaw run OpClawX --schedule --time 07:00 --webhook https://discord.com/api/webhooks/...
```

### Xプレミアム分析対応

Xプレミアムの分析データを直接読み込み：
1. X Premium → アナリティクス → データエクスポート
2. CSVで保存（インプレッション、エンゲージメント含む）
3. OpClawXにそのまま渡す

読み込むカラム：`text`, `impressions`, `engagements`, `likes`, `retweets`, `replies`, `bookmarks`

### カスタマイズ可能なパターン（あなたのナレッジが重要！）

**15の組み込みパターンは出発点に過ぎない。** 自分だけの型を追加：

```bash
# 設定ファイルをコピー
cp config/patterns.example.json config/patterns.json
```

```json
{
  "my-hype-pattern": {
    "name": { "en": "Hype Drop", "ja": "ドロップ型" },
    "indicators": ["🔥","先行","Exclusive"],
    "keywords": { "ja": ["先行","限定","ゲリラ"], "en": ["exclusive","drop"] },
    "structure": "【先行】Product\n・Point 1\n・Point 2\n入手方法👇",
    "weight": 2.5
  }
}
```

自分の業界・知識に合わせたパターンを自由に追加可能。

---

<a id="中文"></a>
## 🇨🇳 中文 — 专为中文社交媒体优化

### 为什么要用这个？

每个爆款帖子都遵循心理学模式。这个系统**从你的X Premium分析数据（或任何CSV导出）中学习你的受众实际反应的模式**，然后生成每天适合你粉丝的内容建议。

### 中国市场特别优化

- ✅ **小红书/微博/抖音风格适配** — 支持中文爆款标题结构
- ✅ **中文关键词识别** — "独家"、"首发"、"绝了"、"必看"
- ✅ **简体/繁体支持** — 自动检测并适配
- ✅ **中国时区默认** — 早上7点 = 北京时间

### OpenClaw一键安装

```bash
# 安装为OpenClaw技能
openclaw skills install https://github.com/ichiko5963/OpClawX.git

# 分析你的X Premium数据
openclaw run OpClawX --analyze ./x-premium-data.csv --lang cn

# 生成今日爆款文案
openclaw run OpClawX --generate --topic "AI最新进展" --pattern auto --lang cn
```

### X Premium分析支持

导出你的X Premium分析数据：
1. X Premium → Analytics → Export Data
2. 保存为CSV（包含曝光量、互动等）
3. 直接导入OpClawX

系统读取：`text`, `impressions`, `engagements`, `likes`, `retweets`, `replies`, `bookmarks`

### 可自定义模式（你的行业知识很重要！）

**15个内置模式只是起点。** 创建你自己的：

```bash
# 复制配置模板
cp config/patterns.example.json config/patterns.json
```

```json
{
  "xiaohongshu-style": {
    "name": { "cn": "小红书种草型", "en": "Xiaohongshu Style" },
    "indicators": ["绝了","必看","🔥"],
    "keywords": { "cn": ["种草","必入","测评","真心推荐"] },
    "structure": "【绝了】Topic\n・Point 1\n・Point 2\n・Point 3\n冲！👇",
    "weight": 2.2
  }
}
```

根据你的行业、受众、知识自由添加自定义模式。

### 中文社交媒体适配

| 平台 | 适配说明 |
|-----|---------|
| 小红书 | 种草文案结构、表情使用 |
| 微博 | 热搜标题模式 |
| 抖音 | 钩子开头、悬念结尾 |
| X/Twitter | 国际受众优化 |

---

<a id="한국어"></a>
## 🇰🇷 한국어

```bash
git clone https://github.com/ichiko5963/OpClawX.git && cd OpClawX
npm install
node cli.js analyze ./posts.csv --lang ko
node cli.js generate --topic "AI 소식" --pattern auto --lang ko
```

---

<a id="español"></a>
## 🇪🇸 Español

```bash
git clone https://github.com/ichiko5963/OpClawX.git && cd OpClawX
npm install
node cli.js analyze ./posts.csv --lang es
node cli.js generate --topic "Noticias de IA" --pattern auto --lang es
```

---

## 📊 15 Built-in Viral Patterns / 15の組み込みバズ型 / 15个内置爆款模式

| # | Pattern | EN Name | JP Name | CN Name | Psychology |
|---|---------|---------|---------|---------|-----------|
| 01 | Breaking News | 速報型 | 突发新闻 | FOMO |
| 02 | Save for Later | 保存版型 | 收藏版 | Utility |
| 03 | Global Trend | 海外バズ型 | 全球趋势 | Social Proof |
| 04 | Conclusion First | 結論型 | 结论先行 | Instant Gratification |
| 05 | Honest Opinion | 正直型 | 诚实观点 | Trust |
| 06 | VS Battle | 比較型 | 对决 | Decision Support |
| 07 | First Impression | 体験記型 | 第一印象 | Curiosity |
| 08 | By The Numbers | 数字強調型 | 数字强调 | Credibility |
| 09 | Insight | 洞察型 | 洞察 | Exclusivity |
| 10 | Free Resource | 配布型 | 免费资源 | Loss Aversion |
| 11 | Pro Tips | 裏技型 | 专业技巧 | Superiority |
| 12 | Warning | 警告型 | 警告 | Fear |
| 13 | Storytelling | ストーリー型 | 故事 | Empathy |
| 14 | Complete Guide | 完全解説型 | 完整指南 | Efficiency |
| 15 | Future Forecast | 予測型 | 未来预测 | Preparedness |

**→ Add your own in `config/patterns.json`!**

---

## 🔧 Configuration / 設定 / 配置

### Custom Patterns カスタムパターン 自定义模式

```bash
mkdir -p config
cp config/patterns.example.json config/patterns.json
# Edit config/patterns.json with your own patterns
```

### Environment Variables

```bash
export VPA_WEBHOOK_URL="https://discord.com/api/webhooks/..."
export VPA_DEFAULT_LANG="ja"
export VPA_TIMEZONE="Asia/Tokyo"
```

---

## 📁 Repository Structure

```
OpClawX/
├── cli.js                    # Main CLI entry
├── core/
│   ├── analyzer.js           # Pattern detection engine
│   └── generator.js          # Post prompt generator
├── scheduler/
│   └── daily.js              # Daily delivery system
├── i18n/
│   └── index.js              # EN/JP/CN/KR/ES translations
├── config/
│   └── patterns.example.json # Custom pattern template
├── web/
│   └── index.html            # Web dashboard
├── openclaw-integration/     # OpenClaw skill files
├── .github/workflows/        # GitHub Actions automation
└── tests/                    # Test suite
```

---

## 🤝 Contributing / 貢献 / 贡献

PRs welcome in any language!  
どの言語でのPRも歓迎！  
欢迎任何语言的PR！

## 📄 License

MIT — free for personal and commercial use.

## ✨ Made by

[AirCle](https://x.com/AiAircle34052) — Japan's student AI community  
Powered by [OpenClaw](https://openclaw.ai)
