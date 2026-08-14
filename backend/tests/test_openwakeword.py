"""Unit tests for openWakeWord zero-code PyPI wrapper plugin.

Verifies:
- Tool registration in Hands registry
- Input validation (empty paths, missing files)
- Wake word name normalization and alias resolution
- Live inference execution on synthetic audio WAV files
- Mocked detection above and below confidence threshold
- Graceful uninitialized fallback when dependencies are missing
- End-to-end tool execution via registry.execute()
"""
from __future__ import annotations

import os
import struct
import tempfile
import wave
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from backend.app.hands import registry
from backend.plugins.openwakeword import (
    _normalize_wakewords,
    _wakeword_predict,
)

# Ensure plugins are discovered
registry.discover_plugins()


@pytest.fixture
def temp_wav_file(tmp_path: Path) -> Path:
    """Create a temporary 1-second 16kHz mono 16-bit PCM WAV file."""
    wav_path = tmp_path / "sample_test.wav"
    sample_rate = 16000
    num_samples = sample_rate  # 1 second of silence
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack("<" + "h" * num_samples, *([0] * num_samples)))
    return wav_path


def test_wakeword_tool_registered():
    """Verify wakeword_predict is properly registered in Hands registry."""
    registry.discover_plugins()
    assert "wakeword_predict" in registry.REGISTRY
    tool_def = registry.REGISTRY["wakeword_predict"]
    assert tool_def["phase"] == 4
    assert tool_def["risk_level"] == "auto"
    assert "audio_path" in tool_def["parameters"]["properties"]
    assert "wakeword" in tool_def["tags"]


def test_normalize_wakewords_aliases():
    """Verify wake word alias normalization maps common names to openWakeWord model keys."""
    assert _normalize_wakewords(None) == ["hey_jarvis"]
    assert _normalize_wakewords("") == ["hey_jarvis"]
    assert _normalize_wakewords("jarvis") == ["hey_jarvis"]
    assert _normalize_wakewords("hey jarvis") == ["hey_jarvis"]
    assert _normalize_wakewords(["jarvis", "alexa"]) == ["hey_jarvis", "alexa"]
    assert _normalize_wakewords(["mycroft", "rhasspy", "weather"]) == [
        "hey_mycroft",
        "hey_rhasspy",
        "weather",
    ]
    assert _normalize_wakewords("alexa, timer, jarvis") == ["alexa", "timer", "hey_jarvis"]


def test_wakeword_predict_empty_audio_path():
    """Verify wakeword_predict rejects empty audio path."""
    res = _wakeword_predict(audio_path="")
    assert res["status"] == "error"
    assert res["detected"] is False
    assert "empty" in res["error"].lower()

    res_spaces = _wakeword_predict(audio_path="   ")
    assert res_spaces["status"] == "error"
    assert res_spaces["detected"] is False


def test_wakeword_predict_nonexistent_file():
    """Verify wakeword_predict returns clean error for missing file."""
    fake_path = "non_existent_audio_file_12345.wav"
    res = _wakeword_predict(audio_path=fake_path)
    assert res["status"] == "error"
    assert res["detected"] is False
    assert "not found" in res["error"].lower()


def test_wakeword_predict_with_real_wav(temp_wav_file: Path):
    """Verify live inference runs on a real synthetic WAV file."""
    res = _wakeword_predict(
        audio_path=str(temp_wav_file),
        wakewords=["hey_jarvis"],
        threshold=0.5,
    )
    assert res["status"] in ("not_detected", "detected")
    assert res["engine"] == "openwakeword"
    assert "scores" in res
    assert "hey_jarvis" in res["scores"]
    assert isinstance(res["max_score"], float)
    assert res["audio_path"] == str(temp_wav_file)


def test_wakeword_predict_mocked_detection(temp_wav_file: Path):
    """Verify wakeword_predict handles positive detection above threshold."""
    mock_model = MagicMock()
    mock_model.predict_clip.return_value = [
        {"hey_jarvis": 0.05, "alexa": 0.01},
        {"hey_jarvis": 0.93, "alexa": 0.02},
        {"hey_jarvis": 0.40, "alexa": 0.01},
    ]

    with patch("backend.plugins.openwakeword._get_or_create_model", return_value=mock_model):
        res = _wakeword_predict(
            audio_path=str(temp_wav_file),
            wakewords=["hey_jarvis", "alexa"],
            threshold=0.5,
        )

        assert res["status"] == "detected"
        assert res["detected"] is True
        assert res["wakeword"] == "hey_jarvis"
        assert "hey_jarvis" in res["detected_wakewords"]
        assert res["max_score"] == 0.93
        assert res["scores"]["hey_jarvis"] == 0.93
        assert res["scores"]["alexa"] == 0.02


def test_wakeword_predict_mocked_below_threshold(temp_wav_file: Path):
    """Verify wakeword_predict handles confidence scores below threshold."""
    mock_model = MagicMock()
    mock_model.predict_clip.return_value = [
        {"hey_jarvis": 0.12},
        {"hey_jarvis": 0.35},
        {"hey_jarvis": 0.20},
    ]

    with patch("backend.plugins.openwakeword._get_or_create_model", return_value=mock_model):
        res = _wakeword_predict(
            audio_path=str(temp_wav_file),
            wakewords=["hey_jarvis"],
            threshold=0.6,
        )

        assert res["status"] == "not_detected"
        assert res["detected"] is False
        assert res["wakeword"] is None
        assert res["detected_wakewords"] == []
        assert res["max_score"] == 0.35
        assert res["scores"]["hey_jarvis"] == 0.35


def test_wakeword_predict_uninitialized_fallback(temp_wav_file: Path):
    """Verify graceful fallback response when openwakeword is not installed."""
    with patch("backend.plugins.openwakeword._HAS_OPENWAKEWORD", False):
        res = _wakeword_predict(audio_path=str(temp_wav_file))
        assert res["status"] == "uninitialized"
        assert res["detected"] is False
        assert "pip install openwakeword" in res["error"]


def test_wakeword_predict_exception_handling(temp_wav_file: Path):
    """Verify wakeword_predict handles runtime errors gracefully."""
    mock_model = MagicMock()
    mock_model.predict_clip.side_effect = RuntimeError("ONNX runtime failure")

    with patch("backend.plugins.openwakeword._get_or_create_model", return_value=mock_model):
        res = _wakeword_predict(audio_path=str(temp_wav_file))
        assert res["status"] == "error"
        assert res["detected"] is False
        assert "ONNX runtime failure" in res["error"]


@pytest.mark.asyncio
async def test_wakeword_predict_via_registry_execution(temp_wav_file: Path):
    """Verify end-to-end execution of wakeword_predict via Hands registry."""
    registry.discover_plugins()
    exec_res = await registry.execute(
        "wakeword_predict",
        {
            "audio_path": str(temp_wav_file),
            "wakewords": ["hey_jarvis"],
            "threshold": 0.5,
        },
    )
    assert "result" in exec_res
    result = exec_res["result"]
    assert result["status"] in ("not_detected", "detected")
    assert result["engine"] == "openwakeword"
    assert "hey_jarvis" in result["scores"]
