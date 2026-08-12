"""Notes plugin — SQLite FTS5 full-text search note-taking.

Stores notes with full-text search capability in the central brain database.
Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import sqlite3
import uuid
from contextlib import closing
from datetime import UTC, datetime
from typing import Any

from backend.app.config import DB_PATH
from backend.app.hands import registry


def _connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            tags TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
    )
    # FTS5 virtual table for full-text search
    conn.execute(
        """CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts
           USING fts5(title, content, tags, content='notes', content_rowid='rowid')"""
    )
    return conn


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _rebuild_fts(conn: sqlite3.Connection) -> None:
    """Rebuild FTS index after insert/update/delete."""
    try:
        conn.execute("INSERT INTO notes_fts(notes_fts) VALUES('rebuild')")
    except sqlite3.OperationalError:
        pass  # FTS rebuild can fail on empty table


def _note_create(title: str, content: str = "", tags: str = "") -> dict[str, Any]:
    """Create a new note."""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("title cannot be empty.")
    now = _now_iso()
    note = {
        "id": uuid.uuid4().hex[:12],
        "title": clean_title,
        "content": content.strip(),
        "tags": tags.strip(),
        "created_at": now,
        "updated_at": now,
    }
    with closing(_connection()) as conn:
        with conn:
            conn.execute(
                """INSERT INTO notes (id, title, content, tags, created_at, updated_at)
                   VALUES(:id, :title, :content, :tags, :created_at, :updated_at)""",
                note,
            )
            _rebuild_fts(conn)
    return note


def _note_search(query: str, limit: int = 20) -> dict[str, Any]:
    """Full-text search across notes title, content, and tags."""
    q = query.strip()
    if not q:
        return {"count": 0, "notes": [], "message": "Empty query."}
    # Try FTS5 first, fall back to LIKE
    with closing(_connection()) as conn:
        try:
            rows = conn.execute(
                """SELECT n.* FROM notes n
                   JOIN notes_fts f ON n.rowid = f.rowid
                   WHERE notes_fts MATCH ?
                   ORDER BY rank LIMIT ?""",
                (q, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            # Fallback to LIKE search
            pattern = f"%{q}%"
            rows = conn.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? ORDER BY updated_at DESC LIMIT ?",
                (pattern, pattern, pattern, limit),
            ).fetchall()
    notes = [dict(r) for r in rows]
    return {"count": len(notes), "notes": notes}


def _note_list(limit: int = 20) -> dict[str, Any]:
    """List all notes, most recently updated first."""
    with closing(_connection()) as conn:
        rows = conn.execute("SELECT * FROM notes ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
    notes = [dict(r) for r in rows]
    return {"count": len(notes), "notes": notes}


def _note_edit(note_id: str, title: str = "", content: str = "", tags: str = "") -> dict[str, Any]:
    """Edit a note by id. Only non-empty fields are updated."""
    with closing(_connection()) as conn:
        with conn:
            row = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
            if not row:
                raise ValueError(f"No note found with id '{note_id}'.")
            updates: dict[str, str] = {}
            if title.strip():
                updates["title"] = title.strip()
            if content.strip():
                updates["content"] = content.strip()
            if tags.strip():
                updates["tags"] = tags.strip()
            if not updates:
                return {"id": note_id, "changed": False}
            updates["updated_at"] = _now_iso()
            set_clause = ", ".join(f"{k}=:{k}" for k in updates)
            updates["id"] = note_id
            conn.execute(f"UPDATE notes SET {set_clause} WHERE id=:id", updates)
            _rebuild_fts(conn)
    return {"id": note_id, "changed": True, "updated_fields": list(updates.keys())}


def _note_delete(note_id: str) -> dict[str, Any]:
    """Delete a note by id."""
    with closing(_connection()) as conn:
        with conn:
            row = conn.execute("SELECT id, title FROM notes WHERE id=?", (note_id,)).fetchone()
            if not row:
                raise ValueError(f"No note found with id '{note_id}'.")
            conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
            _rebuild_fts(conn)
    return {"id": row["id"], "title": row["title"], "deleted": True}


# ── Register tools ──────────────────────────────────────────────

registry.register(
    {
        "name": "note_create", "description": "Create a new note with title, content, and optional tags.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_once", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "title": {"type": "string"}, "content": {"type": "string"}, "tags": {"type": "string"},
        }, "required": ["title"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "title": {"type": "string"}}},
        "scopes": ["notes:write"], "tags": ["productivity", "notes"],
    }, _note_create,
)

registry.register(
    {
        "name": "note_search", "description": "Full-text search across all notes (title, content, tags).",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}, "limit": {"type": "integer"},
        }, "required": ["query"]},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "notes": {"type": "array"}}},
        "scopes": ["notes:read"], "tags": ["productivity", "notes"],
    }, _note_search,
)

registry.register(
    {
        "name": "note_list", "description": "List all notes, most recently updated first.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {"limit": {"type": "integer"}}, "required": []},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "notes": {"type": "array"}}},
        "scopes": ["notes:read"], "tags": ["productivity", "notes"],
    }, _note_list,
)

registry.register(
    {
        "name": "note_edit", "description": "Edit a note by id. Only non-empty fields are updated.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_once", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "note_id": {"type": "string"}, "title": {"type": "string"},
            "content": {"type": "string"}, "tags": {"type": "string"},
        }, "required": ["note_id"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "changed": {"type": "boolean"}}},
        "scopes": ["notes:write"], "tags": ["productivity", "notes"],
    }, _note_edit,
)

registry.register(
    {
        "name": "note_delete", "description": "Delete a note by its id.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_always", "executor": "brain",
        "parameters": {"type": "object", "properties": {"note_id": {"type": "string"}}, "required": ["note_id"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "deleted": {"type": "boolean"}}},
        "scopes": ["notes:write"], "tags": ["productivity", "notes"],
    }, _note_delete,
)
