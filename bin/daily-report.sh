#!/bin/bash
# Daily Report Generator
# Generates a comprehensive daily report for the user
# Usage: ./daily-report.sh [date]

VAULT_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian"
WORKSPACE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared"
DATE="${1:-$(date '+%Y-%m-%d')}"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    📊 Daily Report                           ║"
echo "║                    $DATE                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Section 1: Task Summary
echo "═══════════════════════════════════════════"
echo "📋 タスクサマリー"
echo "═══════════════════════════════════════════"
echo ""

# Count tasks across all projects
PENDING_TOTAL=0
COMPLETED_TOTAL=0

for project_dir in "$VAULT_DIR/04_Project/"*/; do
    if [ -d "$project_dir" ]; then
        project_name=$(basename "$project_dir")
        [ "$project_name" = "prompt" ] && continue
        
        pending=$(find "$project_dir" -name "*.md" -type f -exec grep -h "^\s*- \[ \]" {} \; 2>/dev/null | wc -l | tr -d ' ')
        completed=$(find "$project_dir" -name "*.md" -type f -exec grep -h "^\s*- \[x\]" {} \; 2>/dev/null | wc -l | tr -d ' ')
        
        if [ "$pending" -gt 0 ] || [ "$completed" -gt 0 ]; then
            echo "  📁 $project_name: ✅ $completed / ⏳ $pending"
        fi
        
        PENDING_TOTAL=$((PENDING_TOTAL + pending))
        COMPLETED_TOTAL=$((COMPLETED_TOTAL + completed))
    fi
done

echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  合計: ✅ $COMPLETED_TOTAL 完了 / ⏳ $PENDING_TOTAL 未完了"
echo ""

# Section 2: Git Activity
echo "═══════════════════════════════════════════"
echo "📂 Git活動"
echo "═══════════════════════════════════════════"
echo ""

cd "$WORKSPACE" 2>/dev/null
if [ -d ".git" ]; then
    TODAY_COMMITS=$(git log --since="$DATE 00:00" --until="$DATE 23:59" --oneline 2>/dev/null | wc -l | tr -d ' ')
    echo "  今日のコミット数: $TODAY_COMMITS"
    echo ""
    
    if [ "$TODAY_COMMITS" -gt 0 ]; then
        echo "  最新コミット:"
        git log --since="$DATE 00:00" --until="$DATE 23:59" --pretty=format:"    • %s" 2>/dev/null | head -5
        echo ""
    fi
    
    # Changed files
    CHANGED_FILES=$(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')
    STAGED_FILES=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
    echo "  変更ファイル: $CHANGED_FILES"
    echo "  ステージ済み: $STAGED_FILES"
else
    echo "  Git リポジトリなし"
fi
echo ""

# Section 3: Memory/Notes
echo "═══════════════════════════════════════════"
echo "📝 今日のメモ"
echo "═══════════════════════════════════════════"
echo ""

MEMORY_FILE="$WORKSPACE/memory/$DATE.md"
if [ -f "$MEMORY_FILE" ]; then
    echo "  メモリファイルあり: memory/$DATE.md"
    LINE_COUNT=$(wc -l < "$MEMORY_FILE" | tr -d ' ')
    echo "  行数: $LINE_COUNT"
else
    echo "  メモリファイルなし"
fi
echo ""

DAILY_NOTE="$VAULT_DIR/05_Daily/$DATE.md"
if [ -f "$DAILY_NOTE" ]; then
    echo "  デイリーノートあり: 05_Daily/$DATE.md"
else
    echo "  デイリーノートなし"
fi
echo ""

# Section 4: Recent Files
echo "═══════════════════════════════════════════"
echo "🕐 最近更新されたファイル"
echo "═══════════════════════════════════════════"
echo ""

find "$WORKSPACE" -name "*.md" -type f -mtime 0 2>/dev/null | head -10 | while read -r file; do
    basename=$(basename "$file")
    mtime=$(stat -f "%Sm" -t "%H:%M" "$file" 2>/dev/null || echo "??:??")
    echo "  $mtime - $basename"
done

echo ""

# Section 5: Recommendations
echo "═══════════════════════════════════════════"
echo "💡 おすすめアクション"
echo "═══════════════════════════════════════════"
echo ""

if [ "$PENDING_TOTAL" -gt 10 ]; then
    echo "  ⚠️ 未完了タスクが多いです。優先順位を見直しましょう"
fi

if [ ! -f "$DAILY_NOTE" ]; then
    echo "  📝 デイリーノートを作成しましょう: ./create-daily.sh"
fi

if [ "$CHANGED_FILES" -gt 0 ]; then
    echo "  💾 未コミットの変更があります。コミットしましょう"
fi

if [ ! -f "$MEMORY_FILE" ]; then
    echo "  🧠 今日のメモを記録しましょう"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Have a productive day! 🚀                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
