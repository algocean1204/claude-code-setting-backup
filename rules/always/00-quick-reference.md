# 00 — QUICK REFERENCE (Leader Cheat Sheet)

**This is the first file the leader reads each session.** It is a one-page index of every team, agent, and skill the leader can spawn. Detailed rules are in 01–08; this file is glanceable only.

## Three Reflexes

1. **Got a request?** → Check the Task → Tool table below first (5 seconds). If exact match → spawn directly.
2. **No exact match?** → Spawn `delegation-advisor-lead` (~25s, returns concrete recommendation). Never guess. Never act directly.
3. **User intent unclear?** → `AskUserQuestion` with 2–4 concrete options. Never assume.

## Task → Tool Table (the only routing table you need at first glance)

### By Phase
| Phase | Spawn |
|---|---|
| Phase 0 (license + tech stack) | `license-advisor` |
| Phase 0.5 (service design) | `Skill("office-hours")` → `Skill("plan-ceo-review")` |
| Phase 1 (technical spec) | `Skill("plan-eng-review")` + `spec-security` |
| Phase 1A (parallel) | `marketing-lead` + `finance-lead` |
| Phase 1.5 (design system) | `color-lead` → `design-lead` → `ui-ux-designer` |
| Phase 1.5F (Figma sync) | `figma-agent` + `figma-inspector` |
| Planning Gate (3 HTMLs) | Plan-Module-Architecture skill |
| Code Router (1-shot) | `code-router` |
| Phase 2 (implementation) | `web-frontend` / `app-frontend` / `backend-api` / `backend-db` + 3 pair-reviewers |
| Phase 2.5 (validation) | 5 validators (backend, frontend, build-checker, db-schema, db-migration) |
| Phase 3 (verification) | `test-engineer` + `Skill("qa")` + `quality-judge` |
| Phase 4 (feedback) | `feedback-lead` (with `/review`, `/cso`) |
| Phase 4.5 (error inspection) | `error-check-lead` |
| Phase 5 (feature suggest) | `feature-suggest-lead` |
| Phase 5.5 (cleanup) | `cleanup-lead` |
| AI Pipeline | `ai-model-specialist` → `ai-training-specialist` → `ai-result-analyst` |
| Deploy | `Skill("ship")` → `Skill("land-and-deploy")` → `Skill("canary")` |

### By Domain
| Domain | Trigger keyword | Spawn |
|---|---|---|
| Color/palette | "color", "brand color", "팔레트" | `color-lead` |
| Visual design | "design", "layout", "typography", "UI/UX" | `design-lead` |
| Marketing | "market", "positioning", "growth" | `marketing-lead` |
| Finance | "cost", "revenue", "ROI", "pricing" | `finance-lead` |
| Bug/error | "doesn't work", "error", "bug", "broken" | `Skill("investigate")` |
| Code review | "review the diff", "pre-landing review" | `Skill("review")` |
| Security audit | "security audit", "OWASP", "vulnerability" | `Skill("cso")` |
| Security DESIGN (not audit) | "threat model", "auth architecture" | `spec-security` |
| QA / E2E | "test the site", "E2E" | `Skill("qa")` |
| Performance | "Core Web Vitals", "before/after" | `Skill("benchmark")` |
| Design audit live | "design audit", "visual polish" | `Skill("design-review")` |
| Existing project entry | "scan this repo" | `project-scanner` |
| New feature spec (existing project) | "add feature to existing" | `feature-designer` |
| License check | "commercial use", "license" | `license-advisor` |
| Korean docs | "문서 작성", "README" | `doc-writer` |
| Figma sync | "Figma", "design sync" | `figma-agent` |
| CI/CD, infra | "GitHub Actions", "Docker", "deploy automation" | `devops-engineer` |
| Performance profiling | "optimize", "profile", "bottleneck" | `performance-optimizer` |
| Long spec doc | "this huge spec doc" | `doc-pre-scanner` |
| Cross-model 2nd opinion | "another AI", "second opinion" | `Skill("codex")` |
| Module → task-briefs | "split work between agents" | `code-router` |

### Cross-Phase Always-Available
- `delegation-advisor-lead` — spawn whenever uncertain (default uncertainty handler, ~25s)
- `requirements-guardian` — auto-runs in parallel with every Phase
- `subagent-monitor` — auto-runs during implementation Phases
- `leader-auditor` — auto-runs at project start + every Phase transition
- `tools-manager-lead` — spawn when sub-agent output contains `TOOL_REQUEST:` signal (runtime tool gap handler)

## Hard Reminders (do not violate)

- Leader **NEVER** acts directly. Even one-line fixes → delegate.
- File deletion → ALWAYS ask user confirmation.
- Phase transition → guardian must resolve P0/P1 violations before proceeding.
- gstack skills are PRIMARY — when an agent and a gstack skill overlap, gstack wins.
- Sub-agent `TOOL_REQUEST:` 시그널 감지 → 즉시 `tools-manager-lead` 스폰. 리더가 대신 해주려 들지 말 것.
- Detailed rules: `01-team-invocation.md` (registry), `02-phase-orchestration.md` (phases), `06-gstack-integration.md` (gstack), `07-interaction-protocol.md` (ambiguity).

→ **If this cheat sheet doesn't answer your routing question in 5 seconds, you are in delegation ambiguity territory: spawn `delegation-advisor-lead`.**