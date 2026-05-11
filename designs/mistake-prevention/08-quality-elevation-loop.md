# Phase 3.6 Quality Elevation Loop — Design Document

## 목적

Phase 3.5(정확성 레이어)를 통과한 구현이 단순히 "동작"하는 것을 넘어
사용자 의도 범위 내에서 품질을 끌어올리는 관찰 전용 레이어.

합격/불합격 이진 판정이 아닌 다차원 품질 관찰을 통해
증거에 기반한 발견(finding)만이 블로킹 근거가 됨.

---

## Phase 3.5와의 관계

```
Phase 3.5 (정확성) ← 선행 필수
  └─ 기능 동작, 회귀 없음, 스펙 충족 여부 검증

Phase 3.6 (품질 향상) ← 3.5 통과 후 진입
  └─ 품질 차원 관찰 → finding 수집 → disposition → 선택적 수리
  └─ 수리 발생 시 Phase 3.5 재검증 필수
```

3.5가 실패하면 3.6은 시작하지 않음.
3.6 수리 후에는 반드시 3.5로 되돌아가 재검증.

---

## 신뢰 경계 원칙

> "모델의 말은 증거가 아니다."

- 점수는 관찰 전용(observe-only). 점수 자체는 블로킹 불가.
- 블로킹은 오직 증거 기반 finding(upheld 처리된 것)으로만 가능.
- evidence 필드: 코드 라인, 메트릭 측정값, 도구 출력 등 구체적 참조 필수.
- "복잡해 보인다", "문제가 있을 수 있다" 같은 추정은 finding 불가.

---

## 5개 핵심 차원 (항상 활성)

| 차원 | 목적 |
|---|---|
| requirement_fidelity | 인수 기준 완전 이행 여부 |
| maintainability | 함수/파일 크기, 복잡도, 명명 |
| robustness | 예외 처리, 경계값, 외부 호출 안전성 |
| security_safety | 입력 검증, 권한, 민감 데이터 노출 |
| architecture_fit | 레이어 의존성 방향, SRP, 모듈 경계 |

---

## 조건부 차원 (활성화 조건 충족 시)

| 차원 | 활성화 조건 |
|---|---|
| performance | hot path, 대규모 워크로드, 동시성 시스템 |
| test_quality | 동작 변경, 버그 수정, 리팩터 포함 |
| accessibility | UI, TUI, 데스크탑, 웹 작업 |
| user_experience | UI, TUI, 데스크탑, CLI 흐름 변경 |
| documentation | public API, 배포, 사용자 대면 동작 변경 |

---

## 태스크 프로파일과 루브릭 선택

task_profile 문자열을 분석해 적용할 rubric_refs 결정.
루브릭 파일: `registry/quality/rubrics/*.json`

```
task_profile 예시:
  "backend API endpoint"   → base.json + performance.json + test_quality.json
  "React UI component"     → base.json + accessibility.json + user_experience.json
  "CLI tool"               → base.json + user_experience.json + documentation.json
  "database migration"     → base.json + test_quality.json + documentation.json
```

루브릭은 finding 생성 규칙만 정의. 점수 산출 규칙 없음.

---

## Finding Disposition 시스템

각 finding은 4가지 disposition 중 하나를 받음:

| Disposition | 의미 |
|---|---|
| upheld | 증거가 충분, 수리 권고 |
| dismissed | 증거 불충분 또는 context상 허용 (P0/P1 기각 시 기각 증거 필수) |
| needs_user | 사용자 의사결정 필요 (범위/트레이드오프) |
| deferred | 현재 작업 범위 외, 다음 작업으로 이월 |

---

## Scope Guard — 7개 불리언 판별자

수리 제안이 범위를 벗어나는지 판별:

```
1. changes_user_visible_behavior       → 사용자 체감 동작 변경 여부
2. adds_new_capability                 → 새 기능 추가 여부
3. changes_public_api_or_schema        → 공개 API/스키마 변경 여부
4. changes_architecture_boundary       → 아키텍처 경계 변경 여부
5. touches_files_outside_directive_scope → directive 범위 외 파일 수정 여부
6. required_to_satisfy_acceptance_criteria → 인수 기준 충족에 필수 여부
7. reduces_existing_risk_without_new_behavior → 신규 동작 없이 기존 위험 감소 여부
```

분류 규칙:

```
IN_SCOPE_REFINEMENT:
  (6=true AND 1~5 모두 false) OR
  (7=true AND 2=false AND 3=false)

NEEDS_USER_APPROVAL:
  1=true OR 2=true OR 3=true OR 4=true

REJECT_SCOPE_CREEP:
  5=true AND 6=false
```

---

## 리스크 티어별 적용

| Tier | 핵심 차원 | 조건부 차원 | 추가 조치 |
|---|---|---|---|
| LOW | 생략 또는 최소 관찰 | 없음 | 없음 |
| MEDIUM | 5개 관찰 전용 | 없음 | 없음 |
| HIGH | 5개 전체 | 해당되는 모든 조건부 | 없음 |
| CRITICAL | 5개 전체 | 해당되는 모든 조건부 | 독립 검증자 + Phase 3.5 재검증 |

---

## quality-judge 관계

- Phase 3.6: finding 수준 품질 검증 (루브릭 기반, 자동)
- quality-judge: 최종 독립 판단 (사람 판단 대리, 통합 시각)

quality-judge의 finding도 동일하게 증거 기반이어야 함.
quality-judge = Phase 3.6 결과를 검토하고 최종 승인/거부 결정.
Phase 3.6이 quality-judge를 대체하지 않음.

---

## 관찰 전용 롤아웃 계획

| 단계 | 이름 | 내용 |
|---|---|---|
| 3.6a | Observe | finding 수집, disposition 없음, 블로킹 없음 |
| 3.6b | P0 Block | upheld P0 finding만 블로킹 가능 |
| 3.6c | Evidence-backed Block | upheld + 증거 확인된 P0/P1 블로킹 |
| 3.6d | Calibrated | 전체 disposition 시스템 + scope guard 활성 |

현재 롤아웃: **3.6a (observe-only)**

---

## 구현 파일 목록

```
~/.claude/designs/mistake-prevention/
  08-quality-elevation-loop.md          ← 이 파일

~/.claude/mistakes/schema/
  quality-directive.schema.json
  quality-finding.schema.json
  finding-disposition.schema.json
  scope-guard-decision.schema.json

~/.claude/mistakes/registry/quality/
  directives/    ← quality-directive 인스턴스
  findings/      ← quality-finding 인스턴스
  dispositions/  ← finding-disposition 인스턴스
  scope-guard/   ← scope-guard-decision 인스턴스
  rollups/       ← directive별 집계 요약
  rubrics/       ← 루브릭 정의 JSON
    base.json
    performance.json
    test_quality.json
    accessibility.json
    user_experience.json
    documentation.json
```
