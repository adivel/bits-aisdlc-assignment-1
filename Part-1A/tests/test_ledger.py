"""Deterministic unit and contract tests derived from Part-1A spec (AC-1 to AC-7)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cli import main as cli_main
from ledger import (
    LedgerError,
    add_expense,
    archive_project,
    create_project,
    get_summary,
    list_expenses,
)
from storage import LedgerCorruptedError


def test_ac1_create_project_persists(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    exit_code = cli_main(
        [
            "--ledger",
            str(ledger),
            "--json",
            "project",
            "create",
            "--id",
            "acme-web",
            "--name",
            "Acme Website",
            "--client",
            "Acme Corp",
            "--budget",
            "1000.00",
        ]
    )
    assert exit_code == 0
    assert ledger.exists()


def test_ac2_reject_duplicate_and_non_positive_budget(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    create_project(ledger, "p1", "Proj 1", "Client A", "500.00")

    with pytest.raises(LedgerError, match="already exists"):
        create_project(ledger, "p1", "Proj 1 Dup", "Client A", "500.00")

    with pytest.raises(ValueError, match="greater than 0"):
        create_project(ledger, "p2", "Proj 2", "Client B", "0")

    with pytest.raises(ValueError, match="greater than 0"):
        create_project(ledger, "p3", "Proj 3", "Client C", "-50")


def test_ac3_decimal_precision_no_float_drift(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    create_project(ledger, "p1", "Decimal Test", "Client", "1.00")
    add_expense(ledger, "p1", "0.10", "software", "Item 1", "2026-11-01")
    add_expense(ledger, "p1", "0.20", "software", "Item 2", "2026-11-02")

    summary = get_summary(ledger, "p1")
    assert summary["total_spent"] == "0.30"
    assert summary["remaining_budget"] == "0.70"
    assert summary["utilization_pct"] == 30.0


def test_ac4_alert_status_transitions(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    create_project(ledger, "p1", "Alert Test", "Client", "100.00")

    add_expense(ledger, "p1", "79.99", "software", "Under 80", "2026-11-01")
    assert get_summary(ledger, "p1")["alert_status"] == "OK"

    add_expense(ledger, "p1", "0.01", "software", "Hit 80", "2026-11-02")
    assert get_summary(ledger, "p1")["alert_status"] == "WARNING"

    add_expense(ledger, "p1", "20.01", "software", "Over 100", "2026-11-03")
    assert get_summary(ledger, "p1")["alert_status"] == "OVER_BUDGET"


def test_ac5_archived_project_rejects_expenses(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    create_project(ledger, "p1", "Archive Test", "Client", "500.00")
    archive_project(ledger, "p1")

    with pytest.raises(LedgerError, match="archived"):
        add_expense(ledger, "p1", "25.00", "other", "Late expense", "2026-11-05")


def test_ac6_filter_expenses_by_category(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    create_project(ledger, "p1", "Filter Test", "Client", "500.00")
    add_expense(ledger, "p1", "10.00", "software", "IDE", "2026-11-01")
    add_expense(ledger, "p1", "50.00", "travel", "Train", "2026-11-02")
    add_expense(ledger, "p1", "20.00", "software", "Domain", "2026-11-03")

    software = list_expenses(ledger, "p1", category="software")
    assert len(software) == 2
    assert all(e.category == "software" for e in software)


def test_ac7_corrupted_ledger_raises_without_overwriting(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    corrupted_content = "{not valid json"
    ledger.write_text(corrupted_content, encoding="utf-8")

    with pytest.raises(LedgerCorruptedError):
        get_summary(ledger, "p1")

    assert ledger.read_text(encoding="utf-8") == corrupted_content
