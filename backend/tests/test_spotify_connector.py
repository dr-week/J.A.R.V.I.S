"""Tests for Spotify Connector Plugin.

Validates:
- Tool registration in Hands registry (playback, search, play, pause, next)
- Missing token detection
- Parameter validation
- Mocked HTTP execution for get playback
- Mocked HTTP execution for search
- Mocked HTTP execution for play, pause, next
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch
import pytest

from backend.app.hands import registry
from backend.plugins.spotify import (
    _spotify_get_playback,
    _spotify_next_track,
    _spotify_pause,
    _spotify_play,
    _spotify_search,
)

# Ensure plugins are discovered
registry.discover_plugins()


def test_spotify_tools_registered():
    """Verify all Spotify tools are in registry."""
    registry.discover_plugins()
    assert "spotify_get_playback" in registry.REGISTRY
    assert "spotify_search" in registry.REGISTRY
    assert "spotify_play" in registry.REGISTRY
    assert "spotify_pause" in registry.REGISTRY
    assert "spotify_next_track" in registry.REGISTRY


def test_spotify_missing_token_raises():
    """Verify missing API key raises error."""
    with patch.dict(os.environ, {"JARVIS_SPOTIFY_ACCESS_TOKEN": "", "SPOTIFY_ACCESS_TOKEN": ""}, clear=True):
        with pytest.raises(RuntimeError, match="Spotify is not configured"):
            _spotify_get_playback()


def test_spotify_get_playback_success():
    """Verify current playback response parsing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "has-content"
    mock_resp.json.return_value = {
        "is_playing": True,
        "progress_ms": 120000,
        "device": {"name": "Living Room Echo"},
        "item": {
            "name": "Starboy",
            "artists": [{"name": "The Weeknd"}, {"name": "Daft Punk"}],
            "album": {"name": "Starboy"},
            "uri": "spotify:track:abc",
        },
    }

    with patch.dict(os.environ, {"SPOTIFY_ACCESS_TOKEN": "token_123"}), patch("httpx.get", return_value=mock_resp):
        res = _spotify_get_playback()
        assert res["is_playing"] is True
        assert res["device"] == "Living Room Echo"
        assert res["track"]["name"] == "Starboy"
        assert res["track"]["artists"] == ["The Weeknd", "Daft Punk"]


def test_spotify_search_success():
    """Verify search response parsing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "tracks": {
            "items": [
                {
                    "name": "Blinding Lights",
                    "artists": [{"name": "The Weeknd"}],
                    "album": {"name": "After Hours"},
                    "uri": "spotify:track:xyz",
                }
            ]
        }
    }

    with patch.dict(os.environ, {"SPOTIFY_ACCESS_TOKEN": "token_123"}), patch("httpx.get", return_value=mock_resp):
        res = _spotify_search(query="Blinding Lights", search_type="track")
        assert res["count"] == 1
        assert res["results"][0]["name"] == "Blinding Lights"
        assert res["results"][0]["artists"] == ["The Weeknd"]


def test_spotify_play_pause_next_success():
    """Verify play, pause, next control calls."""
    mock_resp = MagicMock()
    mock_resp.status_code = 204

    with patch.dict(os.environ, {"SPOTIFY_ACCESS_TOKEN": "token_123"}), patch("httpx.put", return_value=mock_resp) as mock_put, patch("httpx.post", return_value=mock_resp) as mock_post:
        r_play = _spotify_play(context_uri="spotify:album:123")
        assert r_play["status"] == "playing"
        mock_put.assert_called_once()

        r_pause = _spotify_pause()
        assert r_pause["status"] == "paused"

        r_next = _spotify_next_track()
        assert r_next["status"] == "skipped_to_next"
        mock_post.assert_called_once()
