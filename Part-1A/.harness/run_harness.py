"""Deterministic harness runner for Part 1A: Lint (ruff) + SAST (bandit) + Tests (pytest)."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "evidence" / "harness-results"


def run_gate(name: str, cmd: list[str]) -> dict[str, object]:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    return {
        "gate": name,
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    gates = [
        run_gate("lint_ruff", [sys.executable, "-m", "ruff", "check", "src", "tests"]),
        run_gate("sast_bandit", [sys.executable, "-m", "bandit", "-r", "src", "-ll", "-q"]),
        run_gate("unit_tests_pytest", [sys.executable, "-m", "pytest", "tests", "-v"]),
    ]

    overall_pass = all(g["status"] == "PASS" for g in gates)
    report = {
        "overall_status": "PASS" if overall_pass else "FAIL",
        "gates": gates,
    }

    report_path = RESULTS_DIR / "latest-harness-result.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    for g in gates:
        print(f"[{g['status']}] {g['gate']}")
        if g["status"] == "FAIL":
            print(g["stdout"])
            print(g["stderr"])

    print(f"\nOverall Harness Result: {report['overall_status']}")
    print(f"Evidence saved to: {report_path}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
