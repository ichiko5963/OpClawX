# Viral Post Automation 🚀

> **X/Twitter投稿データ → 15型分析 → 毎朝URLで投稿案が届く** 全自動システム
> 
> **Upload your X/Twitter data → 15-pattern analysis → Get daily post suggestions via URL**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![Node](https://img.shields.io/badge/Node-%3E%3D14-brightgreen)](https://nodejs.org)
[![Languages](https://img.shields.io/badge/Languages-EN%20%7C%20JP%20%7C%20CN%20%7C%20KR%20%7C%20ES-orange)](./i18n)

**[English](#english)** | [日本語](#日本語) | [中文](#中文)

---

<a id="english"></a>
## 🇺🇸 English

### What does this do?

1. **📊 Analyze** — Feed it your past X/Twitter CSV data
2. **🧠 Learn** — It identifies which of the 15 viral patterns worked best for *you*
3. **✨ Generate** — Produces daily post suggestions tailored to your top patterns
4. **🔗 Deliver** — Sends a URL every morning (Discord/Slack/email/webhook)

**No code required. Works with OpenClaw or as a standalone CLI.**

### Quick Start

```bash
# 1. Clone
git clone https://github.com/ichiko5963/OpClawX.git && cd OpClawX

# 2. Install
npm install

# 3. Analyze your data
node cli.js analyze ./your-posts.csv --lang en

# 4. Generate today's post
node cli.js generate --pattern 04-conclusion-first --topic "AI tools" --lang en

# 5. Set up daily automation
node cli.js schedule --time "07:00" --webhook https://your-webhook-url --topic "AI News"
```

#### Using OpenClaw
```bash
openclaw skills install .
openclaw run viral-post-automation --analyze ./posts.csv
openclaw run viral-post-automation --generate --topic "AI News"
```

### The 15 Viral Patterns

| # | Pattern | Psychology | Avg. Boost |
|---|---------|-----------|------------|
| 01 | Breaking News | FOMO — "I must see this NOW" | +180% RT |
| 02 | Save for Later | Utility — "I'll need this someday" | +250% 🔖 |
| 03 | Global Trend | Social proof — "The world is watching" | +140% reach |
| 04 | Conclusion First | Instant gratification | +200% ❤️ |
| 05 | Honest Opinion | Trust — "Finally, the truth" | +160% comments |
| 06 | VS Battle | Decision anxiety — "Just tell me which one" | +150% replies |
| 07 | First Impression | Curiosity — "Does it really work?" | +130% clicks |
| 08 | By The Numbers | Credibility — "Show me the data" | +170% saves |
| 09 | Insight | Exclusivity — "I didn't know that" | +155% shares |
| 10 | Free Resource | Loss aversion — "Don't miss out" | +300% follows |
| 11 | Pro Tips | Superiority — "Be ahead of others" | +140% saves |
| 12 | Warning | Fear of loss — "I need to act now" | +190% RT |
| 13 | Storytelling | Empathy — "That's me" | +120% comments |
| 14 | Complete Guide | Efficiency — "One and done" | +200% 🔖 |
| 15 | Future Forecast | Uncertainty — "What should I prepare for?" | +145% saves |

### Data Format (CSV)

```csv
text,likes,retweets,replies,date
"Your post text here",150,45,12,"2026-03-01"
"Another post",89,30,8,"2026-03-02"
```

---

<a id="日本語"></a>
## 🇯🇵 日本語

### これは何をするシステム？

1. **📊 分析** — 過去のX/TwitterデータCSVを渡す
2. **🧠 学習** — 15のバズ型の中で自分のデータに最も効いた型を特定
3. **✨ 生成** — 毎日、あなたに最適化されたバズ投稿案を生成
4. **🔗 配信** — 毎朝URLをDiscord/Slack/メール/Webhookで送信

**コード不要。OpenClawスキルとしても、スタンドアロンCLIとしても動作。**

### クイックスタート

```bash
# 1. クローン
git clone https://github.com/ichiko5963/OpClawX.git && cd OpClawX

# 2. インストール
npm install

# 3. データを分析
node cli.js analyze ./your-posts.csv --lang ja

# 4. 今日の投稿を生成
node cli.js generate --pattern 04-conclusion-first --topic "AI最新情報" --lang ja

# 5. 毎日自動化を設定
node cli.js schedule --time "07:00" --webhook https://your-webhook-url --topic "AIニュース" --lang ja
```

#### OpenClawで使う場合
```bash
openclaw skills install .
openclaw run viral-post-automation --analyze ./posts.csv --lang ja
openclaw run viral-post-automation --generate --topic "AIニュース" --lang ja
```

### 15のバズ型

| # | 型名 | 心理メカニズム | 平均効果 |
|---|------|-------------|---------|
| 01 | 速報型 | FOMO「今すぐ見なければ」 | RT +180% |
| 02 | 保存版型 | 実用性「いつか使う」 | 🔖 +250% |
| 03 | 海外バズ型 | 社会的証明「世界が注目」 | リーチ +140% |
| 04 | 結論型 | 即時満足「結論が知りたい」 | ❤️ +200% |
| 05 | 正直型 | 信頼「本音が聞きたい」 | コメント +160% |
| 06 | 比較型 | 決断不安「どっちか教えて」 | リプライ +150% |
| 07 | 体験記型 | 好奇心「本当に使えるの？」 | クリック +130% |
| 08 | 数字強調型 | 信頼性「データで見せて」 | 保存 +170% |
| 09 | 洞察型 | 優越感「知らなかった」 | シェア +155% |
| 10 | 配布型 | 損失回避「逃したくない」 | フォロー +300% |
| 11 | 裏技型 | 優越感「他より先に知る」 | 保存 +140% |
| 12 | 警告型 | 損失恐怖「今すぐ対処を」 | RT +190% |
| 13 | ストーリー型 | 共感「それ自分だ」 | コメント +120% |
| 14 | 完全解説型 | 効率性「これ一本でOK」 | 🔖 +200% |
| 15 | 予測型 | 不安「何を準備すべき？」 | 保存 +145% |

### データ形式（CSV）

```csv
text,likes,retweets,replies,date
"投稿テキスト",150,45,12,"2026-03-01"
"別の投稿",89,30,8,"2026-03-02"
```

Numbersファイル（.numbers）をお持ちの場合は、
「ファイル → 書き出す → CSV」でエクスポートしてください。

---

<a id="中文"></a>
## 🇨🇳 中文

### 这个系统做什么？

1. **📊 分析** — 上传过去的 X/Twitter CSV 数据
2. **🧠 学习** — 识别15种病毒式模式中最适合您数据的模式
3. **✨ 生成** — 每天生成针对您优化的病毒式帖子建议
4. **🔗 交付** — 每天早上通过 Discord/Slack/邮件/Webhook 发送 URL

```bash
git clone https://github.com/ichiko5963/OpClawX.git && cd OpClawX
npm install
node cli.js analyze ./your-posts.csv --lang cn
node cli.js generate --pattern 04-conclusion-first --topic "AI新闻" --lang cn
node cli.js schedule --time "07:00" --webhook https://your-webhook --topic "AI新闻" --lang cn
```

---

## 📚 Documentation

- [Installation Guide](./docs/INSTALL.md)
- [Usage Guide](./docs/USAGE.md)
- [Pattern Details](./docs/PATTERNS.md)
- [API Reference](./docs/API.md)
- [Contributing](./CONTRIBUTING.md)

## 🤝 Contributing

PRs welcome in any language! See [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📄 License

MIT — free for personal and commercial use.

## ✨ Made by

[AirCle](https://x.com/AiAircle34052) — Japan's student AI community
