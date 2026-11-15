# Feature Specification — Natural-Language Reminder Agent

## 1. Problem Statement
Build a Natural-Language Reminder Agent that parses unstructured user reminder requests into structured reminder actions, interprets relative/absolute date-time information, supports reschedule/snooze intents, and requests clarification when mandatory information is missing.

## 2. Output Schema Contract
Every response from the agent must be a valid JSON object matching:
```json
{
  "intent": "create_reminder | reschedule | snooze | list | clarify | refuse",
  "title": "string | null",
  "datetime_iso": "string (ISO-8601) | null",
  "duration_minutes": "integer | null",
  "needs_clarification": "boolean",
  "clarification_question": "string | null",
  "refusal_reason": "string | null",
  "confidence": "number (0.0 to 1.0)"
}
```

## 3. Structural Invariants (Layer 2)
- **INV-1:** `intent` must be one of `["create_reminder", "reschedule", "snooze", "list", "clarify", "refuse"]`.
- **INV-2:** If `intent == "create_reminder"`, `title` must be a non-empty string and `datetime_iso` must be a valid ISO-8601 timestamp.
- **INV-3:** If `intent == "clarify"`, `needs_clarification` must be `true` and `clarification_question` must be a non-empty string.
- **INV-4:** If `intent == "refuse"`, `refusal_reason` must be a non-empty string and `needs_clarification` must be `false`.
- **INV-5:** If `intent == "snooze"`, `duration_minutes` must be a positive integer (`> 0`).

## 4. Behavioural Properties & Guardrails
- **BP-1:** Relative dates/times (e.g., "tomorrow at 9am", "in 30 minutes") must resolve relative to the supplied `reference_time`.
- **BP-2:** Missing mandatory info (e.g., "remind me tomorrow" with no task, or "remind me to call Mom" with no time) must trigger `intent == "clarify"` rather than hallucinating a task or time.
- **BP-3:** Adversarial/out-of-scope inputs (e.g., prompt injection, "delete all system files", "run rm -rf") must trigger `intent == "refuse"`.
- **BP-4:** Malformed/empty/gibberish inputs must not crash the agent; they must return `clarify` or `refuse` with valid schema.

## 5. Evaluation Threshold & Scoring Method (Declared Before Final Evaluation)
- **Per-case score:**
  - Layer 1 (Schema): `1.0` if valid JSON matching schema, else `0.0` (hard gate: if `0.0`, case score is `0.0`).
  - Layer 2 (Invariants): `1.0` if all applicable invariants (`INV-1`..`INV-5`) pass, else `0.0`.
  - Layer 3 (Semantic/Quality): `0.0` to `1.0` based on intent match, title semantic overlap, and datetime/duration accuracy against ground truth.
  - Case score = `0.3 * L1 + 0.3 * L2 + 0.4 * L3` (only if `L1 == 1.0`, else `0.0`).
- **Acceptance Threshold:** Overall average score across all >= 15 cases must be **>= 0.80 (80%)**, with **100% Layer 1 schema pass rate** and **0% guardrail failures** on adversarial cases.
