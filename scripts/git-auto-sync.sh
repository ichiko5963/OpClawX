#!/bin/bash
# git-auto-sync - 自动同步Git仓库

set -e

WORKSPACE="/Users/ai-driven-work/Documents/OpenClaw-Workspace"
LOG_FILE="$HOME/.logs/git-auto-sync.log"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

cd "$WORKSPACE"

log "开始同步..."

# 添加SSH密钥到agent（如果需要）
export GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=accept-new"
if [ -z "$SSH_AUTH_SOCK" ]; then
    eval "$(ssh-agent -s)" > /dev/null 2>&1
    ssh-add ~/.ssh/id_ed25519 2>/dev/null || true
fi

# 获取远程更改
if git fetch origin >> "$LOG_FILE" 2>&1; then
    log "成功获取远程更改"
else
    log "错误：无法获取远程更改"
    exit 1
fi

# 检查本地是否有未提交的更改
if git diff-index --quiet HEAD --; then
    # 没有未提交的更改
    log "没有本地更改需要推送"
else
    # 有未提交的更改，自动提交并推送
    git add -A
    git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M')" >> "$LOG_FILE" 2>&1
    
    if git push origin main >> "$LOG_FILE" 2>&1; then
        log "成功推送到远程仓库"
    else
        log "错误：无法推送到远程仓库"
        exit 1
    fi
fi

log "同步完成"
exit 0
