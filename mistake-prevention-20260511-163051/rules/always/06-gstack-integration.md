# GSTACK INTEGRATION (Non-negotiable)

gstack (github.com/garrytan/gstack) is the **PRIMARY** skill toolset. When a gstack skill covers the same function as a built-in agent, the gstack skill MUST be used instead. The replaced agent has been removed.

## Replacement Mapping

| gstack Skill | Replaces | Phase |
|---|---|---|
| `/office-hours` | *(new — no prior equivalent)* | Phase 0.5 |
| `/plan-ceo-review` | *(new — no prior equivalent)* | Phase 0.5 |
| `/plan-eng-review` | `spec-architect` | Phase 1 |
| `/design-consultation` | `design-trend-researcher` | Phase 1.5 |
| `/design-review` | `design-critic` | Phase 1.5 |
| `/review` | `feedback-code-reviewer` | Phase 4 |
| `/cso` | `feedback-security-reviewer` | Phase 4 |
| `/qa` | `test-e2e-engineer` | Phase 3 |
| `/investigate` | `bug-detective` | Bug Fix |
| `/ship` | `github-deployer` (PR creation) | Deploy |
| `/land-and-deploy` | `github-deployer` (deploy + verify) | Deploy |

---

## Phase 0.5 — Service Design Discussion (Non-negotiable)

**When**: After Phase 0 (tech stack confirmed), BEFORE Phase 1 (technical spec).
**Purpose**: Discuss features from the USER's perspective — add, remove, change, expand — before any technical design begins. Perfect WHAT to build before discussing HOW.

### Mandatory Flow

```
[Phase 0 complete]
       ▼
[1] Invoke /office-hours
    └─ YC-style product questioning with user
    └─ Challenge assumptions, extract hidden capabilities
    └─ Generate implementation alternatives with effort estimates
       ▼
[2] Invoke /plan-ceo-review
    └─ Rethink scope using 4 modes:
       • Expansion — what could make this 10x better?
       • Selective — what subset delivers 80% of value?
       • Hold — what should stay exactly as requested?
       • Reduction — what can be cut without losing core value?
       ▼
[3] Leader + user discuss results together
    └─ Iterate until feature scope is FULLY decided
    └─ User explicitly approves final feature list
       ▼
[4] Output: docs/service-design-decisions.md
       ▼
[5] Proceed to Phase 1
```

### Rules
- This phase is **conversational, not technical**. No architecture, no code, no module design.
- Leader MUST present `/office-hours` findings to user and discuss interactively.
- Leader MUST present `/plan-ceo-review` scope options to user for selection.
- Phase 0.5 is NOT skippable. Even for "simple" projects, run the full flow.
- User must explicitly approve the feature scope before proceeding.

---

## Phase 1 — Technical Spec (Updated)

- `/plan-eng-review` replaces `spec-architect` for architecture locking with diagrams and test plans.
- Design Discussion team: **`/plan-eng-review` (gstack) + `spec-security`** (2 members, not 3).
- `/plan-eng-review` locks architecture, generates dependency diagrams, and produces test plans.

---

## Phase 1.5 — Design System (Updated)

- `/design-consultation` replaces `design-trend-researcher` for initial design system creation (includes competitive research and creative risks).
- `/design-review` replaces `design-critic` for design audit and critique.
- Design team: **`design-lead` → `/design-consultation` (gstack), `design-motion-specialist`, `/design-review` (gstack), `ui-ux-designer`**.

---

## Phase 3 — Verification (Updated)

- `/qa` replaces `test-e2e-engineer` for browser-based E2E testing with real Chromium.
- Verification team: **`/qa` (gstack), `quality-judge`**.
- `/qa` tests in real browsers, identifies bugs, fixes atomically, re-verifies, and auto-generates regression tests.

---

## Phase 4 — Feedback (Updated)

- `/review` replaces `feedback-code-reviewer` for production-grade code review.
- `/cso` replaces `feedback-security-reviewer` for OWASP Top 10 + STRIDE security audit.
- Feedback team: **`feedback-lead` → `/review` (gstack), `ux`, `integration`, `/cso` (gstack), `performance`, `visual`** (6 reviewers, 2 are gstack skills).

