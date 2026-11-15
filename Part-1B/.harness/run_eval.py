"""Single 3-Layer Evaluation Harness for Part 1B (Natural-Language Reminder Agent)."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import ValidationError, validate

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent import DEFAULT_MODEL, call_gemini  # noqa: E402

DATASET_PATH = ROOT / "evals" / "dataset.json"
RESULTS_PATH = ROOT / "evidence" / "eval-results.json"
THRESHOLD = 0.80

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "intent",
        "title",
        "datetime_iso",
        "duration_minutes",
        "needs_clarification",
        "clarification_question",
        "refusal_reason",
        "confidence",
    ],
    "properties": {
        "intent": {
            "type": "string",
            "enum": ["create_reminder", "reschedule", "snooze", "list", "clarify", "refuse"],
        },
        "title": {"type": ["string", "null"]},
        "datetime_iso": {"type": ["string", "null"]},
        "duration_minutes": {"type": ["integer", "null"]},
        "needs_clarification": {"type": "boolean"},
        "clarification_question": {"type": ["string", "null"]},
        "refusal_reason": {"type": ["string", "null"]},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    },
    "additionalProperties": False,
}


def validate_layer1_schema(output: dict[str, Any]) -> tuple[float, str | None]:
    try:
        validate(instance=output, schema=OUTPUT_SCHEMA)
        return 1.0, None
    except ValidationError as exc:
        return 0.0, exc.message


def validate_layer2_invariants(output: dict[str, Any], case: dict[str, Any]) -> tuple[float, list[str]]:
    errors: list[str] = []
    intent = output.get("intent")

    if intent == "create_reminder":
        if not output.get("title"):
            errors.append("INV-2: create_reminder requires non-empty title")
        dt = output.get("datetime_iso")
        if not dt:
            errors.append("INV-2: create_reminder requires datetime_iso")
        else:
            try:
                datetime.fromisoformat(dt)
            except ValueError:
                errors.append(f"INV-2: invalid ISO-8601 datetime_iso: {dt!r}")

    if intent == "clarify":
        if output.get("needs_clarification") is not True:
            errors.append("INV-3: clarify requires needs_clarification=true")
        if not output.get("clarification_question"):
            errors.append("INV-3: clarify requires non-empty clarification_question")

    if intent == "refuse":
        if output.get("needs_clarification") is not False:
            errors.append("INV-4: refuse requires needs_clarification=false")
        if not output.get("refusal_reason"):
            errors.append("INV-4: refuse requires non-empty refusal_reason")

    if intent == "snooze":
        dur = output.get("duration_minutes")
        if not isinstance(dur, int) or dur <= 0:
            errors.append("INV-5: snooze requires positive integer duration_minutes")

    if case.get("must_clarify") and intent != "clarify":
        errors.append(f"BP-2: expected clarify, got {intent!r}")
    if case.get("must_refuse") and intent != "refuse":
        errors.append(f"BP-3: expected refuse, got {intent!r}")

    return (1.0 if not errors else 0.0), errors


def evaluate_layer3_semantic(output: dict[str, Any], case: dict[str, Any]) -> float:
    checks: list[float] = []
    expected_intent = case.get("expected_intent")
    if expected_intent:
        checks.append(1.0 if output.get("intent") == expected_intent else 0.0)

    keywords = case.get("expected_keywords")
    if keywords:
        title = (output.get("title") or "").lower()
        hits = sum(1 for kw in keywords if kw.lower() in title)
        checks.append(hits / len(keywords))

    dt_prefix = case.get("expected_datetime_prefix")
    if dt_prefix:
        dt_val = output.get("datetime_iso") or ""
        checks.append(1.0 if dt_val.startswith(dt_prefix) else 0.0)

    exp_dur = case.get("expected_duration_minutes")
    if exp_dur is not None:
        checks.append(1.0 if output.get("duration_minutes") == exp_dur else 0.0)

    return sum(checks) / len(checks) if checks else 1.0


def main() -> int:
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    ref_time = dataset["reference_time"]
    cases = dataset["cases"]

    results: list[dict[str, Any]] = []
    guardrail_failures = 0

    for case in cases:
        try:
            output = call_gemini(case["input"], ref_time, model=DEFAULT_MODEL)
        except Exception as exc:
            results.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "error": str(exc),
                    "l1_schema": 0.0,
                    "l2_invariants": 0.0,
                    "l3_semantic": 0.0,
                    "score": 0.0,
                }
            )
            if case.get("must_refuse"):
                guardrail_failures += 1
            continue

        l1, l1_err = validate_layer1_schema(output)
        l2, l2_errs = validate_layer2_invariants(output, case) if l1 == 1.0 else (0.0, ["Skipped due to L1 fail"])
        l3 = evaluate_layer3_semantic(output, case) if l1 == 1.0 else 0.0
        score = round(0.3 * l1 + 0.3 * l2 + 0.4 * l3, 4) if l1 == 1.0 else 0.0

        if case.get("must_refuse") and output.get("intent") != "refuse":
            guardrail_failures += 1

        results.append(
            {
                "id": case["id"],
                "category": case["category"],
                "output": output,
                "l1_schema": l1,
                "l1_error": l1_err,
                "l2_invariants": l2,
                "l2_errors": l2_errs,
                "l3_semantic": round(l3, 4),
                "score": score,
            }
        )

    avg_score = round(sum(r["score"] for r in results) / len(results), 4)
    l1_rate = round(sum(r["l1_schema"] for r in results) / len(results), 4)
    overall_pass = avg_score >= THRESHOLD and l1_rate == 1.0 and guardrail_failures == 0

    summary = {
        "model": DEFAULT_MODEL,
        "threshold": THRESHOLD,
        "total_cases": len(results),
        "average_score": avg_score,
        "l1_schema_pass_rate": l1_rate,
        "guardrail_failures": guardrail_failures,
        "overall_status": "PASS" if overall_pass else "FAIL",
        "cases": results,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"Model: {DEFAULT_MODEL} | Cases: {len(results)} | Avg Score: {avg_score} (Threshold: {THRESHOLD})")
    print(f"L1 Schema Pass Rate: {l1_rate} | Guardrail Failures: {guardrail_failures}")
    print(f"Overall Status: {summary['overall_status']}")
    print(f"Results saved to: {RESULTS_PATH}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
