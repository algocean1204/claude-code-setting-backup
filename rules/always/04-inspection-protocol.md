# MULTI-ANGLE ITERATIVE INSPECTION PROTOCOL (Non-negotiable)

Applies to: Phase 2.5, Phase 3, Phase 4, Phase 4.5 — all phases involving inspection and fixing.

## Iterative Cycle

1. **Write feature list**: Create a COMPLETE list of all implemented features (serves as inspection checklist)
2. **Sequential feature inspection**: Inspect each feature one by one in order. Fix issues immediately before moving to next
3. **Fresh perspective re-inspection**: After completing full inspection, if ANY fixes were made → re-inspect entire project from a different angle
4. **Multi-angle coverage**: Not limited to features. Inspect sequentially from EVERY angle:
   - Functional correctness (feature-by-feature)
   - Type safety + API contracts
   - UI/UX consistency + responsiveness
   - Error handling + edge cases
   - Performance + optimization
   - Security vulnerabilities
   - Accessibility compliance
   - Design token + style consistency
   - Cross-module integration + data flow
   - Build + deployment readiness
5. **Repeat until convergence**: Only complete when a FULL multi-angle pass produces ZERO issues

```
[Write feature list] → [Inspect #1] → [Inspect #2] → ... → [Inspect #N]
       ↓
[Any fixes made?] → YES → [Re-inspect ALL from fresh angle] → loop back
       ↓ NO
[Next inspection angle] → [All angles zero issues?] → YES → ✅ Complete
                                                    → NO → loop back
```

## Inspection Lead Context Preservation
Inspection leads (error-check-lead, feedback-lead, quality-judge, etc.) MUST hold the full inspection item list in context throughout the entire cycle:
- Minimize context compression, keep original checklist intact
- Do NOT summarize or abbreviate list mid-inspection
- Only clear the list after full cycle complete + all issues resolved

## End-to-End Data Flow Tracing

Trace synthetic data through the entire code path for every feature — **mandatory inspection item**.

Process:
1. Write complete feature list
2. For each feature, create synthetic test data → trace full path (entry point → middleware → controller → service → repository → DB → final response)
3. **Diverse test data**: happy-path only is prohibited. Must include:
   - Normal valid data (expected to pass)
   - Boundary/edge cases (limit values, empty string, 0, null)
   - Ambiguous data (string "0", empty arrays, Unicode, whitespace-only)
   - Invalid data (expected to be rejected → verify error handling)
4. Verify at each step:
   - No logic dead-ends (no unreachable code)
   - Path references are correct (imports, routes, service calls, DB queries)
   - Connections are intact (controller → service → repository → DB)
   - Data transformations produce intended results
   - Final output matches expected feature behavior
5. Pay special attention to:
   - Route/path references pointing to wrong handlers or non-existent files
   - Misconfigured or missing service/repository injections
   - Queries silently returning wrong results instead of failing
   - Middleware ordering issues skipping validation or auth
