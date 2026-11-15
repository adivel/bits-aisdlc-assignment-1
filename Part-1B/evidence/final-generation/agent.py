"""Natural-Language Reminder Agent using Gemini API (with offline mock fallback)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import time
from typing import Any
import urllib.error
import urllib.request

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "system_prompt.txt"
DEFAULT_MODEL = "gemini-2.5-flash-lite"


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()
    return json.loads(cleaned)


def call_gemini(user_input: str, reference_time: str, model: str = DEFAULT_MODEL) -> dict[str, Any]:
    """Call Gemini generateContent REST API using GEMINI_API_KEY."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set")

    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"reference_time: {reference_time}\nuser_input: {user_input}"}],
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }

    max_attempts = 5
    for attempt in range(max_attempts):
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:  # nosec B310
                body = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < max_attempts - 1:
                time.sleep(5 * (attempt + 1))
                continue
            raise RuntimeError(f"Gemini API request failed: {exc}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt < max_attempts - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise RuntimeError(f"Gemini API request failed: {exc}") from exc

    text = body["candidates"][0]["content"]["parts"][0]["text"]
    return _extract_json(text)
