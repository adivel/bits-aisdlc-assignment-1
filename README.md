# BITS AI-Augmented SDLC — Assignment 1

## Overview
This repository contains the implementation, Spec Kit artifacts, evaluation/quality harnesses, and evidence logs for Assignment 1:
- **Part 1A:** Freelance Project Expense & Budget Ledger CLI (`Part-1A/`)
- **Part 1B:** Natural-Language Reminder Agent (`Part-1B/`)

## Environment Setup
```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install ruff bandit pytest jsonschema
```

## Part 1A — Freelance Project Expense & Budget Ledger CLI
- **Spec Kit:** `Part-1A/.specify/{constitution,spec,plan,tasks}.md`
- **Source:** `Part-1A/src/{models,storage,ledger,cli}.py`
- **Tests:** `Part-1A/tests/test_ledger.py` (7 acceptance-criteria tests, AC-1 to AC-7)
- **Run Harness:**
  ```powershell
  .venv\Scripts\python.exe Part-1A\.harness\run_harness.py
  ```
- **Results:** `PASS` — `ruff` (0 errors), `bandit` (0 medium/high issues), `pytest` (7/7 passed). See `Part-1A/evidence/harness-log.md`.

## Part 1B — Natural-Language Reminder Agent
- **Spec Kit:** `Part-1B/.specify/{constitution,spec}.md`
- **Prompt & Agent:** `Part-1B/prompts/system_prompt.txt`, `Part-1B/src/agent.py`
- **Eval Dataset:** `Part-1B/evals/dataset.json` (15 cases)
- **Run Eval Harness:**
  ```powershell
  $env:GEMINI_API_KEY = "<your-api-key>"
  .venv\Scripts\python.exe Part-1B\.harness\run_eval.py
  ```
- **Results:** `PASS` — Model `gemini-2.5-flash-lite`, Avg Score `0.9067` (Threshold `0.8`), L1 Schema Pass Rate `1.0`, Guardrail Failures `0`. See `Part-1B/evidence/harness-log.md`.
