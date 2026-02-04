#!/bin/bash
# Quick Note Creator
# Quickly creates a note in Obsidian with automatic linking
# Usage: ./quick-note.sh "title" "content" [folder]

VAULT_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian"

TITLE="$1"
CONTENT="$2"
FOLDER="${3:-01_Notes}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
DATE=$(date '+%Y-%m-%d')

if [ -z "$TITLE" ]; then
    echo "Usage: $0 \"title\" \"content\" [folder]"
    echo ""
    echo "Folders: 01_Notes, 04_Project, 05_Daily, 08-prompt"
    exit 1
fi

# Create safe filename
SAFE_TITLE=$(echo "$TITLE" | tr ' ' '_' | tr -cd '[:alnum:]_-日本語' | head -c 50)
FILE_PATH="$VAULT_DIR/$FOLDER/${DATE}_${SAFE_TITLE}.md"

# Detect tags from content
TAGS=""
if echo "$CONTENT" | grep -qi "ai\|claude\|gpt"; then
    TAGS="$TAGS #AI"
fi
if echo "$CONTENT" | grep -qi "obsidian\|note"; then
    TAGS="$TAGS #Obsidian"
fi
if echo "$CONTENT" | grep -qi "aircle\|コミュニティ"; then
    TAGS="$TAGS #AirCle"
fi

cat > "$FILE_PATH" << EOF
# $TITLE

**作成日時**: $TIMESTAMP
**タグ**: $TAGS

---

$CONTENT

---

## 関連ノート
- 

## 次のアクション
- [ ] 

EOF

echo "✅ ノート作成完了: $FILE_PATH"
echo ""
echo "Obsidianで開く:"
echo "open \"obsidian://open?vault=Ichioka%20Obsidian&file=${DATE}_${SAFE_TITLE}\""
