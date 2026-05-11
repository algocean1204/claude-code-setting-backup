# Phase 3.5 — Verification Directive Contract

## 개요

핵심 문제: 모델이 검증 없이 완료를 주장할 수 있다.
VerificationDirective는 "검증 지시", VerificationEvidence는 "검증 증거"다.
증거 없는 완료 선언은 경고(observe-only) 처리한다. Phase 4에서 차단으로 전환한다.
신뢰 경계 원칙: **모델의 말은 증거가 아니다.** 시스템이 직접 생성한 데이터만 증거로 인정한다.

## Part A: 스키마 요약

### VerificationDirective (20 fields)

```jsonc
{
  "directive_id": "vd-<ulid>",           // 시스템 생성
  "goal_summary": "string",              // 검증 목표 요약
  "scope": {
    "files_to_check": ["path/to/file"],  // git diff 기반 — agent 주장 아님
    "test_commands": ["pytest tests/"],  // 실행할 명령 목록
    "acceptance_criteria": ["string"]    // 통과 기준
  },
  "risk_tier": "low|medium|high|critical",
  "verifier_chain": [                    // 검증 단계 DAG (단순화, Codex 피드백 반영)
    {"step": "lint",  "depends_on": []},
    {"step": "test",  "depends_on": ["lint"]},
    {"step": "build", "depends_on": ["test"]}
  ],
  "changed_files": ["path/to/file"],     // git diff --name-only 실행 결과 — agent 주장 금지
  "max_runtime_sec": 120,
  "created_at": "ISO8601",
  "status": "pending|running|verified|failed|blocked"
}
```

### VerificationEvidence (13 fields)

```jsonc
{
  "evidence_id": "ve-<ulid>",            // 시스템 생성
  "directive_id": "vd-<ulid>",
  "check_type": "syntax|test|lint|runtime|manual|integration",
  "executor": "system|model|hybrid",
  "raw_output_hash": "sha256:...",        // 레코더 래퍼가 생성 — 모델이 채우지 않음
  "pass": true,
  "findings": [                          // 실패 항목 목록
    {"finding_id": "f-<ulid>", "message": "string", "file": "...", "line": 0}
  ],
  "timestamp": "ISO8601",
  "duration_ms": 340
}
```

### RepairDirective (12 fields)

```jsonc
{
  "repair_id": "rd-<ulid>",
  "directive_id": "vd-<ulid>",
  "finding_id": "f-<ulid>",
  "repair_type": "auto_fix|manual_fix|config_change|rollback",
  "target_files": ["path/to/file"],
  "write_scope": ["path/to/file"],        // auto-fix 허용 범위 (이 외 파일 수정 금지)
  "risk_tier": "low|medium|high|critical",
  "proposed_fix": "string",
  "expected_verification": "string",
  "rollback_plan": "string",
  "auto_fix_allowed": true,
  "reason_if_not_auto_fixable": "string" // auto_fix_allowed=false 시 필수
}
```

---

## Part B: 상태 머신
```
EXECUTE
  │
  ▼
VERIFY ──────────────────────────────────────────────────────┐
  │                                                           │
  ▼                                                           │
findings_empty? ──YES──► COMPLETE                            │
  │ NO                                                        │
  ▼                                                           │
FINDINGS_FOUND                                               │
  │                                                           │
  ├─ AUTO_FIXABLE ──► REPAIR_PLANNED ──► REPAIR_EXECUTED ──► REVERIFY
  │                                                           │ (pass)
  │                                                           ▼
  │                                                        COMPLETE
  │
  ├─ NEEDS_USER_DECISION ──► BLOCKED_USER_DECISION
  ├─ UNSAFE_TO_FIX       ──► BLOCKED_UNSAFE
  ├─ ENVIRONMENT_BLOCKED ──► BLOCKED_BUDGET (외부 서비스 불가)
  └─ MODEL_LIMITATION    ──► BLOCKED_USER_DECISION (에스컬레이션)
```

### Finding 분류

