"""M1 / ISSUE-147 — Phase 2 exit proof (Windows path).

Fake Windows bridge: two windows_open steps + action_log rows.
Run: python scripts/proof_phase2_windows.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.hands.builtin_tools import register_builtin_tools  # noqa: E402
from app.hands.registry import REGISTRY, run_tool  # noqa: E402
from app.soul.memory import init_db, list_action_log  # noqa: E402
from app.sync.manager import manager  # noqa: E402


class FakeWindowsWS:
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.sent: list[dict] = []
        self.loop = asyncio.get_event_loop()
        self.last_tool_execute: dict | None = None

    async def accept(self) -> None:
        return None

    async def send_json(self, message: dict) -> None:
        self.sent.append(message)
        if message.get("type") != "tool_execute":
            return
        self.last_tool_execute = message
        req_id = message["request_id"]
        tool = message.get("tool")
        params = message.get("params") or {}
        if tool == "windows_open":
            result = {
                "status": "ok",
                "request_id": req_id,
                "result": {"opened": params.get("target"), "shell": True},
            }
        else:
            result = {"status": "error", "request_id": req_id, "error": f"unknown {tool}"}
        self.loop.create_task(asyncio.to_thread(manager.resolve, req_id, result))


async def main() -> bool:
    init_db()
    if "windows_open" not in REGISTRY:
        register_builtin_tools()
    assert REGISTRY["windows_open"]["executor"] == "client"

    device_id = "windows-proof-147"
    fake = FakeWindowsWS(device_id)
    await manager.connect(fake, device_id)
    manager.register_device(fake, device_id)

    session = "sess-phase2-m1"
    step1 = await run_tool(
        "windows_open",
        {"target": "notepad"},
        session_id=session,
        device_id=device_id,
        user_text="open notepad",
        explicit_confirm=True,
    )
    step2 = await run_tool(
        "windows_open",
        {"target": "calc"},
        session_id=session,
        device_id=device_id,
        user_text="open calc",
        explicit_confirm=False,  # confirm_once allowlist after step1
    )
    print("step1:", step1)
    print("step2:", step2)
    assert "error" not in step1 and step1.get("result", {}).get("opened") == "notepad"
    assert "error" not in step2 and step2.get("result", {}).get("opened") == "calc"
    assert fake.last_tool_execute and fake.last_tool_execute.get("request_id")

    rows = [r for r in list_action_log(limit=30) if r.get("tool_name") == "windows_open"]
    print("action_log windows_open count:", len(rows))
    assert len(rows) >= 2, "need ≥2 action_log entries for multi-step proof"
    print("ISSUE-147 Phase 2 Windows exit PROVED")
    return True


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(main()) else 1)
