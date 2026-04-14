# MANDATORY PLANNING GATE (Non-negotiable)

Before code implementation (Phase 2) in development projects, **3 HTML design documents** MUST be created + user approval required.

## Workflow

```
[Phase 0: Tech stack confirmed]
       ▼
[Phase 1: Spec discussion]
       ▼
[★ PLANNING GATE ★] ← MUST stop here
       │
       ├─ 1. Execute Plan-Module-Architecture skill
       ├─ 2. Generate 3 HTML design documents
       ├─ 3. Deliver to user via macOS `open` command
       └─ 4. Wait for user approval
              ├── All 3 approved → Proceed to Phase 2 (implementation)
              ├── Partial modification → Fix only the requested HTML, re-confirm
              └── Rejected → Stop or full redesign
```

## 3 HTML Deliverables

### HTML 1: Module Design (module-design.html)
- Generated via Plan-Module-Architecture skill
- Tech stack, module hierarchy (C0 common + F1~FN features), IN/OUT specs
- Main pipeline visualization + step-by-step IN/OUT tables
- Dependency matrix, collapsible module blocks, color coding
- Implementation checklist

### HTML 2: ERD Design (erd-design.html)
- Table cards (PK/FK indicators, column types/constraints)
- Relationship visualization (1:1, 1:N, N:M)
- Detailed table specs (indexes, Enums, seed data)
- For projects without DB: replace with data model/state structure diagram

### HTML 3: Page-Feature-Module-ERD Connection Map (connection-map.html)
- For each page (screen/view):
  - Feature list for that page
  - Module mapping for each feature (F1.1, F2.3, etc.)
  - DB table mapping for each module
- Visual connection lines: Page → Feature → Module → Table
- Full system data flow at a glance
- Identify missing connections / unused modules & tables

## Plan-Module-Architecture Skill

**Skill path**: `~/Documents/Plan-Module-Architecture/`

| File | Purpose | When to read |
|---|---|---|
| `SKILL.md` | 4-Phase workflow definition | First when starting design |
| `references/module-design-rules.md` | Module IN/OUT rules, SRP verification, dependency direction | When entering Phase 2 (module layer design) |
| `references/html-template-guide.md` | HTML design doc color/typography/component specs | When entering Phase 4 (HTML generation) |
| `references/ai-behavior-guide.md` | Conversation protocol, split/merge decisions, large project strategy | When entering Phase 1 (project understanding) |

**Execution order**: Phase 1 (tech stack) → Phase 2 (module layers) → Phase 3 (IN/OUT spec) → Phase 4 (HTML generation)

**Trigger keywords**:
- Korean: `설계`, `아키텍처`, `모듈 설계`, `시스템 설계`, `파이프라인 설계`, `구조 잡아줘`, `설계도`
- English: `architecture`, `module design`, `system design`, `pipeline design`, `SRP design`

**Core principles**:
- 1 module = exactly 1 OUT, IN = main + auxiliary
- Main pipeline = single straight line without branches
- C0 (common) + F1~FN (feature) layer structure
- Split immediately on SRP violation (2+ reasons for change = split)
- Final deliverable: **Pampas #F4F3EE background** interactive HTML (collapsible, color coding, dependency matrix)
- Large projects (30+ modules): split by Feature unit, user approval at every step
