# Usage Guide / 使用ガイド

**English** | [日本語](#japanese-guide)

---

## 🇺🇸 English Guide

### Table of Contents
1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Pattern Reference](#pattern-reference)
4. [Advanced Usage](#advanced-usage)
5. [Platform-Specific Tips](#platform-specific-tips)
6. [Troubleshooting](#troubleshooting)

### Installation

#### Option 1: Clone Repository

```bash
git clone https://github.com/ichiko5963/OpClawX.git
cd OpClawX/viral-post-patterns
npm install
```

#### Option 2: NPM Install (when published)

```bash
npm install -g viral-post-patterns
```

### Basic Usage

#### 1. Generate a Post

```bash
# Using OpenClaw
openclaw run viral-post-patterns --pattern 01-breaking-news --theme "AI Revolution"

# Using CLI
viral-post generate -p 01-breaking-news -t "AI Revolution"
```

#### 2. List All Patterns

```bash
viral-post list
```

Output:
```
01. Breaking News       - "Finally here!" announcements
02. Save for Later      - Bookmark-worthy content
03. Global Trend        - Overseas buzz introduction
...
```

#### 3. Get Pattern Suggestion

```bash
viral-post suggest -t "comparing two products"
# Output: Suggested: 06-vs-battle (VS Battle)
```

### Pattern Reference

#### 01 - Breaking News
**When to use**: New product launches, feature announcements

**Example**:
```
【速報】ChatGPT新機能がついにリリース🔥
・画像生成が無料化
・日本語精度が向上
・API応答速度2倍に
これはgame changer。詳細は👇
```

**Prompt Template**:
```
Generate a breaking news style post about {theme}:
- Start with 【速報】
- Include "ついに" and "登場"
- 3 bullet points of key features
- End with 🔥 and 👇
```

#### 04 - Conclusion First
**When to use**: Analysis, reviews, opinions

**Example**:
```
【結論】AIツールはもう選ばなくていい💡
理由は3つ👇
・統合が進んでいる
・差別化が難しくなった
・コストが問題にならない
今は「使いこなす」時代。詳細は👇
```

### Advanced Usage

#### Using as Node.js Module

```javascript
const { generatePost, suggestPattern, loadPatterns } = require('viral-post-patterns');

// Generate with custom settings
const post = generatePost('04-conclusion-first', 'Remote Work', 'linkedin');

// Get all patterns
const allPatterns = loadPatterns();

// Find best pattern
const bestPattern = suggestPattern('tutorial');
```

#### Custom Configuration

Create `config.json`:
```json
{
  "platform": "x-twitter",
  "language": "ja",
  "max_length": 280,
  "emoji_limit": 3,
  "tone": "professional"
}
```

### Platform-Specific Tips

#### X (Twitter)
- Max 280 characters
- Use 🔥👇 only (avoid 📱📅🔗📰🚨)
- No numbered lists (①②③)
- End with strong CTA

#### Instagram
- Up to 2,200 characters
- More emojis allowed
- Use line breaks generously
- Include hashtags

#### LinkedIn
- Up to 3,000 characters
- Professional tone
- Use data and insights
- Encourage comments

### Troubleshooting

**Error: Pattern not found**
- Check pattern ID with `viral-post list`
- Use full ID like `01-breaking-news`

**Error: Theme required**
- Always provide `--theme` or `-t` parameter

---

## 🇯🇵 Japanese Guide

### 目次
1. [インストール](#インストール)
2. [基本的な使い方](#基本的な使い方)
3. [パターンリファレンス](#パターンリファレンス)
4. [高度な使い方](#高度な使い方)
5. [プラットフォーム別Tips](#プラットフォーム別tips)
6. [トラブルシューティング](#トラブルシューティング)

### インストール

#### 方法1: リポジトリをクローン

```bash
git clone https://github.com/ichiko5963/OpClawX.git
cd OpClawX/viral-post-patterns
npm install
```

#### 方法2: NPMインストール（公開後）

```bash
npm install -g viral-post-patterns
```

### 基本的な使い方

#### 1. 投稿を生成

```bash
# OpenClawを使用
openclaw run viral-post-patterns --pattern 01-breaking-news --theme "AI革命"

# CLIを使用
viral-post generate -p 01-breaking-news -t "AI革命"
```

#### 2. パターン一覧

```bash
viral-post list
```

出力例:
```
01. 速報型       - 「ついに登場」アナウンス
02. 保存版型     - ブックマークしたくなる内容
03. 海外バズ型   - 海外トレンド紹介
...
```

#### 3. パターン推奨

```bash
viral-post suggest -t "製品比較"
# 出力: 推奨: 06-vs-battle (比較型)
```

### パターンリファレンス

#### 01 - 速報型
**使うタイミング**: 新製品発表、機能アナウンス

**例文**:
```
【速報】ChatGPT新機能がついにリリース🔥
・画像生成が無料化
・日本語精度が向上
・API応答速度2倍に
これはgame changer。詳細は👇
```

**プロンプトテンプレート**:
```
{theme}について速報型の投稿を作成:
- 【速報】から始める
- 「ついに」「登場」を含める
- 核心ポイントを3つ箇条書き
- 🔥と👇で締める
```

#### 04 - 結論型
**使うタイミング**: 分析、レビュー、意見表明

**例文**:
```
【結論】AIツールはもう選ばなくていい💡
理由は3つ👇
・統合が進んでいる
・差別化が難しくなった
・コストが問題にならない
今は「使いこなす」時代。詳細は👇
```

### 高度な使い方

#### Node.jsモジュールとして使用

```javascript
const { generatePost, suggestPattern, loadPatterns } = require('viral-post-patterns');

// カスタム設定で生成
const post = generatePost('04-conclusion-first', 'リモートワーク', 'linkedin');

// 全パターン取得
const allPatterns = loadPatterns();

// 最適パターン提案
const bestPattern = suggestPattern('チュートリアル');
```

#### カスタム設定

`config.json`を作成:
```json
{
  "platform": "x-twitter",
  "language": "ja",
  "max_length": 280,
  "emoji_limit": 3,
  "tone": "professional"
}
```

### プラットフォーム別Tips

#### X (Twitter)
- 最大280文字
- 絵文字は🔥👇のみ（📱📅🔗📰🚨は禁止）
- 番号リスト（①②③）は使わない
- 強いCTAで締める

#### Instagram
- 最大2,200文字
- 絵文字を多めにOK
- 改行を積極的に使用
- ハッシュタグを含める

#### LinkedIn
- 最大3,000文字
- プロフェッショナルなトーン
- データと洞察を含める
- コメントを促す

#### note
- 最大10,000文字
- 長文OK
- 画像・埋め込み活用
- ストーリー重視

### トラブルシューティング

**エラー: Pattern not found**
- `viral-post list`で正しいIDを確認
- `01-breaking-news` のようにフルIDを使用

**エラー: Theme required**
- `--theme` または `-t` パラメータを必ず指定

**絵文字が多すぎる警告**
- 各プラットフォームの絵文字制限を確認
- Xは3つまで、Instagramは10個まで

---

## 📚 Additional Resources / 追加リソース

- [Pattern JSON Schema](./docs/schema.md)
- [API Reference](./docs/api.md)
- [Examples Gallery](./examples/)

## 💬 Support / サポート

- GitHub Issues: [Report bugs or request features](https://github.com/ichiko5963/OpClawX/issues)
- Discussions: [Ask questions](https://github.com/ichiko5963/OpClawX/discussions)
- X/Twitter: [@AiAircle34052](https://x.com/AiAircle34052)
