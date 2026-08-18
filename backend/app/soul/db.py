"""Soul — SQLite connection and schema bootstrap.

All store modules use `_db()` and `_utc()` from here. Do not open ad-hoc connections elsewhere.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime

from ..config import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT NOT NULL UNIQUE,
    value       TEXT NOT NULL,
    source      TEXT DEFAULT 'explicit',
    updated_at  DATETIME NOT NULL,
    device_id   TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS preferences (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT NOT NULL UNIQUE,
    value       TEXT NOT NULL,
    updated_at  DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS interaction_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          DATETIME NOT NULL,
    topic       TEXT,
    intent      TEXT,
    device_id   TEXT DEFAULT '',
    context_json TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS habits (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type    TEXT NOT NULL,
    pattern_key     TEXT NOT NULL,
    pattern_value   TEXT NOT NULL,
    confidence      REAL DEFAULT 0.5,
    occurrences     INTEGER DEFAULT 1,
    last_seen       DATETIME,
    created_at      DATETIME NOT NULL,
    active          INTEGER DEFAULT 1,
    UNIQUE(pattern_type, pattern_key)
);

CREATE TABLE IF NOT EXISTS sessions (
    id          TEXT PRIMARY KEY,
    device_id   TEXT DEFAULT '',
    surface     TEXT DEFAULT '',
    room        TEXT DEFAULT '',
    created_at  DATETIME NOT NULL,
    updated_at  DATETIME NOT NULL,
    title       TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL REFERENCES sessions(id),
    client_msg_id TEXT UNIQUE,
    role        TEXT NOT NULL,
    content     TEXT NOT NULL,
    ts          DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS action_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              DATETIME NOT NULL,
    tool_name       TEXT NOT NULL,
    parameters_json TEXT DEFAULT '{}',
    result_summary  TEXT DEFAULT '',
    device_id       TEXT DEFAULT '',
    confirmed_by    TEXT DEFAULT 'auto'
);

CREATE TABLE IF NOT EXISTS config (
    key     TEXT PRIMARY KEY,
    value   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS devices (
    token       TEXT PRIMARY KEY,
    device_id   TEXT NOT NULL,
    device_name TEXT,
    expires_at  REAL NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    key,
    value,
    content='memories',
    content_rowid='id',
    tokenize='porter unicode61'
);

CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, key, value) VALUES (new.id, new.key, new.value);
END;

CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, key, value) VALUES('delete', old.id, old.key, old.value);
END;

CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, key, value) VALUES('delete', old.id, old.key, old.value);
    INSERT INTO memories_fts(rowid, key, value) VALUES (new.id, new.key, new.value);
END;
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def _db() -> Generator[sqlite3.Connection, None, None]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _utc() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def init_db() -> None:
    """Create all tables if they don't exist."""
    with _db() as conn:
        conn.executescript(_SCHEMA)
        try:
            conn.execute("ALTER TABLE messages ADD COLUMN client_msg_id TEXT UNIQUE")
        except sqlite3.OperationalError:
            pass
        for col in ("surface", "room"):
            try:
                conn.execute(f"ALTER TABLE sessions ADD COLUMN {col} TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
