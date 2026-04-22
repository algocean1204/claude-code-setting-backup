# Rules Changelog

규칙 파일 변경 이력을 기록합니다.

| 날짜 | 파일 | 변경 내용 |
|------|------|-----------|
| 2026-03-30 | (전체) | 초기 생성 — CLAUDE.md 701줄 → rules/ 구조로 개편 |
| 2026-03-30 | always/01-team-invocation.md | 팀 레지스트리 + 호출 규칙 (CLAUDE.md에서 이동) |
| 2026-03-30 | always/02-phase-orchestration.md | Phase 요약 + 프로젝트 프로토콜 (CLAUDE.md에서 압축 이동) |
| 2026-03-30 | always/03-core-principles.md | SRP, No Workarounds, 버전 정책 (CLAUDE.md에서 이동) |
| 2026-03-30 | always/04-inspection-protocol.md | 다각도 검수 + 데이터 플로우 추적 (CLAUDE.md에서 이동) |
| 2026-03-30 | always/05-planning-gate.md | 신규 — 필수 계획 게이트 (3개 HTML 산출물) |
| 2026-03-30 | conditional/*.md (7개) | 코드 스타일/인프라/DB/테스트/문서 조건부 규칙 |
| 2026-03-31 | always/06-gstack-integration.md | 신규 — gstack 스킬을 primary 툴셋으로 통합, Phase 0.5 신설 |
| 2026-03-31 | always/01-team-invocation.md | 팀 레지스트리 업데이트: 9개 에이전트를 gstack 스킬로 대체 |
| 2026-03-31 | always/02-phase-orchestration.md | Phase 0.5 추가, Phase 1/3/4/Deploy gstack 반영 |
| 2026-03-31 | CLAUDE.md | Phase 0.5 추가, gstack 통합 섹션 추가 |
| 2026-03-31 | agents/ (9개 삭제) | 제거: spec-product, spec-architect, design-trend-researcher, design-critic, bug-detective, feedback-code-reviewer, feedback-security-reviewer, test-e2e-engineer, github-deployer |
| 2026-03-31 | always/06-gstack-integration.md | 확장 — 스프린트 프로세스, 스킬 체이닝, 프로액티브 라우팅, Phase 전환 제안 추가 |
| 2026-03-31 | always/07-interaction-protocol.md | 신규 — 모호한 입력 처리, AskUserQuestion 프로토콜, 대화 흐름 규칙 |
| 2026-03-31 | CLAUDE.md | 인터랙션 프로토콜 섹션 추가 |
| 2026-04-07 | agents/code-router.md | 신규 — Planning Gate→Phase 2 사이 코드라우터 에이전트 (모듈설계→에이전트별 task-brief 변환) |
| 2026-04-07 | CLAUDE.md | Phase 실행 순서에 Code Router 단계 삽입 |
| 2026-04-07 | always/01-team-invocation.md | Solo Agents에 code-router 추가, 팀별 모델 배정 표기 업데이트 |
| 2026-04-07 | always/02-phase-orchestration.md | Phase Summary에 Code Router 행 추가 |
| 2026-04-07 | agents/ (구현 4개) | web-frontend, app-frontend, backend-api, backend-db에 Task Brief Protocol 추가 |
| 2026-04-07 | agents/ (페어리뷰어 3개) | frontend/backend/db-pair-reviewer에 Task Brief 교차 검증 추가, model→sonnet |
| 2026-04-07 | agents/error-check-lead.md | Context Compression Response 프로토콜 추가, model→sonnet |
| 2026-04-07 | agents/feedback-lead.md | Step 0: Context anchoring 프로토콜 추가 |
| 2026-04-07 | agents/devops-engineer.md | Task Brief Protocol 추가, model→sonnet |
| 2026-04-07 | agents/ (40개) | 모델 배정 최적화: Opus 61→21개, Sonnet 4→44개 (66% Opus 감소) |
| 2026-04-11 | CLAUDE.md | 최상단에 LEADER ABSOLUTE RULE 블록 신설 — 리더 직접 행동 절대 금지 영문 강조 |
| 2026-04-11 | agents/delegation-advisor-lead.md | 신규 — 위임 조언팀 리더 (Opus). 리더가 위임 대상 못 정할 때만 호출되는 최후 수단 |
| 2026-04-11 | agents/delegation-advisor-fit.md | 신규 — 적합도 관점 의견조율 팀원 (Opus). 기존 레지스트리에서 최적 후보 추천 |
| 2026-04-11 | agents/delegation-advisor-risk.md | 신규 — 리스크 관점 의견조율 팀원 (Opus). 후보 에이전트의 능력/권한/페이즈 미스매치 검증 |
| 2026-04-11 | agents/delegation-advisor-alternative.md | 신규 — 대안 경로 의견조율 팀원 (Opus). 스킬 체인/팀 조합/태스크 분할 제안 |
| 2026-04-11 | always/01-team-invocation.md | 팀 레지스트리에 Delegation Advisor (last-resort) 추가, 사용 최소화 규칙 명시, Rule #10 추가 |
| 2026-04-11 | CLAUDE.md | LEADER ABSOLUTE RULE에 🧭 WHEN UNCERTAIN escape hatch 추가, Phase 차트 아래 Cross-Phase Ambient Team 박스 추가 |
| 2026-04-11 | agents/delegation-advisor-lead.md | 재포지셔닝 — Last-resort → Default uncertainty handler. tools에 Agent 도구 추가, BLOCKED 프로토콜 + 콜 버짓 (1차/2차/3차) 명시, ~25초 wall time 목표, gstack precedence 동기화 룰 |
| 2026-04-11 | agents/delegation-advisor-{fit,risk,alternative}.md | model: opus → sonnet (병렬 속도 최적화 ~10–15s), 출력 길이 강화 (fit/alt 400→300, risk 500→350), last-resort 표현 제거, fit에 gstack 우선 hard rule 격상 |
| 2026-04-11 | always/01-team-invocation.md | Delegation Advisor를 Default Uncertainty Handler로 재정의, 25-entry Obvious-Match Whitelist 신설, Rule #10 재작성 (routinely 사용) |
| 2026-04-11 | always/02-phase-orchestration.md | Cross-Phase Ambient Team 섹션 신설 — Delegation Advisor가 모든 Phase에서 가용함을 명시 |
| 2026-04-11 | always/07-interaction-protocol.md | Two Types of Ambiguity 표 신설 — User-intent ambiguity vs Delegation ambiguity 구분 (전자는 AskUserQuestion, 후자는 delegation-advisor-lead) |
| 2026-04-11 | agents/(8 team leads) | 사이드 이슈 수정 — color/design/feedback/marketing/finance/error-check/feature-suggest/cleanup-lead 모두 tools에 Agent 추가. 이전까지 lead들이 sub-agent 스폰 도구 누락 상태였음 |
| 2026-04-11 | agents/(stale refs 6 files) | 삭제된 에이전트 사문 참조 10곳 → gstack 스킬로 교체 (design-lead, design-motion-specialist, feedback-lead, feedback-ux-reviewer, spec-security, doc-writer) |
| 2026-04-11 | agents/(monitoring 3) | frontmatter 형식 정상화 — leader-auditor model 표기 정정(claude-opus-4-6 → opus) + tools YAML 리스트 → 콤마 표기, subagent-monitor tools 표기 정정, requirements-guardian 비표준 subagent_type 필드 제거 |
| 2026-04-11 | agents/(specialists 3) | 누락 sub-specialist 모델 최적화 — color-harmony-specialist, color-psychologist, design-motion-specialist 모두 opus → sonnet (lead가 종합 책임, 본인은 빠른 병렬 처리) |
| 2026-04-11 | always/00-quick-reference.md | 신규 — 1페이지 cheat sheet. 리더가 매 세션 첫 번째로 보는 글랜서블 인덱스. Phase별/도메인별 Task→Tool 표 + 3 Reflexes |
| 2026-04-11 | always/01-team-invocation.md | Obvious-Match Whitelist 25 → 47 엔트리로 확장. CI/CD, DB 최적화, 보안 설계, SRP 리팩터, 공수 추정, 인증 E2E, AI/모바일/웹/백엔드 직접 매핑, gstack 추가 스킬(codex/design-shotgun/design-html/autoplan/setup-deploy/document-release/retro/learn) 라우팅 추가. Rule #10 표현 갱신 |
| 2026-04-11 | CLAUDE.md | RULES STRUCTURE 섹션 always/ 목록 최상단에 00-quick-reference.md 추가 |
| 2026-04-11 | plans/(cleanup 33) | stale plan 파일 29개 + side-effect plan 3개 + .consolidate-lock 1개 삭제 (총 33). 보존: temporal-splashing-mist + humming-meandering-walrus + keen-singing-lovelace + sunny-chasing-quasar + starry-meandering-tome |
| 2026-04-13 | agents/figma-agent.md, figma-inspector.md | frontmatter `tools:` 필드에 MCP 툴 allowlist 명시 — 서브에이전트가 MCP 호출 불가했던 BLOCKED 이슈 해결, 리더 직접 실행 재발 방지. figma-inspector는 read-only 툴만 부여, 본문 BANNED 툴(get_pages, scan_text_nodes, scan_nodes_by_types, read_my_design)은 allowlist 제외로 물리 차단 |
| 2026-04-13 | agents/tools-manager-{lead,scout,builder,risk}.md | 신규 — Tools Manager 4-에이전트 팀 (Opus ×4) 신설. 서브에이전트가 tools 필드 한계로 막혔을 때 TOOL_REQUEST 시그널로 리더를 통해 요청 → scout/builder/risk 병렬 분석 → Mode A(조언)/Mode B(사용자 승인 후 생성). 2026-04-13 figma 사건 재발 방지 + 시스템 학습 루프 제도화 |
| 2026-04-13 | always/01-team-invocation.md | Team Registry에 🔧 Tools Manager 추가, Obvious-Match Whitelist에 TOOL_REQUEST 엔트리 추가, Rule #11 추가 |
| 2026-04-13 | always/00-quick-reference.md | Cross-Phase Always-Available에 tools-manager-lead 추가, Hard Reminders에 TOOL_REQUEST 감지 규칙 추가 |
| 2026-04-13 | always/02-phase-orchestration.md | Cross-Phase Ambient Team 표에 🔧 Tools Manager 행 추가 |
| 2026-04-13 | CLAUDE.md | Phase 차트 아래 🔧 Cross-Phase Ambient Team — Tools Manager 박스 추가 |
| 2026-04-13 | agents/design-motion-specialist.md, license-advisor.md | tools 필드에서 Edit 제거 — Read/Write만으로 충분한 역할(스펙 작성 or raw 데이터 전달)인데 Edit 보유 중이었던 권한 원칙 위반 수정. specialist 동료들과 일관성 확보 |
| 2026-04-18 | CLAUDE.md | Document Operations Rule 신설 (Design Delegation Rule 다음 위치) — 모든 문서 작업(Docs CRUD, README, ADR 등)은 Sonnet 모델의 doc-writer 서브에이전트에 위임 의무화. 리더 직접 작성 금지 재확인, 구현 에이전트도 문서는 doc-writer에 위임. 사용자 직접 지시로 글로벌 규칙 격상 |
| 2026-04-22 | CLAUDE.md, rules/always/00, 01, 07 | Trivial Task Fast Path 신설 — 1줄 수정·질답·읽기·Skill 호출은 리더 직접 허용, delegation-advisor 25s 경로 우회. Document Operations Rule을 프로젝트 문서 디렉토리 한정으로 축소. 사용자 불만 "간단한 작업 오래 걸림" 대응 |
| 2026-04-22 | settings.json, hooks/ | env 플래그(EFFORT_LEVEL, DISABLE_ADAPTIVE_THINKING) 제거, PostToolUse hook 경로 필터 추가, Stop hook의 GitHub push 제거 후 launchd 하루 1회 전환. devops-engineer 서브에이전트가 병렬 수행 |
| 2026-04-22 | agents/ (6개 삭제), plugins/ (2개 전체 삭제), rules/always/99-superpowers-extraction.md (신규) | 중복 감사 후 정리 — 에이전트: error-check 팀 4개 + test-engineer + performance-optimizer 제거 (gstack /qa, /benchmark, /investigate 스킬 및 feedback 팀과 역할 중복). 플러그인: superpowers 14 스킬 전체 + code-review:code-review 제거. superpowers 중 receiving-code-review, systematic-debugging 유일 가치 원칙만 99-superpowers-extraction.md로 보존. Phase 4.5 (Error Inspection), Performance 단계 Phase 차트에서 제거. db-pair-reviewer·db-migration-auditor는 사용자 "유지" 결정 및 흡수 검토 필요로 이번 제거에서 제외 |
| 2026-04-22 | rules/always/01,04,06 | 1차 cleanup 패스가 놓친 stale 참조 4건 수정 (test-engineer, error-check-lead, Phase 4.5) |
