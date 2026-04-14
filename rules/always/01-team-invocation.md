# TEAM INVOCATION RULES (Non-negotiable)

Leader MUST invoke agents as **COMPLETE TEAMS**. NEVER spawn individual team members.

## Team Registry

| Team | Members | Spawn Method |
|---|---|---|
| **Service Design** | **gstack /office-hours, gstack /plan-ceo-review** | **Leader invokes skills directly** |
| Design Discussion | gstack /plan-eng-review, spec-security | Leader invokes skill + spawns agent |
| Marketing | marketing-lead (Opus) → 3 specialists (strategist=Opus, content-analyst=Sonnet, growth-hacker=Sonnet) | Lead Opus, sub Sonnet |
| Finance | finance-lead (Opus) → 3 specialists (cost-analyst=Sonnet, revenue-strategist=Sonnet, risk-assessor=Opus) | Lead Opus, sub mixed |
| Color | color-lead → color-psychologist, color-harmony-specialist, color-accessibility-analyst | via color-lead |
| Design | design-lead → gstack /design-consultation, motion-specialist, gstack /design-review, ui-ux-designer | via design-lead |
| Implementation | web-frontend, app-frontend, backend-api, backend-db (ALL Sonnet) + 3 pair-reviewers (ALL Sonnet) | Leader spawns 7 directly, ALL read task-briefs |
| Full Validation | backend-validator, frontend-validator, frontend-build-checker, db-schema-validator, db-migration-auditor (ALL Sonnet) | Leader spawns 5 directly |
| Verification | test-engineer, gstack /qa, quality-judge | Leader spawns agent + invokes skill |
| Feedback | feedback-lead → gstack /review, ux, integration, gstack /cso, performance, visual | via feedback-lead |
| Error Inspection | error-check-lead → 3 inspectors (ui, api, structure) | ALL Sonnet |
| Feature Suggestion | feature-suggest-lead → 3 analysts (consumer, ops, business) | ALL Sonnet |
| File Cleanup | cleanup-lead → 3 scanners + 3 verifiers | via cleanup-lead |
| AI Pipeline | ai-model-specialist, ai-training-specialist, ai-result-analyst, image-quality-evaluator | Sequential |
| **🔧 Tools Manager** *(runtime tool gap handler, cross-phase)* | **tools-manager-lead (Opus) → tools-manager-scout, tools-manager-builder, tools-manager-risk (ALL Opus)** | **via tools-manager-lead — leader spawns when sub-agent output contains `TOOL_REQUEST:` signal** |
| **Delegation Advisor** *(default uncertainty handler, cross-phase)* | **delegation-advisor-lead (Opus) → delegation-advisor-fit, delegation-advisor-risk, delegation-advisor-alternative (ALL Sonnet)** | **via delegation-advisor-lead — leader uses ROUTINELY whenever the task does not match an obvious-match whitelist entry** |

## Global Agents (always running)
- requirements-guardian — MUST run in parallel during every Phase
- subagent-monitor — MUST run in parallel during implementation Phases (code quality/rule compliance monitoring)
- leader-auditor — Verifies leader behavior at every Phase transition

## Solo Agents (spawned individually)
license-advisor, doc-pre-scanner, project-scanner, feature-designer, doc-writer, devops-engineer, performance-optimizer, figma-agent, figma-inspector, code-router

### Code Router (Non-negotiable)
- **MUST** run after Planning Gate approval and before Phase 2
- Translates 3 HTML design documents → per-agent task-briefs in `docs/task-briefs/`
- Each implementation agent receives ONLY its own task-brief (not the full design docs)
- 1-shot execution: runs once, produces files, exits
- Leader does NOT hold module-level details — code-router handles the translation

