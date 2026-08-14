"""Tests for Piper TTS local zero-code CLI wrapper plugin.

Verifies tool registration in Hands registry, parameter validation,
uninitialized fallback, mocked CLI subprocess execution, and HTTP sidecar fallback.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from backend.app.hands import registry

# Ensure all plugins are discovered
registry.discover_plugins()


def test_piper_tts_tools_registered():
    """Verify piper_tts_speak and piper_tts tools are registered in the Hands registry."""
    tool_names = list(registry.REGISTRY.keys())
    assert "piper_tts_speak" in tool_names
    assert "piper_tts" in tool_names

    tool_def = registry.REGISTRY["piper_tts_speak"]
    assert tool_def["executor"] == "brain"
    assert tool_def["phase"] == 4
    assert "text" in tool_def["parameters"]["properties"]


@pytest.mark.asyncio
async def test_piper_tts_empty_text():
    """Verify piper_tts_speak rejects empty or whitespace-only text."""
    res = await registry.execute("piper_tts_speak", {"text": "   "})
    assert "result" in res or "error" in res
    output = res.get("result", res)
    assert "error" in output
    assert "cannot be empty" in output["error"]


@pytest.mark.asyncio
async def test_piper_tts_uninitialized_fallback():
    """Verify piper_tts returns clean guidance when piper binary is absent and no HTTP URL is set."""
    old_tts_url = os.environ.pop("JARVIS_TTS_URL", None)
    old_piper_url = os.environ.pop("PIPER_TTS_URL", None)
    old_piper_bin = os.environ.pop("PIPER_BIN", None)
    old_jarvis_bin = os.environ.pop("JARVIS_PIPER_BIN", None)

    try:
        with patch("shutil.which", return_value=None):
            res = await registry.execute("piper_tts_speak", {"text": "Good morning, Sir."})
            assert "result" in res
            result = res["result"]
            assert result.get("status") == "uninitialized" or "error" in result
            assert "Piper TTS is uninitialized" in result.get("error", "") or "not found" in result.get("message", "")
    finally:
        if old_tts_url is not None:
            os.environ["JARVIS_TTS_URL"] = old_tts_url
        if old_piper_url is not None:
            os.environ["PIPER_TTS_URL"] = old_piper_url
        if old_piper_bin is not None:
            os.environ["PIPER_BIN"] = old_piper_bin
        if old_jarvis_bin is not None:
            os.environ["JARVIS_PIPER_BIN"] = old_jarvis_bin


@pytest.mark.asyncio
async def test_piper_tts_mocked_cli_success(tmp_path: Path):
    """Verify piper_tts executes CLI subprocess with expected arguments and generates output."""
    out_file = tmp_path / "piper_test.wav"

    mock_run_result = MagicMock()
    mock_run_result.returncode = 0
    mock_run_result.stdout = ""
    mock_run_result.stderr = ""

    with patch("shutil.which", return_value="piper"), \
         patch("subprocess.run", return_value=mock_run_result) as mock_subproc:

        res = await registry.execute(
            "piper_tts_speak",
            {
                "text": "All systems operational.",
                "model": "en_US-lessac-high",
                "output_path": str(out_file),
                "speaker": 2,
                "length_scale": 0.85,
            },
        )

        assert "result" in res
        result = res["result"]
        assert result["status"] == "synthesized"
        assert result["engine"] == "piper_cli"
        assert result["model"] == "en_US-lessac-high"
        assert result["speaker"] == 2
        assert result["length_scale"] == 0.85

        mock_subproc.assert_called_once()
        cmd_args = mock_subproc.call_args[0][0]
        assert cmd_args[0] == "piper"
        assert "--model" in cmd_args
        assert "en_US-lessac-high" in cmd_args
        assert "--output_file" in cmd_args
        assert str(out_file) in cmd_args
        assert "--speaker" in cmd_args
        assert "2" in cmd_args
        assert "--length_scale" in cmd_args
        assert "0.85" in cmd_args
        assert mock_subproc.call_args[1]["input"] == "All systems operational."


@pytest.mark.asyncio
async def test_piper_tts_mocked_cli_error():
    """Verify piper_tts handles subprocess errors gracefully without crashing."""
    mock_error = subprocess.CalledProcessError(
        returncode=1,
        cmd=["piper"],
        stderr="Error: model file does not exist",
    )

    with patch("shutil.which", return_value="piper"), \
         patch("subprocess.run", side_effect=mock_error):

        res = await registry.execute(
            "piper_tts_speak",
            {
                "text": "Diagnostics complete.",
                "model": "nonexistent_model.onnx",
            },
        )

        assert "result" in res
        result = res["result"]
        assert "error" in result
        assert "Piper CLI execution failed with return code 1" in result["error"]
        assert "model file does not exist" in result["error"]


@pytest.mark.asyncio
async def test_piper_tts_mocked_http_sidecar(tmp_path: Path):
    """Verify piper_tts falls back to HTTP TTS endpoint when configured."""
    mock_audio_bytes = b"RIFFpiperaudio12345678"
    out_file = tmp_path / "test_piper_http.wav"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.content = mock_audio_bytes

    with patch("shutil.which", return_value=None), \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        res = await registry.execute(
            "piper_tts_speak",
            {
                "text": "Switching to auxiliary power.",
                "output_path": str(out_file),
                "url": "http://127.0.0.1:5000/v1/audio/speech",
            },
        )

        assert "result" in res
        result = res["result"]
        assert result["status"] == "synthesized"
        assert result["engine"] == "piper_http"
        assert result["url"] == "http://127.0.0.1:5000/v1/audio/speech"
        assert out_file.exists()
        assert out_file.read_bytes() == mock_audio_bytes


def test_piper_tts_speak_sync_wrapper(tmp_path: Path):
    """Verify synchronous wrapper handles invocation directly."""
    from backend.plugins.piper_tts import _piper_tts_speak_sync

    out_file = tmp_path / "sync_test.wav"
    mock_run_result = MagicMock(returncode=0, stdout="", stderr="")

    with patch("shutil.which", return_value="piper"), \
         patch("subprocess.run", return_value=mock_run_result):
        res = _piper_tts_speak_sync(text="Sync test", output_path=str(out_file), piper_bin="piper")
        assert res["status"] == "synthesized"
        assert res["engine"] == "piper_cli"


def test_voice_engine_supports_piper():
    """Verify voice_engine plugin config accepts piper as an active engine."""
    from backend.plugins.voice_engine import _voice_set_engine

    res = _voice_set_engine(engine="piper", url="http://127.0.0.1:5000/v1/audio/speech", rate=190)
    assert res["ok"] is True
    assert res["engine"] == "piper"
    assert os.environ["JARVIS_TTS_ENGINE"] == "piper"
    assert os.environ["JARVIS_TTS_URL"] == "http://127.0.0.1:5000/v1/audio/speech"
    assert os.environ["JARVIS_VOICE_RATE"] == "190"
