"""Piper TTS Plugin Facade.

Implements Zero-Code CLI subprocess wrapper (Pattern 2) and optional HTTP sidecar
fallback (Pattern 3) for Rhasspy Piper TTS.
"""
from __future__ import annotations

from .engine import (
    DEFAULT_MODEL as _DEFAULT_MODEL,
    DEFAULT_OUTPUT as _DEFAULT_OUTPUT,
    resolve_piper_bin as _resolve_piper_bin,
    resolve_model_path as _resolve_model_path,
    synthesize_speech,
)
from .tools import (
    _piper_tts,
    _piper_tts_speak_sync,
    piper_tts_speak,
    register_piper_tools,
)

# Auto-register upon import
register_piper_tools()

__all__ = [
    "_DEFAULT_OUTPUT",
    "_DEFAULT_MODEL",
    "_resolve_piper_bin",
    "_resolve_model_path",
    "_piper_tts",
    "_piper_tts_speak_sync",
    "piper_tts_speak",
    "synthesize_speech",
    "register_piper_tools",
]
