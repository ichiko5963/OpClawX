#!/bin/bash
# Auto-sync script for OpenClaw-Workspace (conflict resolution: remote wins)

WORKSPACE="/Users/ai-driven-work/Documents/OpenClaw-Workspace"
cd "$WORKSPACE" || exit 1

# Fetch latest from GitHub
git fetch origin main

# Add any local changes first
git add -A

# Commit local changes if any
if ! git diff-index --quiet HEAD --; then
    git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M')"
fi

# Pull with automatic conflict resolution (remote wins)
git pull origin main --rebase -X theirs || {
    # If rebase fails, abort and force remote version
    git rebase --abort
    git reset --hard origin/main
    echo "Conflict resolved: remote version applied"
}

# Push to GitHub
git push origin main || {
    # If push fails (e.g., force-push needed), force it
    git push origin main --force-with-lease
}

echo "Sync completed at $(date)"
