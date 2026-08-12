"""ISSUE-149 / M3 — Phase 3 life-tools acceptance pack.

Domains (REQUIREMENTS-style samples):
  1. reminder_set / reminder_list — durable productivity
  2. weather_current — non-Google connector (mocked network)
  3. home_scene — house scene activation (mocked HA)
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend.app.hands.registry import REGISTRY
from backend.app.soul.memory import init_db
from backend.plugins.homeassistant import _home_scene
from backend.plugins.reminders import _list_reminders, _set_reminder
from backend.plugins.weather import weather_current


@pytest.fixture(autouse=True)
def _db():
    init_db()


def test_reminder_set_and_list():
    assert "reminder_set" in REGISTRY
    created = _set_reminder("Buy milk", "2026-08-12T09:00:00Z", notes="store")
    assert created["title"] == "Buy milk"
    assert created["id"]
    listed = _list_reminders()
    assert listed["count"] >= 1
    assert any(r["id"] == created["id"] for r in listed["reminders"])


def test_weather_current_happy_path():
    assert "weather_current" in REGISTRY
    fake = {
        "current": {
            "temperature_2m": 21.5,
            "relative_humidity_2m": 55,
            "apparent_temperature": 20.0,
            "weather_code": 0,
            "wind_speed_10m": 3.0,
        }
    }
    with (
        patch("backend.plugins.weather._geocode", return_value=(51.5, -0.12)),
        patch("backend.plugins.weather._fetch", return_value=fake),
    ):
        out = weather_current(city="London")
    assert out["temperature_c"] == 21.5
    assert "clear" in out.get("conditions", out.get("summary", "clear"))


def test_home_scene_happy_path():
    assert "home_scene" in REGISTRY
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    with (
        patch("backend.plugins.homeassistant._ha_configured", return_value=True),
        patch("backend.plugins.homeassistant._ha_url", return_value="http://ha.local:8123"),
        patch("backend.plugins.homeassistant._ha_token", return_value="token"),
        patch("backend.plugins.homeassistant.httpx.post", return_value=mock_resp),
    ):
        result = _home_scene("movie_night")
    assert result["activated"] is True
    assert result["scene_id"] == "scene.movie_night"
