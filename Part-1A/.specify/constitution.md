# Part 1A Constitution — Freelance Project Expense & Budget Ledger CLI

## 1. Engineering Principles
- **Language & Runtime:** Python 3.11+ standard library only for production code (`src/`), ensuring zero external runtime dependencies and deterministic behavior.
- **Code Quality:** All source and test files must pass `ruff check` with zero errors and zero warnings.
- **Security:** All source files must pass `bandit -r src/` with zero medium/high severity findings. No `eval`, `exec`, `pickle`, `shell=True`, or hardcoded secrets.
- **Determinism:** All calculations (totals, remaining budget, utilization percentage, over-budget flags) must be exact and deterministic using `Decimal` or integer cents (no floating-point drift).
- **Persistence:** Atomic or safe JSON file persistence with explicit schema validation on load.

## 2. Harness & SDD Rules
- Specifications and acceptance criteria are authoritative.
- The coding agent must not weaken acceptance criteria, delete failing tests, or disable lint/security checks to achieve PASS.
- Initial generated implementation must be preserved in `evidence/initial-generation/` before any harness-driven repair.
