"""Tests for browser_use plugin."""
from __future__ import annotations

import pytest

from backend.app.hands.registry import REGISTRY
from backend.plugins.browser_use import _browser_use_action


def test_browser_use_tool_registered():
    """Verify tool registration in REGISTRY."""
    assert "browser_use_action" in REGISTRY


@pytest.mark.asyncio
async def test_browser_use_action_execution():
    """Test running browser_use_action on a target site."""
    res = await _browser_use_action("https://example.com")
    assert res["ok"] is True
    assert "Example Domain" in res.get("page_title", "") or "task" in res
