#!/bin/bash
# Pi Voice Assistant 起動スクリプト

cd "/Users/ai-driven-work/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared"

# マイクのアクセス許可を確認
echo "🎤 マイクを使用します..."

# 音声アシスタントを起動
python3 scripts/voice_assistant_v2.py
