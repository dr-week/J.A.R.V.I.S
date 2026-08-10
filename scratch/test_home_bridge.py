"""Offline verification for ISSUE-061 Home Assistant bridge.

Verifies the plugin registers and the confirm/risk gate applies, in a fully
offline (HA not configured) environment. No real HA calls needed.
"""
import asyncio
import os
import sys
from pathlib import Path

# Make backend/ importable when run from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Force "not configured" so we never hit a real Home Assistant.
os.environ["JARVIS_HA_URL"] = ""
os.environ["JARVIS_HA_TOKEN"] = ""
os.environ["JARVIS_HA_ENTITY"] = "light.living_room"


async def main() -> None:
    from backend.app.hands import registry
    from backend.app.hands.registry import run_tool

    registry.discover_plugins()

    names = [t["name"] for t in registry.list_tools()]
    assert "home_entity_list" in names, "home_entity_list not registered"
    assert "home_entity_set" in names, "home_entity_set not registered"
    print("REGISTERED OK:", [n for n in names if n.startswith("home_")])

    # 1) home_entity_list is read-only risk=auto -> runs, but HA not configured
    #    -> should produce a clear error, not crash.
    r = await run_tool(
        "home_entity_list", {},
        session_id="s", device_id="d", user_text="list entities",
    )
    print("home_entity_list ->", r)
    assert "error" in r, "graceful error expected when HA unconfigured"
    assert r["error"].startswith("Home Assistant not configured")

    # 2) home_entity_set is confirm_once -> without confirmation it should be
    #    blocked and require confirmation.
    r = await run_tool(
        "home_entity_set", {"entity_id": "light.test", "state": "on"},
        session_id="s", device_id="d", user_text="turn on the light",
    )
    print("home_entity_set (no confirm) ->", r)
    assert r.get("requires_confirmation") is True, "confirm_once should block"

    # 3) With explicit confirm it proceeds (still errors because HA is offline,
    #    but the gate passed).
    r = await run_tool(
        "home_entity_set", {"entity_id": "light.test", "state": "on"},
        session_id="s", device_id="d", user_text="turn on",
        explicit_confirm=True,
    )
    print("home_entity_set (confirmed) ->", r)
    print("GATE OK: confirm_once enforced, read-only auto allowed")


if __name__ == "__main__":
    asyncio.run(main())
