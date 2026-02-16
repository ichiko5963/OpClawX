# Mission Control ダッシュボード - 要件定義

## 概要
OpenClaw用のMission Controlダッシュボード。AIアシスタントが行った全行動の記録、スケジュール管理、グローバル検索を提供。

## 技術スタック
- **フレームワーク**: Next.js (App Router)
- **データベース**: Convex
- **スタイリング**: Tailwind CSS (ダークテーマ)
- **言語**: TypeScript

## 参考デザイン
添付画像の3カラムレイアウト:
- 左: ナビゲーションサイドバー (Tasks, Content, Memory, Docs, People等)
- 中央: メインコンテンツエリア (日付ごとのリスト表示)
- 右: 詳細パネル (選択したアイテムの内容表示)

## 機能要件

### 1. アクティビティフィード
**目的**: AIアシスタントが実行した全ての行動と完了したタスクを記録・表示

**データ構造**:
```typescript
interface Activity {
  id: string;
  timestamp: number; // Unix timestamp
  type: 'task_completed' | 'file_created' | 'file_modified' | 'cron_executed' | 'email_sent' | 'calendar_event_added' | 'search_performed' | 'other';
  title: string;
  description: string;
  metadata?: {
    filePath?: string;
    taskId?: string;
    cronJobId?: string;
    [key: string]: any;
  };
}
```

**表示機能**:
- 日付ごとにグループ化
- タイムラインビュー
- フィルター機能 (タイプ別、日付範囲)
- 詳細表示 (クリックで右パネルに詳細)
- 無限スクロール / ページネーション

**データ取得**:
- Convexから履歴データを取得
- リアルタイム更新 (新しいアクティビティが追加されたら自動反映)

### 2. カレンダービュー (週表示)
**目的**: 未来のスケジュール済みタスクを週単位で視覚的に表示

**データソース**:
- Googleカレンダー連携
- OpenClaw cronジョブ
- Google TODOリスト

**表示機能**:
- 週表示カレンダー (月曜〜日曜)
- 時間軸付きグリッド (0:00-23:59)
- イベント/タスクをカード形式で表示
- 色分け (タイプ別: ミーティング、TODO、cronジョブ等)
- 今日のハイライト
- 週の切り替え (前週/次週ボタン)
- クリックで詳細表示

**データ構造**:
```typescript
interface ScheduledTask {
  id: string;
  title: string;
  startTime: number; // Unix timestamp
  endTime?: number;
  type: 'meeting' | 'todo' | 'cron' | 'reminder';
  description?: string;
  location?: string;
  participants?: string[];
  metadata?: {
    calendarId?: string;
    taskListId?: string;
    cronJobId?: string;
    [key: string]: any;
  };
}
```

### 3. グローバル検索
**目的**: ワークスペース内のあらゆる情報を横断的に検索

**検索対象**:
- MEMORY.md + memory/*.md
- Obsidian Vault全体
- アクティビティ履歴
- TODOリスト
- カレンダーイベント
- プロジェクトファイル

**検索機能**:
- フルテキスト検索
- ファジー検索
- 検索結果のハイライト
- タイプ別フィルター (メモリ、ドキュメント、タスク、イベント)
- 日付範囲フィルター
- 関連性スコアによるソート

**検索結果表示**:
```typescript
interface SearchResult {
  id: string;
  type: 'memory' | 'document' | 'task' | 'event' | 'activity';
  title: string;
  snippet: string; // 検索キーワード周辺のテキスト
  path?: string; // ファイルパス
  score: number; // 関連性スコア
  timestamp?: number;
  metadata?: any;
}
```

**UI**:
- 検索バー (グローバルヘッダー内)
- 検索結果パネル (モーダルまたは専用ページ)
- クリックで該当箇所にジャンプ

## レイアウト構成

### ナビゲーション (左サイドバー)
- Dashboard (ホーム)
- **Activity Feed** ⭐ NEW
- **Calendar** ⭐ NEW
- Tasks (既存のTODO管理)
- Memory (MEMORY.md表示)
- Docs (ドキュメント一覧)
- People (人物情報)
- Companies (企業情報)
- Projects (プロジェクト一覧)

### グローバルヘッダー
- **検索バー** ⭐ NEW (Cmd+K / Ctrl+K でフォーカス)
- ユーザーアイコン
- 設定メニュー

### メインエリア
- 選択したページのコンテンツ
- 3カラムレイアウト (Activity Feed, Calendar時)
- 2カラムレイアウト (その他のページ)

## データベーススキーマ (Convex)

### activities テーブル
```typescript
{
  _id: Id<"activities">,
  _creationTime: number,
  timestamp: number,
  type: string,
  title: string,
  description: string,
  metadata: any,
}
```

### scheduled_tasks テーブル
```typescript
{
  _id: Id<"scheduled_tasks">,
  _creationTime: number,
  title: string,
  startTime: number,
  endTime: number | null,
  type: string,
  description: string | null,
  location: string | null,
  participants: string[] | null,
  metadata: any,
  completed: boolean,
}
```

### search_index テーブル (検索インデックス用)
```typescript
{
  _id: Id<"search_index">,
  _creationTime: number,
  type: string,
  title: string,
  content: string,
  path: string | null,
  timestamp: number,
  metadata: any,
}
```

## API連携

### 必要な外部API
1. **Google Calendar API** - イベント取得
2. **Google Tasks API** - TODOリスト取得
3. **OpenClaw Internal API** - cronジョブ情報、メモリ検索

### データ同期
- 定期的なポーリング (5分ごと)
- Webhook対応 (可能な場合)
- リアルタイム更新 (Convex Subscriptions)

## セキュリティ
- 認証: OpenClaw Gatewayトークン
- アクセス制御: ローカルホストのみ (または特定IPのみ)
- データ暗号化: Convex標準機能

## パフォーマンス最適化
- 仮想スクロール (大量のアクティビティ表示時)
- ページネーション (検索結果)
- インデックス作成 (timestamp, type等)
- キャッシュ戦略 (React Query / SWR)

## デプロイ
- Vercel (Next.jsアプリ)
- Convex (データベース・バックエンド)
- 環境変数: Google API credentials, OpenClaw Gateway URL等

## フェーズ1: MVP
1. プロジェクト初期化 (Next.js + Convex)
2. 基本レイアウト (3カラム、ナビゲーション)
3. アクティビティフィード (静的データ)
4. カレンダービュー (静的データ)
5. グローバル検索 (ローカルデータ)

## フェーズ2: データ連携
1. Convexスキーマ定義
2. アクティビティ記録システム (OpenClaw側)
3. Google API連携
4. リアルタイム更新

## フェーズ3: 拡張機能
1. フィルター・ソート機能拡張
2. エクスポート機能 (CSV, JSON)
3. 統計ダッシュボード (週間/月間サマリー)
4. 通知機能