---

## Bug Fix Protocol (Updated)

- `/investigate` replaces `bug-detective` for systematic root-cause analysis.
- Flow: `project-scanner` → `/investigate` (gstack) + `guardian` (parallel) → relevant implementation team + `guardian` → Verification → repeat until S grade.

---

## Deploy (Updated)

- `/ship` replaces `github-deployer` for syncing, testing, auditing coverage, and opening PRs.
- `/land-and-deploy` handles merging, deploying to production, and verifying health.
- Flow: `/ship` → `/land-and-deploy` → `/canary` (optional post-deploy monitoring).

---

## Sprint Process — Skill Chaining (Non-negotiable)

gstack follows a sprint process where **each skill feeds into the next**. The leader MUST follow this chain. Do not skip steps — completeness is cheap when AI makes the marginal cost near-zero.

```
Think → Plan → Build → Review → Test → Ship → Reflect
```

### Full Skill Chain

| Stage | Skill | Feeds Into | What It Produces |
|---|---|---|---|
| **Think** | `/office-hours` | `/plan-ceo-review` | Design doc, reframed problem, implementation alternatives |
| **Think** | `/plan-ceo-review` | `/plan-eng-review` | Scope decision (expansion/selective/hold/reduction) |
| **Plan** | `/plan-eng-review` | Implementation | Architecture diagrams, test plans, edge cases |
| **Plan** | `/plan-design-review` | `/design-consultation` | Design dimension ratings, improvement targets |
| **Plan** | `/design-consultation` | `/design-shotgun` | Complete design system, DESIGN.md |
| **Plan** | `/design-shotgun` | `/design-html` | Approved visual direction from multiple variants |
| **Plan** | `/design-html` | Implementation | Production-quality HTML from approved mockup |
| **Build** | Implementation agents | `/review` | Code |
| **Review** | `/review` | `/qa` | Auto-fixed bugs, flagged issues |
| **Review** | `/codex` | Cross-model analysis | Independent second opinion from OpenAI |
| **Test** | `/qa` | `/ship` | Bug fixes, regression tests, browser verification |
| **Test** | `/cso` | `/ship` | Security audit (OWASP + STRIDE) |
| **Test** | `/benchmark` | `/ship` | Performance baselines, Core Web Vitals |
| **Ship** | `/ship` | `/land-and-deploy` | PR with tests, coverage audit |
| **Ship** | `/land-and-deploy` | `/canary` | Merged + deployed + health verified |
| **Ship** | `/canary` | `/document-release` | Post-deploy monitoring results |
| **Reflect** | `/document-release` | `/retro` | Updated docs matching shipped code |
| **Reflect** | `/retro` | Next sprint | Per-person metrics, shipping streaks, growth opportunities |

### Proactive Skill Routing (Non-negotiable)

The leader MUST detect when a gstack skill matches the current context and **invoke it automatically** via the Skill tool. Do NOT answer directly when a skill exists for the task.

| User Signal | Invoke |
|---|---|
| Describes a new idea, asks "is this worth building", wants to brainstorm | `/office-hours` |
| Asks about strategy, scope, ambition, "think bigger" | `/plan-ceo-review` |
| Asks to review architecture, lock in the plan | `/plan-eng-review` |
| Asks about design system, brand, visual identity | `/design-consultation` |
| Asks to review design of a plan | `/plan-design-review` |
| Wants all reviews done automatically | `/autoplan` |
| Reports a bug, error, broken behavior, "why is this broken" | `/investigate` |
| Asks to test the site, find bugs, QA | `/qa` |
| Asks to review code, check the diff, pre-landing review | `/review` |
| Asks about visual polish, design audit of a live site | `/design-review` |
| Asks to ship, deploy, push, create a PR | `/ship` |
| PR is approved, ready to merge and deploy | `/land-and-deploy` |
| Post-deploy, wants to monitor for issues | `/canary` |
| Asks to update docs after shipping | `/document-release` |
| Asks for a weekly retro, what did we ship | `/retro` |
| Asks for a second opinion, another AI review | `/codex` |
| Asks for safety mode, careful mode | `/careful` or `/guard` |
| Wants to restrict edits to a directory | `/freeze` or `/unfreeze` |
| Wants to see performance before/after | `/benchmark` |
| Wants to test authenticated pages, import cookies | `/setup-browser-cookies` |
| Wants to learn/remember patterns across sessions | `/learn` |

