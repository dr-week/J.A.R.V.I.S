"""Phase 1 Soul exit proofs — memory recall + proactive habits in prompt."""
from __future__ import annotations

from datetime import UTC, datetime

from backend.app.soul.learner import get_proactive_context
from backend.app.soul.memory import delete_memory, upsert_habit, upsert_memory
from backend.app.soul.persona import build_system_prompt


def test_memory_upsert_appears_in_system_prompt():
    key = "test_favorite_drink_phase1"
    upsert_memory(key, "coffee", source="test", device_id="device-a")
    prompt = build_system_prompt()
    assert key in prompt
    assert "coffee" in prompt
    # Same brain DB = cross-session / cross-device source of truth
    assert "coffee" in build_system_prompt()
    delete_memory(key)


def test_proactive_context_in_system_prompt():
    hour_bucket = f"{datetime.now(UTC).hour:02d}:00"
    # Start 0.5; bump once → 0.6 (proactive threshold)
    upsert_habit("time_of_day", hour_bucket, "Offer morning brief", confidence_delta=0.1)
    upsert_habit("time_of_day", hour_bucket, "Offer morning brief", confidence_delta=0.1)
    suggestions = get_proactive_context()
    assert any("morning brief" in s.lower() for s in suggestions)
    prompt = build_system_prompt()
    assert "Proactive suggestions" in prompt
    assert "Offer morning brief" in prompt
