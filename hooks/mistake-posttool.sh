#!/bin/bash
# 실수 예방 PostToolUse 훅 — 이벤트 기록 전용
# 도구 실행 결과를 관찰하고 이벤트로 기록
# 항상 exit 0 반환 (관찰만, 차단 없음)

RECORDER="$HOME/.claude/mistakes/bin/record_event.py"
[ ! -f "$RECORDER" ] && exit 0

# stdin → 기본 이벤트 JSON 생성 → record_event.py에 전달
python3 -c "
import json,sys
from datetime import datetime,timezone
raw=sys.stdin.read().strip()
if not raw: sys.exit(0)
try: data=json.loads(raw)
except: sys.exit(0)
evt={'ts':datetime.now(timezone.utc).isoformat(),'session_id':'unknown',
  'pattern_id':'posttool.observation','source':'PostToolUse','severity':'P2',
  'surface':data.get('tool_name','unknown').lower(),'outcome':'observed',
  'tool_output_summary':json.dumps(data,ensure_ascii=False)[:200]}
print(json.dumps(evt,ensure_ascii=False))
" 2>/dev/null | python3 "$RECORDER" 2>/dev/null
exit 0
