"""Soul store — user memories (LWW v1)."""
from __future__ import annotations

from typing import Any

from ..db import _db, _utc


def upsert_memory(
    key: str,
    value: str,
    source: str = "explicit",
    device_id: str = "",
    updated_at: str | None = None,
) -> bool:
    ts = updated_at or _utc()
    with _db() as conn:
        existing = conn.execute(
            "SELECT updated_at FROM memories WHERE key=?", (key,)
        ).fetchone()
        if existing:
            if ts <= existing["updated_at"]:
                return False
            conn.execute(
                """UPDATE memories SET value=?, source=?, updated_at=?, device_id=?
                   WHERE key=?""",
                (value, source, ts, device_id, key),
            )
            return True
        conn.execute(
            """INSERT INTO memories(key,value,source,updated_at,device_id)
               VALUES(?,?,?,?,?)""",
            (key, value, source, ts, device_id),
        )
        return True


def get_memory(key: str) -> str | None:
    with _db() as conn:
        row = conn.execute("SELECT value FROM memories WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None


def list_memories() -> list[dict[str, Any]]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT key, value, source, updated_at FROM memories ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_memory(key: str) -> bool:
    with _db() as conn:
        cur = conn.execute("DELETE FROM memories WHERE key=?", (key,))
        return cur.rowcount > 0
