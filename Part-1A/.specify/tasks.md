# Implementation Tasks — Part 1A

- [ ] **T-1:** Implement `models.py` with `Category`, `AlertStatus`, `Project`, `Expense`, and `Decimal`/ISO-date validators.
- [ ] **T-2:** Implement `storage.py` for JSON ledger load/save and corruption handling (AC-7).
- [ ] **T-3:** Implement `ledger.py` for project creation, archiving, expense addition, filtering, and exact `Decimal` budget calculations (AC-1 to AC-6).
- [ ] **T-4:** Implement `cli.py` with `argparse` subcommands and `--json` output.
- [ ] **T-5:** Implement `tests/test_ledger.py` and `tests/test_cli.py` derived from AC-1 through AC-7.
- [ ] **T-6:** Implement `.harness/run_harness.py` (ruff + bandit + pytest) and preserve `evidence/initial-generation/` before any repair.
