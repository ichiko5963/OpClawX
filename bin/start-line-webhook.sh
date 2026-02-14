#!/bin/bash
# LINE Webhook サーバー起動スクリプト

cd /Users/ai-driven-work/Documents/OpenClaw-Workspace

# 環境変数読み込み
export LINE_CHANNEL_ACCESS_TOKEN="McPVn4sc9LKdm2jc5e5g2EG1DUX6hqIHlrvTpKsKAtmp3xmlXoH0W1T8yQhdtvwUiy5cE2UmX+mm+1CWZtTq3nztSUqU03RoH5MF1XjvHMm/RcdjqKOha+i+gBmcV29rXWpT9QpCnpRSWBSBkIHthwdB04t89/1O/w1cDnyilFU="
export LINE_CHANNEL_SECRET="59c8cb272d41d5a849adb7b08764f83e"

# venv起動
source venv/bin/activate

# サーバー起動
echo "=== LINE Webhook サーバー起動 ==="
echo "Port: 5000"
python3 tools/line_webhook_server.py
