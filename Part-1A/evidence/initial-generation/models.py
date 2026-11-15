"""Data models and validation helpers for the Freelance Project Expense & Budget Ledger."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from typing import Any


class Category(str, Enum):
    """Allowed expense categories."""

    SOFTWARE = "software"
    HARDWARE = "hardware"
    TRAVEL = "travel"
    CONTRACTOR = "contractor"
    OTHER = "other"


class ProjectStatus(str, Enum):
    """Project lifecycle status."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class AlertStatus(str, Enum):
    """Budget utilization alert status."""

    OK = "OK"
    WARNING = "WARNING"
    OVER_BUDGET = "OVER_BUDGET"


def parse_positive_decimal(value: str | int | float | Decimal, field_name: str = "amount") -> Decimal:
    """Parse a positive Decimal rounded to 2 decimal places."""
    try:
        dec = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc

    if not dec.is_finite() or dec <= Decimal("0"):
        raise ValueError(f"{field_name} must be greater than 0")

    return dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_iso_date(value: str) -> str:
    """Validate YYYY-MM-DD ISO date string."""
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO date (expected YYYY-MM-DD): {value!r}") from exc
    return value


@dataclass
class Expense:
    """Single expense entry tied to a project."""

    expense_id: str
    amount: str
    category: str
    description: str
    date: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Expense:
        return cls(
            expense_id=str(data["expense_id"]),
            amount=str(data["amount"]),
            category=str(data["category"]),
            description=str(data["description"]),
            date=str(data["date"]),
        )


@dataclass
class Project:
    """Freelance project with a budget and list of expenses."""

    project_id: str
    name: str
    client: str
    budget: str
    status: str = ProjectStatus.ACTIVE.value
    expenses: list[Expense] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "client": self.client,
            "budget": self.budget,
            "status": self.status,
            "expenses": [exp.to_dict() for exp in self.expenses],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Project:
        return cls(
            project_id=str(data["project_id"]),
            name=str(data["name"]),
            client=str(data["client"]),
            budget=str(data["budget"]),
            status=str(data.get("status", ProjectStatus.ACTIVE.value)),
            expenses=[Expense.from_dict(e) for e in data.get("expenses", [])],
        )
