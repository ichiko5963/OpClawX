#!/bin/bash
# OpenClaw-Workspace Git Auto Sync Script
# Documents内の本物のリポジトリを同期

REPO_DIR="$HOME/Documents/OpenClaw-Workspace"
LOG_FILE="$REPO_DIR/bin/git-sync.log"
TIMEOUT=30  # 30秒タイムアウト

cd "$REPO_DIR" || exit 1

# ログ関数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

# タイムアウト付きコマンド実行（Perl使用）
run_with_timeout() {
    local cmd="$1"
    local description="$2"
    
    log "Running: $description"
    
    # Perlでタイムアウト実装
    perl -e "
        use strict;
        use warnings;
        
        my \$timeout = $TIMEOUT;
        my \$cmd = q{$cmd};
        
        eval {
            local \$SIG{ALRM} = sub { die \"timeout\\n\" };
            alarm \$timeout;
            system(\$cmd);
            alarm 0;
        };
        
        if (\$@ eq \"timeout\\n\") {
            exit 124;  # timeout exit code
        } elsif (\$?) {
            exit \$? >> 8;
        }
        exit 0;
    " 2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -eq 0 ]; then
        log "✅ Success: $description"
        return 0
    elif [ $exit_code -eq 124 ]; then
        log "⏱️ Timeout (${TIMEOUT}s): $description"
        return 124
    else
        log "❌ Failed: $description (code: $exit_code)"
        return $exit_code
    fi
}

# Git設定確認
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log "❌ Not a git repository"
    exit 1
fi

# リモート確認（タイムアウト付き）
if ! run_with_timeout "git remote -v" "Check remote"; then
    log "⚠️ Remote check failed, skipping sync"
    exit 0
fi

# 変更があるか確認
CHANGES=$(git status --porcelain 2>/dev/null)

# 変更がなければPullだけ試す
if [ -z "$CHANGES" ]; then
    log "💤 No changes to commit"
    
    # Pullだけ試す（タイムアウト付き）
    if run_with_timeout "git pull --rebase" "Pull remote changes"; then
        log "✅ Pull successful"
    else
        log "⚠️ Pull failed or timeout, skipping"
    fi
    
    exit 0
fi

# ステージング（タイムアウト付き）
if ! run_with_timeout "git add -A" "Stage changes"; then
    log "❌ Failed to stage changes"
    exit 1
fi

# コミット
COMMIT_MSG="Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')"
if ! run_with_timeout "git commit -m \"$COMMIT_MSG\"" "Commit changes"; then
    log "❌ Failed to commit"
    exit 1
fi

# プッシュ（タイムアウト付き）
if ! run_with_timeout "git push origin main" "Push to remote"; then
    log "❌ Failed to push (may need manual intervention)"
    exit 1
fi

log "✅ Git auto-sync completed successfully"
