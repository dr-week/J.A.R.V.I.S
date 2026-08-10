"""Scratch verification for ISSUE-033 (Android device bridge).

Simulates a real Android phone (fake websocket) connected to the brain's
/ws handler and verifies:
  1. Brain registers the device and can route `android_open`.
  2. The client receives `tool_execute`, replies `tool_result` with the
     matching request_id, and the brain returns the result.
  3. The result is written to `action_log`.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.hands.registry import run_tool, REGISTRY  # noqa: E402
from app.sync.manager import manager  # noqa: E402
from app.soul.memory import get_config, set_config  # noqa: E402


class FakeWS:
    """Minimal stand-in for a FastAPI WebSocket so we can test the manager."""

    def __init__(self, device_id: str):
        self.device_id = device_id
        self.sent: list[dict] = []
        self.loop = asyncio.get_event_loop()

    async def accept(self):
        pass

    async def send_json(self, message: dict):
        self.sent.append(message)
        # Auto-reply like a device bridge would: echo request_id + tool_result
        if message.get("type") == "tool_execute":
            req_id = message["request_id"]
            tool = message.get("tool")
            params = message.get("params", {})
            if tool == "android_open":
                result = {
                    "status": "ok",
                    "request_id": req_id,
                    "result": {
                        "opened": params.get("target"),
                        "intent": "ACTION_VIEW",
                    },
                }
            else:
                result = {
                    "status": "error",
                    "request_id": req_id,
                    "error": f"unknown tool {tool}",
                }
            # schedule resolve so the pending future completes
            self.loop.create_task(asyncio.to_thread(self._resolve, req_id, result))
            self.last_tool_execute = message

    def _resolve(self, req_id: str, result: dict):
        manager.resolve(req_id, result)


async def main() -> bool:
    # 1. android_open registered as a client-executor tool
    assert "android_open" in REGISTRY, "android_open not in REGISTRY"
    tool = REGISTRY["android_open"]
    assert tool["executor"] == "client", "android_open must be client-executor"
    assert tool["risk_level"] == "confirm_once"
    assert "target" in tool["parameters"]["required"], "target must be required"

    # 2. Connect a fake Android device and register it
    device_id = "android-fake-1234"
    fake = FakeWS(device_id)
    # connect() accepts the socket; then register binds device -> socket
    await manager.connect(fake, device_id)
    manager.register_device(fake, device_id)
    assert manager._by_device.get(device_id) is fake, "device not bound"

    # 3. Dispatch android_open (explicit confirm = allowlist once)
    result = await run_tool(
        "android_open",
        {"target": "com.google.android.youtube"},
        session_id="sess-033-test",
        device_id=device_id,
        user_text="open youtube",
        explicit_confirm=True,
    )
    print("dispatch result:", result)

    # The fake replied status ok -> we expect an 'ok' result echoing the target
    assert "error" not in result, f"dispatch failed: {result}"
    assert result.get("result", {}).get("opened") == "com.google.android.youtube"

    # Confirm the device actually received the tool_execute with a request_id
    assert fake.last_tool_execute is not None, "device never got tool_execute"
    assert fake.last_tool_execute.get("request_id"), "no request_id in tool_execute"

    # 4. action_log must have a row for android_open
    rows = await _latest_action_log("android_open")
    print("action_log rows:", rows)
    assert rows, "no action_log row for android_open"

    # 5. allowlist set for this device/tool (confirm_once)
    allow_key = f"tool_allowlist:{device_id}:android_open"
    assert get_config(allow_key, "0") == "1", "confirm_once allowlist not set"

    print("\nISSUE-033 brain-side dispatch VERIFIED: register + execute + result + log")
    return True


async def _latest_action_log(tool_name: str):
    from app.soul.memory import list_action_log

    rows = list_action_log(limit=50)
    return [r for r in rows if r.get("tool_name") == tool_name]


if __name__ == "__main__":
    ok = asyncio.run(main())
    sys.exit(0 if ok else 1)

