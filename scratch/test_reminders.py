"""Offline smoke test for the ISSUE-041 reminders plugin."""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

with tempfile.TemporaryDirectory() as temporary_dir:
    os.environ["JARVIS_DATA_DIR"] = temporary_dir

    from backend.app.soul.memory import init_db, upsert_memory
    from backend.app.hands import registry
    import backend.plugins.reminders  # noqa: F401 -- registers the tools

    init_db()
    upsert_memory("work_priority", "Finish the design review")

    async def main() -> None:
        first = await registry.run_tool("reminder_set", {"title": "Design review", "due_at": "2030-01-02T09:00:00Z"}, explicit_confirm=True)
        second = await registry.run_tool("reminder_set", {"title": "Team sync", "due_at": "2030-01-02T08:00:00Z"}, explicit_confirm=True)
        assert first["result"]["id"] and second["result"]["id"]
        listed = await registry.run_tool("reminder_list", {})
        assert [item["title"] for item in listed["result"]["reminders"]] == ["Team sync", "Design review"]
        plan = await registry.run_tool("plan_today", {"date": "2030-01-02"})
        assert [item["title"] for item in plan["result"]["ordered_plan"]] == ["Team sync", "Design review"]
        assert plan["result"]["context"] == [{"key": "work_priority", "value": "Finish the design review"}]
        cancelled = await registry.run_tool("reminder_cancel", {"reminder_id": first["result"]["id"]}, explicit_confirm=True)
        assert cancelled["result"]["cancelled"] is True
        remaining = await registry.run_tool("reminder_list", {})
        assert remaining["result"]["count"] == 1

    asyncio.run(main())

print("reminders smoke test: OK")
