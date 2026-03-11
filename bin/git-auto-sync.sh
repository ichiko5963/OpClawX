#!/usr/bin/env zsh
# git-auto-sync.sh - Auto stage, commit, and push workspace changes

set -euo pipefail

REPO_DIR=~/Documents/OpenClaw-Workspace
LOG_FILE="$REPO_DIR/bin/git-sync.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M JST')

log() {
  echo "$1"
  echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

cd "$REPO_DIR"

log "=== Git Auto Sync: $TIMESTAMP ==="

# Check for changes (staged, unstaged, or untracked)
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  log "✅ No changes to commit."
  exit 0
fi

log "Running: Stage changes"
git add -A
log "✅ Success: Stage changes"

log "Running: Commit changes"
git commit -m "Auto-sync: $TIMESTAMP" || {
  log "ℹ️ Nothing to commit after staging."
  exit 0
}
log "✅ Success: Commit changes"

log "Running: Pull rebase before push"
git pull --rebase origin main 2>&1 | tee -a "$LOG_FILE" || {
  log "❌ Pull rebase failed. Skipping push."
  exit 1
}
log "✅ Success: Pull rebase"

log "Running: Push to remote"
git push origin main 2>&1 | tee -a "$LOG_FILE"
log "✅ Success: Push to remote"

log "=== Sync complete ==="
