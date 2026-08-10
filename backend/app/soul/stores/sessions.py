"""Soul store — chat sessions and messages."""
from __future__ import annotations

import sqlite3
from typing import Any

from ..db import _db, _utc


def get_or_create_session(
    session_id: str,
    device_id: str = "",
    surface: str = "",
    room: str = "",
) -> dict[str, Any]:
    now = _utc()
    with _db() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
        if row:
            return dict(row)
        conn.execute(
            "INSERT INTO sessions(id,device_id,surface,room,created_at,updated_at) VALUES(?,?,?,?,?,?)",
            (session_id, device_id, surface, room, now, now),
        )
        return {
            "id": session_id,
            "device_id": device_id,
            "surface": surface,
            "room": room,
            "created_at": now,
            "updated_at": now,
        }


def list_sessions(limit: int = 50) -> list[dict[str, Any]]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, device_id, surface, room, title, created_at, updated_at "
            "FROM sessions ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_session(session_id: str) -> dict[str, Any] | None:
    with _db() as conn:
        row = conn.execute(
            "SELECT id, device_id, surface, room, title, created_at, updated_at "
            "FROM sessions WHERE id=?",
            (session_id,),
        ).fetchone()
        return dict(row) if row else None


def set_session_surface(
    session_id: str,
    surface: str = "",
    room: str = "",
    device_id: str = "",
) -> dict[str, Any] | None:
    now = _utc()
    with _db() as conn:
        row = conn.execute("SELECT id FROM sessions WHERE id=?", (session_id,)).fetchone()
        if not row:
            return None
        conn.execute(
            "UPDATE sessions SET surface=?, room=?, device_id=?, updated_at=? WHERE id=?",
            (surface, room, device_id, now, session_id),
        )
        out = conn.execute(
            "SELECT id, device_id, surface, room, title, created_at, updated_at "
            "FROM sessions WHERE id=?",
            (session_id,),
        ).fetchone()
        return dict(out) if out else None


def set_session_title(session_id: str, title: str) -> None:
    now = _utc()
    with _db() as conn:
        conn.execute(
            "UPDATE sessions SET title=?, updated_at=? WHERE id=?",
            (title, now, session_id),
        )


def append_message(
    session_id: str,
    role: str,
    content: str,
    client_msg_id: str | None = None,
) -> bool:
    now = _utc()
    with _db() as conn:
        if client_msg_id:
            try:
                conn.execute(
                    "INSERT INTO messages(session_id, role, content, ts, client_msg_id) VALUES(?,?,?,?,?)",
                    (session_id, role, content, now, client_msg_id),
                )
            except sqlite3.IntegrityError:
                return False
        else:
            conn.execute(
                "INSERT INTO messages(session_id, role, content, ts) VALUES(?,?,?,?)",
                (session_id, role, content, now),
            )
        conn.execute("UPDATE sessions SET updated_at=? WHERE id=?", (now, session_id))
        return True


def get_session_messages(session_id: str, limit: int = 40) -> list[dict[str, Any]]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT role, content, ts FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
        return list(reversed([dict(r) for r in rows]))