### Phase Transition Skill Suggestions

At every phase transition, the leader MUST suggest the natural next gstack skill to the user:

| After Completing | Suggest Next |
|---|---|
| Phase 0 (tech stack) | "Let's start `/office-hours` to discuss what to build from your perspective." |
| `/office-hours` | "Now let's run `/plan-ceo-review` to challenge the scope and find the best product." |
| `/plan-ceo-review` | "Scope is decided. Running `/plan-eng-review` to lock architecture." |
| Phase 1 (spec) | "Moving to design. Starting `/design-consultation` for the design system." |
| Phase 1.5 (design) | "Design ready. Proceeding to implementation." |
| Phase 2 (build) | "Build complete. Running `/review` for code review." |
| `/review` | "Review done. Running `/qa` to test in real browser." |
| `/qa` | "QA passed. Running `/cso` for security audit." |
| `/cso` | "Security clear. Running `/ship` to create PR." |
| `/ship` | "PR open. Ready for `/land-and-deploy` when approved." |
| `/land-and-deploy` | "Deployed. Running `/canary` to monitor." |
| `/canary` | "All clear. Running `/document-release` to update docs." |
| `/document-release` | "Docs updated. Run `/retro` for retrospective when ready." |

---

## Additional gstack Skills (Always Available)

These skills do not replace any agent but are available throughout the project lifecycle:

| Skill | Purpose | When to Use |
|---|---|---|
| `/browse` | Real Chromium browser control (~100ms per command) | Testing, dogfooding, verification |
| `/connect-chrome` | Launch real Chrome with Side Panel; watch actions live | Live observation of QA flows |
| `/benchmark` | Performance baselines and Core Web Vitals comparison | Before/after every PR |
| `/canary` | Post-deployment monitoring for errors and regressions | After every deploy |
| `/careful` | Warns before destructive commands | Production work, sensitive operations |
| `/freeze` / `/guard` / `/unfreeze` | Directory-level edit restrictions for safety | Debugging, focused work |
| `/design-shotgun` | Generate multiple visual variants for comparison | Design exploration phase |
| `/design-html` | Convert mockups to production HTML with framework detection | After design approval |
| `/design-review` | Design audit + fix with atomic commits | Design polish, visual QA |
| `/codex` | Cross-model review (Claude + OpenAI second opinion) | Critical reviews, complex logic |
| `/learn` | Persistent pattern learning across sessions | Continuously — patterns compound over time |
| `/autoplan` | Automated CEO → design → engineering review pipeline | When user wants full review in one command |
| `/qa-only` | Bug reports only (no code changes) | When reporting is needed without fixes |
| `/retro` | Weekly team retrospectives with metrics | End of sprint, weekly review |
| `/document-release` | Update all docs to match shipped code | After every deploy |
| `/plan-design-review` | Design dimension rating with interactive decisions | Plan review with design focus |
| `/setup-browser-cookies` | Import real browser cookies for authenticated testing | Before testing authenticated pages |
| `/setup-deploy` | One-time deploy configuration | Before first `/land-and-deploy` |

---

## Invocation Method

gstack skills are invoked via the **Skill tool** with the slash command name:
- Example: `Skill("office-hours")`, `Skill("review")`, `Skill("cso")`
- Agents that need to use gstack skills invoke them through the Skill tool, same as any other skill.
- gstack skills follow the same guardian monitoring requirements as the agents they replaced.

## Completion Status Protocol

All gstack skill outputs MUST end with one of:
- **DONE** — All steps completed successfully with evidence.
- **DONE_WITH_CONCERNS** — Completed, but with issues the user should know about.
- **BLOCKED** — Cannot proceed. State what is blocking and what was tried.
- **NEEDS_CONTEXT** — Missing information required to continue.

If a gstack skill fails 3 times, STOP and escalate to the user. Bad work is worse than no work.
