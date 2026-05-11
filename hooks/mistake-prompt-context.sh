#!/bin/bash
# 실수 예방 UserPromptSubmit 훅 — 컨텍스트 주입
# 활성 패턴 상위 3개를 사용자 프롬프트에 주입
# 컨텍스트 없으면 조용히 통과

CONTEXT_FILE="$HOME/.claude/mistakes/registry/compiled/prompt/context.jsonl"

if [ ! -f "$CONTEXT_FILE" ] || [ ! -s "$CONTEXT_FILE" ]; then
  # 컨텍스트 파일 없거나 비어있으면 주입 없음
  exit 0
fi

# 상위 3개 패턴을 알림 형식으로 stdout 출력
head -3 "$CONTEXT_FILE" | python3 -c "
import sys, json
patterns = []
for line in sys.stdin:
    line = line.strip()
    if line:
        try:
            p = json.loads(line)
            patterns.append(f\"- {p.get('message', '')}\")
        except json.JSONDecodeError:
            pass
if patterns:
    print('[실수 예방 알림] 최근 활성 패턴:')
    print('\n'.join(patterns))
" 2>/dev/null

# 미완료 검증 디렉티브 알림 — unresolved 큐에 파일 있으면 간략 주입
UNRESOLVED_DIR="$HOME/.claude/mistakes/registry/queue/unresolved"
if [ -d "$UNRESOLVED_DIR" ]; then
  COUNT=$(find "$UNRESOLVED_DIR" -maxdepth 1 -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$COUNT" -gt 0 ]; then
    echo "[검증 필수 알림] 미완료 검증 디렉티브 ${COUNT}건 — 작업 완료 전 evidence 기록 필요"
  fi
fi

exit 0
