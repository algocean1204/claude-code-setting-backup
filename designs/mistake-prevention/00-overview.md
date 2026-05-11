# Mistake Prevention Control Plane — 설계 개요

## 배경

현재 하네스에는 5개 레이어가 존재한다:

- **Layer 1**: 정적 규칙 (`CLAUDE.md`, `rules/always/`, `rules/conditional/`)
- **Layer 2**: 런타임 감시 (`requirements-guardian`, `subagent-monitor`, `leader-auditor`, `quality-judge`)
- **Layer 3**: Hooks (`PostToolUse Write|Edit` → CHANGELOG + 백업)
- **Layer 4**: 메모리 (`feedback_*.md`, `project_*.md`, `/learn`)
- **Layer 5**: 검증 파이프라인 (Phase 2.5 validators, Phase 3 QA, Phase 4 feedback)

## 핵심 진단

현재 시스템은 "실수 예방 시스템"이 아니라 "실수 발생 후 감시·검증 시스템"에 가깝다.

### 5가지 구조적 갭

1. **실수 기록이 체계화되어 있지 않음** — `feedback_*.md`에 산발적으로 저장, taxonomy/빈도/패턴 추적 없음
2. **해결방법이 실수와 연결되어 있지 않음** — "이런 실수가 있었다"와 "이렇게 해결했다"가 1:1 페어링 안 됨
3. **Hook이 방지(prevention)가 아닌 기록(logging)에만 사용됨** — `PostToolUse`만 존재, `PreToolUse` 없음
4. **세션 간 학습 루프가 불완전** — `feedback memory`가 자동으로 규칙으로 승격되는 경로 없음
5. **실수 분류 체계(taxonomy)가 없음** — 모든 종류의 실수가 flat하게 저장됨

## 설계 철학

### Hybrid 접근 (Agent Team + Hooks)

- **Hooks**: 실시간 도구 실행 전 차단 (`PreToolUse` 중심). 빠르고 확실한 패턴만 처리.
- **Agent Team**: 반복 패턴 분석, taxonomy 분류, prevention rule 생성, 승격 제안. 학습과 정책 큐레이션 담당.
- Pure agent 방식은 예방이 늦고, pure hook 방식은 학습을 못 한다.

### 핵심 원칙

1. **Monitors emit, Curator curates** — 기존 감시자들은 이벤트를 발행만 하고, 새 팀이 정책으로 변환한다
2. **Hook은 칼이 아니라 안전장치** — 판단 실수(요구 해석 실패, 아키텍처 오판)는 hook이 아닌 phase gate가 잡아야 한다
3. **Context window 보호** — compiled rules는 disk에서만 읽음, context에 절대 로드하지 않음
4. **자동 적용 금지** — 자동 "제안"까지만 허용, always rule 승격은 사용자 명시 승인 필수
5. **기존 SRP/No Workarounds/Phase 파이프라인과 충돌 없음**

### Cross-Model 합의 (Claude Opus + OpenAI Codex)

- 2라운드 토론, 합계 ~186,000 tokens 소모
- Agreement rate: ~95% (19/20 세부 결정 합의)
- Claude가 수정받은 부분: `PostToolUse` 확장 → `PreToolUse` 중심 전환
- Codex가 보강한 부분: 승격 기준 수치화, 이중 구조(event log + pattern state), demotion policy
