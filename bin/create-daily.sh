#!/bin/bash
# Create daily note in Obsidian vault
# Usage: ./create-daily.sh [date]
# date format: YYYY-MM-DD (default: today)

VAULT_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian"
DAILY_DIR="$VAULT_DIR/05_Daily"

# Get date (today if not specified)
if [ -n "$1" ]; then
    DATE="$1"
else
    DATE=$(date '+%Y-%m-%d')
fi

# Parse date components
YEAR=$(echo "$DATE" | cut -d'-' -f1)
MONTH=$(echo "$DATE" | cut -d'-' -f2)
DAY=$(echo "$DATE" | cut -d'-' -f3)
WEEKDAY=$(date -j -f "%Y-%m-%d" "$DATE" "+%A" 2>/dev/null || date -d "$DATE" "+%A" 2>/dev/null)

FILE_PATH="$DAILY_DIR/$DATE.md"

# Check if file already exists
if [ -f "$FILE_PATH" ]; then
    echo "Daily note already exists: $FILE_PATH"
    exit 0
fi

# Create daily note
cat > "$FILE_PATH" << EOF
# $DATE ($WEEKDAY)

## 📌 今日の目標
- [ ] 

## 📋 タスク
### 🔴 高優先度
- [ ] 

### 🟡 中優先度
- [ ] 

### 🟢 低優先度
- [ ] 

## 📝 メモ


## 💡 アイデア・気づき


## 📊 振り返り
### うまくいったこと


### 改善点


### 明日への引き継ぎ


---
*Created: $(date '+%Y-%m-%d %H:%M')*
EOF

echo "Created daily note: $FILE_PATH"
