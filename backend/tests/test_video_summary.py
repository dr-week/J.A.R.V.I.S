"""Unit tests for video_summary plugin (yt-dlp CLI subprocess wrapper)."""
from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock

import pytest

from backend.app.hands import registry
from backend.plugins.video_summary import _video_summarize

# Ensure plugins are discovered
registry.discover_plugins()


def test_video_summarize_tool_registered():
    """Verify tool registration in hands registry."""
    assert "video_summarize" in registry.REGISTRY
    tool_def = registry.REGISTRY["video_summarize"]
    assert tool_def["name"] == "video_summarize"
    assert tool_def["risk_level"] == "auto"
    assert "url" in tool_def["parameters"]["properties"]
    assert "video:read" in tool_def["scopes"]


def test_video_summarize_success(monkeypatch: pytest.MonkeyPatch):
    """Test successful video metadata extraction with mocked yt-dlp CLI output."""
    mock_payload = {
        "title": "Jarvis AI Architecture Overview",
        "description": "A comprehensive deep dive into autonomous personal AI agents.",
        "uploader": "Jarvis Project",
        "duration": 420,
    }

    mock_run = MagicMock(
        return_value=subprocess.CompletedProcess(
            args=["yt-dlp", "--dump-json", "--skip-download", "https://youtube.com/watch?v=test1234"],
            returncode=0,
            stdout=json.dumps(mock_payload),
            stderr="",
        )
    )
    monkeypatch.setattr(subprocess, "run", mock_run)

    url = "https://youtube.com/watch?v=test1234"
    res = _video_summarize(url=url)

    assert "error" not in res
    assert res["title"] == "Jarvis AI Architecture Overview"
    assert "comprehensive deep dive" in res["description"]
    assert res["uploader"] == "Jarvis Project"
    assert res["duration"] == 420
    assert res["url"] == url
    mock_run.assert_called_once()


def test_video_summarize_missing_url():
    """Test calling video_summarize with empty URL returns error."""
    res = _video_summarize(url="")
    assert "error" in res
    assert "Missing required" in res["error"]


def test_video_summarize_cli_error(monkeypatch: pytest.MonkeyPatch):
    """Test graceful handling when yt-dlp fails or is missing."""
    def mock_fail(*args, **kwargs):
        raise FileNotFoundError("No such file or directory: 'yt-dlp'")

    monkeypatch.setattr(subprocess, "run", mock_fail)

    res = _video_summarize(url="https://youtube.com/watch?v=invalid")
    assert "error" in res
    assert "yt-dlp execution failed" in res["error"]


@pytest.mark.asyncio
async def test_video_summarize_registry_execution(monkeypatch: pytest.MonkeyPatch):
    """Test executing video_summarize via registry.execute."""
    mock_payload = {
        "title": "Automated Agent Demo",
        "description": "Short description.",
        "uploader": "Test Channel",
        "duration": 60,
    }

    mock_run = MagicMock(
        return_value=subprocess.CompletedProcess(
            args=["yt-dlp", "--dump-json", "--skip-download", "https://youtube.com/watch?v=demo"],
            returncode=0,
            stdout=json.dumps(mock_payload),
            stderr="",
        )
    )
    monkeypatch.setattr(subprocess, "run", mock_run)

    exec_res = await registry.execute("video_summarize", {"url": "https://youtube.com/watch?v=demo"})
    assert "result" in exec_res
    result = exec_res["result"]
    assert result["title"] == "Automated Agent Demo"
    assert result["uploader"] == "Test Channel"
    assert result["duration"] == 60
