# Chat Organ AI 実装メモ

## 実装アーティファクトの所在

- Next.js (App Router) ベースの UI/UX・API 実装は **`/Users/ichiokanaoto/Downloads/Ichioka Obsidian/09-開発/2_実装/Chat Organ AI`** に集約されています。  
- AI/Minutes/Automation のモックデータと API Routes は `Chat Organ AI/lib/server/mock-db.ts` および `Chat Organ AI/app/api/**` に配置済みです。

※ 以降すべてのコード・設定・ドキュメントは `2_実装/Chat Organ AI` 配下に保管し、このフォルダを基準に手順やコマンドを記述してください。

## ローカル起動方法

```
cd "/Users/ichiokanaoto/Downloads/Ichioka Obsidian/09-開発/2_実装/Chat Organ AI"
npm install
npm run dev
```

ブラウザで http://localhost:3000 を開くと、自動的に `/chat` へリダイレクトし Chat Organ AI のワークスペース UI が表示されます。

## 主要画面とパス

- `/chat`: スレッド／タスク提案／Temporalリマインドをまとめたメインチャット。  
- `/minutes`: Minutes Agent UI（議事録リスト + アップロードフォーム）。  
- `/tasks`: 部署横断タスク（ガント／かんばん相当のカラム表示）。  
- `/knowledge`: RAG検索・根拠表示。  
- `/automations`: GUIルールビルダー。  
- `/analytics`: 参加率・反応・未回答スレのアナリティクス。  
- `/admin`: 部署メンションとインテグレーション管理。  
- `/settings`: SSO/RBAC/監査ログ設定。

## API キーが必要な箇所

- GitHub Actions ディスパッチ API (`/api/integrations/github/actions/[workflow]/dispatch`) を本番相当で動かすには `.env.local` に `GITHUB_TOKEN=<workflow権限を持つPersonal Access Token>` を設定してください。トークン未設定の場合は API レスポンスが明示的にエラーと対応方法を返します。
