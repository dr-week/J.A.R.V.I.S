"""Speech-to-Text plugin — faster-whisper local STT wrapper.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import os
from typing import Any
from backend.app.hands import registry

try:
    from faster_whisper import WhisperModel
    _HAS_WHISPER = True
except ImportError:
    _HAS_WHISPER = False

_MODEL_CACHE: dict[str, Any] = {}


def _stt_transcribe(audio_file_path: str, model_size: str = "tiny") -> dict[str, Any]:
    """Transcribe audio file locally using faster-whisper."""
    if not _HAS_WHISPER:
        return {"error": "faster-whisper is not installed. Run: pip install faster-whisper"}
    if not os.path.exists(audio_file_path):
        return {"error": f"Audio file not found: {audio_file_path}"}
    try:
        if model_size not in _MODEL_CACHE:
            _MODEL_CACHE[model_size] = WhisperModel(model_size, device="cpu", compute_type="int8")
        model = _MODEL_CACHE[model_size]
        segments, info = model.transcribe(audio_file_path, beam_size=5)
        text = " ".join([segment.text for segment in segments])
        return {"text": text.strip(), "language": info.language, "probability": info.language_probability}
    except Exception as exc:
        return {"error": str(exc)}


registry.register(
    {
        "name": "stt_transcribe",
        "description": "Transcribe audio file to text locally using faster-whisper.",
        "version": "1.0.0",
        "phase": 4,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "audio_file_path": {"type": "string"},
                "model_size": {"type": "string"},
            },
            "required": ["audio_file_path"],
        },
        "returns": {"type": "object", "properties": {"text": {"type": "string"}}},
        "scopes": ["audio:read"],
        "tags": ["audio", "stt", "speech"],
    },
    _stt_transcribe,
)