### Delegation Advisor Team (Default Uncertainty Handler, Non-negotiable)
- **Purpose**: Whenever the leader is uncertain which agent/team/skill should handle a task, this team returns a single concrete delegation recommendation in ~25 seconds so the leader NEVER ends up breaking the absolute rule and acting directly. This is the **default uncertainty handler**, not a last resort.
- **Members**: `delegation-advisor-lead` (Opus, holds `Agent` tool) → 3 advisors (`-fit`, `-risk`, `-alternative`, ALL Sonnet). Lead spawns the 3 advisors in parallel via the Agent tool and synthesizes their reports into a single recommendation.
- **Wall-time target**: ~10–15s for 3 parallel Sonnet advisors + ~10–15s for Opus synthesis = **~25s end-to-end**. Cheap enough to call routinely.
- **Spawn rule**: Spawn this team WHEN the task does **NOT** match any entry in the Obvious-Match Whitelist below. If the leader is even slightly uncertain about delegation, spawn this team — do not guess.
- **Cost is NOT a constraint**. Quality of delegation matters more than saving 4 model calls.
- **Output**: a `Delegation Recommendation` block (primary pick + fallback + pre-flight checklist + stop conditions + advisor vote summary). The leader copies the recommendation and acts on it.
- **Hard prohibitions**: this team NEVER performs the work itself, NEVER recommends "leader does it directly", NEVER recommends creating a new agent on the fly (except in 3rd-call escalation, which becomes a user-facing proposal).
- **Per-task call budget**: 1st call → recommendation OR `BLOCKED` (with exactly 3 clarifying questions). 2nd call (after user clarification) → recommendation OR escalate. 3rd call forbidden — instead, recommend user define a new agent for this task type.
- **Guardian exemption**: spawning the advisor team itself does NOT require requirements-guardian/subagent-monitor (it is meta-routing, not phase work). However, the team that the advisor recommends MUST follow normal guardian rules when spawned.

### Obvious-Match Whitelist (DO NOT spawn delegation-advisor — spawn directly)

The leader spawns the matching team/agent/skill **directly** for these cases. These are obvious enough that running the advisor team would only waste ~25s.

| Trigger (user signal) | Direct spawn |
|---|---|
| Color, palette, hex codes, brand colors | `color-lead` (full Color team) |
| Visual design, layout, typography, animation, UI/UX patterns | `design-lead` (full Design team) |
| Marketing, positioning, market research, growth, copy | `marketing-lead` (full Marketing team) |
| Finance, cost, revenue, pricing, ROI, financial risk | `finance-lead` (full Finance team) |
| Bug, error, "doesn't work", root-cause investigation | `Skill("investigate")` |
| Code review, "review the diff", pre-landing review | `Skill("review")` |
| Security audit, OWASP, STRIDE, vulnerability check | `Skill("cso")` |
| QA, E2E browser testing, "test the site" | `Skill("qa")` |
| Performance benchmark, Core Web Vitals, before/after | `Skill("benchmark")` |
| Design audit of live site, visual polish review | `Skill("design-review")` |
| Ship, deploy, "create a PR" | `Skill("ship")` |
| Merge approved PR, deploy to production | `Skill("land-and-deploy")` |
| Post-deploy monitoring | `Skill("canary")` |
| New idea brainstorming, "is this worth building" | `Skill("office-hours")` |
| Scope/strategy reframing, "think bigger" | `Skill("plan-ceo-review")` |
| Architecture lock, dependency diagrams, test plan | `Skill("plan-eng-review")` |
| Entering existing project, "scan this repo" | `project-scanner` |
| Adding feature to existing project (needs spec) | `feature-designer` |
| License/commercial use check | `license-advisor` |
| Korean documentation writing | `doc-writer` |
| Module design → per-agent task-briefs | `code-router` |
| Figma sync (read or push designs) | `figma-agent` |
| CI/CD, Docker, Nginx, infrastructure automation | `devops-engineer` |
| Performance profiling and optimization (after benchmarks) | `performance-optimizer` |
| Long spec document pre-scan | `doc-pre-scanner` |
| CI/CD pipeline setup, GitHub Actions, build automation | `devops-engineer` |
| Database query optimization, slow query analysis, index tuning | `backend-db` (if implementation) or `Skill("benchmark")` (if measurement) |
| API threat modeling, security architecture design (NOT audit) | `spec-security` |
| Module/code refactoring for SRP, breaking up oversized files | `code-router` (design-time) → implementation team (execution) |
| Feature effort estimation, "how long would X take" | `feature-designer` (for spec-level estimate) |
| Error handling strategy review across system | `feedback-lead` (full Feedback team) |
| Authenticated user flow E2E testing | `Skill("qa")` (auto-imports cookies via `/setup-browser-cookies` if needed) |
| Module interface documentation, API documentation | `doc-writer` |
| AI model integration, ML model serving | `ai-model-specialist` |
| AI model fine-tuning, training, dataset prep | `ai-training-specialist` |
| Mobile app screens, navigation, app frontend | `app-frontend` |
| Web React/Next.js components, web frontend | `web-frontend` |
| Backend API routes, business logic, auth | `backend-api` |
| DB schema, migrations, seed data | `backend-db` |
| Cross-model second opinion (Claude + OpenAI) | `Skill("codex")` |
| Multiple visual design variants, design exploration | `Skill("design-shotgun")` |
| Mockup → production HTML conversion | `Skill("design-html")` |
| Full automated CEO + design + eng review pipeline | `Skill("autoplan")` |
| One-time deploy environment setup | `Skill("setup-deploy")` |
| Update docs after shipping a release | `Skill("document-release")` |
| Weekly retrospective, sprint review | `Skill("retro")` |
| Pattern learning across sessions | `Skill("learn")` |
| Sub-agent output contains `TOOL_REQUEST:` signal | `tools-manager-lead` |

