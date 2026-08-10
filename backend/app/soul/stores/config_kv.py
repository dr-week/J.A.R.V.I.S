"""Soul store — key/value config (persona name, etc.)."""
from __future__ import annotations

from ..db import _db


def get_config(key: str, default: str = "") -> str:
    with _db() as conn:
        row = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_config(key: str, value: str) -> None:
    with _db() as conn:
        conn.execute(
            "INSERT INTO config(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
