#!/bin/bash
# Auto-sync script for OpenClaw-Workspace

WORKSPACE="/Users/ai-driven-work/Documents/OpenClaw-Workspace"
cd "$WORKSPACE" || exit 1

# Pull latest from GitHub
git pull origin main --rebase

# Add any local changes
git add -A

# Check if there are changes to commit
if ! git diff-index --quiet HEAD --; then
    # Commit with timestamp
    git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M')"
    
    # Push to GitHub
    git push origin main
fi

echo "Sync completed at $(date)"
