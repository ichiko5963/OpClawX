#!/bin/bash
# Project Status Dashboard
# Shows status of all projects in Obsidian vault
# Usage: ./project-status.sh

VAULT_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian"
PROJECT_DIR="$VAULT_DIR/04_Project"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║             📊 プロジェクト ステータス ダッシュボード             ║"
echo "║                    $(date '+%Y-%m-%d %H:%M')                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

for project_path in "$PROJECT_DIR/"*/; do
    [ ! -d "$project_path" ] && continue
    
    project_name=$(basename "$project_path")
    [ "$project_name" = "prompt" ] && continue
    
    # Count files
    total_files=$(find "$project_path" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
    
    # Count tasks
    pending_tasks=$(find "$project_path" -name "*.md" -type f -exec grep -h "^\s*- \[ \]" {} \; 2>/dev/null | wc -l | tr -d ' ')
    completed_tasks=$(find "$project_path" -name "*.md" -type f -exec grep -h "^\s*- \[x\]" {} \; 2>/dev/null | wc -l | tr -d ' ')
    
    # Calculate completion rate
    total_tasks=$((pending_tasks + completed_tasks))
    if [ "$total_tasks" -gt 0 ]; then
        completion_rate=$((completed_tasks * 100 / total_tasks))
    else
        completion_rate=0
    fi
    
    # Progress bar
    filled=$((completion_rate / 5))
    empty=$((20 - filled))
    progress_bar=$(printf '█%.0s' $(seq 1 $filled 2>/dev/null) 2>/dev/null)$(printf '░%.0s' $(seq 1 $empty 2>/dev/null) 2>/dev/null)
    [ -z "$progress_bar" ] && progress_bar="░░░░░░░░░░░░░░░░░░░░"
    
    # Last modified
    last_modified=$(find "$project_path" -name "*.md" -type f -exec stat -f "%m %N" {} \; 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
    last_modified_date=""
    if [ -n "$last_modified" ]; then
        last_modified_date=$(stat -f "%Sm" -t "%Y-%m-%d" "$last_modified" 2>/dev/null || echo "N/A")
    fi
    
    # Display
    echo "┌──────────────────────────────────────────────────────────────┐"
    echo "│ 📁 $project_name"
    echo "├──────────────────────────────────────────────────────────────┤"
    printf "│ 進捗: [%-20s] %3d%%\n" "$progress_bar" "$completion_rate"
    echo "│ タスク: ✅ $completed_tasks / ⏳ $pending_tasks / 合計 $total_tasks"
    echo "│ ファイル数: $total_files"
    echo "│ 最終更新: $last_modified_date"
    echo "└──────────────────────────────────────────────────────────────┘"
    echo ""
done

echo "═══════════════════════════════════════════════════════════════"
echo "  ヒント: ./extract-tasks.sh [project] でタスク詳細を確認"
echo "═══════════════════════════════════════════════════════════════"
