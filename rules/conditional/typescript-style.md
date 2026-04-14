---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.jsx"
---

# TypeScript/React Code Style

## Korean Comments (Required)
- All comments must be in Korean. English comments prohibited
- Focus on "why it's done this way"

## Workaround Detection — Fix immediately upon discovery
- `// @ts-ignore`, `// @ts-expect-error`: prohibited
- `eslint-disable`: prohibited
- `as any` type bypass: prohibited
- `setTimeout`/`requestAnimationFrame` to temporarily avoid timing issues: prohibited
- Direct DOM manipulation bypassing framework state management: prohibited

## SRP Size Limits
- Component: 150 lines max
- File: 200 lines max

## Type & Import Rules
- Shared types must be imported from `shared/types/` (duplicate definitions prohibited)
- Design tokens required — hardcoded colors/spacing prohibited, import from design system
