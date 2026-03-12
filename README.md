# OpClawX 🚀 — AI-Powered with OpenClaw Memory

<p align="center">
  <img src="./assets/logo.png" alt="OpClawX Logo" width="400">
</p>

<p align="center">
  <strong>あなたのナレッジ × AI = 毎日3回、バズるX投稿を自動生成</strong><br>
  <strong>Your Knowledge × AI = 3x daily viral X posts, auto-generated</strong><br>
  <strong>你的知识 × AI = 每日3次自动生成爆款X帖子</strong>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://nodejs.org"><img src="https://img.shields.io/badge/Node-%3E%3D16-brightgreen.svg" alt="Node.js"></a>
  <img src="https://img.shields.io/badge/AI-Generated-ff6b6b.svg" alt="AI Generated">
  <img src="https://img.shields.io/badge/Memory-Enabled-success.svg" alt="Memory Enabled">
  <img src="https://img.shields.io/badge/Schedule-3x%20Daily-blue.svg" alt="3x Daily">
</p>

---

## ✨ What Makes OpClawX Different

Unlike other tools that just use templates, **OpClawX learns from YOU**:

```
┌────────────────────────────────────────────────────────────────┐
│  🧠 OpenClaw Memory Layer                                       │
│  ├── Your writing style (tone, phrases, emoji usage)           │
│  ├── Your expertise topics                                      │
│  ├── Your first-hand experiences (体験記・実体験)              │
│  └── Your high-performing post patterns                         │
├────────────────────────────────────────────────────────────────┤
│  📊 X Premium Data (Optional)                                   │
│  ├── Engagement analytics                                       │
│  ├── Best performing content types                              │
│  └── Audience response patterns                                 │
├────────────────────────────────────────────────────────────────┤
│  🤖 AI Generation Layer (Claude/OpenAI)                        │
│  ├── Analyzes your memory profile                               │
│  ├── Incorporates real experiences                              │
│  ├── Generates authentic posts (not AI-sounding)                │
│  └── 15 unique patterns × 3 times daily                         │
└────────────────────────────────────────────────────────────────┘
```

**Result:** Posts that sound like YOU wrote them, based on YOUR actual experiences.

---

## 📱 What You Get (3x Daily)

```
🌅 7:00 AM  — Morning Posts   (朝の投稿案)
🌞 12:00 PM — Lunch Posts     (昼の投稿案)  
🌆 6:00 PM  — Evening Posts   (夕方の投稿案)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

① 【速報型】AIの最新情報をあなたの視点で解説
② 【保存版型】実践的なノウハウをまとめて提供
③ 【海外バズ型】海外トレンドをあなたの分析付きで
④ 【結論型】あなたの経験に基づく結論ファースト
⑤ 【正直型】本音で語る、メモリから抽出したリアルな声
⑥ 【比較型】あなたの検証結果に基づく比較
⑦ 【体験記型】OpenClawメモリから抽出した実体験
⑧ 【数字型】データに基づく分析
⑨ 【洞察型】あなただけの深い洞察
⑩ 【配布型】メモリに蓄積したナレッジの配布
⑪ 【裏技型】実践から生まれた裏技
⑫ 【警告型】経験から学んだ注意点
⑬ 【ストーリー型】あなたの成長ストーリー
⑭ 【完全解説型】メモリに基づく包括ガイド
⑮ 【予測型】あなたの知見に基づく未来予測

🔗 https://your-domain.com/daily.html
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🚀 Quick Start

```bash
# 1. Clone & Install
git clone https://github.com/ichiko5963/OpClawX.git
cd OpClawX
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Set up cron (1日3回自動実行)
crontab -e

# 朝7時 — OpenClawメモリを分析して朝の投稿を生成
0 7 * * * cd /path/to/OpClawX && node scheduler/daily-15.js --lang ja --slot morning

# 昼12時 — 最新ニュースを取り入れて昼の投稿を生成  
0 12 * * * cd /path/to/OpClawX && node scheduler/daily-15.js --lang ja --slot lunch