| 분류 | 정의 | 처리 |
|---|---|---|
| AUTO_FIXABLE | syntax error, missing import, lint 위반, type annotation | auto-repair (최대 3회) |
| NEEDS_USER_DECISION | API contract 변경, 의존성 버전 충돌, 아키텍처 변경 | BLOCKED_USER_DECISION → 사용자 보고 |
| UNSAFE_TO_FIX | 타 팀 코드, 프로덕션 데이터, 보안 경계 | BLOCKED_UNSAFE → 즉시 에스컬레이션 |
| ENVIRONMENT_BLOCKED | 크리덴셜 없음, 외부 서비스 다운 | BLOCKED_BUDGET |
| MODEL_LIMITATION | 코드 이해 불가, 환각 출력 감지 | BLOCKED_USER_DECISION |

---

## Part C: 자동 수리 정책

1. **AUTO_FIXABLE finding만** auto-repair 허용
2. **최대 3회** REVERIFY 시도. 초과 시 BLOCKED_USER_DECISION
3. **동일 finding이 2회 반복** → 즉시 BLOCKED (루프 탈출 방지)
4. **write_scope 외 파일 수정 금지** — RepairDirective.write_scope 엄수
5. **중간 실패는 사용자에게 노출하지 않는다** — AUTO_FIXABLE 과정은 내부 처리
6. **최종 보고는 goal 중심**:
   - 달성한 것
   - 내부 자동 수리 횟수
   - 미해결 리스크
   - evidence 경로

---

## Part D: 훅 통합

### Stop Hook — evidence-gap 탐지 (observe-only)

`mistake-stop-gate.sh` 에 추가:

```python
# 코드 변경 있는데 VerificationEvidence 없으면 경고
changed = get_changed_files_from_git()  # git diff HEAD
evidences = load_evidences_for_session()
if changed and not evidences:
    warn("[VERIFY] 코드 변경 감지, 검증 증거 없음 — 완료 주장 불가 (observe-only)")
    record_event("evidence_gap", severity="P1", observe_only=True)
```

Phase 4에서 차단(deny)으로 전환 예정.

### UserPromptSubmit — context 주입 (300-600 token)

```json
{
  "additionalContext": "[VERIFICATION] 이번 작업은 VerificationDirective 생성 후 실행하십시오.\n변경된 파일: git diff 기반 추출 필수 (agent 주장 금지)\nchanged_files, raw_output_hash는 시스템 생성값입니다."
}
```

### PostToolUse — auto-repair 이벤트 기록

auto-repair 실행은 일반 MistakeEvent로 기록:

```python
record_event(
    category="verification",
    sub_type="auto_repair",
    directive_id="vd-...",
    finding_id="f-...",
    repair_attempt=1,
    result="pass|fail"
)
```

---

## Part E: 신뢰 경계 (Codex 피드백 반영)

| 항목 | 잘못된 방식 | 올바른 방식 |
|---|---|---|
| changed_files | agent가 "수정했다"고 보고한 파일 목록 사용 | `git diff --name-only HEAD` 실행 결과만 사용 |
| raw_output_hash | 모델이 hash 값을 직접 채움 | recorder 래퍼가 stdout을 캡처해 sha256 생성 |
| VerificationEvidence | 모델이 JSON 직접 생성 | 시스템(hook runner, recorder)이 생성, 모델은 읽기만 |
| 완료 판정 | 모델의 "완료했습니다" 발화 | evidence_id 존재 + pass=true 확인 후 판정 |

**observe-only 현황**: Phase 3.5는 경고만 발행한다. 차단(deny) 전환은 Phase 4에서 수행한다.

---

## 구현 파일 목록

```
~/.claude/mistakes/
  schema/
    verification-directive.schema.json  # VerificationDirective JSON Schema
    verification-evidence.schema.json   # VerificationEvidence JSON Schema
    repair-directive.schema.json        # RepairDirective JSON Schema
  bin/
    create_verification_directive.py    # VerificationDirective JSON 생성기
    record_verification_evidence.py     # VerificationEvidence 기록 (recorder 래퍼 포함)
  registry/
    directives/
      *.json                            # 세션별 VerificationDirective 로그
    evidence/
      *.json                            # VerificationEvidence 축적 (시스템 생성)
    queue/
      unresolved/
        *.json                          # 미해결 발견 사항 큐
```
