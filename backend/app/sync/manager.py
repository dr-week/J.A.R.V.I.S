"""Sync Manager — WebSocket connections, per-device routing and
request/response tool dispatch.

Upgraded for ISSUE-032 (Windows device bridge): connections are tracked by
`device_id` so the brain can route `client`-executor tools to a specific
device and await a correlated result.
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        # websocket -> device_id ("" if the client has not registered yet)
        self._conns: dict[WebSocket, str] = {}
        # device_id -> websocket (last registered connection per device)
        self._by_device: dict[str, WebSocket] = {}
        # request_id -> asyncio.Future awaiting a tool_result
        self._pending: dict[str, asyncio.Future] = {}

    # ── Connection lifecycle ─────────────────────────────────────────────
    async def connect(self, websocket: WebSocket, device_id: str = "") -> None:
        await websocket.accept()
        self._conns[websocket] = device_id
        if device_id:
            self._by_device[device_id] = websocket

    def disconnect(self, websocket: WebSocket) -> None:
        device_id = self._conns.pop(websocket, None)
        if device_id and self._by_device.get(device_id) is websocket:
            self._by_device.pop(device_id, None)
        # Fail any pending requests targeting this connection
        to_fail = [rid for rid, fut in self._pending.items() if not fut.done()]
        for rid in to_fail:
            fut = self._pending.get(rid)
            if fut and not fut.done():
                fut.set_result({"error": "device disconnected", "request_id": rid})

    def register_device(self, websocket: WebSocket, device_id: str) -> None:
        """(Re)bind a connection to a device_id after handshake."""
        if device_id:
            self._conns[websocket] = device_id
            self._by_device[device_id] = websocket

    def active_device_ids(self) -> list[str]:
        return [d for d in self._by_device if d]

    # ── Broadcast / unicast ──────────────────────────────────────────────
    async def broadcast(self, message: dict[str, Any]) -> None:
        """Send a message to all connected clients."""
        dead: list[WebSocket] = []
        for ws in list(self._conns):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def send_to_device(
        self, device_id: str, message: dict[str, Any]
    ) -> bool:
        """Send a message to the connection registered for device_id."""
        ws = self._by_device.get(device_id)
        if ws is None:
            return False
        try:
            await ws.send_json(message)
            return True
        except Exception:
            self.disconnect(ws)
            return False

    # ── Request / response (tool dispatch) ────────────────────────────────
    async def request(
        self,
        device_id: str,
        message: dict[str, Any],
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """Send a request to a device and await its correlated result.

        The outbound message is tagged with a `request_id`; the client must
        echo it back in a `tool_result` message, which `resolve()` completes.
        Returns the result dict, or an error dict on timeout/disconnect.
        """
        request_id = str(uuid.uuid4())
        payload = {"request_id": request_id, **message}
        loop = asyncio.get_running_loop()
        fut: asyncio.Future = loop.create_future()
        self._pending[request_id] = fut

        sent = await self.send_to_device(device_id, payload)
        if not sent:
            self._pending.pop(request_id, None)
            return {"error": f"device '{device_id}' not connected", "request_id": request_id}

        try:
            return await asyncio.wait_for(fut, timeout=timeout)
        except TimeoutError:
            self._pending.pop(request_id, None)
            return {
                "error": f"device '{device_id}' did not respond",
                "request_id": request_id,
            }

    def resolve(self, request_id: str, result: dict[str, Any]) -> bool:
        """Complete a pending request with the device's result."""
        fut = self._pending.pop(request_id, None)
        if fut is None or fut.done():
            return False
        fut.set_result(result)
        return True

    # ── Push helpers ─────────────────────────────────────────────────────
    async def push_memory_update(self, key: str, value: str) -> None:
        await self.broadcast({"type": "push_memory", "key": key, "value": value})

    async def push_habit_update(self, habit: dict[str, Any]) -> None:
        await self.broadcast({"type": "push_habit", "habit": habit})


# Global singleton
manager = ConnectionManager()
