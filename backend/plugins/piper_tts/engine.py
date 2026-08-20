"""Piper TTS synthesis engine — executes speech synthesis via local CLI or HTTP sidecar."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any
import httpx

DEFAULT_OUTPUT = "piper_output.wav"
DEFAULT_MODEL = "en_US-lessac-medium"


def resolve_piper_bin(bin_override: str = "") -> str:
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


def resolve_model_path(model_override: str = "") -> str:
    """Resolve Piper ONNX model path or identifier."""
    if model_override and model_override.strip():
        return model_override.strip()

    return (
        os.environ.get("PIPER_MODEL")
        or os.environ.get("JARVIS_PIPER_MODEL")
        or DEFAULT_MODEL
    ).strip()


async def synthesize_speech(
    text: str,
    model: str = "",
    output_path: str = DEFAULT_OUTPUT,
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
    resolved_bin = resolve_piper_bin(piper_bin)
    resolved_model = resolve_model_path(model)

    # 1. Pattern 2: CLI Subprocess execution if piper binary is available
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

            subprocess.run(
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

    # 3. Uninitialized fallback notice matching test expectations
    return {
        "status": "uninitialized",
        "engine": "none",
        "error": "Piper TTS is uninitialized: Neither local Piper binary nor PIPER_TTS_URL is available.",
        "fallback_hint": "Install Piper via ''pip install piper-tts'' or start sidecar at http://localhost:5000.",
    }
