"""Tests for Slack Communications Connector Plugin.

Validates:
- Tool registration in Hands registry (post message, list channels, history, webhooks)
- Missing token detection
- Parameter validation
- Mocked HTTP execution for chat.postMessage
- Mocked HTTP execution for conversations.list
- Mocked HTTP execution for conversations.history
- Mocked HTTP execution for incoming webhook dispatch
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch
import pytest

from backend.app.hands import registry
from backend.plugins.slack import (
    _slack_get_history,
    _slack_list_channels,
    _slack_post_message,
    _slack_send_webhook,
)

# Ensure plugins are discovered
registry.discover_plugins()


def test_slack_tools_registered():
    """Verify all Slack tools are in registry."""
    registry.discover_plugins()
    assert "slack_post_message" in registry.REGISTRY
    assert "slack_list_channels" in registry.REGISTRY
    assert "slack_get_history" in registry.REGISTRY
    assert "slack_send_webhook" in registry.REGISTRY


def test_slack_missing_token_raises():
    """Verify missing bot token raises error."""
    with patch.dict(os.environ, {"JARVIS_SLACK_BOT_TOKEN": "", "SLACK_BOT_TOKEN": ""}, clear=True):
        with pytest.raises(RuntimeError, match="Slack is not configured"):
            _slack_post_message(channel="#general", text="Hello")


def test_slack_post_message_success():
    """Verify chat.postMessage call and parsing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"ok": True, "ts": "1234567890.123456"}

    with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test"}), patch("httpx.post", return_value=mock_resp) as mock_post:
        res = _slack_post_message(channel="C123", text="Deploy complete")
        assert res["status"] == "sent"
        assert res["channel"] == "C123"
        assert res["ts"] == "1234567890.123456"
        mock_post.assert_called_once()


def test_slack_list_channels_success():
    """Verify conversations.list parsing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "ok": True,
        "channels": [
            {"id": "C1", "name": "general", "is_private": False, "num_members": 12, "topic": {"value": "Company updates"}},
            {"id": "C2", "name": "secret", "is_private": True, "num_members": 3, "topic": {"value": "Internal"}},
        ],
    }

    with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test"}), patch("httpx.get", return_value=mock_resp):
        res = _slack_list_channels()
        assert res["count"] == 2
        assert res["channels"][0]["id"] == "C1"
        assert res["channels"][0]["name"] == "general"
        assert res["channels"][1]["is_private"] is True


def test_slack_get_history_success():
    """Verify conversations.history parsing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "ok": True,
        "messages": [
            {"user": "U1", "text": "Good morning team", "ts": "1000.1"},
            {"user": "U2", "text": "Standup in 5m", "ts": "1000.2"},
        ],
    }

    with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test"}), patch("httpx.get", return_value=mock_resp):
        res = _slack_get_history(channel="C1")
        assert res["count"] == 2
        assert res["messages"][0]["text"] == "Good morning team"


def test_slack_send_webhook_success():
    """Verify incoming webhook dispatch."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200

    webhook_url = "https://hooks.slack.com/services/T00/B00/XXXX"
    with patch("httpx.post", return_value=mock_resp) as mock_post:
        res = _slack_send_webhook(webhook_url=webhook_url, text="CI Pipeline Alert")
        assert res["status"] == "dispatched"
        mock_post.assert_called_once()
