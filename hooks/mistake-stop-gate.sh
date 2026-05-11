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
# evidence-gap 감지 — directive_id 이벤트 중 evidence 없는 항목을 관찰 전용으로 기록
python3 -c "
import json,sys
from pathlib import Path
from datetime import date
ed=Path.home()/'.claude'/'mistakes'/'registry'/'events'
evd=Path.home()/'.claude'/'mistakes'/'registry'/'evidence'
gd=Path.home()/'.claude'/'mistakes'/'registry'/'queue'/'evidence-gaps'
tf=ed/f'{date.today().isoformat()}.jsonl'
if not tf.exists(): sys.exit(0)
# 오늘 이벤트에서 directive_id 수집
directives=set()
for l in tf.read_text().splitlines():
    if l.strip():
        try:
            ev=json.loads(l)
            did=ev.get('directive_id','')
            if did: directives.add(did)
        except: pass
if not directives: sys.exit(0)
gd.mkdir(parents=True,exist_ok=True)
for did in directives:
    ep=evd/did
    # evidence .json 없으면 gap 기록 (관찰 전용)
    if not (ep.is_dir() and any(ep.glob('*.json'))):
        gf=gd/f'{did.replace(\".\",\"_\")}.json'
        if not gf.exists():
            gf.write_text(json.dumps({'directive_id':did,
              'detected_date':date.today().isoformat(),
              'source':'stop_hook_evidence_gap','status':'observe_only'},
              ensure_ascii=False,indent=2))
" 2>/dev/null
exit 0
