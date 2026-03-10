# AirCle X投稿自動化システム

X（Twitter）運用を自動化する包括的システムです。

## 🚀 デモ

[![Vercel](https://img.shields.io/badge/Vercel-Deployed-black?logo=vercel)](https://your-vercel-url.vercel.app)

## ✨ 機能

### 1. 保存投稿ベースの投稿案生成
- Xで「保存」した投稿を自動取得
- AirCleバズ型（結論型・速報型・配布型等）を参考に新しい投稿案を生成
- 毎日朝7時自動実行（GitHub Actions）

### 2. キーワード監視システム
- 注目キーワード（Claude Code, Cursor, Vercel等）の24時間以内の投稿を監視
- いいね500以上の投稿を対象に投稿案生成
- 毎日20時自動実行（GitHub Actions）

### 3. アカウント監視（リアルタイム）
- 15分ごとに監視アカウントをチェック
- 新規投稿を検出しDiscord #daily-xに通知
- 日本語訳＋バズる型に変換して送信

## 👀 監視アカウント

- [@cursor_ai](https://x.com/cursor_ai)
- [@vercel](https://x.com/vercel)
- [@antigravity](https://x.com/antigravity)
- [@AnthropicAI](https://x.com/AnthropicAI)
- [@geminicli](https://x.com/geminicli)
- [@OpenAI](https://x.com/OpenAI)

## 🛠️ 技術スタック

- **フレームワーク**: Next.js 14 + React 18
- **言語**: TypeScript
- **スタイリング**: Tailwind CSS
- **デプロイ**: Vercel
- **自動化**: GitHub Actions
- **API**: X API v2 (twitter-api-v2)

## 📦 セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/aircle-x-automation.git
cd aircle-x-automation
```

### 2. 依存関係のインストール

```bash
npm install
# または
yarn install
```

### 3. 環境変数の設定

```bash
cp .env.example .env.local
```

`.env.local` に以下を設定:

```env
# X API Credentials (必須)
# https://developer.twitter.com/en/portal/dashboard で取得
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_SECRET=your_access_secret
X_BEARER_TOKEN=your_bearer_token

# Discord Webhook URL（監視通知用・オプション）
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# OpenAI API Key（オプション・高度な生成用）
OPENAI_API_KEY=your_openai_key

# Vercel URL（GitHub Actions用）
VERCEL_URL=https://your-project.vercel.app
```

### X APIの設定手順

1. [X Developer Portal](https://developer.twitter.com/en/portal/dashboard) にアクセス
2. 新しいProjectとAppを作成
3. **User authentication settings** で以下を有効化:
   - OAuth 2.0
   - OAuth 1.0a
4. **Permissions** を設定:
   - Read (ブックマーク読み取りに必須)
   - Write (投稿に必要)
5. **Keys and Tokens** タブで API Key, Secret, Access Token を取得

### 4. 開発サーバーの起動

```bash
npm run dev
```

http://localhost:3000 でアクセス可能

## 🚀 デプロイ

### Vercelへのデプロイ

1. [Vercel Dashboard](https://vercel.com) にアクセス
2. 「Add New Project」→ GitHubリポジトリを選択
3. フレームワークプリセット: Next.js
4. **Environment Variables** セクションで必要な変数を設定
5. Deploy

### GitHub Secretsの設定

1. リポジトリの **Settings** → **Secrets and variables** → **Actions** を開く
2. 以下のSecretsを追加:
   - `X_API_KEY`
   - `X_API_SECRET`
   - `X_ACCESS_TOKEN`
   - `X_ACCESS_SECRET`
   - `X_BEARER_TOKEN`
   - `DISCORD_WEBHOOK_URL` (任意)
   - `VERCEL_URL` (デプロイ後のURL)

## 📅 自動化スケジュール

| タスク | スケジュール | 説明 |
|--------|-----------|------|
| 保存投稿生成 | 毎日 7:00 JST | ブックマークから60件の投稿案生成 |
| キーワード生成 | 毎日 20:00 JST | 監視キーワードから投稿案生成 |
| アカウント監視 | 15分ごと | 新規投稿検出・Discord通知 |

## 📱 使い方

### ダッシュボード

URL: `/`

- 投稿案の一覧表示（ステータス別フィルタリング）
- 検索・ソート機能
- グリッド/リスト表示切り替え
- ページネーション

### 投稿案の生成

URL: `/generator`

1. 「ブックマーク」または「キーワード」を選択
2. 「投稿案を生成」ボタンをクリック
3. 生成された投稿案を確認、保存
4. ダッシュボードで管理

### 投稿の流れ

1. **自動**: Xで興味のある投稿を「保存」
2. **自動**: 毎朝7時に投稿案が生成される
3. **手動**: ダッシュボードで内容を確認・編集
4. **手動**: 「Xで投稿」ボタンでXの投稿画面を開く
5. **手動**: 内容を確認して投稿

### Discord通知

アカウント監視で新規投稿を検出時、`#daily-x` チャンネルに通知:

- 監視アカウント名
- 日本語訳された投稿内容
- 適用されたバズ型
- 「投稿する」「スキップ」「コピー」ボタン

## 🎨 バズる型（テンプレート）

| 型名 | 平均いいね | 特徴 |
|------|-----------|------|
| 結論型 | 306.7 | 結論から始める。最もバズりやすい |
| 速報型 | 173.2 | ニュース速報スタイル |
| 配布型 | 85.3 | RT率が高い（平均35.1RT）|
| 正直型 | 127.5 | 親近感が出せる |
| 海外バズ型 | 142.8 | トレンド感がある |
| 公式型 | 98.4 | 信頼性が高い |

## 📁 プロジェクト構造

```
aircle-x-automation/
├── .github/workflows/          # GitHub Actions設定
│   ├── daily-generation.yml    # 日次投稿案生成
│   └── monitor-accounts.yml    # アカウント監視
├── scripts/
│   └── monitor-accounts.js     # 監視スクリプト
├── public/
│   └── data/
│       └── drafts.json         # 生成された投稿案
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── api/
│   │   │   ├── generate-drafts/  # 投稿案生成API
│   │   │   ├── post-to-x/        # 投稿API
│   │   │   └── discord/          # Discord通知API
│   │   ├── generator/          # 生成ページ
│   │   ├── layout.tsx
│   │   ├── page.tsx            # ダッシュボード
│   │   └── globals.css
│   ├── components/             # Reactコンポーネント
│   │   ├── DraftCard.tsx       # 投稿案カード
│   │   ├── DraftList.tsx       # 投稿案一覧
│   │   ├── PostButton.tsx      # 投稿ボタン
│   │   └── MediaPreview.tsx    # メディアプレビュー
│   ├── lib/                    # ユーティリティ
│   │   ├── x-api.ts            # X API連携
│   │   ├── templates.ts        # テンプレート定義
│   │   ├── storage.ts          # ローカルストレージ操作
│   │   └── monitor.ts          # 監視機能
│   └── types/                  # TypeScript型定義
│       └── index.ts
├── .env.example
├── next.config.ts
├── tailwind.config.ts
├── package.json
└── README.md
```

## ⚠️ 重要な制約

1. **X APIブックマーク**: OAuth 2.0が必要。Basicプラン以上が推奨
2. **下書き投稿**: X APIの一般エンドポイントでは下書き作成ができません。投稿文をコピーしてXで手動投稿してください
3. **動画URL**: X動画のURLは `/video/1` 形式に正規化され、投稿文の先頭に配置されます
4. **レートリミット**: X APIの15分あたりのリクエスト制限に注意

## 🔧 カスタマイズ

### 監視キーワードの変更

`src/app/api/generate-drafts/route.ts` の `MONITORED_KEYWORDS` を編集:

```typescript
const MONITORED_KEYWORDS = [
  'Claude Code', 'Cursor', 'Vercel',
  // 追加のキーワード
  'YourKeyword',
];
```

### 監視アカウントの変更

`scripts/monitor-accounts.js` の `MONITORED_ACCOUNTS` を編集:

```javascript
const MONITORED_ACCOUNTS = [
  { username: 'cursor_ai', displayName: 'Cursor' },
  // 追加のアカウント
  { username: 'new_account', displayName: 'New Account' },
];
```

### テンプレートのカスタマイズ

`src/lib/templates.ts` で既存の型を編集または新規追加:

```typescript
export const TEMPLATES: Record<TemplateType, PostTemplate> = {
  // 既存のテンプレート...
  myCustom: {
    id: 'myCustom',
    name: 'カスタム型',
    pattern: '【カスタム】{content}\n\n{details}',
    avgLikes: 200,
    avgRetweets: 30,
    description: '独自の構成',
    isActive: true,
  },
};
```

## 🔍 API エンドポイント

### POST `/api/generate-drafts`

投稿案を生成します。

```json
{
  "type": "bookmarks",  // "bookmarks" または "keywords"
  "limit": 10,          // 生成数（デフォルト: 60）
  "minLikes": 500       // 最小いいね数（キーワード検索時）
}
```

レスポンス:
```json
{
  "success": true,
  "count": 10,
  "total": 150,
  "drafts": [...]
}
```

### POST `/api/post-to-x`

投稿を準備/実行します。

```json
{
  "draftId": "draft_xxx",
  "content": "投稿内容",
  "action": "prepare"  // "prepare", "post", "schedule"
}
```

## 📝 ライセンス

MIT License

## 🤝 貢献

IssueやPRを歓迎します。

---

Made with ⚡ by AirCle
