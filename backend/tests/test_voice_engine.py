"""Tests for voice_engine plugin and neural TTS bridge."""
from __future__ import annotations

import os
import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.hands.registry import REGISTRY
from backend.plugins.voice_engine import _voice_set_engine
from clients.windows.voice import speak, tts_available


def test_voice_set_engine_tool_registered():
    """Verify tool registration in REGISTRY."""
    assert "voice_set_engine" in REGISTRY


def test_voice_set_engine_config():
    """Test switching voice engine settings via tool executor."""
    res = _voice_set_engine(engine="piper", url="http://127.0.0.1:5000/v1/audio/speech", rate=200)

    assert res["ok"] is True
    assert res["engine"] == "piper"
    assert res["url"] == "http://127.0.0.1:5000/v1/audio/speech"
    assert os.environ["JARVIS_TTS_ENGINE"] == "piper"
    assert os.environ["JARVIS_TTS_URL"] == "http://127.0.0.1:5000/v1/audio/speech"


def test_speak_fallback_when_http_unreachable():
    """Test that speak falls back cleanly when HTTP TTS server is unreachable."""
    os.environ["JARVIS_TTS_ENGINE"] = "piper"
    os.environ["JARVIS_TTS_URL"] = "http://127.0.0.1:59999/unreachable_tts"

    # Should attempt HTTP, fail cleanly, and fall back to pyttsx3/console output without crashing
    spoken = speak("Testing voice fallback")
    # Returns True if pyttsx3 is available or False if pyttsx3 is not installed, but must not raise an unhandled exception
    assert isinstance(spoken, bool)
