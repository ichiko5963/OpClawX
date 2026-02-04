#!/bin/bash
# Google Integration Setup Script
# いちさんが実行するセットアップスクリプト（修正版）

echo "🔧 Google連携セットアップを開始します..."
echo ""

# Step 0: gogcli インストール
echo "=== Step 0: gogcli (gog) インストール ==="
echo ""
if command -v gog &> /dev/null; then
    echo "✅ gogcli は既にインストールされています"
else
    echo "gogcli をインストールします..."
    brew install steipete/tap/gogcli
fi
echo ""

# Step 1: Google Cloud OAuth設定
echo "=== Step 1: Google Cloud OAuth設定 ==="
echo ""
echo "Google Cloud ConsoleでOAuthクライアントを作成する必要があります："
echo ""
echo "1. https://console.cloud.google.com/ にアクセス"
echo "2. プロジェクトを選択（または新規作成）"
echo "3. 左メニュー → APIとサービス → 認証情報"
echo "4. '認証情報を作成' → 'OAuthクライアントID'"
echo "5. アプリケーションの種類: 'デスクトップアプリ'"
echo "6. 名前: 'gog' (任意)"
echo "7. 作成後、JSONをダウンロード（client_secret_xxx.json）"
echo ""
read -p "JSONファイルをダウンロードしたらパスを入力 (例: ~/Downloads/client_secret.json): " CLIENT_JSON

if [ -f "$CLIENT_JSON" ]; then
    gog auth credentials "$CLIENT_JSON"
    echo "✅ 認証情報を保存しました"
else
    echo "⚠️ ファイルが見つかりません。後で手動で実行してください："
    echo "   gog auth credentials <JSONファイルパス>"
fi
echo ""

# Step 2: アカウント認証
echo "=== Step 2: Googleアカウント認証 ==="
echo ""
read -p "使用するGmailアドレス: " GMAIL_ADDRESS

if [ -n "$GMAIL_ADDRESS" ]; then
    echo "ブラウザが開きます。Googleアカウントでログインしてください。"
    gog auth add "$GMAIL_ADDRESS"
    echo ""
    echo "デフォルトアカウントに設定..."
    export GOG_ACCOUNT="$GMAIL_ADDRESS"
    echo "export GOG_ACCOUNT=\"$GMAIL_ADDRESS\"" >> ~/.bash_profile
    echo "export GOG_ACCOUNT=\"$GMAIL_ADDRESS\"" >> ~/.zshrc
fi
echo ""

# Step 3: Google Calendar (gcalcli)
echo "=== Step 3: Google Calendar設定 ==="
echo ""
echo "gcalcli を初期化します..."
gcalcli init
echo ""
echo "カレンダー一覧を確認："
gcalcli list
echo ""

# Step 4: 確認
echo "=== 設定確認 ==="
echo ""
echo "Gmail:"
gog gmail labels list --max 5 2>/dev/null || echo "  (未設定またはエラー)"
echo ""
echo "Calendar:"
gcalcli agenda --nostarted 2>/dev/null | head -5 || echo "  (未設定またはエラー)"
echo ""

echo "🎉 Google連携セットアップ完了！"
echo ""
echo "使い方:"
echo "  gog gmail search 'is:unread' --max 10  # 未読メール"
echo "  gcalcli agenda                          # 今日の予定"
