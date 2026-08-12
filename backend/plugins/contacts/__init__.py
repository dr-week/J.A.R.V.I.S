"""Contacts plugin — local contacts management with search.

Stores contacts in the central brain SQLite database.
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
        """CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL DEFAULT '',
            email TEXT NOT NULL DEFAULT '',
            company TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
    )
    return conn


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _contact_add(name: str, phone: str = "", email: str = "", company: str = "", notes: str = "") -> dict[str, Any]:
    """Add a new contact."""
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("name cannot be empty.")
    now = _now_iso()
    contact = {
        "id": uuid.uuid4().hex[:12],
        "name": clean_name,
        "phone": phone.strip(),
        "email": email.strip(),
        "company": company.strip(),
        "notes": notes.strip(),
        "created_at": now,
        "updated_at": now,
    }
    with closing(_connection()) as conn:
        with conn:
            conn.execute(
                """INSERT INTO contacts (id, name, phone, email, company, notes, created_at, updated_at)
                   VALUES(:id, :name, :phone, :email, :company, :notes, :created_at, :updated_at)""",
                contact,
            )
    return contact


def _contact_search(query: str, limit: int = 20) -> dict[str, Any]:
    """Search contacts by name, email, or phone (case-insensitive LIKE)."""
    pattern = f"%{query.strip()}%"
    with closing(_connection()) as conn:
        rows = conn.execute(
            "SELECT * FROM contacts WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? ORDER BY name ASC LIMIT ?",
            (pattern, pattern, pattern, limit),
        ).fetchall()
    contacts = [dict(r) for r in rows]
    return {"count": len(contacts), "contacts": contacts}


def _contact_list(limit: int = 50) -> dict[str, Any]:
    """List all contacts ordered by name."""
    with closing(_connection()) as conn:
        rows = conn.execute("SELECT * FROM contacts ORDER BY name ASC LIMIT ?", (limit,)).fetchall()
    contacts = [dict(r) for r in rows]
    return {"count": len(contacts), "contacts": contacts}


def _contact_edit(contact_id: str, name: str = "", phone: str = "", email: str = "", company: str = "", notes: str = "") -> dict[str, Any]:
    """Edit a contact's fields by id. Only non-empty fields are updated."""
    with closing(_connection()) as conn:
        with conn:
            row = conn.execute("SELECT * FROM contacts WHERE id=?", (contact_id,)).fetchone()
            if not row:
                raise ValueError(f"No contact found with id '{contact_id}'.")
            updates = {}
            if name.strip():
                updates["name"] = name.strip()
            if phone.strip():
                updates["phone"] = phone.strip()
            if email.strip():
                updates["email"] = email.strip()
            if company.strip():
                updates["company"] = company.strip()
            if notes.strip():
                updates["notes"] = notes.strip()
            if not updates:
                return {"id": contact_id, "changed": False, "message": "No fields to update."}
            updates["updated_at"] = _now_iso()
            set_clause = ", ".join(f"{k}=:{k}" for k in updates)
            updates["id"] = contact_id
            conn.execute(f"UPDATE contacts SET {set_clause} WHERE id=:id", updates)
    return {"id": contact_id, "changed": True, "updated_fields": list(updates.keys())}


def _contact_delete(contact_id: str) -> dict[str, Any]:
    """Delete a contact by id."""
    with closing(_connection()) as conn:
        with conn:
            row = conn.execute("SELECT id, name FROM contacts WHERE id=?", (contact_id,)).fetchone()
            if not row:
                raise ValueError(f"No contact found with id '{contact_id}'.")
            conn.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
    return {"id": row["id"], "name": row["name"], "deleted": True}


# ── Register tools ──────────────────────────────────────────────

registry.register(
    {
        "name": "contact_add", "description": "Add a new contact with name, phone, email, company, and notes.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_once", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string"}, "phone": {"type": "string"}, "email": {"type": "string"},
            "company": {"type": "string"}, "notes": {"type": "string"},
        }, "required": ["name"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "name": {"type": "string"}}},
        "scopes": ["contacts:write"], "tags": ["productivity", "contacts"],
    }, _contact_add,
)

registry.register(
    {
        "name": "contact_search", "description": "Search contacts by name, email, or phone number.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}, "limit": {"type": "integer"},
        }, "required": ["query"]},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "contacts": {"type": "array"}}},
        "scopes": ["contacts:read"], "tags": ["productivity", "contacts"],
    }, _contact_search,
)

registry.register(
    {
        "name": "contact_list", "description": "List all contacts ordered by name.",
        "version": "1.0.0", "phase": 3, "risk_level": "auto", "executor": "brain",
        "parameters": {"type": "object", "properties": {"limit": {"type": "integer"}}, "required": []},
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "contacts": {"type": "array"}}},
        "scopes": ["contacts:read"], "tags": ["productivity", "contacts"],
    }, _contact_list,
)

registry.register(
    {
        "name": "contact_edit", "description": "Edit a contact's fields by id. Only non-empty fields are updated.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_once", "executor": "brain",
        "parameters": {"type": "object", "properties": {
            "contact_id": {"type": "string"}, "name": {"type": "string"}, "phone": {"type": "string"},
            "email": {"type": "string"}, "company": {"type": "string"}, "notes": {"type": "string"},
        }, "required": ["contact_id"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "changed": {"type": "boolean"}}},
        "scopes": ["contacts:write"], "tags": ["productivity", "contacts"],
    }, _contact_edit,
)

registry.register(
    {
        "name": "contact_delete", "description": "Delete a contact by its id.",
        "version": "1.0.0", "phase": 3, "risk_level": "confirm_always", "executor": "brain",
        "parameters": {"type": "object", "properties": {"contact_id": {"type": "string"}}, "required": ["contact_id"]},
        "returns": {"type": "object", "properties": {"id": {"type": "string"}, "deleted": {"type": "boolean"}}},
        "scopes": ["contacts:write"], "tags": ["productivity", "contacts"],
    }, _contact_delete,
)
