#!/usr/bin/env zsh
# git-auto-sync.sh - Auto commit and push all changes in OpenClaw-Workspace

set -e

WORKSPACE=~/Documents/OpenClaw-Workspace
cd "$WORKSPACE"

# Check if there are any changes
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo "Nothing to sync. Workspace is clean."
  exit 0
fi

# Stage all changes
git add -A

# Commit with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M JST')
git commit -m "Auto-sync: $TIMESTAMP"

# Push to remote
git push origin main

echo "Sync complete: $TIMESTAMP"
