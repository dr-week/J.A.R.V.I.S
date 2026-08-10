"""Soul store — interaction log and learned habits."""
from __future__ import annotations

import json
from typing import Any

from ..db import _db, _utc


def log_interaction(
    topic: str = "",
    intent: str = "",
    device_id: str = "",
    context: dict | None = None,
) -> None:
    with _db() as conn:
        conn.execute(
            "INSERT INTO interaction_log(ts,topic,intent,device_id,context_json) VALUES(?,?,?,?,?)",
            (_utc(), topic, intent, device_id, json.dumps(context or {})),
        )


def upsert_habit(
    pattern_type: str,
    pattern_key: str,
    pattern_value: str,
    confidence_delta: float = 0.1,
) -> dict | None:
    now = _utc()
    with _db() as conn:
        existing = conn.execute(
            "SELECT id, confidence, occurrences FROM habits WHERE pattern_type=? AND pattern_key=?",
            (pattern_type, pattern_key),
        ).fetchone()

        if existing:
            new_conf = min(1.0, existing["confidence"] + confidence_delta)
            conn.execute(
                "UPDATE habits SET confidence=?, occurrences=occurrences+1, last_seen=?, pattern_value=? WHERE id=?",
                (new_conf, now, pattern_value, existing["id"]),
            )
            habit_id = existing["id"]
        else:
            cur = conn.execute(
                "INSERT INTO habits(pattern_type,pattern_key,pattern_value,confidence,occurrences,last_seen,created_at) VALUES(?,?,?,0.5,1,?,?)",
                (pattern_type, pattern_key, pattern_value, now, now),
            )
            habit_id = cur.lastrowid

        row = conn.execute("SELECT * FROM habits WHERE id=?", (habit_id,)).fetchone()
        return dict(row) if row else None


def list_habits(active_only: bool = True) -> list[dict[str, Any]]:
    with _db() as conn:
        q = (
            "SELECT * FROM habits WHERE active=1 ORDER BY confidence DESC"
            if active_only
            else "SELECT * FROM habits ORDER BY confidence DESC"
        )
        return [dict(r) for r in conn.execute(q).fetchall()]


def archive_habit(habit_id: int) -> bool:
    with _db() as conn:
        cur = conn.execute("UPDATE habits SET active=0 WHERE id=?", (habit_id,))
        return cur.rowcount > 0
