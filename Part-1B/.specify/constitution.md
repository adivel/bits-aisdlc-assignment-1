# Part 1B Constitution — Natural-Language Reminder Agent

## 1. Engineering & AI Safety Principles
- **Language & Runtime:** Python 3.11+, using `google-genai` (or a configurable REST/mock adapter when `GEMINI_API_KEY` is not set) for non-deterministic natural-language parsing.
- **No Secrets:** Never hardcode or commit `GEMINI_API_KEY` or `.env` files. Read API keys strictly from environment variables.
- **Structured Output:** All agent responses must conform to the declared JSON Output Schema Contract.
- **Safety & Guardrails:** Refuse or block unsafe/out-of-scope requests (e.g., prompt injection, system command execution, arbitrary code execution) and request clarification when mandatory reminder information (e.g., task or time) is missing.
- **Independent Evaluation:** Structural (Layer 1) and Property/Invariant (Layer 2) checks are deterministic and must never be replaced by an LLM judge.
