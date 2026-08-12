"""Voice Engine Plugin (Phase 4 — Neural TTS & Voice Configuration).

Allows Jarvis to dynamically switch between offline pyttsx3 and open-source
neural TTS servers (Piper, GPT-SoVITS, Kokoro).
"""
from __future__ import annotations

import os
from typing import Any

from backend.app.hands import registry


def _voice_set_engine(
    engine: str = "pyttsx3",
    url: str = "",
    rate: int = 180,
) -> dict[str, Any]:
    """Configure active voice TTS engine and endpoint settings."""
    clean_engine = (engine or "pyttsx3").strip().lower()
    clean_url = (url or "").strip()

    if clean_engine not in ("pyttsx3", "piper", "gpt_sovits", "http", "kokoro"):
        return {
            "ok": False,
            "error": f"Unsupported engine '{clean_engine}'. Supported: pyttsx3, piper, gpt_sovits, kokoro, http",
        }

    os.environ["JARVIS_TTS_ENGINE"] = clean_engine
    if clean_url:
        os.environ["JARVIS_TTS_URL"] = clean_url
    os.environ["JARVIS_VOICE_RATE"] = str(rate)

    return {
        "ok": True,
        "engine": clean_engine,
        "url": clean_url or os.environ.get("JARVIS_TTS_URL", ""),
        "rate": rate,
    }


registry.register(
    {
        "name": "voice_set_engine",
        "description": (
            "Configure Jarvis's voice TTS engine. Options: 'pyttsx3' (offline fallback), "
            "'piper', 'gpt_sovits', 'kokoro'. Set URL for neural HTTP endpoint."
        ),
        "version": "1.0.0",
        "phase": 4,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "engine": {
                    "type": "string",
                    "description": "Engine name: 'pyttsx3', 'piper', 'gpt_sovits', 'kokoro'",
                },
                "url": {
                    "type": "string",
                    "description": "HTTP endpoint URL for local neural TTS server (e.g. 'http://127.0.0.1:5000/v1/audio/speech')",
                },
                "rate": {
                    "type": "integer",
                    "description": "Speech rate / speed (default 180)",
                },
            },
            "required": ["engine"],
        },
        "returns": {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "engine": {"type": "string"},
                "url": {"type": "string"},
            },
        },
        "scopes": ["voice:config"],
        "tags": ["voice", "tts", "audio"],
    },
    _voice_set_engine,
)
