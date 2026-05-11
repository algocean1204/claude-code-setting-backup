# 승격 파이프라인 — 전체 Lifecycle

## 7단계 Lifecycle

### 1. Event Observed (이벤트 관측)

hook 또는 monitor가 `record_event.py`로 JSONL append한다. 원시 관측 사실만 기록하며 해석/판단은 없다.

### 2. Pattern Candidate (패턴 후보 생성)

Stop hook이 threshold를 감지하면 (동일 `pattern_id` 3회 이상) `queue/curation/*.json`을 생성한다. 사용자가 명시 요청해도 생성된다.

### 3. Curator Team Analysis (큐레이션 팀 분석)

`curator-lead`가 3 specialists를 병렬 스폰한다.

- `taxonomy-analyst`: 분류, severity, confidence 정규화
- `prevention-engineer`: hook rule 변환 가능 여부, detection 설계
- `promotion-auditor`: 충돌, FP rate, context cost 심사

결과: `candidates/*.json` 생성

### 4. Active Pattern (활성 패턴 등록)

- P2 observe/context-only는 auto-active 가능 (사용자 확인 없이)
- P1 ask/deny, P0 deny는 사용자 승인 필요
- `registry/patterns/{category}/{id}.json`에 저장

### 5. Compiled Rule (컴파일된 룰 배포)

`compile_rules.py`가 `registry/patterns/*.json`을 읽어 `compiled/pretool/*.jsonl`로 변환한다. deterministic script만 compiled 파일을 작성하며 agent는 직접 작성 불가. 다음 hook 실행부터 즉시 적용된다.

### 6. Conditional/Always Rule Proposal (규칙 승격 제안)

`proposals/conditional/*.md` 또는 `proposals/always/*.md`를 생성한다. proposal 내용에는 frequency, escape count, FP rate, context cost, exact diff가 포함된다. 사용자 승인 전 자동 적용은 절대 금지이며, 승인 시 `~/.claude/rules/conditional/` 또는 `always/`로 이동한다.

### 7. Demotion/Retirement (강등/은퇴)

`maintenance.py`가 SessionStart 시 하루 1회 실행된다. 60일 무발생이면 demotion candidate flag를 붙이고, 90일 무발생 + low severity이면 `retired/` 이동을 제안한다. 사용자 확인 후 `retired/`로 이동한다.

---

## 승격 기준 (수치화)

### Hook Rule로 승격 (compiled rule)

```
occurrences_30d >= 3       # 30일 내 3회 이상 발생
distinct_sessions >= 2     # 2개 이상 세션에서 발생
severity >= P1             # 심각도 P1 이상
precision >= 0.85          # 정밀도 85% 이상 (오탐 15% 미만)
prevention_cost_ms <= 200  # 탐지 비용 200ms 이하
```

### Conditional Rule로 승격

```
category가 file/project specific  # 특정 파일 유형에만 해당
model judgment 필요               # regex만으로 부족
hook precision < 0.85             # hook으로는 정밀도 부족
context cost < 50 lines           # 컨텍스트 비용 50줄 미만
```

### Always Rule로 승격

```
severity P0 or P1                 # 심각도 높음
cross-project recurrence          # 여러 프로젝트에서 발생
rule length <= 15 lines           # 규칙이 간결함
canonical solution exists         # 해결책이 명확함
no conflict with existing rules   # 기존 규칙과 충돌 없음
false_positive_rate < 0.05        # 오탐률 5% 미만
user explicitly approved          # 사용자 명시 승인
```

## 추가 승격 기준 (빈도+심각도만으로 부족한 이유)

| 기준 | 이유 |
|---|---|
| distinct sessions/agents | 한 번의 사고가 중복 카운트되는 것 방지 |
| preventability | hook/rule로 실제 예방 가능한가 |
| precision / false positive rate | always-loaded rule은 오탐 비용이 큼 |
| canonical solution 존재 | "하지 마라"만 있고 해결책 없으면 모델 품질 저하 |
| context budget 영향 | 항상 로드할 만큼 짧고 보편적인가 |
| blast radius | 한 번 발생 시 피해가 큰가 |
| escape rate | validator까지 뚫고 사용자에게 도달했는가 |
| demotion policy | 60-90일 무발생이면 archive 또는 conditional rule로 강등 |
| conflict check | 기존 `CLAUDE.md`/`rules`와 충돌하지 않는가 |

## Demotion (강등) 정책

```
60일 무발생
  → status: "demotion_candidate"
  → compiled rule에서 action을 "warn"으로 약화

90일 무발생 + severity <= P2
  → proposals/retirement/*.md 생성
  → 사용자 확인 후 retired/로 이동
  → compiled rule에서 제거

conditional/always rule이 된 경우
  → 180일 무발생 시 conditional → retired
  → always → conditional 강등 제안 (자동 제거 금지)
```
