"""Piper TTS Plugin — Lightweight local neural text-to-speech CLI wrapper.

Implements Zero-Code CLI subprocess wrapper (Pattern 2) and optional HTTP sidecar
fallback (Pattern 3) for Rhasspy Piper TTS per docs/OSS.md and docs/GITHUB_INTEGRATIONS.md.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from typing import Any
import httpx

from backend.app.hands import registry

_DEFAULT_OUTPUT = "piper_output.wav"
_DEFAULT_MODEL = "en_US-lessac-medium"


def _resolve_piper_bin(bin_override: str = "") -> str:
    """Resolve path to piper binary executable."""
    if bin_override and bin_override.strip():
        return bin_override.strip()

    env_bin = (
        os.environ.get("PIPER_BIN")
        or os.environ.get("JARVIS_PIPER_BIN")
        or os.environ.get("PIPER_PATH")
        or ""
    ).strip()
    if env_bin:
        return env_bin

    which_piper = shutil.which("piper") or shutil.which("piper-tts") or shutil.which("piper.exe")
    return which_piper or ""


def _resolve_model_path(model_override: str = "") -> str:
    """Resolve Piper ONNX model path or identifier."""
    if model_override and model_override.strip():
        return model_override.strip()

    return (
        os.environ.get("PIPER_MODEL")
        or os.environ.get("JARVIS_PIPER_MODEL")
        or _DEFAULT_MODEL
    ).strip()


async def _piper_tts(
    text: str,
    model: str = "",
    output_path: str = _DEFAULT_OUTPUT,
    speaker: int | None = None,
    length_scale: float = 1.0,
    piper_bin: str = "",
    url: str = "",
) -> dict[str, Any]:
    """Synthesize speech using local Piper CLI subprocess or HTTP TTS sidecar."""
    clean_text = (text or "").strip()
    if not clean_text:
        return {"error": "Text to synthesize cannot be empty."}

    out_file = Path(output_path)

    # 1. Pattern 2: CLI Subprocess execution if piper binary is available
    resolved_bin = _resolve_piper_bin(piper_bin)
    resolved_model = _resolve_model_path(model)

    if resolved_bin:
        try:
            out_file.parent.mkdir(parents=True, exist_ok=True)
            cmd = [
                resolved_bin,
                "--model",
                resolved_model,
                "--output_file",
                str(out_file),
            ]
            if speaker is not None:
                cmd.extend(["--speaker", str(speaker)])
            if length_scale != 1.0:
                cmd.extend(["--length_scale", str(length_scale)])

            res = subprocess.run(
                cmd,
                input=clean_text,
                text=True,
                capture_output=True,
                check=True,
            )

            return {
                "status": "synthesized",
                "engine": "piper_cli",
                "output_path": str(out_file.resolve()),
                "model": resolved_model,
                "text_length": len(clean_text),
                "speaker": speaker,
                "length_scale": length_scale,
            }
        except subprocess.CalledProcessError as exc:
            stderr_msg = (exc.stderr or "").strip()
            return {
                "error": f"Piper CLI execution failed with return code {exc.returncode}: {stderr_msg or exc}",
                "engine": "piper_cli",
            }
        except Exception as exc:
            return {
                "error": f"Piper CLI execution failed: {exc}. Ensure Piper is installed correctly.",
                "engine": "piper_cli",
            }

    # 2. Pattern 3: HTTP sidecar REST fallback if URL is configured
    http_url = (
        url
        or os.environ.get("JARVIS_TTS_URL")
        or os.environ.get("PIPER_TTS_URL", "")
    ).strip()
    if http_url:
        try:
            payload: dict[str, Any] = {
                "text": clean_text,
                "input": clean_text,
                "model": resolved_model,
                "length_scale": length_scale,
            }
            if speaker is not None:
                payload["speaker"] = speaker

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(http_url, json=payload)
                resp.raise_for_status()
                audio_bytes = resp.content

            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_bytes(audio_bytes)
            return {
                "status": "synthesized",
                "engine": "piper_http",
                "output_path": str(out_file.resolve()),
                "model": resolved_model,
                "url": http_url,
            }
        except Exception as exc:
            return {
                "error": f"Piper HTTP synthesis failed at {http_url}: {exc}. Ensure Piper TTS server is running.",
            }

    # 3. Graceful fallback when neither binary nor HTTP endpoint is available
    return {
        "status": "uninitialized",
        "error": (
            "Piper TTS is uninitialized: 'piper' CLI executable was not found on PATH "
            "and no HTTP TTS server URL is configured. "
            "Install Piper CLI (https://github.com/rhasspy/piper) or configure PIPER_BIN / JARVIS_TTS_URL."
        ),
        "text": clean_text,
        "message": "piper executable not found. Install Piper via CLI or package manager to enable lightweight local TTS.",
    }


def _piper_tts_speak_sync(
    text: str,
    model: str = "",
    output_path: str = _DEFAULT_OUTPUT,
    speaker: int | None = None,
    length_scale: float = 1.0,
    piper_bin: str = "",
    url: str = "",
) -> dict[str, Any]:
    """Synchronous execution wrapper for piper_tts_speak."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return _piper_tts(  # type: ignore[return-value]
                text=text,
                model=model,
                output_path=output_path,
                speaker=speaker,
                length_scale=length_scale,
                piper_bin=piper_bin,
                url=url,
            )
        return loop.run_until_complete(
            _piper_tts(
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
            _piper_tts(
                text=text,
                model=model,
                output_path=output_path,
                speaker=speaker,
                length_scale=length_scale,
                piper_bin=piper_bin,
                url=url,
            )
        )


if "piper_tts_speak" not in registry.REGISTRY:
    registry.register(
        {
            "name": "piper_tts_speak",
            "description": (
                "Synthesize speech from text using local Piper neural TTS CLI subprocess or HTTP sidecar. "
                "Generates high-performance local speech audio with zero cloud API cost."
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
                    "model": {
                        "type": "string",
                        "description": "Path to Piper ONNX voice model file or model identifier (e.g. 'en_US-lessac-medium.onnx').",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Destination file path for synthesized WAV audio (default 'piper_output.wav').",
                    },
                    "speaker": {
                        "type": "integer",
                        "description": "Speaker index ID for multi-speaker voice models.",
                    },
                    "length_scale": {
                        "type": "number",
                        "description": "Phoneme length scale multiplier (speech rate/speed, default 1.0).",
                    },
                    "piper_bin": {
                        "type": "string",
                        "description": "Optional path to piper executable binary override.",
                    },
                    "url": {
                        "type": "string",
                        "description": "Optional HTTP TTS server endpoint URL override.",
                    },
                },
                "required": ["text"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "output_path": {"type": "string"},
                    "engine": {"type": "string"},
                    "error": {"type": "string"},
                },
            },
            "scopes": ["voice:synthesize", "audio:write"],
            "tags": ["voice", "tts", "piper", "speech", "zero-code"],
        },
        _piper_tts,
    )

if "piper_tts" not in registry.REGISTRY:
    registry.register(
        {
            "name": "piper_tts",
            "description": "Synthesize speech using local Piper TTS CLI subprocess (zero-code wrapper).",
            "version": "1.0.0",
            "phase": 4,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to synthesize into speech"},
                    "model": {"type": "string", "description": "Piper ONNX model path or identifier"},
                    "output_path": {"type": "string", "description": "Output WAV file path"},
                    "speaker": {"type": "integer", "description": "Speaker ID"},
                    "length_scale": {"type": "number", "description": "Length scale / speed factor"},
                    "piper_bin": {"type": "string", "description": "Piper executable binary override"},
                    "url": {"type": "string", "description": "HTTP endpoint URL override"},
                },
                "required": ["text"],
            },
            "returns": {"type": "object", "properties": {"status": {"type": "string"}}},
            "scopes": ["voice:synthesize", "audio:write"],
            "tags": ["voice", "tts", "piper", "speech", "zero-code"],
        },
        _piper_tts,
    )
