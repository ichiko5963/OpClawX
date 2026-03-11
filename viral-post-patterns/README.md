# Viral Post Patterns 🚀 / バズる投稿15型

**English** | [日本語](#日本語)

> Generate viral social media posts using proven 15 patterns / 検証済み15の型でバイラル投稿を生成

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)

---

## 🇺🇸 English

### Overview

Open-source library that systematizes **15 viral post patterns** derived from analyzing thousands of high-engagement social media posts.

**Concept**: "Viral posts have patterns" / 「バズる投稿には型がある」

### 🎯 15 Viral Patterns

| ID | Pattern | Best For | Key Hook |
|---|---|---|---|
| 01 | [Breaking News](./patterns/01-breaking-news.md) | New releases | "Finally here!" |
| 02 | [Save for Later](./patterns/02-save-for-later.md) | Tutorials | "Bookmark this" |
| 03 | [Global Trend](./patterns/03-global-trend.md) | Overseas trends | "Trending worldwide" |
| 04 | [Conclusion First](./patterns/04-conclusion-first.md) | Analysis | "Conclusion: ..." |
| 05 | [Honest Opinion](./patterns/05-honest-opinion.md) | Reviews | "Honestly..." |
| 06 | [VS Battle](./patterns/06-vs-battle.md) | Comparisons | "A vs B" |
| 07 | [First Impression](./patterns/07-first-impression.md) | Reviews | "I tried..." |
| 08 | [By The Numbers](./patterns/08-by-numbers.md) | Reports | "XX% improvement" |
| 09 | [Insight](./patterns/09-insight.md) | Analysis | "The truth is..." |
| 10 | [Free Resource](./patterns/10-freebie.md) | Giveaways | "Want this?" |
| 11 | [Pro Tips](./patterns/11-pro-tips.md) | Hacks | "Secret trick" |
| 12 | [Warning](./patterns/12-warning.md) | Alerts | "Watch out" |
| 13 | [Storytelling](./patterns/13-storytelling.md) | Experiences | "From zero to..." |
| 14 | [Complete Guide](./patterns/14-complete-guide.md) | Tutorials | "Ultimate guide" |
| 15 | [Future Forecast](./patterns/15-future-forecast.md) | Predictions | "In X years..." |

### 🚀 Quick Start

#### Option 1: OpenClaw Skill (Recommended)

```bash
# Install as OpenClaw skill
openclaw skills install ./openclaw-integration

# Generate a post
openclaw run viral-post-patterns --pattern 01-breaking-news --theme "AI new feature"

# Interactive mode
openclaw run viral-post-patterns --interactive
```

#### Option 2: CLI Tool

```bash
# Install globally
npm install -g viral-post-patterns

# Generate
viral-post generate -p 01-breaking-news -t "AI new feature"

# List patterns
viral-post list

# Suggest pattern
viral-post suggest -t "product comparison"
```

#### Option 3: Node.js Module

```javascript
const { generatePost, suggestPattern } = require('viral-post-patterns');

// Generate post
const result = generatePost('01-breaking-news', 'ChatGPT Update', 'x-twitter');
console.log(result.prompt);

// Get pattern suggestion
const pattern = suggestPattern('comparison');
console.log(pattern.name); // "VS Battle"
```

### 📋 Pattern Structure

Each pattern includes:
- **Definition** - Psychological mechanism
- **Structure** - Hook → Body → CTA
- **Prompt Template** - Copy-paste ready
- **Examples** - Real viral posts
- **Platform Settings** - Length limits, emoji counts

---

## 🇯🇵 日本語

### 概要

数千の高エンゲージメントSNS投稿を分析して抽出した**15のバズ投稿型**を体系化したオープンソースライブラリ。

**コンセプト**: 「バズる投稿には型がある」

### 🎯 15のバズ型

| ID | 型名 | 向いている内容 | フック |
|---|---|---|---|
| 01 | [速報型](./patterns/01-breaking-news.md) | 新製品発表 | 「ついに登場！」 |
| 02 | [保存版型](./patterns/02-save-for-later.md) | チュートリアル | 「保存版」 |
| 03 | [海外バズ型](./patterns/03-global-trend.md) | 海外トレンド | 「海外で話題」 |
| 04 | [結論型](./patterns/04-conclusion-first.md) | 分析・考察 | 「結論：...」 |
| 05 | [正直型](./patterns/05-honest-opinion.md) | レビュー | 「正直...」 |
| 06 | [比較型](./patterns/06-vs-battle.md) | 製品比較 | 「○○ vs △△」 |
| 07 | [体験記型](./patterns/07-first-impression.md) | レビュー | 「使ってみた」 |
| 08 | [数字強調型](./patterns/08-by-numbers.md) | 成果報告 | 「○○%向上」 |
| 09 | [批判・論評型](./patterns/09-insight.md) | 分析 | 「実は...」 |
| 10 | [リソース配布型](./patterns/10-freebie.md) | 無料配布 | 「欲しい人いますか？」 |
| 11 | [裏技・Tips型](./patterns/11-pro-tips.md) | 裏技 | 「知ってると差がつく」 |
| 12 | [警告・アラート型](./patterns/12-warning.md) | 注意喚起 | 「注意が必要」 |
| 13 | [ストーリー型](./patterns/13-storytelling.md) | 体験談 | 「○○だった私が」 |
| 14 | [完全解説型](./patterns/14-complete-guide.md) | 解説 | 「これだけ読めばOK」 |
| 15 | [予測・展望型](./patterns/15-future-forecast.md) | 予測 | 「○○年後には」 |

### 🚀 クイックスタート

#### 方法1: OpenClawスキル（推奨）

```bash
# OpenClawスキルとしてインストール
openclaw skills install ./openclaw-integration

# 投稿を生成
openclaw run viral-post-patterns --pattern 01-breaking-news --theme "AI新機能"

# 対話式モード
openclaw run viral-post-patterns --interactive
```

#### 方法2: CLIツール

```bash
# グローバルインストール
npm install -g viral-post-patterns

# 生成
viral-post generate -p 01-breaking-news -t "AI新機能"

# 一覧表示
viral-post list

# パターン推奨
viral-post suggest -t "製品比較"
```

#### 方法3: Node.jsモジュール

```javascript
const { generatePost, suggestPattern } = require('viral-post-patterns');

// 投稿生成
const result = generatePost('01-breaking-news', 'ChatGPTアップデート', 'x-twitter');
console.log(result.prompt);

// パターン推奨
const pattern = suggestPattern('比較');
console.log(pattern.name); // "比較型"
```

### 📋 パターンの構造

各パターンには以下が含まれます：
- **定義** - バズる心理メカニズム
- **構造** - 書き出し → 本文 → 締め
- **プロンプトテンプレート** - コピペで使用可能
- **例文** - 実際のバズ投稿
- **プラットフォーム設定** - 文字数制限、絵文字数

---

## 📚 Documentation / ドキュメント

- [Usage Guide](./docs/USAGE.md) - Detailed usage instructions
- [Contributing](./CONTRIBUTING.md) - How to contribute
- [Pattern Analysis](./docs/ANALYSIS.md) - Methodology

## 🤝 Contributing / コントリビューション

Pull requests welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md)

プルリクエスト歓迎！[CONTRIBUTING.md](./CONTRIBUTING.md)をご覧ください。

## 📄 License / ライセンス

MIT License - See [LICENSE](./LICENSE)

## 🙏 Credits / クレジット

Created by [AirCle](https://x.com/AiAircle34052) / いち@Aircle代表

Repository: [OpClawX](https://github.com/ichiko5963/OpClawX)
