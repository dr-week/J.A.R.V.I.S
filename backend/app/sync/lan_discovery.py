"""Sync — LocalSend LAN Device Discovery Protocol.

Enables zero-config, peer-to-peer device discovery over local Wi-Fi/LAN using UDP broadcast,
inspired by the open-source LocalSend architecture.
"""
from __future__ import annotations

import asyncio
import json
import logging
import socket
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_LAN_PORT = 9384
DISCOVER_REQ_MAGIC = "JARVIS_DISCOVER_REQ"
DISCOVER_RESP_MAGIC = "JARVIS_DISCOVER_RESP"


def encode_beacon_payload(
    device_id: str,
    service: str = "jarvis_brain",
    port: int = 8000,
    meta: dict[str, Any] | None = None,
) -> bytes:
    """Encode device metadata into a UDP discovery payload."""
    payload = {
        "magic": DISCOVER_RESP_MAGIC,
        "device_id": device_id,
        "service": service,
        "port": port,
        "meta": meta or {},
    }
    return json.dumps(payload).encode("utf-8")


def decode_beacon_payload(data: bytes) -> dict[str, Any] | None:
    """Decode and validate a UDP discovery payload."""
    try:
        raw = json.loads(data.decode("utf-8"))
        if isinstance(raw, dict) and raw.get("magic") == DISCOVER_RESP_MAGIC:
            return raw
    except Exception:
        pass
    return None


class LANBeaconProtocol(asyncio.DatagramProtocol):
    """UDP protocol listener that responds to local network discovery queries."""

    def __init__(self, device_id: str, service: str = "jarvis_brain", port: int = 8000) -> None:
        self.device_id = device_id
        self.service = service
        self.port = port
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport  # type: ignore[assignment]

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        text = data.decode("utf-8", errors="ignore").strip()
        if DISCOVER_REQ_MAGIC in text and self.transport:
            resp = encode_beacon_payload(
                device_id=self.device_id,
                service=self.service,
                port=self.port,
            )
            self.transport.sendto(resp, addr)


async def start_lan_beacon(
    device_id: str = "central_brain",
    service: str = "jarvis_brain",
    port: int = 8000,
    listen_port: int = DEFAULT_LAN_PORT,
) -> tuple[asyncio.DatagramTransport, LANBeaconProtocol]:
    """Start listening for local discovery queries on `listen_port`."""
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: LANBeaconProtocol(device_id=device_id, service=service, port=port),
        local_addr=("0.0.0.0", listen_port),
        family=socket.AF_INET,
    )
    return transport, protocol


async def discover_lan_devices(
    timeout: float = 1.0,
    target_port: int = DEFAULT_LAN_PORT,
) -> list[dict[str, Any]]:
    """Broadcast a discovery query on LAN and collect responding Jarvis nodes."""
    discovered: list[dict[str, Any]] = []

    class ClientProtocol(asyncio.DatagramProtocol):
        def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
            decoded = decode_beacon_payload(data)
            if decoded:
                decoded["ip"] = addr[0]
                discovered.append(decoded)

    loop = asyncio.get_running_loop()
    try:
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: ClientProtocol(),
            local_addr=("0.0.0.0", 0),
            family=socket.AF_INET,
        )

        sock = transport.get_extra_info("socket")
        if sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        req_bytes = DISCOVER_REQ_MAGIC.encode("utf-8")
        transport.sendto(req_bytes, ("<broadcast>", target_port))
        try:
            transport.sendto(req_bytes, ("127.0.0.1", target_port))
        except Exception:
            pass

        await asyncio.sleep(timeout)
        transport.close()
    except Exception as exc:
        logger.warning("LAN discovery broadcast error: %s", exc)

    return discovered
