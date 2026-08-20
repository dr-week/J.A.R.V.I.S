"""Piper TTS tool registration and handlers."""
from __future__ import annotations

import asyncio
from typing import Any
from backend.app.hands import registry
from .engine import (
    DEFAULT_MODEL,
    DEFAULT_OUTPUT,
    synthesize_speech,
    resolve_model_path,
    resolve_piper_bin,
)


async def _piper_tts(
    text: str,
    model: str = "",
    output_path: str = DEFAULT_OUTPUT,
    speaker: int | None = None,
    length_scale: float = 1.0,
    piper_bin: str = "",
    url: str = "",
) -> dict[str, Any]:
    return await synthesize_speech(
        text=text,
        model=model,
        output_path=output_path,
        speaker=speaker,
        length_scale=length_scale,
        piper_bin=piper_bin,
        url=url,
    )


def _piper_tts_speak_sync(
    text: str,
    model: str = "",
    output_path: str = DEFAULT_OUTPUT,
    speaker: int | None = None,
    length_scale: float = 1.0,
    piper_bin: str = "",
    url: str = "",
) -> dict[str, Any]:
    """Sync execution wrapper for non-async callers."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    synthesize_speech(
                        text=text,
                        model=model,
                        output_path=output_path,
                        speaker=speaker,
                        length_scale=length_scale,
                        piper_bin=piper_bin,
                        url=url,
                    ),
                )
                return future.result()
        else:
            return loop.run_until_complete(
                synthesize_speech(
                    text=text,
                    model=model,
                    output_path=output_path,
                    speaker=speaker,
                    length_scale=length_scale,
                    piper_bin=piper_bin,
                    url=url,
                )
            )
    except Exception:
        return asyncio.run(
            synthesize_speech(
                text=text,
                model=model,
                output_path=output_path,
                speaker=speaker,
                length_scale=length_scale,
                piper_bin=piper_bin,
                url=url,
            )
        )


piper_tts_speak = _piper_tts_speak_sync


def register_piper_tools() -> None:
    """Register piper_tts_speak and piper_tts tools in Hands registry."""
    schema = {
        "name": "piper_tts_speak",
        "description": (
            "Synthesize text into speech audio file using local Rhasspy Piper neural TTS."
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
                    "description": "The text string to synthesize into speech audio.",
                },
                "model": {
                    "type": "string",
                    "description": "Piper ONNX voice model path or name (default: ''en_US-lessac-medium'').",
                },
                "output_path": {
                    "type": "string",
                    "description": "Output audio file path (.wav). Default: ''piper_output.wav''.",
                },
                "speaker": {
                    "type": "integer",
                    "description": "Speaker ID index for multi-speaker voice models.",
                },
                "length_scale": {
                    "type": "number",
                    "description": "Speech speed modifier (default: 1.0, lower=faster, higher=slower).",
                },
            },
            "required": ["text"],
        },
        "returns": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "engine": {"type": "string"},
                "output_path": {"type": "string"},
                "model": {"type": "string"},
                "text_length": {"type": "integer"},
                "error": {"type": "string"},
            },
        },
        "scopes": ["tts:speak", "audio:generate"],
        "tags": ["tts", "voice", "piper", "speech", "zero-code"],
    }

    if "piper_tts_speak" not in registry.REGISTRY:
        registry.register(schema, _piper_tts_speak_sync)

    if "piper_tts" not in registry.REGISTRY:
        schema_alias = dict(schema)
        schema_alias["name"] = "piper_tts"
        registry.register(schema_alias, _piper_tts_speak_sync)
