"""Unit tests for Flet Desktop Voice & Wake Word loop integration."""
from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch
import pytest

from clients.windows.ui_gui import mount_jarvis_desktop


def test_flet_mount_registers_wake_word_loop():
    """Verify that mount_jarvis_desktop correctly configures wake word state controls."""
    mock_flet = MagicMock()
    mock_page = MagicMock()
    mock_args = MagicMock()
    mock_args.pair = False
    mock_args.wake_word = "jarvis"

    session_holder = {"session_id": "test-session"}
    token_holder = {"token": "test-token"}
    bridge_slot = {}

    with patch.dict(sys.modules, {"flet": mock_flet}):
        mount_jarvis_desktop(
            mock_page,
            mock_args,
            brain="http://localhost:8787",
            device_id="test-device",
            session_holder=session_holder,
            token_holder=token_holder,
            pair_fn=lambda *a, **k: "token",
            auth_headers_fn=lambda t: {},
            brain_start_hint=lambda b: "hint",
            bridge_slot=bridge_slot,
        )

    # Check that bridge slot registered status handlers for wake word UI updates
    assert "set_wake_status" in bridge_slot
    assert callable(bridge_slot["set_wake_status"])
