# 마이그레이션 계획 — 8단계

## 전제

- 기존 시스템은 모두 유지한다. 파괴적 변경 없음.
- 점진적 활성화. 각 단계마다 안정성 확인 후 다음 단계로 넘어간다.
- 기존 `PostToolUse` hooks (CHANGELOG + backup)은 그대로 유지한다.

## Phase 0: 백업 및 준비

```
작업:
  - 현재 ~/.claude/settings.json, agents/, rules/, hooks/ 전체 백업
  - 백업 위치: ~/Documents/Develop_Fold/Claude-code-agent-backup/ (기존 백업 경로 활용)

산출물:
  - 백업 완료 확인

위험: 없음 (읽기 전용)
```

## Phase 1: 저장소 구조 생성 (enforcement 없음)

```
작업:
  - ~/.claude/mistakes/ 전체 디렉토리 트리 생성
  - schema/*.json 생성 (event, pattern, compiled-rule)
  - bin/*.py 스크립트 생성 (hook_runner, record_event, compile_rules, maintenance)
  - 빈 compiled rule 파일 생성 (pretool/*.jsonl — 빈 JSONL)

산출물:
  - 완전한 디렉토리 구조
  - 실행 가능한 bin scripts (테스트 가능)

위험: 없음 (파일 생성만, 기존 시스템 변경 없음)
```

## Phase 2: 기존 Feedback Memory Import

```
작업:
  - import_feedback_memories.py 실행
  - 6개 프로젝트 feedback_*.md → registry/candidates/*.json 변환
  - ~80개 글로벌 메모리 중 feedback 타입만 선별 import
  - 원본 memory 파일은 삭제하지 않음 (provenance 보존)

산출물:
  - candidates/*.json (초기 후보 패턴)
  - import 보고서

위험: 낮음 (읽기 + 새 파일 생성만, 기존 memory 변경 없음)
```

## Phase 3: PostToolUse + UserPromptSubmit 관찰 모드 활성화

```
작업:
  - settings.json에 PostToolUse hook 추가 (기존 Write|Edit hook 유지)
  - settings.json에 UserPromptSubmit hook 추가
  - 모든 hook는 관찰(observe) 모드 — event 기록만, 차단 없음
  - UserPromptSubmit는 context 주입 시작 (상위 3 패턴)

산출물:
  - events/*.jsonl에 이벤트 축적 시작
  - 사용자 프롬프트에 active pattern context 주입

위험: 낮음 (차단 없음, 기록만)

검증: 1주일 운영 후 event log 검토, latency 측정
```

## Phase 4: PreToolUse:Bash P0 차단 활성화

```
작업:
  - PreToolUse:Bash hook 활성화
  - destructive_bash.json 패턴 등록 (rm -rf, force push, git reset --hard)
  - P0 deny 적용 (즉시 차단)

산출물:
  - destructive Bash 명령 실시간 차단
  - 차단 이벤트 기록

위험: 중간 (정당한 rm 명령이 차단될 수 있음)

검증: FP rate 모니터링. 5% 초과 시 signal 조정
```

## Phase 5: PreToolUse:Edit/Write P1 Ask 활성화

```
작업:
  - PreToolUse:Edit|Write|MultiEdit hook 활성화
  - workaround, stub, scope 패턴 등록
  - P1 ask 적용 (경고 + 사유 설명 요구)

산출물:
  - 코드 품질 위반 실시간 경고
  - 경고 이벤트 기록

위험: 중간 (정당한 TODO 주석이 false positive 될 수 있음)

검증: 2주일 운영 후 FP rate 측정, precision 0.85 미만이면 signal 조정
```

## Phase 6: Curator 에이전트 팀 추가

```
작업:
  - 4개 에이전트 정의 파일 생성 (agents/*.md)
  - 01-team-invocation.md 업데이트 (Team Registry, Whitelist)
  - 02-phase-orchestration.md 업데이트 (Cross-Phase Ambient Team)
  - 00-quick-reference.md 업데이트
  - Stop hook에 curation queue trigger 추가

산출물:
  - curator team 운영 시작
  - 30일 축적 데이터 기반 첫 큐레이션 실행

위험: 낮음 (큐레이션은 비파괴적, 제안만)
```

## Phase 7: 승격 파이프라인 활성화

```
작업:
  - promotion queue 처리 로직 활성화
  - proposals/conditional/ 및 proposals/always/ 생성 시작
  - 사용자에게 승격 제안 알림 메커니즘 구현

산출물:
  - 첫 conditional rule 승격 제안
  - 승격 workflow 운영

위험: 낮음 (자동 적용 없음, 제안만)
```

## Phase 8: SessionStart 유지보수 + Demotion 활성화

```
작업:
  - SessionStart hook 활성화 (공식 지원 확인 후)
  - maintenance.py 하루 1회 실행
  - demotion candidate 자동 플래그
  - event 로테이션 (90일 gzip, 180일 archive)

산출물:
  - 자가 유지 시스템 완성
  - 불필요한 규칙 자동 강등 제안

위험: 낮음

대안: SessionStart hook 미지원 시 launchd plist로 대체 (하루 1회 maintenance.py 실행)
```

## 기존 시스템 통합 정밀 충돌 분석

### requirements-guardian과의 관계

충돌 없음.

