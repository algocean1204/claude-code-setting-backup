---
paths:
  - "**/*.py"
---

# Python Code Style

## Type Hints (Required)
- Type hints required for all function parameters/return types and class attributes
- Use Python 3.10+ syntax: `str | None`, `list[str]` (instead of Union, Optional)
- Minimize `Any`, explicitly declare `-> None`

## Korean Comments (Required)
- All comments/docstrings must be in Korean. English comments prohibited
- Focus on "why it's done this way"

## SRP Size Limits
- Atomic Module: 30 lines max
- Manager/Orchestrator: 50 lines max
- File: 200 lines max

## Workaround Detection
- `noqa` comments to suppress lint warnings: prohibited
- Empty `except:` / bare `except Exception:` → error swallowing prohibited
- `Any` type to bypass type checking: prohibited
- `# type: ignore`: prohibited
