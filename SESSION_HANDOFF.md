# Session Handoff — BITS AI-Augmented SDLC Assignment 1

## Current Status
- **Environment:** `.venv` created at `D:\BITS\AISDLC\.venv` with `ruff`, `bandit`, `pytest`, `jsonschema` installed.
- **Part 1A (Freelance Project Expense & Budget Ledger CLI):** **COMPLETE & PASSING**
  - Spec Kit artifacts: `Part-1A/.specify/{constitution,spec,plan,tasks}.md`
  - Source: `Part-1A/src/{models,storage,ledger,cli}.py`
  - Tests: `Part-1A/tests/test_ledger.py` (AC-1 to AC-7)
  - Harness: `Part-1A/.harness/run_harness.py` (`ruff` + `bandit` + `pytest` — 7/7 passed)
  - Evidence: `Part-1A/evidence/initial-generation/`, `Part-1A/evidence/final-generation/`, `Part-1A/evidence/harness-results/latest-harness-result.json`, `Part-1A/evidence/harness-log.md`
- **Part 1B (Natural-Language Reminder Agent):** **COMPLETE & PASSING**
  - Spec Kit artifacts: `Part-1B/.specify/{constitution,spec}.md`
  - Prompt & Agent: `Part-1B/prompts/system_prompt.txt`, `Part-1B/src/agent.py` (uses `gemini-2.5-flash-lite` with `429` exponential backoff)
  - Eval Dataset: `Part-1B/evals/dataset.json` (15 cases)
  - 3-Layer Harness: `Part-1B/.harness/run_eval.py` — **PASS** (Avg Score: `0.9067` / Threshold: `0.8`, L1 Schema Pass Rate: `1.0`, Guardrail Failures: `0`)
  - Evidence: `Part-1B/evidence/initial-generation/`, `Part-1B/evidence/final-generation/`, `Part-1B/evidence/eval-results.json`, `Part-1B/evidence/harness-log.md`
- **Root Documentation:** `README.md` created.

## Remaining (For User)
1. Record the 3–4 minute demo video (script provided in chat).
2. Fill out `Assignment Submission-Template for students.docx` with personal details, GitHub repo URL, and demo video link.
3. Push repository to a public GitHub repo and submit the `.docx` to LMS.