- guardian 역할: "이번 Phase에서 요구사항을 어겼는가" (현재 시제)
- curator 역할: "이 위반 유형이 반복되는가, 다음부터 어떻게 막을 것인가" (과거→미래)

통합 지점: guardian이 P1+ 위반 감지 시 `record_event.py`를 호출하여 이벤트를 기록한다. guardian agent 정의에 `MISTAKE_EVENT` emit 프로토콜을 추가한다. guardian은 registry를 읽지 않는다 (독립성 유지).

### subagent-monitor와의 관계

중복 위험 있음. 해결책이 필요하다.

- subagent-monitor 역할: SRP, workaround, 디렉토리 경계 실시간 감시 (현재 시제)
- curator 역할: 반복 품질 실수의 정책 자산화 (과거→미래)

중복 영역은 workaround 패턴 탐지다. subagent-monitor는 구현 중 실시간 감시 후 리더에게 보고하고, `PreToolUse` hook은 도구 실행 전에 차단한다. 둘 다 `@ts-ignore`를 감지하지만 시점이 다르다.

해결: hook은 도구 실행 전 차단(선제적), monitor는 도구 실행 후 맥락 있는 감시(후행적, 더 정밀). 둘 다 event를 기록하되 dedup은 curator가 처리한다.

### quality-judge와의 관계

충돌 없음.

- quality-judge 역할: 산출물 최종 점수화 (독립 평가)
- curator 역할: escape defect 기록 및 recurrence 계산

통합 지점: judge가 S등급 미만 항목을 `record_event.py`로 기록한다. curator는 judge 결과에 개입하지 않는다 (독립성 유지).

### /learn gstack skill과의 관계

일부 중복. 공존 처리.

- `/learn` 역할: narrative memory — "이 프로젝트에서는 이렇게 하면 잘 됐다"
- registry 역할: operational policy — "이 실수가 반복되니까 hook으로 막자"

통합: `/learn` 결과는 candidate source로 import만 한다. `/learn`이 기록한 패턴 중 prevention 가능한 것만 curator가 선별한다. `/learn`은 기존대로 계속 운영한다.

### feedback_*.md와의 관계

대체가 아닌 공존이다.

현재 `feedback memory`가 실수의 유일한 기록이다. 전환 후에는 registry가 source-of-truth가 되고 memory는 provenance로 보존된다.

처리: `import_feedback_memories.py`가 기존 memory를 candidates로 변환한다. 원본 memory 파일은 삭제하지 않는다. 새로운 실수는 registry에 직접 기록된다. memory 시스템은 기존대로 사용자 피드백 기록용으로 유지한다.

### 99-superpowers-extraction.md와의 관계

흡수하지 않는다.

3-fail rule, 자기 합리화 패턴 감지는 "원칙"이다. registry는 그 원칙을 "숫자로 실행"하는 도구다.

처리: `99-superpowers-extraction.md`는 그대로 유지(참고 원칙). registry의 `architecture` 카테고리가 3-fail rule을 실행한다 — 동일 패턴 3회 반복 시 severity 자동 상승 + 아키텍처 리뷰 trigger.

## settings.json 최종 변경 사항

기존 설정은 그대로 유지하면서 아래를 추가한다:

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash", "hooks": [{"type": "command", "command": "~/.claude/hooks/mistake-pretool.sh", "timeout": 2}]},
      {"matcher": "Edit|MultiEdit|Write", "hooks": [{"type": "command", "command": "~/.claude/hooks/mistake-pretool.sh", "timeout": 2}]},
      {"matcher": "Agent|Task", "hooks": [{"type": "command", "command": "~/.claude/hooks/mistake-pretool.sh", "timeout": 2}]}
    ],
    "PostToolUse": [
      {"matcher": "Write|Edit", "hooks": ["기존 CHANGELOG + 백업 유지"]},
      {"matcher": "Bash|Edit|MultiEdit|Write|Agent|Task", "hooks": [{"type": "command", "command": "~/.claude/hooks/mistake-posttool.sh", "timeout": 2}]}
    ],
    "UserPromptSubmit": [
      {"hooks": [{"type": "command", "command": "~/.claude/hooks/mistake-prompt-context.sh", "timeout": 2}]}
    ],
    "Stop": [
      {"hooks": [{"type": "command", "command": "~/.claude/hooks/mistake-stop-gate.sh", "timeout": 3}]}
    ]
  }
}
```

`SubagentStop`과 `SessionStart`는 공식 지원 확인 후 추가한다.

## 새 규칙 파일

`~/.claude/rules/always/11-mistake-prevention-control-plane.md` (80-120줄):

- Mistake registry 위치와 구조 설명
- Hook 예방 원칙
- `MISTAKE_EVENT` emit 프로토콜
- Promotion은 user approval 전 적용 금지
- P0/P1 unresolved event 존재 시 완료 선언 금지
- Curator team trigger signal 정의

## 결정 보류 사항 (구현 시 확인 필요)

1. `SessionStart` hook 공식 지원 여부 — 미지원 시 launchd plist로 대체
2. `SubagentStop` hook 공식 지원 여부 — 미지원 시 `Stop` hook에서 대체 처리
3. `PreToolUse` hook의 정확한 stdin JSON 구조 — 공식 docs 확인 필요
4. 기존 `PostToolUse` hook과 신규 `PostToolUse` hook의 실행 순서 — matcher 우선순위 테스트 필요
