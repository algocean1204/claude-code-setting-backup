---
paths:
  - "**/*.prisma"
  - "**/*.sql"
  - "**/db/**"
  - "**/prisma/**"
  - "**/supabase/**"
---

# Database Rules

## Schema Design
- Schema must match docs/spec.md
- FK, Enum, index coverage must be complete
- Environment separation: dev/staging/prod

## Migration
- Reversible migrations required
- Migration chain integrity must be maintained
- Destructive changes require rollback plan
- Consider ALTER lock implications
- Review data loss risks

## Required Elements
- Index strategy required
- Seed data required
- Prevent N+1 queries
- Use transactions appropriately
- Verify connection pool configuration
