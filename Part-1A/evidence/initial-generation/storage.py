"""JSON persistence for the Freelance Project Expense & Budget Ledger."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models import Project


class LedgerCorruptedError(RuntimeError):
    """Raised when the ledger JSON file is invalid or malformed."""


def load_ledger(path: Path) -> dict[str, Project]:
    """Load projects from a JSON ledger file.

    Returns an empty dict if the file does not exist yet.
    Raises LedgerCorruptedError if the file exists but contains invalid JSON.
    """
    if not path.exists():
        return {}

    try:
        raw_text = path.read_text(encoding="utf-8")
        data: Any = json.loads(raw_text)
    except (OSError, json.JSONDecodeError) as exc:
        raise LedgerCorruptedError(f"Failed to read valid JSON from {path}: {exc}") from exc

    if not isinstance(data, dict) or "projects" not in data or not isinstance(data["projects"], dict):
        raise LedgerCorruptedError(f"Malformed ledger structure in {path}")

    projects: dict[str, Project] = {}
    for pid, pdata in data["projects"].items():
        projects[pid] = Project.from_dict(pdata)
    return projects


def save_ledger(path: Path, projects: dict[str, Project]) -> None:
    """Persist projects to a JSON ledger file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"projects": {pid: proj.to_dict() for pid, proj in projects.items()}}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
