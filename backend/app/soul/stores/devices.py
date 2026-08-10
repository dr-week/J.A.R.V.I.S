"""Soul store — paired device tokens."""
from __future__ import annotations

import time
from typing import Any

from ..db import _db


def save_device_token(token: str, device_id: str, device_name: str, expires_at: float) -> None:
    with _db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO devices (token, device_id, device_name, expires_at) VALUES (?, ?, ?, ?)",
            (token, device_id, device_name, expires_at),
        )


def get_device_by_token(token: str) -> dict[str, Any] | None:
    with _db() as conn:
        row = conn.execute(
            "SELECT device_id, device_name, expires_at FROM devices WHERE token = ?", (token,)
        ).fetchone()
        if not row:
            return None
        return {
            "device_id": row["device_id"],
            "device_name": row["device_name"],
            "expires_at": row["expires_at"],
        }


def delete_expired_tokens() -> None:
    with _db() as conn:
        conn.execute("DELETE FROM devices WHERE expires_at < ?", (time.time(),))
