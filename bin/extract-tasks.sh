#!/bin/bash
# Extract uncompleted tasks from Obsidian vault
# Usage: ./extract-tasks.sh [project]

VAULT_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian"
PROJECT="$1"

echo "=== 未完了タスク一覧 ==="
echo "取得日時: $(date '+%Y-%m-%d %H:%M')"
echo ""

if [ -n "$PROJECT" ]; then
    echo "プロジェクト: $PROJECT"
    echo "---"
    # Search in specific project folder
    find "$VAULT_DIR/04_Project/$PROJECT" -name "*.md" -type f 2>/dev/null | while read -r file; do
        tasks=$(grep -n "^\s*- \[ \]" "$file" 2>/dev/null)
        if [ -n "$tasks" ]; then
            echo ""
            echo "📄 $(basename "$file")"
            echo "$tasks" | while read -r line; do
                echo "  $line"
            done
        fi
    done
else
    echo "全プロジェクト"
    echo "---"
    
    # Check To Do folder first
    echo ""
    echo "### 📋 To Do フォルダ ###"
    find "$VAULT_DIR/07-To Do" -name "*.md" -type f 2>/dev/null | while read -r file; do
        tasks=$(grep -n "^\s*- \[ \]" "$file" 2>/dev/null)
        if [ -n "$tasks" ]; then
            echo ""
            echo "📄 $(basename "$file")"
            echo "$tasks" | while read -r line; do
                echo "  $line"
            done
        fi
    done
    
    # Check project folders
    echo ""
    echo "### 📁 プロジェクト ###"
    for project_dir in "$VAULT_DIR/04_Project/"*/; do
        project_name=$(basename "$project_dir")
        if [ "$project_name" != "prompt" ]; then
            project_tasks=$(find "$project_dir" -name "*.md" -type f -exec grep -l "^\s*- \[ \]" {} \; 2>/dev/null | wc -l | tr -d ' ')
            if [ "$project_tasks" -gt 0 ]; then
                echo ""
                echo "=== $project_name ($project_tasks files with tasks) ==="
                find "$project_dir" -name "*.md" -type f 2>/dev/null | head -5 | while read -r file; do
                    tasks=$(grep -n "^\s*- \[ \]" "$file" 2>/dev/null | head -3)
                    if [ -n "$tasks" ]; then
                        echo "  📄 $(basename "$file")"
                        echo "$tasks" | while read -r line; do
                            echo "    $line"
                        done
                    fi
                done
            fi
        fi
    done
fi

echo ""
echo "=== 完了 ==="
