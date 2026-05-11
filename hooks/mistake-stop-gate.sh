#!/bin/bash
# 실수 예방 Stop 훅 — 세션 종료 시 curation queue 갱신
# 동일 pattern_id 3회 이상 → 큐 추가. 항상 exit 0 반환
[ ! -d "$HOME/.claude/mistakes/registry/events" ] && exit 0
python3 -c "
import json,sys
from pathlib import Path
from collections import Counter
from datetime import date
ed=Path.home()/'.claude'/'mistakes'/'registry'/'events'
qd=Path.home()/'.claude'/'mistakes'/'registry'/'queue'/'curation'
tf=ed/f'{date.today().isoformat()}.jsonl'
if not tf.exists(): sys.exit(0)
c=Counter()
for l in tf.read_text().splitlines():
    if l.strip():
        try: c[json.loads(l).get('pattern_id','')]+=1
        except: pass
qd.mkdir(parents=True,exist_ok=True)
for pid,cnt in c.items():
    if cnt>=3 and pid:
        qf=qd/f'{pid.replace(\".\",\"_\")}.json'
        if not qf.exists():
            qf.write_text(json.dumps({'pattern_id':pid,'trigger_count':cnt,
              'trigger_date':date.today().isoformat(),'source':'stop_hook_threshold'},
              ensure_ascii=False,indent=2))
" 2>/dev/null
exit 0
