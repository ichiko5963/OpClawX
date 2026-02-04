#!/bin/bash
# OpenClaw-Shared Git Auto Sync Script
# 1時間ごとに実行して、変更があればコミット&プッシュ

REPO_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared"
LOG_FILE="$REPO_DIR/bin/git-sync.log"

cd "$REPO_DIR" || exit 1

# Git初期化されてなければ初期化
if [ ! -d ".git" ]; then
    git init >> "$LOG_FILE" 2>&1
    echo "$(date): Git initialized" >> "$LOG_FILE"
fi

# リモートが設定されてなければスキップ（手動でリモート追加が必要）
# git remote add origin <YOUR_REPO_URL>

# 変更があればコミット
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    git add -A >> "$LOG_FILE" 2>&1
    git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1
    echo "$(date): Committed changes" >> "$LOG_FILE"
    
    # リモートがあればプッシュ
    if git remote | grep -q origin; then
        git push origin main >> "$LOG_FILE" 2>&1
        echo "$(date): Pushed to remote" >> "$LOG_FILE"
    fi
else
    echo "$(date): No changes to commit" >> "$LOG_FILE"
fi
