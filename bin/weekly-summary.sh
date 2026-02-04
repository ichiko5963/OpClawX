#!/bin/bash
# Weekly Summary Generator
# Generates a summary of the week's activities from daily notes and git commits
# Usage: ./weekly-summary.sh [start_date]

VAULT_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian"
WORKSPACE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared"
DAILY_DIR="$VAULT_DIR/05_Daily"

# Calculate week start (Monday)
if [ -n "$1" ]; then
    START_DATE="$1"
else
    # Get last Monday
    DAYS_SINCE_MONDAY=$(date +%u)
    START_DATE=$(date -v-${DAYS_SINCE_MONDAY}d '+%Y-%m-%d' 2>/dev/null || date -d "last monday" '+%Y-%m-%d')
fi

echo "# 週次サマリー"
echo "## 期間: $START_DATE ～"
echo ""
echo "生成日時: $(date '+%Y-%m-%d %H:%M')"
echo ""

echo "---"
echo ""

# Daily notes summary
echo "## 📅 日次ノートまとめ"
echo ""

for i in {0..6}; do
    DATE=$(date -v+${i}d -j -f "%Y-%m-%d" "$START_DATE" "+%Y-%m-%d" 2>/dev/null || date -d "$START_DATE +$i days" "+%Y-%m-%d")
    WEEKDAY=$(date -v+${i}d -j -f "%Y-%m-%d" "$START_DATE" "+%A" 2>/dev/null || date -d "$START_DATE +$i days" "+%A")
    NOTE_FILE="$DAILY_DIR/$DATE.md"
    
    echo "### $DATE ($WEEKDAY)"
    if [ -f "$NOTE_FILE" ]; then
        # Extract completed tasks
        COMPLETED=$(grep -c "\[x\]" "$NOTE_FILE" 2>/dev/null || echo "0")
        PENDING=$(grep -c "\[ \]" "$NOTE_FILE" 2>/dev/null || echo "0")
        echo "- ✅ 完了タスク: $COMPLETED"
        echo "- ⏳ 未完了タスク: $PENDING"
        
        # Extract key sections if they exist
        if grep -q "## 💡" "$NOTE_FILE" 2>/dev/null; then
            echo "- 💡 アイデアあり"
        fi
    else
        echo "- 📝 ノートなし"
    fi
    echo ""
done

echo "---"
echo ""

# Git commits summary
echo "## 📊 Git活動"
echo ""

cd "$WORKSPACE" 2>/dev/null
if [ -d ".git" ]; then
    echo "### コミット履歴"
    echo "\`\`\`"
    git log --since="$START_DATE" --pretty=format:"%h %ad %s" --date=short 2>/dev/null | head -20
    echo ""
    echo "\`\`\`"
    echo ""
    
    COMMIT_COUNT=$(git log --since="$START_DATE" --oneline 2>/dev/null | wc -l | tr -d ' ')
    echo "- 合計コミット数: $COMMIT_COUNT"
else
    echo "Git リポジトリが見つかりません"
fi

echo ""
echo "---"
echo ""

# Projects with activity
echo "## 📁 プロジェクト活動"
echo ""

for project_dir in "$VAULT_DIR/04_Project/"*/; do
    project_name=$(basename "$project_dir")
    if [ "$project_name" != "prompt" ]; then
        # Count recently modified files
        recent_files=$(find "$project_dir" -name "*.md" -type f -mtime -7 2>/dev/null | wc -l | tr -d ' ')
        if [ "$recent_files" -gt 0 ]; then
            echo "### $project_name"
            echo "- 更新されたファイル: $recent_files"
            echo ""
        fi
    fi
done

echo "---"
echo ""
echo "*このレポートは自動生成されました*"
