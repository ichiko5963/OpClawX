# Email Auto Reply システム

Gmailの重要度高(P1/P2)メールに対して、AIが返信の下書きを自動作成するシステム。

## 機能

- Gmailの未読メールから重要度高(P1/P2)のメールを自動検出
- AI (GPT-4o-mini) が返信の下書きを自動生成
- 自動送信モード: ONなら確認なしに送信、OFFなら下書き保存
- cronで定期実行可能

## ファイル構成

```
scripts/
├── email_auto_reply.py      # メインスクリプト
└── config/
    └── email_auto_reply.yaml  # 設定ファイル
```

## 設定 (email_auto_reply.yaml)

```yaml
# 自動送信モード: true = 確認なしに送信, false = 下書き保存
auto_send_mode: false

# 処理する優先度
process_priorities:
  - P1
  - P2

# cronスケジュール (デフォルト: 毎時0分)
cron_schedule: "0 * * * *"

# 1回の実行で処理するメール数
max_emails_per_run: 10

# AI設定
ai_settings:
  temperature: 0.7
  max_tokens: 500
  language: "ja"
```

## 使用方法

### テスト実行 (1回だけ実行)

```bash
python scripts/email_auto_reply.py
```

### 自動送信モードを有効化

```bash
python scripts/email_auto_reply.py --auto-send
```

### 自動送信モードを無効化（下書き保存のみ）

```bash
python scripts/email_auto_reply.py --no-auto-send
```

### cronにインストール (毎時実行)

※注意: macOSではcronがデフォルトで無効な場合があります

```bash
python scripts/email_auto_reply.py --install-cron
```

macOSでcronが動かない場合は、launchdを使うか、OpenClawのheartbeat機能を使用して定期実行してください。

### 手動でcronを設定する場合

```bash
# 毎時0分に実行
0 * * * * /usr/bin/python3 /Users/ai-driven-work/Documents/OpenClaw-Workspace/scripts/email_auto_reply.py
```

## 優先度判定

### P1 (緊急)
- 至急、urgent、ASAP、緊急などのキーワード
- 重要度高の送信者からのメール

### P2 (重要)
- ご確認、お返事、ご質問」などのキーワード
- 設定された重要送信者リスト

### 無視されるメール
- noreply, notifications, newsletter など
- 配信停止メール
- サクラメール etc.

## ログ

- ログファイル: `logs/email_auto_reply.log`
- 状態ファイル: `data/email_auto_reply_state.json`

## 必要な環境変数

```bash
# OpenAI API Key (AI返信生成に使用)
export OPENAI_API_KEY="sk-..."
```

## 注意事项

1. **Gmail認証**: n8nのcredentialsを使用。tokenが期限切れの場合はn8nで再認証が必要
2. **自動送信モード**: 有効にする場合は注意！必ずテスト環境で動作確認すること
3. **API制限**: Gmail APIのクォータに注意

## 問題の解決

### "Gmail refresh token expired" エラー
→ n8nでGmail credentialsを再認証してください

### "OPENAI_API_KEY not set" 
→ 環境変数を設定してください

### macOSでcronが動かない
macOSではcronデーモンがデフォルトで無効です。以下の方法で有効化できます：

```bash
# cronを有効化 (macOS)
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.cron.plist
```

または、OpenClawのheartbeat機能を使用して定期実行してください。
