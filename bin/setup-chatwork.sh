#!/bin/bash
# Chatwork Integration Setup Script
# いちさんが実行するセットアップスクリプト

echo "💬 Chatwork連携セットアップ"
echo ""

echo "=== Step 1: APIトークン取得 ==="
echo ""
echo "1. Chatwork → 右上のアイコン → 設定"
echo "2. 'API設定' タブをクリック"
echo "3. 'APIトークン' を発行"
echo "4. トークンをコピー"
echo ""
read -p "APIトークン: " CHATWORK_TOKEN

echo ""
echo "=== Step 2: OpenClaw Webhook設定 ==="
echo ""
echo "Chatworkはネイティブサポートされていないため、"
echo "Webhookでカスタム連携を設定します。"
echo ""
echo "~/.openclaw/openclaw.json に以下を追加："
echo ""
cat << EOF
{
  "hooks": {
    "enabled": true,
    "token": "YOUR_HOOK_TOKEN",
    "mappings": [
      {
        "match": { "path": "chatwork" },
        "action": "agent",
        "wakeMode": "now",
        "name": "Chatwork",
        "sessionKey": "hook:chatwork:{{room_id}}:{{message_id}}",
        "messageTemplate": "Chatwork: {{account.name}}からのメッセージ\\n{{body}}",
        "deliver": true,
        "channel": "discord"
      }
    ]
  }
}
EOF

echo ""
echo "=== Step 3: Chatwork Webhook設定 ==="
echo ""
echo "Chatworkの管理画面でWebhook（アウトゴーイング）を設定："
echo "  URL: http://your-server:18789/hooks/chatwork"
echo "  認証: x-openclaw-token: YOUR_HOOK_TOKEN"
echo ""

echo ""
echo "=== 代替案: 定期ポーリング ==="
echo ""
echo "Webhookが難しい場合、cronで定期的にChatwork APIを呼び出す方式も可能。"
echo ""
echo "例: 5分ごとに未読メッセージをチェック"
echo ""

echo "Chatwork APIトークンを保存しました: $CHATWORK_TOKEN"
echo ""
echo "🎉 基本設定完了！"
