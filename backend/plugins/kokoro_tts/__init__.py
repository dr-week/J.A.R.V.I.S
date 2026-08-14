"""Kokoro TTS Plugin (voice engine tool fallback).

Enables high-quality neural text-to-speech synthesis using local Kokoro
PyPI wrapper (Pattern 1) or local neural HTTP sidecar (Pattern 3) per docs/OSS.md.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import httpx

from backend.app.hands import registry

try:
    from kokoro import KPipeline
    import soundfile as sf
    _HAS_KOKORO = True
except ImportError:
    _HAS_KOKORO = False

_DEFAULT_VOICE = "af_heart"
_DEFAULT_LANG = "a"


async def _kokoro_tts(
    text: str,
    voice: str = _DEFAULT_VOICE,
    speed: float = 1.0,
    lang_code: str = _DEFAULT_LANG,
    output_path: str = "kokoro_output.wav",
    url: str = "",
) -> dict[str, Any]:
    """Synthesize speech using local Kokoro PyPI package or HTTP TTS sidecar."""
    clean_text = (text or "").strip()
    if not clean_text:
        return {"error": "Text to synthesize cannot be empty."}

    # 1. Pattern 1: 3-line PyPI Wrapper if kokoro is installed locally
    if _HAS_KOKORO:
        try:
            pipeline = KPipeline(lang_code=lang_code)
            generator = pipeline(clean_text, voice=voice, speed=speed, split_pattern=r"\n+")
            all_audio = []
            sample_rate = 24000
            for _, _, audio in generator:
                all_audio.append(audio)

            if all_audio:
                import numpy as np
                combined = np.concatenate(all_audio)
                out_file = Path(output_path)
                out_file.parent.mkdir(parents=True, exist_ok=True)
                sf.write(str(out_file), combined, sample_rate)
                return {
                    "status": "synthesized",
                    "engine": "kokoro_pypi",
                    "output_path": str(out_file.resolve()),
                    "voice": voice,
                    "sample_rate": sample_rate,
                }
        except Exception as exc:
            return {"error": f"Kokoro local synthesis failed: {exc}"}

    # 2. Pattern 3: HTTP sidecar REST fallback if URL is configured
    http_url = (
        url
        or os.environ.get("JARVIS_TTS_URL")
        or os.environ.get("KOKORO_TTS_URL", "")
    ).strip()
    if http_url:
        try:
            payload = {
                "input": clean_text,
                "text": clean_text,
                "voice": voice,
                "speed": speed,
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(http_url, json=payload)
                resp.raise_for_status()
                audio_bytes = resp.content

            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_bytes(audio_bytes)
            return {
                "status": "synthesized",
                "engine": "kokoro_http",
                "output_path": str(out_file.resolve()),
                "voice": voice,
                "url": http_url,
            }
        except Exception as exc:
            return {
                "error": f"Kokoro HTTP synthesis failed at {http_url}: {exc}. Ensure Kokoro/Piper server is running.",
            }

    # 3. Graceful notice when dependencies/sidecar are not yet installed
    return {
        "status": "uninitialized",
        "error": (
            "Kokoro TTS is uninitialized: 'kokoro' PyPI package is not installed and "
            "no HTTP TTS server URL is configured. "
            "Run: pip install kokoro soundfile, or configure JARVIS_TTS_URL."
        ),
        "text": clean_text,
        "message": "kokoro library not installed in Python env. Run `pip install kokoro` to enable local neural TTS.",
    }


def _kokoro_tts_speak_sync(text: str, voice: str = _DEFAULT_VOICE, speed: float = 1.0) -> dict[str, Any]:
    """Synchronous bridge for kokoro_tts_speak tool."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # In async contexts, run via coroutine
            return _kokoro_tts(text=text, voice=voice, speed=speed)  # type: ignore[return-value]
        return loop.run_until_complete(_kokoro_tts(text=text, voice=voice, speed=speed))
    except Exception:
        return asyncio.run(_kokoro_tts(text=text, voice=voice, speed=speed))


if "kokoro_tts" not in registry.REGISTRY:
    registry.register(
        {
            "name": "kokoro_tts",
            "description": (
                "Synthesize speech from text using local Kokoro neural TTS model or HTTP sidecar. "
                "Saves WAV audio to output path."
            ),
            "version": "1.0.0",
            "phase": 4,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text string to convert to spoken audio.",
                    },
                    "voice": {
                        "type": "string",
                        "description": "Voice identifier (e.g. 'af_heart', 'af_bella', 'am_adam', 'bf_emma').",
                    },
                    "speed": {
                        "type": "number",
                        "description": "Speech speed multiplier (default 1.0).",
                    },
                    "lang_code": {
                        "type": "string",
                        "description": "Language code: 'a' for American English, 'b' for British English.",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "File path where synthesized audio WAV will be written.",
                    },
                    "url": {
                        "type": "string",
                        "description": "Optional HTTP neural TTS server endpoint URL override.",
                    },
                },
                "required": ["text"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "output_path": {"type": "string"},
                    "error": {"type": "string"},
                },
            },
            "scopes": ["voice:synthesize", "audio:write"],
            "tags": ["voice", "tts", "kokoro", "audio", "speech"],
        },
        _kokoro_tts,
    )

if "kokoro_tts_speak" not in registry.REGISTRY:
    for tool_name in ["kokoro_tts_speak", "kokoro_tts"]:
        registry.register(
            {
                "name": tool_name,
                "description": "Synthesize high-quality neural voice speech using Kokoro local TTS (0 API cost).",
                "version": "1.0.0",
                "phase": 4,
                "risk_level": "auto",
                "executor": "brain",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to convert to speech"},
                        "voice": {"type": "string", "description": "Kokoro voice ID (default 'af_heart')"},
                        "speed": {"type": "number", "description": "Speech rate multiplier"},
                    },
                    "required": ["text"],
                },
                "returns": {"type": "object", "properties": {"status": {"type": "string"}}},
                "scopes": ["voice:write"],
                "tags": ["kokoro", "tts", "voice", "zero-code"],
            },
            _kokoro_tts_speak_sync,
        )
