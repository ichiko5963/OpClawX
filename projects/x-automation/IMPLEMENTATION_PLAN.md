# AirCle X自動化プロジェクト - 実装計画書

## プロジェクト概要

### 1. 每日X投稿自动生成网站
- **目标**: 毎日約60件の投稿案を自动生成
- **参考**: 過去のバズった投稿の型（结论型、速報型、リスト型等）
- **配置**: Vercelに每日朝自动デプロイ
- **機能**:
  - 投稿一覧をウェブサイトで表示
  - 「投稿する」ボタンでXに投稿（下書き保存）
  - 画像、视频を自动取得・添付
  - 動画の場合はURL+/video/1を冒頭に入力

### 2. 每日趋势监控 (20:00)
- **监控关键词**: ClaudeCode, Opus, Antigravity, GeminiCLI, Codex, Cursor, vercel, supabase, Next.js, react, Vibe Coding, OpenClaw
- **条件**: 1000いいね以上、24時間以内
- **网站化**: ウェブサイトで一覧表示
- **投稿機能**: ウェブサイトから直接投稿可能
- **動画处理**: URL+/video/1を冒头に追加

### 3. 特定アカウント監視 (15分间隔)
- **監視対象**: @openclaw @cursor_ai @vercel @antigravity @AnthropicAI @geminicli @OpenAI
- **通知先**: Discord #daily-x チャンネル
- **自动翻译**: 日本語に翻訳
- **投稿确认**: 「これ投稿しとこうか？」と确认

---

## 実装ステータス

### Phase 1: 基盤 ✅
- [x] X API Client (`backend/x_api_client.py`)
- [x] Post Generator (`backend/post_generator.py`)
- [x] Next.js Frontend skeleton

### Phase 2: 自动化 (進行中)
- [ ] Cron: 每日6:00 - 投稿生成
- [ ] Cron: 每日20:00 - トレンド監視
- [ ] Cron: 15分間隔 - アカウント監視

### Phase 3: Webサイト (未開始)
- [ ] Vercelデプロイ
- [ ] X投稿機能実装

---

## 必要なもの

1. **X API credentials** - developer.twitter.com で取得
2. **Vercel アカウント** - デプロイ用
3. **Discord Webhook** - 通知用

---

## 次のステップ

1. X APIの認証情報を設定
2. Vercelにデプロイ
3. Cron Jobを設定

---

## バズの型（参考）

| 型 | 平均いいね |
|---|---|
| 結論型 | 306.7 |
| 速報型 | 173.2 |
| リスト型 | 153.3 |
| Vibe Coding | 146.9 |
| 配布型 | 78.5 |

---

## 動画引用规则

```
元のURL: https://x.com/user/status/123456789
投稿文冒头: https://x.com/user/status/123456789/video/1

改行
投稿文...
```
