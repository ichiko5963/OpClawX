#!/bin/bash
# Slack Integration Setup Script
# いちさんが実行するセットアップスクリプト

echo "💬 Slack連携セットアップ"
echo ""

echo "=== Step 1: Slack App作成 ==="
echo ""
echo "1. https://api.slack.com/apps にアクセス"
echo "2. 'Create New App' → 'From scratch'"
echo "3. App名: OpenClaw (または任意)"
echo "4. Workspace: 対象のワークスペースを選択"
echo ""
read -p "アプリを作成したらEnterキー..."

echo ""
echo "=== Step 2: Socket Mode有効化 ==="
echo ""
echo "1. 左メニュー 'Socket Mode' をクリック"
echo "2. 'Enable Socket Mode' をON"
echo "3. App Level Token を生成:"
echo "   - Token Name: openclaw-socket"
echo "   - Scope: connections:write"
echo "4. 生成されたトークン (xapp-...) をコピー"
echo ""
read -p "App Token (xapp-): " APP_TOKEN

echo ""
echo "=== Step 3: Bot Token取得 ==="
echo ""
echo "1. 左メニュー 'OAuth & Permissions' をクリック"
echo "2. 'Bot Token Scopes' に以下を追加:"
echo "   - chat:write"
echo "   - channels:history, channels:read"
echo "   - groups:history, groups:read"
echo "   - im:history, im:read, im:write"
echo "   - mpim:history, mpim:read"
echo "   - users:read"
echo "   - reactions:read, reactions:write"
echo "   - pins:read, pins:write"
echo "   - emoji:read"
echo "   - files:read, files:write"
echo "   - app_mentions:read"
echo "   - commands"
echo ""
echo "3. 'Install to Workspace' をクリック"
echo "4. Bot User OAuth Token (xoxb-...) をコピー"
echo ""
read -p "Bot Token (xoxb-): " BOT_TOKEN

echo ""
echo "=== Step 4: Event Subscriptions ==="
echo ""
echo "1. 左メニュー 'Event Subscriptions' をクリック"
echo "2. 'Enable Events' をON"
echo "3. 'Subscribe to bot events' に以下を追加:"
echo "   - message.channels"
echo "   - message.groups"
echo "   - message.im"
echo "   - message.mpim"
echo "   - app_mention"
echo "   - reaction_added, reaction_removed"
echo ""
read -p "設定完了したらEnterキー..."

echo ""
echo "=== Step 5: App Home設定 ==="
echo ""
echo "1. 左メニュー 'App Home' をクリック"
echo "2. 'Messages Tab' を有効化"
echo ""
read -p "設定完了したらEnterキー..."

echo ""
echo "=== Step 6: OpenClaw設定 ==="
echo ""
echo "以下のコマンドを実行してください："
echo ""
echo "openclaw configure --section slack"
echo ""
echo "または手動で ~/.openclaw/openclaw.json に追加："
echo ""
cat << EOF
{
  "channels": {
    "slack": {
      "enabled": true,
      "appToken": "${APP_TOKEN}",
      "botToken": "${BOT_TOKEN}",
      "groupPolicy": "allowlist",
      "channels": {
        "#general": { "allow": true, "requireMention": true }
      }
    }
  }
}
EOF

echo ""
echo "🎉 Slack設定完了！"
echo ""
echo "最後にボットをチャンネルに招待："
echo "  /invite @OpenClaw"
