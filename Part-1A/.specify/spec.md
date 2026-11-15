# Feature Specification — Freelance Project Expense & Budget Ledger CLI

## 1. Problem Statement
A freelance developer needs a deterministic CLI tool to track budgets and expenses per freelance project, enforce budget thresholds, and generate accurate project financial summaries persisted to a JSON ledger file.

## 2. Functional Requirements

### FR-1: Project Management
- **FR-1.1:** Create a project with `project_id` (unique non-empty slug, e.g., `acme-web`), `name` (non-empty string), `client` (non-empty string), and `budget` (positive decimal > 0, up to 2 decimal places).
- **FR-1.2:** Reject duplicate `project_id` with a non-zero exit code and clear error message.
- **FR-1.3:** Support archiving a project (`status`: `active` -> `archived`). Archived projects cannot accept new expenses.

### FR-2: Expense Recording
- **FR-2.1:** Add an expense to an `active` project with `amount` (positive decimal > 0), `category` (one of: `software`, `hardware`, `travel`, `contractor`, `other`), `description` (non-empty string), and `date` (`YYYY-MM-DD` ISO format).
- **FR-2.2:** Reject expenses for non-existent or `archived` projects, invalid categories, non-positive amounts, or invalid dates.

### FR-3: Budget Tracking & Alerts
- **FR-3.1:** Compute `total_spent`, `remaining_budget` (`budget - total_spent`), and `utilization_pct` (`round((total_spent / budget) * 100, 2)`).
- **FR-3.2:** Compute deterministic alert status:
  - `OK` when `utilization_pct < 80.0`
  - `WARNING` when `80.0 <= utilization_pct <= 100.0`
  - `OVER_BUDGET` when `utilization_pct > 100.0`

### FR-4: Reporting & Filtering
- **FR-4.1:** List expenses for a project, optionally filtered by `--category`.
- **FR-4.2:** Output project summary in `--json` mode (machine-readable) or human-readable table mode.

### FR-5: Persistence
- **FR-5.1:** Persist all projects and expenses to a JSON ledger file (`--ledger <path>`, default `ledger.json`).
- **FR-5.2:** If the ledger file does not exist, initialize an empty ledger on first write. If the ledger file is corrupted (invalid JSON), exit with non-zero status and do not overwrite the file.

## 3. Acceptance Criteria (Binary / Testable)
- **AC-1:** Creating a project with valid inputs persists it to JSON and returns exit code `0`.
- **AC-2:** Creating a duplicate `project_id` or `budget <= 0` returns non-zero exit code and leaves the ledger unchanged.
- **AC-3:** Adding valid expenses updates `total_spent`, `remaining_budget`, `utilization_pct`, and `alert_status` accurately using `Decimal` arithmetic (no float rounding errors like `0.1 + 0.2 != 0.3`).
- **AC-4:** Alert status transitions deterministically: `< 80%` -> `OK`, `80%..100%` -> `WARNING`, `> 100%` -> `OVER_BUDGET`.
- **AC-5:** Adding an expense to an `archived` project fails with non-zero exit code and leaves the ledger unchanged.
- **AC-6:** Filtering expenses by `--category` returns only matching expenses.
- **AC-7:** Corrupted JSON ledger file causes a non-zero exit code without overwriting the file.
