# Layer 6: Mistake Intelligence Control Plane — 아키텍처

## 6-Layer 전체 구조

```
Layer 1: Static Rules         ← compiled rules가 conditional/always로 승격
Layer 2: Runtime Monitoring   ← event emit (MISTAKE_EVENT 시그널)
Layer 3: Hooks                ← compiled rules 소비, allow/ask/deny 실행
Layer 4: Memory               ← feedback provenance 보존, candidate source
Layer 5: Verification         ← escape defect 기록, 품질 점수 제공
Layer 6: Mistake Intelligence ← event 수집 → 패턴 정규화 → 정책 컴파일 → 승격 제안
```

## 데이터 플로우

```
Claude tool call
  → PreToolUse hook
    → compiled rule match
    → allow / ask / deny
    → event append (if matched)

Tool 실행 결과
  → PostToolUse hook
    → evidence scan
    → event append

Monitors / validators / quality-judge
  → record_event.py
    → events/*.jsonl

Stop
  → unresolved event gate
  → curation queue 생성

mistake-registry-curator-lead (trigger 시)
  → taxonomy analyst (event clustering, 분류)
  → prevention engineer (hook rule 변환 가능 여부)
  → promotion auditor (always/conditional 승격 심사)
  → candidate/pattern/proposal 산출

compile_rules.py (pattern 변경 후)
  → compiled/*.jsonl

다음 세션/tool call
  → hooks가 compiled rules 적용
```

## 파일 트리

```
~/.claude/mistakes/
├── schema/
│   ├── event.schema.json            # JSONL 이벤트 스키마 정의
│   ├── pattern.schema.json          # 패턴 레지스트리 스키마
│   └── compiled-rule.schema.json    # 컴파일된 룰 스키마
├── events/
│   ├── global/
│   │   └── 2026-05.jsonl            # 월별 글로벌 이벤트 로그 (append-only)
│   └── projects/
│       └── <project_hash>/
│           └── 2026-05.jsonl        # 프로젝트별 이벤트 로그
├── registry/
│   ├── patterns/                    # 카테고리별 canonical 패턴
│   │   ├── scope_control/
│   │   │   └── no_workaround_strict.json
│   │   ├── verification/
│   │   │   └── pytest_guard.json
│   │   ├── tool_safety/
│   │   │   └── destructive_bash.json
│   │   ├── requirement_adherence/
│   │   ├── architecture/
│   │   ├── runtime_resource/
│   │   ├── delegation_protocol/
│   │   ├── external_info/
│   │   ├── code_quality/
│   │   └── security_privacy/
│   ├── candidates/                  # 아직 확정 안 된 후보 패턴
│   │   └── <candidate_id>.json
│   └── retired/                     # 비활성화된 패턴
│       └── <pattern_id>.json
├── compiled/                        # hook engine이 읽는 빠른 룰셋
│   ├── pretool/
│   │   ├── Bash.jsonl
│   │   ├── Edit.jsonl
│   │   ├── MultiEdit.jsonl
│   │   ├── Write.jsonl
│   │   └── Agent.jsonl
│   ├── prompt/
│   │   └── context_rules.jsonl
│   ├── stop/
│   │   └── stop_rules.jsonl
│   └── subagent_stop/
│       └── default.jsonl
├── aggregates/
│   └── pattern_stats.json           # 자동 산출 통계 (수동 편집 금지)
├── queue/
│   ├── curation/                    # 큐레이션 대기 큐
│   │   └── <queue_id>.json
│   └── promotion/                   # 승격 대기 큐
│       └── <queue_id>.json
├── proposals/                       # 규칙 승격 제안서
│   ├── conditional/
│   │   └── <proposal>.md
│   └── always/
│       └── <proposal>.md
└── bin/                             # 실행 스크립트
    ├── hook_runner.py               # hook entrypoint (PreToolUse/PostToolUse 판정)
    ├── record_event.py              # 이벤트 기록 유틸리티
    ├── compile_rules.py             # pattern → compiled rule 변환
    ├── import_feedback_memories.py  # 기존 feedback memory 마이그레이션
    └── maintenance.py               # 로테이션, demotion, stats 갱신
```

## Project Overlay 구조

글로벌 레지스트리 외에 프로젝트별 특수 규칙을 지원한다.

```
$PROJECT/.claude/mistakes/
├── registry/patterns/*.json    # 프로젝트 전용 패턴
├── compiled/*.jsonl            # 프로젝트 전용 컴파일 룰
└── project-policy.json         # 프로젝트별 정책 오버라이드
```

Hook은 project overlay를 먼저 읽고, global을 뒤에 읽는다.

## Context Window 관리

| Component | Context 비용 | 로딩 방식 |
|---|---|---|
| `11-mistake-prevention-control-plane.md` (새 규칙) | 80-120줄, ~1,200 words | always-loaded |
| compiled rules | 0 tokens | disk-only, hook이 직접 읽음 |
| UserPromptSubmit context injection | 300-600 tokens/세션 | top 3 active patterns만 |
| pattern registry | 0 tokens | agent가 필요 시만 읽음 |
| event log | 0 tokens | bin scripts만 접근 |
