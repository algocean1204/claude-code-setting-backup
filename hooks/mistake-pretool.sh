#!/bin/bash
# 실수 예방 PreToolUse 훅 — observe-only 모드
# stdin으로 도구 입력 JSON을 받아 hook_runner.py로 전달
# 현재: 항상 allow 반환 (관찰만, 차단 없음)
# 실패 시 조용히 통과 (fail-open)

RUNNER="$HOME/.claude/mistakes/bin/hook_runner.py"

if [ ! -f "$RUNNER" ]; then
  # 러너 없으면 조용히 통과 — 절대 차단하지 않음
  exit 0
fi

# stdin을 hook_runner에 전달하고 결과를 stdout으로 반환
python3 "$RUNNER" < /dev/stdin 2>/dev/null || exit 0
