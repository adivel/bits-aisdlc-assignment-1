# Technical Plan — Freelance Project Expense & Budget Ledger CLI

## Architecture
- `Part-1A/src/models.py`: Data structures (`Project`, `Expense`, `AlertStatus`, `Category` enum) and `Decimal` validation helpers.
- `Part-1A/src/storage.py`: Safe JSON ledger load/save with corruption detection and atomic-style write.
- `Part-1A/src/ledger.py`: Core business logic (`create_project`, `archive_project`, `add_expense`, `get_summary`, `list_expenses`).
- `Part-1A/src/cli.py`: `argparse` CLI entrypoint supporting `project create`, `project archive`, `expense add`, `expense list`, and `summary` subcommands with `--ledger` and `--json` flags.

## Verification Strategy
- **Lint:** `ruff check src tests`
- **SAST:** `bandit -r src -ll`
- **Tests:** `pytest tests/` covering AC-1 through AC-7.
