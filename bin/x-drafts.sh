#!/bin/bash
# X投稿下書き管理ツール
# Usage: 
#   ./x-drafts.sh add "投稿内容"     - 下書き追加
#   ./x-drafts.sh list               - 一覧表示
#   ./x-drafts.sh edit <番号>        - 編集
#   ./x-drafts.sh delete <番号>      - 削除
#   ./x-drafts.sh export             - CSV出力

WORKSPACE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared"
DRAFTS_FILE="$WORKSPACE/x-drafts.json"

# Initialize file if not exists
if [ ! -f "$DRAFTS_FILE" ]; then
    echo '{"drafts":[]}' > "$DRAFTS_FILE"
fi

ACTION="$1"
shift

case "$ACTION" in
    add)
        CONTENT="$1"
        CATEGORY="${2:-general}"
        TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        
        # Add to JSON using jq or python
        if command -v jq &> /dev/null; then
            jq --arg c "$CONTENT" --arg cat "$CATEGORY" --arg ts "$TIMESTAMP" \
               '.drafts += [{"id": (.drafts | length + 1), "content": $c, "category": $cat, "created": $ts, "status": "draft"}]' \
               "$DRAFTS_FILE" > "$DRAFTS_FILE.tmp" && mv "$DRAFTS_FILE.tmp" "$DRAFTS_FILE"
        else
            python3 << PYEOF
import json
with open("$DRAFTS_FILE", "r") as f:
    data = json.load(f)
new_id = len(data["drafts"]) + 1
data["drafts"].append({
    "id": new_id,
    "content": """$CONTENT""",
    "category": "$CATEGORY",
    "created": "$TIMESTAMP",
    "status": "draft"
})
with open("$DRAFTS_FILE", "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
PYEOF
        fi
        echo "✅ 下書きを追加しました (ID: $(jq '.drafts | length' "$DRAFTS_FILE" 2>/dev/null || echo "?"))"
        ;;
        
    list)
        echo "=== X投稿 下書き一覧 ==="
        echo ""
        if command -v jq &> /dev/null; then
            jq -r '.drafts[] | "[\(.id)] [\(.category)] \(.status)\n\(.content)\n---"' "$DRAFTS_FILE"
        else
            python3 << PYEOF
import json
with open("$DRAFTS_FILE", "r") as f:
    data = json.load(f)
for d in data["drafts"]:
    print(f"[{d['id']}] [{d['category']}] {d['status']}")
    print(d['content'])
    print("---")
PYEOF
        fi
        ;;
        
    delete)
        ID="$1"
        if command -v jq &> /dev/null; then
            jq --argjson id "$ID" 'del(.drafts[] | select(.id == $id))' "$DRAFTS_FILE" > "$DRAFTS_FILE.tmp" && mv "$DRAFTS_FILE.tmp" "$DRAFTS_FILE"
        fi
        echo "🗑️ 下書き ID:$ID を削除しました"
        ;;
        
    export)
        OUTPUT_FILE="$WORKSPACE/x-drafts-export-$(date '+%Y%m%d').csv"
        echo "id,content,category,created,status" > "$OUTPUT_FILE"
        if command -v jq &> /dev/null; then
            jq -r '.drafts[] | [.id, .content, .category, .created, .status] | @csv' "$DRAFTS_FILE" >> "$OUTPUT_FILE"
        fi
        echo "📤 エクスポート完了: $OUTPUT_FILE"
        ;;
        
    *)
        echo "Usage: $0 {add|list|delete|export} [args]"
        echo ""
        echo "Commands:"
        echo "  add \"内容\" [カテゴリ]  - 下書きを追加"
        echo "  list                    - 一覧表示"
        echo "  delete <ID>             - 下書きを削除"
        echo "  export                  - CSVにエクスポート"
        ;;
esac