→ **Anything NOT in this table = spawn `delegation-advisor-lead`**. The leader does not guess.

## gstack Skill Override Rules (Non-negotiable)
1. gstack skills are **PRIMARY** — when a gstack skill overlaps with an existing agent, the gstack skill MUST be used. The replaced agent has been removed.
2. Agents/leads invoking gstack skills use the **Skill tool** with the slash command name (e.g., `Skill("review")`).
3. gstack skills follow the **same guardian monitoring** requirements as the agents they replaced.
4. For the full replacement mapping, see `rules/always/06-gstack-integration.md`.
5. **Removed agents** (replaced by gstack): spec-product, spec-architect, design-trend-researcher, design-critic, bug-detective, feedback-code-reviewer, feedback-security-reviewer, test-e2e-engineer, github-deployer.

## Rules
1. **NEVER** spawn a single member from a team. Always spawn the FULL team.
2. Solo agents can be spawned individually.
3. Team leaders are responsible for spawning their own sub-members.
4. If a phase is skipped, that team is not spawned.
5. **ONLY exception**: backend-only or frontend-only fix → spawn only relevant subset.
6. Marketing + Finance teams MUST run in parallel during Phase 1A.
7. Error Inspection + Feature Suggestion + File Cleanup run sequentially after Phase 4.
8. **requirements-guardian MUST run in parallel with the Phase team during every Phase.** Running a Phase without guardian is prohibited.
9. **If guardian reports P0/P1 violations, the leader CANNOT proceed to the next Phase until those violations are resolved.**
10. **Delegation Advisor team is the default uncertainty handler.** Spawn whenever the task does not match an entry in the expanded ~45-entry Obvious-Match Whitelist above. Cost is not a concern (~25s wall time). Use it freely — quality of delegation matters more than saving 4 model calls. The only thing the leader should NEVER do is guess or act directly.
11. **Tools Manager is the runtime tool-gap handler.** When a sub-agent's output contains a `TOOL_REQUEST:` block and ends with `STATUS: BLOCKED_TOOL_REQUEST`, the leader MUST spawn `tools-manager-lead` immediately, NOT retry the sub-agent and NOT attempt the sub-agent's work directly. After the manager returns Mode A advice the leader re-spawns the original sub-agent with the advice included. After the manager returns a Mode B proposal the leader presents the proposal via AskUserQuestion; only on user approval does the leader re-spawn tools-manager-lead with `APPROVED` so it can execute file creation, then re-spawn the original sub-agent.
