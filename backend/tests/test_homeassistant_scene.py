"""Home Assistant home_scene tool — no live HA required."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend.app.hands.registry import REGISTRY
from backend.plugins.homeassistant import _home_scene


def test_home_scene_registered():
    assert "home_scene" in REGISTRY
    assert REGISTRY["home_scene"]["risk_level"] == "confirm_once"


def test_home_scene_requires_config():
    with patch("backend.plugins.homeassistant._ha_configured", return_value=False):
        with pytest.raises(RuntimeError, match="not configured"):
            _home_scene("scene.movie_night")


def test_home_scene_posts_turn_on():
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    with (
        patch("backend.plugins.homeassistant._ha_configured", return_value=True),
        patch("backend.plugins.homeassistant._ha_url", return_value="http://ha.local:8123"),
        patch("backend.plugins.homeassistant._ha_token", return_value="token"),
        patch("backend.plugins.homeassistant.httpx.post", return_value=mock_resp) as post,
    ):
        result = _home_scene("movie_night")
    assert result["activated"] is True
    assert result["scene_id"] == "scene.movie_night"
    post.assert_called_once()
    args, kwargs = post.call_args
    assert args[0].endswith("/services/scene/turn_on")
    assert kwargs["json"]["entity_id"] == "scene.movie_night"
