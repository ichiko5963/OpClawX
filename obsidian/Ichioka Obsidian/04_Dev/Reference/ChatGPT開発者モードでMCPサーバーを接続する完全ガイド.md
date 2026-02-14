# 🎯 ChatGPT開発者モードでMCPサーバーを接続する完全ガイド

## ステップ1️⃣: ChatGPTの開発者モードを有効化

1. ChatGPTを開く: https://chat.openai.com
2. 左下の **あなたのアイコン** をクリック
3. 「Settings」（設定） を選択
4. 「Connectors」 タブをクリック
5. 「Advanced Settings」 を展開
6. 「Developer Mode」 をオンにする

## ステップ2️⃣: ComposioのMCPサーバーをローカルで立てる

### 必要なもの
- Node.js (v18以上)
- Composio APIキー

### コマンド実行
ターミナル（コマンドプロンプト）で以下を実行：

```bash
# ComposioのMCPサーバーをインストール
npx @composio/mcp-server-composio
```

このコマンドで、ローカルにMCPサーバーが立ち上がります。

## ステップ3️⃣: ローカルサーバーをインターネットに公開（Ngrok）

ChatGPTからアクセスするため、ローカルサーバーを公開する必要があります。

### Ngrokのインストールと設定

```bash
# Ngrokをインストール（MacならHomebrew）
brew install ngrok

# または直接ダウンロード
# https://ngrok.com/download

# Ngrokでポート転送（Composioのデフォルトポートは3000）
ngrok http 3000
```

Ngrokが起動すると、以下のようなURLが表示されます：

```
Forwarding   https://abc123.ngrok.io -> http://localhost:3000
```

この `https://abc123.ngrok.io` をコピーしてください。

## ステップ4️⃣: ChatGPTにMCPサーバーを登録

1. ChatGPTの **Settings → Connectors** に戻る
2. 「Add Connector」 ボタンをクリック
3. 以下を入力：
   - **Connector URL:**
     ```
     https://abc123.ngrok.io/mcp
     ```
     （NgrokのURLの後ろに `/mcp` を追加）
   - **Name (任意):**
     ```
     Composio Twitter
     ```
4. 「Connect」 をクリック

## ステップ5️⃣: ChatGPTでテスト

ChatGPTの通常チャットで以下のように入力：

```
@Composio Twitter このテキストをツイートして: AIエージェントが生産性を変えている 🚀
```

ChatGPTがMCPサーバー経由でTwitterに投稿します！

---

## 🔧 より簡単な方法：Composio公式MCPサーバーを直接使う

ローカルサーバーを立てなくても、Composioが提供する公開MCPエンドポイントを直接使えます：

### ChatGPT Connectorsに以下を追加：

- **Connector URL:**
  ```
  https://backend.composio.dev/api/v3/mcp
  ```
- **Authentication:**
  - Type: Bearer Token
  - Token: あなたのComposio APIキー（取得方法は後述）

これで、ローカルサーバーなしでChatGPTからComposioの全ツール（Twitter、Gmail、Slackなど）が使えます！






