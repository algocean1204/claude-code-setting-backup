---
paths:
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/tests/**"
  - "**/__tests__/**"
  - "**/e2e/**"
---

# Testing Rules

## Coverage Target
- Unit/integration tests: 80%+ coverage

## CAUTION: Endpoint Logic Bugs
**Actual business logic** in endpoint handlers MUST be verified.
Not just status codes/response shapes — test that logic produces correct results for various inputs, edge cases, and error conditions.

## Test Data Requirements
- Acceptance criteria (docs/spec.md) → convert to test cases
- Normal data (happy path)
- Boundary/edge cases (limit values, empty string, 0, null)
- Invalid data (verify error handling)

## E2E Testing
- User flows, cross-browser, error scenarios
- Use Playwright or Cypress
