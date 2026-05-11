# 저장소 구조 및 Pattern Registry

## 위치 결정

`~/.claude/mistakes/` (글로벌)

- `~/.gstack/mistakes/`는 gstack 전용이 되어 범용성이 상실됨
- project-level only는 cross-project recurrence 추적 불가
- `~/.claude/` 하위가 하네스 인프라의 표준 위치

## Event Schema

```json
{
  "ts": "2026-05-11T09:12:00+09:00",
  "session_id": "abc-123",
  "project_hash": "macbot-7f3a",
  "pattern_id": "scope_control.no_workaround_strict",
  "source": "requirements-guardian",
  "phase": "Phase2",
  "severity": "P1",
  "confidence": 0.82,
  "surface": "Edit",
  "file": "src/core/auth.ts",
  "tool_input_summary": "Edit on src/core/auth.ts adding @ts-ignore",
  "outcome": "blocked",
  "resolution": "rewritten_to_match_requirement",
  "agent": "web-frontend"
}
```

## Pattern Schema

```json
{
  "id": "scope_control.no_workaround_strict",
  "category": "scope_control",
  "severity": "P1",
  "status": "active",
  "title": "요구사항 우회 구현 금지",
  "failure_mode": "명시 요구 대신 더 쉬운 대체 구현을 수행함",
  "detection": {
    "surfaces": ["PreToolUse:Edit", "PreToolUse:Write", "PostToolUse:Task"],
    "signals": ["workaround", "fallback", "temporary", "TODO: replace"],
    "signal_type": "keyword_regex",
    "precision": "medium",
    "cost": "cheap"
  },
  "prevention": {
    "action": "ask",
    "message": "우회 구현 의심. 원 요구사항 충족 방식인지 증거를 제시하거나 사용자 확인 필요.",
    "allowed_resolution": ["원 요구사항 그대로 구현", "명시 승인 받은 scope change"]
  },
  "solution": {
    "canonical_fix": "요구사항-구현 trace를 먼저 작성하고, 대체안은 승인 전 적용하지 않음",
    "verification": ["requirements_trace_exists", "no_unapproved_scope_change"]
  },
  "stats": {
    "occurrences_30d": 4,
    "distinct_sessions_30d": 3,
    "last_seen": "2026-05-10",
    "false_positive_rate": 0.12,
    "escape_rate": 0.05,
    "prevented_count": 7
  },
  "promotion": {
    "state": "candidate",
    "target": "conditional_rule",
    "reason": "반복성과 심각도는 충분하나 false positive 검토 필요"
  },
  "provenance": {
    "original_memory": "feedback_no_workaround_strict.md",
    "created": "2026-05-11",
    "last_modified": "2026-05-11",
    "created_by": "import_feedback_memories.py"
  }
}
```

## Compiled Rule Schema

```json
{
  "pattern_id": "scope_control.no_workaround_strict",
  "severity": "P1",
  "severity_rank": 2,
  "action": "ask",
  "message": "우회 구현 의심: @ts-ignore 또는 eslint-disable 감지. 원 요구사항 충족 방식인지 확인 필요.",
  "scope": {
    "file_pattern": "*.ts|*.tsx|*.js|*.jsx",
    "exclude": ["node_modules/**", "dist/**"]
  },
  "signals": [
    {"type": "content_regex", "pattern": "@ts-ignore|@ts-expect-error|eslint-disable|noqa"},
    {"type": "content_regex", "pattern": "as\\s+any"},
    {"type": "content_keyword", "words": ["!important"]}
  ]
}
```

## Taxonomy (10종 분류)

| Category ID | 이름 | 예시 패턴 |
|---|---|---|
| `scope_control` | 범위 통제 | 지시 외 구현, workaround, 과잉 리팩터 |
| `requirement_adherence` | 요구 준수 | 요구 누락, 출력 계약 위반 |
| `verification` | 검증 | 테스트 미실행, fake pass, 샘플링 검증 |
| `tool_safety` | 도구 안전 | destructive command, force push, broad delete |
| `architecture` | 아키텍처 | SRP 위반, 3-fail rule, 임시 패치 반복 |
| `runtime_resource` | 런타임 자원 | pytest zombie, port/process leak, RAM 초과 |
| `delegation_protocol` | 위임 프로토콜 | 필수 subagent/monitor 누락, 단독 스폰 |
| `external_info` | 외부 정보 | 최신성 확인 누락, 출처 없는 답변 |
| `code_quality` | 코드 품질 | stub, TODO, NotImplemented, dead path |
| `security_privacy` | 보안/개인정보 | secret 노출, 권한 우회, `.env` 커밋 |

## 데이터 로테이션 정책

| 데이터 | 보존 기간 | 처리 |
|---|---|---|
| Raw JSONL events | 90일 | gzip 압축 |
| 90일 초과 Raw | 180일 | aggregate만 남기고 archive |
| `pattern_stats.json` | 영구 | 계속 갱신 |
| Compiled rules | 영구 | pattern 변경 시 재생성 |
| Retired patterns | 영구 | `retired/` 디렉토리에 보존 |

## 읽기/쓰기 권한

| Component | 권한 |
|---|---|
| Hook scripts (`hook_runner.py`) | events append, queue append (read compiled rules) |
| `record_event.py` | events append only |
| `compile_rules.py` | `compiled/*` overwrite |
| Curator team agents | `candidates/`, `patterns/`, `proposals/` write |
| `maintenance.py` | stats 갱신, retired 이동, event 로테이션 |
| 사용자 | active/promotion 최종 승인 |
| 기존 monitors | `record_event.py` 호출로 append only |
