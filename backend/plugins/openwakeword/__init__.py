"""openWakeWord Plugin — Local AI Wake-Word Detection (Zero-Code PyPI Wrapper).

Enables local, private, zero-latency wake-word detection using openWakeWord (Pattern 1)
per docs/OSS.md and docs/GITHUB_INTEGRATIONS.md (Priority #6 OSS repo).
Self-registers tool 'wakeword_predict' into the Hands registry.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from backend.app.hands import registry

try:
    import numpy as np
    import openwakeword
    from openwakeword.model import Model

    _HAS_OPENWAKEWORD = True
except ImportError:
    _HAS_OPENWAKEWORD = False

# Cached model instances by (models_tuple, framework) to avoid reloading overhead
_MODEL_CACHE: dict[tuple[tuple[str, ...], str], Any] = {}

# Common alias mappings for user convenience
_WAKEWORD_ALIASES: dict[str, str] = {
    "jarvis": "hey_jarvis",
    "hey jarvis": "hey_jarvis",
    "hey_jarvis": "hey_jarvis",
    "alexa": "alexa",
    "mycroft": "hey_mycroft",
    "hey mycroft": "hey_mycroft",
    "hey_mycroft": "hey_mycroft",
    "rhasspy": "hey_rhasspy",
    "hey rhasspy": "hey_rhasspy",
    "hey_rhasspy": "hey_rhasspy",
    "timer": "timer",
    "weather": "weather",
}

_DEFAULT_WAKEWORDS = ["hey_jarvis"]


def _normalize_wakewords(wakewords: list[str] | str | None) -> list[str]:
    """Normalize input wake word names to valid openWakeWord model identifiers."""
    if not wakewords:
        return list(_DEFAULT_WAKEWORDS)

    if isinstance(wakewords, str):
        # Support comma-separated string or single name
        items = [item.strip() for item in wakewords.split(",") if item.strip()]
    elif isinstance(wakewords, (list, tuple, set)):
        items = [str(item).strip() for item in wakewords if str(item).strip()]
    else:
        items = list(_DEFAULT_WAKEWORDS)

    normalized: list[str] = []
    for item in items:
        clean = item.lower()
        model_name = _WAKEWORD_ALIASES.get(clean, clean)
        if model_name not in normalized:
            normalized.append(model_name)

    return normalized or list(_DEFAULT_WAKEWORDS)


def _get_or_create_model(models: list[str], framework: str = "onnx") -> Any:
    """Retrieve cached openWakeWord Model instance or initialize a new one."""
    cache_key = (tuple(sorted(models)), framework)
    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]

    model = Model(wakeword_models=models, inference_framework=framework)
    _MODEL_CACHE[cache_key] = model
    return model


def _wakeword_predict(
    audio_path: str = "",
    wakewords: list[str] | str | None = None,
    threshold: float = 0.5,
    inference_framework: str = "onnx",
    audio_data: Any | None = None,
) -> dict[str, Any]:
    """Detect wake-words in an audio file or audio array using openWakeWord."""
    if not _HAS_OPENWAKEWORD:
        return {
            "status": "uninitialized",
            "error": "openWakeWord is not installed. Run: pip install openwakeword",
            "detected": False,
            "predictions": {},
            "scores": {},
            "message": "openWakeWord library not installed in Python environment.",
        }

    # Validate audio path / data
    clean_path = (audio_path or "").strip()
    if not clean_path and audio_data is None:
        return {
            "status": "error",
            "error": "audio_path cannot be empty. Provide path to a WAV audio file or raw audio data.",
            "detected": False,
            "scores": {},
        }

    if clean_path and not os.path.exists(clean_path):
        return {
            "status": "error",
            "error": f"Audio file not found: {clean_path}",
            "detected": False,
            "scores": {},
        }

    # Normalize threshold
    try:
        thresh = float(threshold)
    except (ValueError, TypeError):
        thresh = 0.5
    thresh = max(0.0, min(1.0, thresh))

    # Normalize wakeword list
    normalized_models = _normalize_wakewords(wakewords)

    try:
        model = _get_or_create_model(normalized_models, framework=inference_framework)

        # Predict clip on audio file or numpy array
        clip_target = audio_data if audio_data is not None else clean_path
        predictions = model.predict_clip(clip_target)

        # Aggregate max score per model across all frames
        scores: dict[str, float] = {}
        for mdl in normalized_models:
            scores[mdl] = 0.0

        if isinstance(predictions, list):
            for frame_pred in predictions:
                if isinstance(frame_pred, dict):
                    for mdl, score in frame_pred.items():
                        float_score = float(score)
                        if mdl not in scores or float_score > scores[mdl]:
                            scores[mdl] = float_score
        elif isinstance(predictions, dict):
            for mdl, score in predictions.items():
                scores[mdl] = float(score)

        # Round scores for clean output
        rounded_scores = {k: round(v, 5) for k, v in scores.items()}

        detected_list = [mdl for mdl, score in scores.items() if score >= thresh]
        detected = len(detected_list) > 0
        best_wakeword = max(scores.keys(), key=lambda k: scores[k]) if scores else None
        max_score = round(max(scores.values()), 5) if scores else 0.0

        return {
            "status": "detected" if detected else "not_detected",
            "detected": detected,
            "wakeword": best_wakeword if detected else None,
            "detected_wakewords": detected_list,
            "max_score": max_score,
            "scores": rounded_scores,
            "threshold": thresh,
            "audio_path": clean_path,
            "engine": "openwakeword",
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": f"Wake word prediction failed: {exc}",
            "detected": False,
            "scores": {},
        }


if "wakeword_predict" not in registry.REGISTRY:
    registry.register(
        {
            "name": "wakeword_predict",
            "description": (
                "Detect wake-words (e.g. 'hey jarvis', 'alexa', 'timer', 'weather') in audio files "
                "or clips locally using openWakeWord (0 API cost, private, offline-capable)."
            ),
            "version": "1.0.0",
            "phase": 4,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "audio_path": {
                        "type": "string",
                        "description": "Path to audio file (e.g. 16kHz WAV) to analyze for wake-word activation.",
                    },
                    "wakewords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of wake words to detect (e.g. ['hey_jarvis', 'alexa', 'timer', 'weather']).",
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Activation confidence threshold between 0.0 and 1.0 (default: 0.5).",
                    },
                    "inference_framework": {
                        "type": "string",
                        "description": "Inference framework: 'onnx' (default) or 'tflite'.",
                    },
                },
                "required": ["audio_path"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "detected": {"type": "boolean"},
                    "wakeword": {"type": "string"},
                    "detected_wakewords": {"type": "array"},
                    "max_score": {"type": "number"},
                    "scores": {"type": "object"},
                    "error": {"type": "string"},
                },
            },
            "scopes": ["voice:read", "audio:read"],
            "tags": ["wakeword", "voice", "audio", "openwakeword", "zero-code"],
        },
        _wakeword_predict,
    )
