#!/bin/bash
# Git Commit Helper with AI Summary
# Generates a meaningful commit message based on changes
# Usage: ./smart-commit.sh [optional message prefix]

WORKSPACE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared"
PREFIX="${1:-}"

cd "$WORKSPACE" || exit 1

# Check if there are changes
if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
    echo "📭 コミットする変更がありません"
    exit 0
fi

echo ""
echo "═══════════════════════════════════════════"
echo "      📝 スマートコミット"
echo "═══════════════════════════════════════════"
echo ""

# Get changed files
CHANGED_FILES=$(git status --porcelain 2>/dev/null)
ADDED=$(echo "$CHANGED_FILES" | grep "^A\|^??" | wc -l | tr -d ' ')
MODIFIED=$(echo "$CHANGED_FILES" | grep "^M\|^ M" | wc -l | tr -d ' ')
DELETED=$(echo "$CHANGED_FILES" | grep "^D\|^ D" | wc -l | tr -d ' ')

echo "📊 変更サマリー:"
echo "  ✅ 追加: $ADDED"
echo "  📝 変更: $MODIFIED"  
echo "  🗑️ 削除: $DELETED"
echo ""

# Get file list
echo "📁 変更ファイル:"
echo "$CHANGED_FILES" | head -10 | while read -r line; do
    status=$(echo "$line" | cut -c1-2)
    file=$(echo "$line" | cut -c4-)
    case "$status" in
        "??") echo "  + $file (new)" ;;
        "A "| " A") echo "  + $file" ;;
        "M "| " M") echo "  ~ $file" ;;
        "D "| " D") echo "  - $file" ;;
        *) echo "  ? $file" ;;
    esac
done

TOTAL_FILES=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
if [ "$TOTAL_FILES" -gt 10 ]; then
    echo "  ... (+$((TOTAL_FILES - 10)) more files)"
fi
echo ""

# Generate commit message
DATE=$(date '+%Y-%m-%d %H:%M')

# Detect main changes
COMMIT_MSG=""

if echo "$CHANGED_FILES" | grep -q "bin/"; then
    COMMIT_MSG="${COMMIT_MSG}tools, "
fi

if echo "$CHANGED_FILES" | grep -q "memory/"; then
    COMMIT_MSG="${COMMIT_MSG}memory, "
fi

if echo "$CHANGED_FILES" | grep -q "projects/"; then
    COMMIT_MSG="${COMMIT_MSG}projects, "
fi

if echo "$CHANGED_FILES" | grep -q "obsidian/"; then
    COMMIT_MSG="${COMMIT_MSG}obsidian, "
fi

if echo "$CHANGED_FILES" | grep -q "\.md"; then
    COMMIT_MSG="${COMMIT_MSG}docs, "
fi

# Remove trailing comma and space
COMMIT_MSG=$(echo "$COMMIT_MSG" | sed 's/, $//')

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="misc updates"
fi

# Add prefix if provided
if [ -n "$PREFIX" ]; then
    COMMIT_MSG="$PREFIX: $COMMIT_MSG"
fi

# Add counts
COMMIT_MSG="$COMMIT_MSG (+$ADDED ~$MODIFIED -$DELETED)"

echo "📝 提案されたコミットメッセージ:"
echo "   \"$COMMIT_MSG\""
echo ""

# Confirm
read -p "このメッセージでコミットしますか? (y/n/e=edit): " choice

case "$choice" in
    y|Y)
        git add -A
        git commit -m "$COMMIT_MSG"
        echo ""
        echo "✅ コミット完了！"
        ;;
    e|E)
        read -p "新しいメッセージを入力: " new_msg
        git add -A
        git commit -m "$new_msg"
        echo ""
        echo "✅ コミット完了！"
        ;;
    *)
        echo "❌ キャンセルしました"
        ;;
esac

echo ""
