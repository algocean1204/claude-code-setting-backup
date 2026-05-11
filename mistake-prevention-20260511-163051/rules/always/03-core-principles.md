# CORE ENGINEERING PRINCIPLES (Non-negotiable)

## SRP-Based Hierarchical Atomic Module Design

All code is separated into 3 layers:

| Layer | Role | Rules |
|---|---|---|
| **Feature** | Business domain unit | Separated by folder |
| **Manager/Orchestrator** | Controls business logic sequence | Direct logic execution prohibited. Only calls Atomic Modules + passes data |
| **Atomic Module** | Smallest unit function | One function = one action. Pure function oriented |

Core rules:
- Atomic Modules: pure functions, DI required. Direct import of external infrastructure prohibited
- Common/infrastructure (env vars, DB, logging): separated into core/. Placement inside Feature folders prohibited
- Lower → upper layer references prohibited (unidirectional flow)
- **Size limits**: Atomic 30 lines, Manager 50 lines, file 200 lines, component 150 lines max
- **Prohibited**: 300+ line single files, circular dependencies, ambiguous function names (processData, handleAll), mixing multiple responsibilities in one file

## No Workarounds — Proper Integration Required

All features must be connected using the **official, intended methods** of the relevant technology/library. Workarounds are prohibited.

Principles:
1. When errors occur, resolve root cause (no bypassing)
2. Workaround detection criteria — fix immediately upon discovery:
   - `// @ts-ignore`, `// @ts-expect-error` (type error bypass)
   - `try-catch` swallowing errors and returning empty/default values
   - `any` type to bypass type checking
   - `!important` to force-resolve CSS conflicts
   - `setTimeout`/`requestAnimationFrame` to temporarily avoid timing issues
   - Direct DOM manipulation bypassing framework state management
   - Hardcoded values avoiding dynamic data connections
   - `eslint-disable`, `noqa` etc. to suppress lint warnings
3. pair-reviewer: workaround pattern detection is top priority, immediate proper implementation instruction upon discovery
4. Workaround code present during Phase 2.5/Phase 4 = FAIL

**Exception**: Only allowed for known bugs registered in external library official issue trackers.
- Format: `// WORKAROUND: [issueURL] - Temporary workaround for [library] bug. Remove when fixed`
- Must record in docs/workarounds.md

## Version Policy
- Always use latest LTS version for all technologies
- Search for current LTS version before confirming tech stack
- Odd-numbered Node.js versions (non-LTS) prohibited
- Pin exact versions in package.json and requirements.txt (no ^ or ~)

## Permission Rules
1. File read/write/edit within project folder: auto-approve
2. File **deletion**: ALWAYS ask user confirmation ("Delete? (y/n)")
3. Background execution: ALWAYS ask user confirmation

## Korean Comments
All code comments/docstrings must be written in Korean. English comments prohibited. Focus on "why it's done this way."