# 夕方18時 — 1日の振り返りと明日の予告で夕方の投稿を生成
0 18 * * * cd /path/to/OpClawX && node scheduler/daily-15.js --lang ja --slot evening
```

---

## 🔧 Configuration

### Environment Variables

```env
# Required: AI API Keys (どちらか必須)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional: OpenClaw Memory Integration
OPENCLAW_WORKSPACE=/Users/yourname/Documents/OpenClaw-Workspace
VPA_USE_MEMORY=true

# Optional: X Premium Data
XPREMIUM_DATA_PATH=./data/x-premium-export.csv

# Optional: Notifications
VPA_WEBHOOK_URL=https://discord.com/api/webhooks/...
VPA_BASE_URL=https://your-domain.com
```

---

## 🧠 How Memory Integration Works

### 1. Memory Analysis

OpClawX analyzes your OpenClaw memory files to understand:

```javascript
// Example: What the system learns from your memory
const userProfile = {
  writingStyle: {
    tone: ['casual', 'energetic'],      // あなたの口調
    commonPhrases: ['実は', '個人的には'], // よく使う表現
    emojiUsage: ['🔥', '👇', '💡'],      // 絵文字の使い方
    sentenceLength: 'medium'             // 文章の長さ
  },
  topics: ['AI', 'Claude', 'マーケティング', '自動化'], // 専門分野
  experiences: [
    'Claude Codeを3ヶ月使って生産性が2倍になった',
    'AIツール選定で失敗した経験から学んだこと',
    // ... メモリから抽出された実体験
  ]
};
```

### 2. AI-Powered Generation

Claude/OpenAI receives this context:

```
SYSTEM PROMPT:
You are writing X posts for [User Name].

THEIR STYLE:
- Casual but professional Japanese
- Uses 🔥 and 👇 frequently
- Likes to share personal experiences
- Short, punchy sentences

THEIR EXPERTISE:
- AI tools (Claude, ChatGPT)
- Marketing automation
- Productivity hacking

FIRST-HAND EXPERIENCES (use these for authentic content):
1. "Claude Codeを3ヶ月使って生産性が2倍になった"
2. "AIツール選定で失敗した経験..."

Generate a post that sounds like THEY wrote it.
```

### 3. Result

**Before (Template-based):**
```
【速報】Claudeが新機能をリリース！
・ポイント1
・ポイント2
詳細👇
```

**After (Memory + AI):**
```
【速報】Claude Codeがついに正式版に🔥

3ヶ月前からベータ版使ってたけど、
本番環境での安定性が段違い...

個人的には「タブ補完」が地味に便利すぎる

詳細👇
```

*This sounds like it came from YOUR actual experience.*

---

## 📊 X Premium Integration (Optional)

If you have X Premium, export your analytics:

1. X Premium → Analytics → Export Data
2. Save as CSV
3. Set `XPREMIUM_DATA_PATH` in .env

The system will merge X engagement data with memory analysis for even better results.

**Without X Premium:** Works perfectly with just OpenClaw memory

---

## 🛠️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Input Sources                                               │
│  ├── OpenClaw Memory (~/Documents/OpenClaw-Workspace)      │
│  ├── X Premium Data (optional CSV)                          │
│  └── Latest News (RSS/API)                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  Analysis Layer                                              │
│  ├── memory-analyzer.js    → Extract user patterns          │
│  ├── experience-extractor  → Find first-hand stories        │
│  └── style-profiler        → Learn writing characteristics  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  AI Generation Layer                                         │
│  ├── ai-generator.js       → Claude/OpenAI integration      │
│  ├── Context builder       → Memory → AI prompt             │
│  └── 15 pattern variants   → One for each type              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  Output & Delivery                                           │
│  ├── JSON API              → /daily/YYYY-MM-DD-ja.json      │
│  ├── Web UI                → /daily.html                    │
│  └── Webhook               → Discord/Slack                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 CLI Usage

```bash
# Generate with full memory analysis (default)
node scheduler/daily-15.js --lang ja --slot morning

# Generate without memory (template only)
node scheduler/daily-15.js --lang ja --no-memory

# Custom topics
node scheduler/daily-15.js --lang ja --topics "AI,Claude,マーケティング"

# English generation
node scheduler/daily-15.js --lang en --slot lunch
```

---

## 📄 License

MIT — free for personal and commercial use.

---

<p align="center">
  Made with ❤️ using OpenClaw
</p>
