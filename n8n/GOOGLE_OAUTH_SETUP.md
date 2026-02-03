# Google API OAuth 設定手順

## 概要
Gmail / Google Calendar / Google Drive に Read-only でアクセスするための OAuth 設定。

## Step 1: Google Cloud プロジェクト作成

1. https://console.cloud.google.com/ にアクセス
2. 新しいプロジェクトを作成（例: `context-curator`）
3. プロジェクトを選択

## Step 2: API の有効化

左メニュー「APIとサービス」→「ライブラリ」から以下を有効化:

- Gmail API
- Google Calendar API
- Google Drive API

## Step 3: OAuth 同意画面の設定

1. 「APIとサービス」→「OAuth同意画面」
2. ユーザータイプ: **外部**（個人アカウントの場合）
3. アプリ名: `Context Curator`
4. サポートメール: あなたのメールアドレス
5. スコープを追加:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/drive.readonly`
6. テストユーザーに自分のメールアドレスを追加

## Step 4: OAuth クライアント作成

1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「OAuthクライアントID」
3. アプリケーションの種類: **ウェブアプリケーション**
4. 名前: `n8n`
5. 承認済みのリダイレクトURI:
   ```
   http://localhost:5678/rest/oauth2-credential/callback
   ```
6. 作成後、**クライアントID** と **クライアントシークレット** をメモ

## Step 5: n8n で Credential 作成

### Gmail

1. n8n で「Credentials」→「New」
2. 「Gmail OAuth2 API」を選択
3. Client ID と Client Secret を入力
4. 「Connect my account」でGoogleログイン
5. 権限を許可

### Google Calendar

1. 「Google Calendar OAuth2 API」を選択
2. 同様に設定

### Google Drive

1. 「Google Drive OAuth2 API」を選択
2. 同様に設定

## 注意事項

### テストモードの制限
- OAuth同意画面が「テスト」状態だと、トークンは7日で失効する
- 長期運用には「公開」にする必要があるが、Google の審査が必要
- 回避策: 失効前にトークンを再取得するか、定期的に手動で再認証

### スコープについて
現在は **readonly** のみ。送信/作成を有効化する場合:
- `gmail.send`
- `calendar.events`
- `drive.file`
を追加する（承認フロー完成後）

## 保存場所

取得した認証情報は n8n の内部に暗号化保存される。
Vault には保存しない（セキュリティ上の理由）。
