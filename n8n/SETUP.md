# n8n セットアップ手順

## 前提条件
- Docker Desktop がインストールされていること
- Mac mini が常時稼働していること

## Step 1: Docker Desktop インストール

```bash
# Homebrew でインストール
brew install --cask docker

# または公式サイトからダウンロード
# https://www.docker.com/products/docker-desktop/
```

インストール後、Docker Desktop を起動して初期設定を完了する。

## Step 2: 認証情報の設定

`docker-compose.yml` を編集して以下を変更:

```yaml
# Basic認証パスワード（強固なものに変更）
N8N_BASIC_AUTH_PASSWORD=your_secure_password

# 暗号化キー（以下のコマンドで生成）
# openssl rand -hex 32
N8N_ENCRYPTION_KEY=your_generated_key
```

## Step 3: n8n 起動

```bash
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/OpenClaw-Shared/n8n
docker compose up -d
```

## Step 4: 動作確認

ブラウザで http://localhost:5678 を開く。
Basic認証のユーザー名・パスワードを入力。

## Step 5: Vault マウント確認

n8n 内で `/vault` にアクセスできることを確認:
1. 新規ワークフローを作成
2. "Execute Command" ノードを追加
3. コマンド: `ls /vault`
4. 実行して Vault のフォルダが見えればOK

## トラブルシューティング

### Docker が起動しない
- Docker Desktop が起動しているか確認
- `docker ps` でコンテナ状態を確認

### Vault が見えない
- docker-compose.yml のパスが正しいか確認
- iCloud 同期が完了しているか確認

### 認証エラー
- N8N_BASIC_AUTH_PASSWORD を正しく設定したか確認
- ブラウザのキャッシュをクリア

## 停止方法

```bash
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/OpenClaw-Shared/n8n
docker compose down
```

## 自動起動設定（オプション）

Docker Desktop の設定で「Start Docker Desktop when you log in」を有効化。
