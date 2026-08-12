"""Tests for LocalSend LAN Discovery Protocol."""
from __future__ import annotations

import asyncio
import pytest

from backend.app.sync.lan_discovery import (
    decode_beacon_payload,
    discover_lan_devices,
    encode_beacon_payload,
    start_lan_beacon,
)


def test_payload_encoding_decoding():
    """Test payload encoding and decoding round-trip."""
    encoded = encode_beacon_payload(
        device_id="test_node_1",
        service="jarvis_windows",
        port=5174,
        meta={"os": "win32"},
    )
    decoded = decode_beacon_payload(encoded)

    assert decoded is not None
    assert decoded["device_id"] == "test_node_1"
    assert decoded["service"] == "jarvis_windows"
    assert decoded["port"] == 5174
    assert decoded["meta"] == {"os": "win32"}


def test_invalid_payload_decoding():
    """Test decoding junk payload returns None gracefully."""
    assert decode_beacon_payload(b"invalid_json") is None
    assert decode_beacon_payload(b'{"key": "value"}') is None


@pytest.mark.asyncio
async def test_lan_beacon_and_discovery_handshake():
    """Test beacon listening and local broadcast discovery handshake."""
    test_listen_port = 9385

    # Start local beacon
    transport, protocol = await start_lan_beacon(
        device_id="brain_node",
        service="jarvis_brain",
        port=8000,
        listen_port=test_listen_port,
    )

    try:
        discovered = await discover_lan_devices(timeout=0.3, target_port=test_listen_port)
        assert len(discovered) >= 1
        found = [d for d in discovered if d["device_id"] == "brain_node"]
        assert len(found) == 1
        assert found[0]["service"] == "jarvis_brain"
        assert found[0]["port"] == 8000
    finally:
        transport.close()
