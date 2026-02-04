#!/bin/bash
# Obsidian Search Tool
# Fuzzy search across Obsidian vault
# Usage: ./obsidian-search.sh "search term" [folder]

VAULT_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared/obsidian/Ichioka Obsidian"
QUERY="$1"
FOLDER="${2:-}"

if [ -z "$QUERY" ]; then
    echo "Usage: $0 \"search term\" [folder]"
    echo ""
    echo "Folders:"
    echo "  01_Notes, 04_Project, 05_Daily, 07-To Do, 08-prompt"
    exit 1
fi

if [ -n "$FOLDER" ]; then
    SEARCH_DIR="$VAULT_DIR/$FOLDER"
else
    SEARCH_DIR="$VAULT_DIR"
fi

echo "=== 検索結果: \"$QUERY\" ==="
echo "検索パス: $SEARCH_DIR"
echo ""

# Use ripgrep if available, otherwise grep
if command -v rg &> /dev/null; then
    rg -i -l "$QUERY" "$SEARCH_DIR" --type md 2>/dev/null | while read -r file; do
        echo "📄 $(basename "$file")"
        echo "   パス: $file"
        rg -i -n -C 1 "$QUERY" "$file" --type md 2>/dev/null | head -6 | sed 's/^/   /'
        echo ""
    done
else
    grep -r -i -l "$QUERY" "$SEARCH_DIR" --include="*.md" 2>/dev/null | while read -r file; do
        echo "📄 $(basename "$file")"
        echo "   パス: $file"
        grep -i -n -C 1 "$QUERY" "$file" 2>/dev/null | head -6 | sed 's/^/   /'
        echo ""
    done
fi

echo "=== 検索完了 ==="
