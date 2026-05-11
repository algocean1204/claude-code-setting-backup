#!/bin/bash
# Claude Code 설정 변경 시 로컬 백업 폴더로 rsync
# 백엔드 등 무관한 파일은 즉시 skip
set -uo pipefail

CLAUDE_ROOT="$HOME/.claude"
BACKUP_ROOT="/Users/kimtaekyu/Documents/Develop_Fold/Claude-code-agent-backup"
LOG_FILE="$CLAUDE_ROOT/hooks/backup.log"

# stdin JSON 에서 파일 경로 추출
payload=$(cat)
file_path=$(echo "$payload" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

if [ -z "$file_path" ]; then
    exit 0
fi

# 매칭 조건 (OR): agents/, rules/, skills/, hooks/, settings.json, CLAUDE.md
case "$file_path" in
    "$CLAUDE_ROOT"/agents/*|"$CLAUDE_ROOT"/rules/*|"$CLAUDE_ROOT"/skills/*|"$CLAUDE_ROOT"/hooks/*)
        ;;
    "$CLAUDE_ROOT"/settings.json|"$CLAUDE_ROOT"/CLAUDE.md)
        ;;
    *)
        exit 0
        ;;
esac

# 상대경로 계산
rel_path="${file_path#$CLAUDE_ROOT/}"
dst="$BACKUP_ROOT/$rel_path"

# 타겟 디렉토리 생성
mkdir -p "$(dirname "$dst")" 2>/dev/null

ts=$(date '+%Y-%m-%d %H:%M:%S')

# rsync 복사 (--mkpath 미지원 fallback 포함)
if rsync -a "$file_path" "$dst" 2>>"$LOG_FILE"; then
    echo "[$ts] local backup: $rel_path" >> "$LOG_FILE"
else
    echo "[$ts] ERROR: rsync failed for $rel_path" >> "$LOG_FILE"
fi

exit 0
