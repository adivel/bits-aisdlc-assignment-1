"""Core business logic for Freelance Project Expense & Budget Ledger."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any
import uuid

from models import (
    AlertStatus,
    Category,
    Expense,
    Project,
    ProjectStatus,
    parse_positive_decimal,
    validate_iso_date,
)
from storage import load_ledger, save_ledger


class LedgerError(ValueError):
    """Domain validation or state error."""


def create_project(
    ledger_path: Path,
    project_id: str,
    name: str,
    client: str,
    budget: str | int | float | Decimal,
) -> Project:
    """Create a new freelance project and persist it."""
    pid = project_id.strip()
    if not pid:
        raise LedgerError("project_id must be non-empty")
    if not name.strip():
        raise LedgerError("name must be non-empty")
    if not client.strip():
        raise LedgerError("client must be non-empty")

    parsed_budget = parse_positive_decimal(budget, field_name="budget")
    projects = load_ledger(ledger_path)
    if pid in projects:
        raise LedgerError(f"Project '{pid}' already exists")

    project = Project(
        project_id=pid,
        name=name.strip(),
        client=client.strip(),
        budget=f"{parsed_budget:.2f}",
        status=ProjectStatus.ACTIVE.value,
    )
    projects[pid] = project
    save_ledger(ledger_path, projects)
    return project


def archive_project(ledger_path: Path, project_id: str) -> Project:
    """Archive an existing project."""
    projects = load_ledger(ledger_path)
    if project_id not in projects:
        raise LedgerError(f"Project '{project_id}' not found")

    project = projects[project_id]
    project.status = ProjectStatus.ARCHIVED.value
    save_ledger(ledger_path, projects)
    return project


def add_expense(
    ledger_path: Path,
    project_id: str,
    amount: str | int | float | Decimal,
    category: str,
    description: str,
    date_str: str,
) -> Expense:
    """Add an expense to an active project."""
    projects = load_ledger(ledger_path)
    if project_id not in projects:
        raise LedgerError(f"Project '{project_id}' not found")

    project = projects[project_id]
    if project.status != ProjectStatus.ACTIVE.value:
        raise LedgerError(f"Cannot add expense to archived project '{project_id}'")

    try:
        valid_category = Category(category.strip().lower()).value
    except ValueError as exc:
        allowed = ", ".join(c.value for c in Category)
        raise LedgerError(f"Invalid category '{category}'. Allowed: {allowed}") from exc

    if not description.strip():
        raise LedgerError("description must be non-empty")

    parsed_amount = parse_positive_decimal(amount, field_name="amount")
    valid_date = validate_iso_date(date_str.strip())

    expense = Expense(
        expense_id=str(uuid.uuid4())[:8],
        amount=f"{parsed_amount:.2f}",
        category=valid_category,
        description=description.strip(),
        date=valid_date,
    )
    project.expenses.append(expense)
    save_ledger(ledger_path, projects)
    return expense


def list_expenses(
    ledger_path: Path,
    project_id: str,
    category: str | None = None,
) -> list[Expense]:
    """List expenses for a project, optionally filtered by category."""
    projects = load_ledger(ledger_path)
    if project_id not in projects:
        raise LedgerError(f"Project '{project_id}' not found")

    expenses = projects[project_id].expenses
    if category is not None:
        try:
            valid_cat = Category(category.strip().lower()).value
        except ValueError as exc:
            raise LedgerError(f"Invalid category filter: '{category}'") from exc
        expenses = [e for e in expenses if e.category == valid_cat]
    return expenses


def get_summary(ledger_path: Path, project_id: str) -> dict[str, Any]:
    """Compute deterministic budget summary and alert status for a project."""
    projects = load_ledger(ledger_path)
    if project_id not in projects:
        raise LedgerError(f"Project '{project_id}' not found")

    project = projects[project_id]
    budget = Decimal(project.budget)
    total_spent = sum((Decimal(e.amount) for e in project.expenses), Decimal("0.00"))
    remaining = budget - total_spent
    utilization = ((total_spent / budget) * Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    if utilization < Decimal("80.00"):
        alert = AlertStatus.OK.value
    elif utilization <= Decimal("100.00"):
        alert = AlertStatus.WARNING.value
    else:
        alert = AlertStatus.OVER_BUDGET.value

    return {
        "project_id": project.project_id,
        "name": project.name,
        "client": project.client,
        "status": project.status,
        "budget": f"{budget:.2f}",
        "total_spent": f"{total_spent:.2f}",
        "remaining_budget": f"{remaining:.2f}",
        "utilization_pct": float(utilization),
        "alert_status": alert,
        "expense_count": len(project.expenses),
    }
