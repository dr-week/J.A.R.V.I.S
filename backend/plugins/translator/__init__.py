"""Offline Translator plugin — neural machine translation via argostranslate.

Enables offline neural machine translation using Argos Translate
PyPI wrapper (Pattern 1: 3-line PyPI Wrapper) per docs/OSS.md.
Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

from typing import Any
from backend.app.hands import registry

try:
    import argostranslate.package
    import argostranslate.translate
    _HAS_ARGOS = True
except ImportError:
    argostranslate = None  # type: ignore[assignment]
    _HAS_ARGOS = False


def _translate_text(
    text: str,
    from_code: str = "en",
    to_code: str = "es",
) -> dict[str, Any]:
    """Translate text offline between languages using Argos Translate.

    Follows Pattern 1: 3-line PyPI Wrapper per docs/OSS.md.
    """
    clean_text = (text or "").strip()
    if not clean_text:
        return {"error": "Text to translate cannot be empty."}

    # 1. Pattern 1: 3-line PyPI wrapper if argostranslate is installed
    if _HAS_ARGOS and argostranslate is not None:
        try:
            translated = argostranslate.translate.translate(clean_text, from_code, to_code)
            return {
                "status": "translated",
                "original": clean_text,
                "translated": translated,
                "from_code": from_code,
                "to_code": to_code,
                "from": from_code,
                "to": to_code,
            }
        except Exception as exc:
            return {"error": f"ArgosTranslate translation failed: {exc}"}

    # 2. Graceful uninitialized fallback when argostranslate is not installed
    return {
        "status": "uninitialized",
        "error": "argostranslate is not installed. Run: pip install argostranslate",
        "message": "argostranslate library not installed in Python env. Run `pip install argostranslate` to enable offline neural translation.",
        "original": clean_text,
        "from_code": from_code,
        "to_code": to_code,
    }


if "translate_text" not in registry.REGISTRY:
    registry.register(
        {
            "name": "translate_text",
            "description": "Translate text offline between languages using ArgosTranslate neural engine (Pattern 1: 3-line PyPI wrapper).",
            "version": "1.0.0",
            "phase": 6,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text string to translate.",
                    },
                    "from_code": {
                        "type": "string",
                        "description": "Source ISO language code (e.g. 'en', 'es', 'fr', 'de'). Default: 'en'.",
                    },
                    "to_code": {
                        "type": "string",
                        "description": "Target ISO language code (e.g. 'es', 'en', 'fr', 'de'). Default: 'es'.",
                    },
                },
                "required": ["text"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "original": {"type": "string"},
                    "translated": {"type": "string"},
                    "from_code": {"type": "string"},
                    "to_code": {"type": "string"},
                    "error": {"type": "string"},
                },
            },
            "scopes": ["translation:read"],
            "tags": ["translation", "language", "argos", "zero-code", "offline"],
        },
        _translate_text,
    )
