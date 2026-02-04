#!/bin/bash
# Workspace Health Check
# Checks the health of the OpenClaw workspace
# Usage: ./health-check.sh

WORKSPACE="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Shared"
VAULT_DIR="$WORKSPACE/obsidian/Ichioka Obsidian"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                🏥 ワークスペース ヘルスチェック                  ║"
echo "║                    $(date '+%Y-%m-%d %H:%M')                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

ISSUES=0
WARNINGS=0

check_pass() {
    echo "  ✅ $1"
}

check_warn() {
    echo "  ⚠️ $1"
    WARNINGS=$((WARNINGS + 1))
}

check_fail() {
    echo "  ❌ $1"
    ISSUES=$((ISSUES + 1))
}

# Section 1: Essential Files
echo "═══════════════════════════════════════════"
echo "📁 必須ファイル"
echo "═══════════════════════════════════════════"

[ -f "$WORKSPACE/AGENTS.md" ] && check_pass "AGENTS.md" || check_fail "AGENTS.md がありません"
[ -f "$WORKSPACE/SOUL.md" ] && check_pass "SOUL.md" || check_fail "SOUL.md がありません"
[ -f "$WORKSPACE/MEMORY.md" ] && check_pass "MEMORY.md" || check_fail "MEMORY.md がありません"
[ -f "$WORKSPACE/IDENTITY.md" ] && check_pass "IDENTITY.md" || check_warn "IDENTITY.md がありません"
[ -d "$WORKSPACE/memory" ] && check_pass "memory/" || check_fail "memory/ がありません"
[ -d "$WORKSPACE/bin" ] && check_pass "bin/" || check_warn "bin/ がありません"

echo ""

# Section 2: Git Status
echo "═══════════════════════════════════════════"
echo "📂 Git ステータス"
echo "═══════════════════════════════════════════"

cd "$WORKSPACE" 2>/dev/null

if [ -d ".git" ]; then
    check_pass "Git リポジトリ初期化済み"
    
    # Check for uncommitted changes
    CHANGES=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [ "$CHANGES" -eq 0 ]; then
        check_pass "未コミットの変更なし"
    elif [ "$CHANGES" -lt 10 ]; then
        check_warn "$CHANGES 個の未コミット変更"
    else
        check_fail "$CHANGES 個の未コミット変更（多すぎます）"
    fi
    
    # Check for remote
    if git remote | grep -q origin; then
        check_pass "リモートリポジトリ設定済み"
    else
        check_warn "リモートリポジトリ未設定"
    fi
else
    check_fail "Git リポジトリが初期化されていません"
fi

echo ""

# Section 3: Obsidian Vault
echo "═══════════════════════════════════════════"
echo "📚 Obsidian Vault"
echo "═══════════════════════════════════════════"

if [ -d "$VAULT_DIR" ]; then
    check_pass "Vault ディレクトリ存在"
    
    # Count files
    MD_COUNT=$(find "$VAULT_DIR" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
    if [ "$MD_COUNT" -gt 0 ]; then
        check_pass "$MD_COUNT 個の Markdown ファイル"
    else
        check_warn "Markdown ファイルがありません"
    fi
    
    # Check .obsidian folder
    [ -d "$VAULT_DIR/.obsidian" ] && check_pass ".obsidian 設定フォルダ" || check_warn ".obsidian がありません"
else
    check_fail "Obsidian Vault が見つかりません"
fi

echo ""

# Section 4: Tools
echo "═══════════════════════════════════════════"
echo "🛠️ ツール"
echo "═══════════════════════════════════════════"

TOOL_COUNT=$(find "$WORKSPACE/bin" -type f \( -name "*.sh" -o -name "*.js" \) 2>/dev/null | wc -l | tr -d ' ')
if [ "$TOOL_COUNT" -gt 0 ]; then
    check_pass "$TOOL_COUNT 個のツール"
else
    check_warn "ツールがありません"
fi

# Check if tools are executable
NON_EXEC=$(find "$WORKSPACE/bin" -type f \( -name "*.sh" \) ! -executable 2>/dev/null | wc -l | tr -d ' ')
if [ "$NON_EXEC" -eq 0 ]; then
    check_pass "全シェルスクリプト実行可能"
else
    check_warn "$NON_EXEC 個のスクリプトが実行不可"
fi

echo ""

# Section 5: Memory
echo "═══════════════════════════════════════════"
echo "🧠 メモリ"
echo "═══════════════════════════════════════════"

MEMORY_FILES=$(find "$WORKSPACE/memory" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
if [ "$MEMORY_FILES" -gt 0 ]; then
    check_pass "$MEMORY_FILES 個のメモリファイル"
else
    check_warn "メモリファイルがありません"
fi

# Check recent memory
RECENT_MEMORY=$(find "$WORKSPACE/memory" -name "*.md" -type f -mtime -7 2>/dev/null | wc -l | tr -d ' ')
if [ "$RECENT_MEMORY" -gt 0 ]; then
    check_pass "過去7日間に $RECENT_MEMORY 件の更新"
else
    check_warn "過去7日間の更新なし"
fi

echo ""

# Section 6: Disk Usage
echo "═══════════════════════════════════════════"
echo "💾 ディスク使用量"
echo "═══════════════════════════════════════════"

WORKSPACE_SIZE=$(du -sh "$WORKSPACE" 2>/dev/null | cut -f1)
echo "  📁 ワークスペース: $WORKSPACE_SIZE"

if [ -d "$VAULT_DIR" ]; then
    VAULT_SIZE=$(du -sh "$VAULT_DIR" 2>/dev/null | cut -f1)
    echo "  📚 Obsidian Vault: $VAULT_SIZE"
fi

echo ""

# Summary
echo "═══════════════════════════════════════════"
echo "📊 サマリー"
echo "═══════════════════════════════════════════"
echo ""

if [ "$ISSUES" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo "  🎉 すべて正常です！"
elif [ "$ISSUES" -eq 0 ]; then
    echo "  ⚠️ $WARNINGS 件の警告"
else
    echo "  ❌ $ISSUES 件の問題 / ⚠️ $WARNINGS 件の警告"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    チェック完了 ✓                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
