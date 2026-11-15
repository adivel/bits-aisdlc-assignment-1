"""Natural-Language Reminder Agent using Gemini API (with offline mock fallback)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
import urllib.error
import urllib.request

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "system_prompt.txt"
DEFAULT_MODEL = "gemini-2.5-flash"


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

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # nosec B310
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Gemini API request failed: {exc}") from exc

    text = body["candidates"][0]["content"]["parts"][0]["text"]
    return _extract_json(text)
