"""Offline Translator plugin — neural machine translation via argostranslate.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

from typing import Any
from backend.app.hands import registry

try:
    import argostranslate.translate
    _HAS_ARGOS = True
except ImportError:
    _HAS_ARGOS = False


def _translate_text(text: str, from_code: str = "en", to_code: str = "es") -> dict[str, Any]:
    """Translate text offline between languages."""
    if not _HAS_ARGOS:
        return {"error": "argostranslate is not installed. Run: pip install argostranslate"}
    try:
        translated = argostranslate.translate.translate(text, from_code, to_code)
        return {"original": text, "translated": translated, "from": from_code, "to": to_code}
    except Exception as exc:
        return {"error": str(exc)}


registry.register(
    {
        "name": "translate_text",
        "description": "Translate text offline between languages using ArgosTranslate engine.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "from_code": {"type": "string"},
                "to_code": {"type": "string"},
            },
            "required": ["text"],
        },
        "returns": {"type": "object", "properties": {"translated": {"type": "string"}}},
        "scopes": ["translation:read"],
        "tags": ["translation", "language"],
    },
    _translate_text,
)
