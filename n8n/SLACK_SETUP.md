# Slack App 設定手順

## 概要
AirCle Slack ワークスペースからメッセージを収集するための Bot 設定。

## Step 1: Slack App 作成

1. https://api.slack.com/apps にアクセス
2. 「Create New App」→「From scratch」
3. App Name: `Context Curator`
4. Workspace: `AirCle｜大学生AI団体` を選択

## Step 2: OAuth スコープ設定

左メニュー「OAuth & Permissions」で以下のスコープを追加:

### Bot Token Scopes（必須）
```
channels:history    # 公開チャンネルの履歴
channels:read       # 公開チャンネル一覧
groups:history      # プライベートチャンネルの履歴
groups:read         # プライベートチャンネル一覧
im:history          # DM履歴
im:read             # DM一覧
mpim:history        # グループDM履歴
mpim:read           # グループDM一覧
users:read          # ユーザー情報
users:read.email    # ユーザーメール（オプション）
```

### User Token Scopes（オプション：メンション取得用）
```
search:read         # メッセージ検索
```

## Step 3: Bot をワークスペースにインストール

1. 「OAuth & Permissions」ページ上部の「Install to Workspace」
2. 権限を確認して「許可する」
3. **Bot User OAuth Token** をコピー（`xoxb-` で始まる）

## Step 4: Bot をチャンネルに追加

収集したいチャンネルで:
1. チャンネル設定 → 「インテグレーション」
2. 「アプリを追加する」
3. `Context Curator` を選択

または、チャンネルで `/invite @Context Curator` を実行。

## Step 5: n8n で Credential 作成

1. n8n で「Credentials」→「New」
2. 「Slack OAuth2 API」または「Slack API」を選択
3. Bot Token を入力
4. 接続テスト

## テスト方法

n8n で新規ワークフロー作成:
1. 「Slack」ノードを追加
2. Resource: Channel
3. Operation: Get Many
4. 実行してチャンネル一覧が取れればOK

## 注意事項

### プライベートチャンネル
- Bot が参加していないプライベートチャンネルは取得できない
- 管理者が Bot を招待する必要あり

### レート制限
- Slack API には Tier 制限あり
- 大量取得時は1秒あたりのリクエスト数に注意
- n8n の「Wait」ノードで調整

### Events API（将来拡張）
リアルタイム通知が必要な場合:
1. 「Event Subscriptions」を有効化
2. Request URL に n8n の Webhook URL を設定
3. イベントを購読（message.channels など）
※ 外部公開が必要なため、初期運用ではポーリングを推奨
