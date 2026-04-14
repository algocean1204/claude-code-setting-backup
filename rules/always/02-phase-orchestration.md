# PHASE ORCHESTRATION

Detailed phase workflows are in each agent definition (~/.claude/agents/). Leader uses the summary below for team spawning + deliverable verification.

## Cross-Phase Ambient Team

| Team | Trigger | Phase Scope |
|---|---|---|
| **🧭 Delegation Advisor** (`delegation-advisor-lead` → -fit, -risk, -alternative) | Leader cannot map a task to an obvious-match whitelist entry in `01-team-invocation.md` | **Available throughout ALL phases** — spawn whenever uncertain which agent/team/skill should own a task. ~25s wall time. Default uncertainty handler, NOT a fallback. |
| **🔧 Tools Manager** (`tools-manager-lead` → -scout, -builder, -risk) | Sub-agent output contains `TOOL_REQUEST:` signal | **Available throughout ALL phases.** Mode A returns advice (no file change). Mode B returns proposal requiring user approval before file creation. Spawning the team itself does NOT require guardian monitoring (meta-routing, not phase work). |

These teams are NOT phase-bound. Spawning the advisor itself does NOT require requirements-guardian to run alongside it (it is meta-routing, not phase work). However, the team that the advisor RECOMMENDS runs under normal Phase rules with normal guardian monitoring.

## Phase Summary

| Phase | Team/Agents | Output | Key Condition |
|---|---|---|---|
| Pre-scan | doc-pre-scanner (if long doc provided) | docs/decisions.md | Resolve BLOCKING decisions first |
| 0 | license-advisor | docs/tech-stack.md, docs/license-report.md | Only GREEN/YELLOW licenses allowed |
| **0.5** | **gstack /office-hours → /plan-ceo-review** | **docs/service-design-decisions.md** | **User must fully approve feature scope** |
| 1 | gstack /plan-eng-review + spec-security | docs/spec.md | Architecture locked + security consensus |
| 1A | marketing-lead + finance-lead (parallel) | docs/marketing-analysis.md, docs/financial-analysis.md | Critical financial risk → user confirmation |
| ★ Planning Gate | Module design + ERD + Connection map (3 HTMLs) | module-design.html, erd-design.html, connection-map.html | **User must approve all 3** |
| 1.5 | color-lead → design-lead (with gstack /design-consultation + /design-review) → ui-ux-designer | docs/design-system.md, docs/animation-spec.md | WCAG pass required, structural diversity 40%+ |
| 1.5F | figma-agent + figma-inspector | Figma sync + per-page inspection | figma-agent creates, figma-inspector verifies each page. See rules/always/08-figma-operations.md |
| **Code Router** | **code-router (solo, 1-shot)** | **docs/task-briefs/*.md** | **All modules assigned to agents, verified** |
| 2 | 4 devs + 3 pair-reviewers | Code implementation | Each agent reads only its own task-brief, shared/types/ first |
| 2.5 | 5 validators (parallel) | Validation report | ALL PASS → Phase 3, endpoint logic inspection mandatory |
| 3 | test-engineer + gstack /qa → quality-judge | Tests + scoring | S grade (96%+) → Phase 4, below → repeat Phase 2 (max 3 times) |
| 4 | feedback-lead → gstack /review + ux + integration + gstack /cso + performance + visual | docs/feedback-report.md | Only feedback-lead has code modification authority |
| 4.5 | error-check-lead → 3 inspectors (ALL Sonnet) | Error report | Analysis only, no code modification |
| 5 | feature-suggest-lead → 3 analysts (ALL Sonnet) | Feature recommendation list | Only user-selected features implemented, auto-implementation prohibited |
| 5.5 | cleanup-lead → 3 scanners + 3 verifiers | Deletion list | 3/3 verifier SAFE + user confirmation before deletion |
| AI | ai-model-specialist → ai-training-specialist → ai-result-analyst | AI pipeline | 95%+ accuracy, images require user visual confirmation |
| Deploy | gstack /ship + /land-and-deploy | GitHub push + production deploy | Exclude sensitive info, Korean README, user final confirmation |

## Existing Project Protocol

### Common First Step
1. project-scanner → docs/project-context.md
2. Report summary to user
3. Immediately run requirements-guardian in parallel

### Bug Fix
project-scanner → gstack /investigate + guardian (parallel) → relevant implementation team + guardian → Verification → repeat until S grade

### Feature Addition
project-scanner → feature-designer + guardian → docs/feature-spec.md → user approval → implementation team + guardian → Verification → repeat until S grade

### Continue Work
project-scanner → assess state → report to user → run guardian → execute per user instructions

## GitHub Deployment
1. Invoke gstack `/ship` — syncs main, runs tests, audits coverage, opens PR
2. Invoke gstack `/land-and-deploy` — merges, deploys to production, verifies health
3. Optionally invoke gstack `/canary` — post-deploy monitoring
4. Auto-exclude sensitive info, large files, tests, existing docs
5. Generate Korean README.md (~ham/~handa declarative style)
6. Push after user final confirmation
7. NEVER include Co-Authored-By in commit messages
