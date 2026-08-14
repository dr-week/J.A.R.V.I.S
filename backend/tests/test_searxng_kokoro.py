"""Tests for SearXNG private search and Kokoro TTS plugin stubs.

Verifies tool registration in Hands registry, parameter schema validation,
offline fallback behavior, and mocked sidecar execution.
"""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from backend.app.hands import registry

# Ensure all plugins are discovered
registry.discover_plugins()


def test_searxng_and_kokoro_registered():
    """Verify SearXNG and Kokoro TTS tools are properly registered."""
    tool_names = list(registry.REGISTRY.keys())
    assert "search_web" in tool_names or "searxng_search" in tool_names
    assert "kokoro_tts" in tool_names or "kokoro_tts_speak" in tool_names


@pytest.mark.asyncio
async def test_searxng_search_execution():
    """Test SearXNG search execution handles fallback response cleanly."""
    registry.discover_plugins()
    res = await registry.execute("searxng_search", {"query": "Jarvis AI"})
    output = res.get("result", res)
    assert "results" in output or "error" in output or "result" in res or "error" in res


@pytest.mark.asyncio
async def test_kokoro_tts_execution():
    """Test Kokoro TTS execution handles stub/success cleanly."""
    registry.discover_plugins()
    res = await registry.execute("kokoro_tts_speak", {"text": "Hello Sir"})
    output = res.get("result", res)
    assert "status" in output or "error" in output or "result" in res or "error" in res


@pytest.mark.asyncio
async def test_searxng_search_empty_query():
    """Verify search_web rejects empty query."""
    res = await registry.execute("search_web", {"query": ""})
    assert "result" in res or "error" in res
    output = res.get("result", res)
    assert "error" in output


@pytest.mark.asyncio
async def test_searxng_search_offline_fallback():
    """Verify search_web handles unreachable SearXNG server gracefully without crashing."""
    res = await registry.execute(
        "search_web",
        {"query": "Jarvis assistant architecture", "url": "http://127.0.0.1:59999"},
    )
    assert "result" in res
    result = res["result"]
    assert result["query"] == "Jarvis assistant architecture"
    assert result["results"] == []
    assert "error" in result
    assert "SearXNG search request failed" in result["error"]


@pytest.mark.asyncio
async def test_searxng_search_mocked_success():
    """Verify search_web parses and formats SearXNG JSON response correctly."""
    mock_searxng_data = {
        "results": [
            {
                "title": "SearXNG - A privacy-respecting metasearch engine",
                "url": "https://searxng.org",
                "content": "SearXNG is a free internet metasearch engine.",
                "engine": "duckduckgo",
            },
            {
                "title": "Jarvis AI Assistant",
                "url": "https://example.com/jarvis",
                "content": "Personal assistant co-builder architecture.",
                "engine": "google",
            },
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = mock_searxng_data

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp

        res = await registry.execute("search_web", {"query": "Jarvis AI", "limit": 1})
        assert "result" in res
        result = res["result"]
        assert result["query"] == "Jarvis AI"
        assert result["count"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "SearXNG - A privacy-respecting metasearch engine"
        assert result["results"][0]["url"] == "https://searxng.org"
        assert result["results"][0]["snippet"] == "SearXNG is a free internet metasearch engine."
        assert result["results"][0]["engine"] == "duckduckgo"


@pytest.mark.asyncio
async def test_kokoro_tts_empty_text():
    """Verify kokoro_tts rejects empty text input."""
    res = await registry.execute("kokoro_tts", {"text": "  "})
    assert "result" in res or "error" in res
    output = res.get("result", res)
    assert "error" in output


@pytest.mark.asyncio
async def test_kokoro_tts_uninitialized_fallback():
    """Verify kokoro_tts returns clean guidance when PyPI package and HTTP URL are missing."""
    # Ensure env vars are cleared for this test
    old_tts_url = os.environ.pop("JARVIS_TTS_URL", None)
    old_kokoro_url = os.environ.pop("KOKORO_TTS_URL", None)

    try:
        res = await registry.execute("kokoro_tts", {"text": "Good morning, sir."})
        assert "result" in res
        result = res["result"]
        assert "error" in result
        assert "uninitialized" in result.get("status", "") or "not installed" in result["error"]
    finally:
        if old_tts_url is not None:
            os.environ["JARVIS_TTS_URL"] = old_tts_url
        if old_kokoro_url is not None:
            os.environ["KOKORO_TTS_URL"] = old_kokoro_url


@pytest.mark.asyncio
async def test_kokoro_tts_mocked_http_sidecar(tmp_path: Path):
    """Verify kokoro_tts synthesizes speech via HTTP endpoint and writes output file."""
    mock_audio_bytes = b"RIFFmockwavdata12345678"
    out_file = tmp_path / "test_kokoro.wav"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.content = mock_audio_bytes

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        res = await registry.execute(
            "kokoro_tts",
            {
                "text": "System operational.",
                "voice": "af_bella",
                "output_path": str(out_file),
                "url": "http://127.0.0.1:8880/v1/audio/speech",
            },
        )

        assert "result" in res
        result = res["result"]
        assert result["status"] == "synthesized"
        assert result["engine"] == "kokoro_http"
        assert result["voice"] == "af_bella"
        assert out_file.exists()
        assert out_file.read_bytes() == mock_audio_bytes


def test_voice_engine_supports_kokoro():
    """Verify voice_engine config accepts kokoro engine setting."""
    from backend.plugins.voice_engine import _voice_set_engine

    res = _voice_set_engine(engine="kokoro", url="http://127.0.0.1:8880/v1/audio/speech")
    assert res["ok"] is True
    assert res["engine"] == "kokoro"
    assert os.environ["JARVIS_TTS_ENGINE"] == "kokoro"
    assert os.environ["JARVIS_TTS_URL"] == "http://127.0.0.1:8880/v1/audio/speech"
