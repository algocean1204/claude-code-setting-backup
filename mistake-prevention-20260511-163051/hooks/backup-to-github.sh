#!/bin/bash
# 세션 응답 종료 시 백업 폴더를 GitHub 에 push
set -uo pipefail

REPO="/Users/kimtaekyu/Documents/Develop_Fold/Claude-code-agent-backup"
LOG_FILE="$HOME/.claude/hooks/backup.log"
ts=$(date '+%Y-%m-%d %H:%M:%S')

if ! cd "$REPO" 2>/dev/null; then
    echo "[$ts] ERROR: cannot cd to $REPO" >> "$LOG_FILE"
    exit 0
fi

git -C "$REPO" add -A 2>>"$LOG_FILE"

if git -C "$REPO" diff --cached --quiet; then
    echo "[$ts] github backup: no changes" >> "$LOG_FILE"
    exit 0
fi

msg="auto-backup: $(date '+%Y-%m-%d %H:%M:%S')"

if git -C "$REPO" commit -m "$msg" >>"$LOG_FILE" 2>&1; then
    if git -C "$REPO" push origin main >>"$LOG_FILE" 2>&1 || true; then
        echo "[$ts] github backup: pushed — $msg" >> "$LOG_FILE"
    else
        echo "[$ts] github backup: commit ok, push FAILED — $msg" >> "$LOG_FILE"
    fi
else
    echo "[$ts] ERROR: commit failed" >> "$LOG_FILE"
fi

exit 0
