#!/bin/bash
# Generate meeting notes template
# Usage: ./meeting-notes.sh "Meeting Title" [participants] [project]

VAULT_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian"
DATE=$(date '+%Y-%m-%d')
TIME=$(date '+%H:%M')

TITLE="${1:-Meeting}"
PARTICIPANTS="${2:-}"
PROJECT="${3:-}"

# Determine output directory
if [ -n "$PROJECT" ]; then
    OUTPUT_DIR="$VAULT_DIR/04_Project/$PROJECT"
    if [ ! -d "$OUTPUT_DIR" ]; then
        OUTPUT_DIR="$VAULT_DIR/01_Notes"
    fi
else
    OUTPUT_DIR="$VAULT_DIR/01_Notes"
fi

# Create safe filename
SAFE_TITLE=$(echo "$TITLE" | tr ' ' '_' | tr -cd '[:alnum:]_-')
FILE_PATH="$OUTPUT_DIR/${DATE}_${SAFE_TITLE}.md"

cat > "$FILE_PATH" << EOF
# $TITLE

## 基本情報
- **日時**: $DATE $TIME
- **参加者**: $PARTICIPANTS
- **プロジェクト**: ${PROJECT:-N/A}

## 📋 アジェンダ
1. 
2. 
3. 

## 📝 議事録

### トピック1


### トピック2


### トピック3


## ✅ 決定事項
- 

## 📌 アクションアイテム
| 担当者 | タスク | 期限 |
|--------|--------|------|
|  |  |  |

## 💡 次回までの宿題
- [ ] 

## 📎 関連リンク
- 

---
*作成: $(date '+%Y-%m-%d %H:%M')*
EOF

echo "Created meeting notes: $FILE_PATH"
echo ""
echo "To open in Obsidian, run:"
echo "open \"obsidian://open?vault=Ichioka%20Obsidian&file=${DATE}_${SAFE_TITLE}\""
