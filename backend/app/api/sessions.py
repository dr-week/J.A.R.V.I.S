"""API — /sessions endpoints for room presence and cross-surface continuity.

ISSUE-062: a house/room surface can start a session, and a phone (or any other
client) can discover it and continue the same conversation. Sessions are the
brain's source of truth for conversation continuity; clients are edges.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..soul import memory as mem

router = APIRouter(prefix="/sessions")


class SessionStart(BaseModel):
    device_id: str = ""
    surface: str = ""
    room: str = ""
    title: str = ""


class SessionSurfacePatch(BaseModel):
    surface: str = ""
    room: str = ""
    device_id: str = ""


@router.post("")
async def start_session(body: SessionStart):
    """Start a new session on a given surface/room and return its id."""
    session_id = str(uuid.uuid4())
    sess = mem.get_or_create_session(
        session_id,
        body.device_id,
        body.surface,
        body.room,
    )
    if body.title:
        mem.set_session_title(session_id, body.title)
        sess["title"] = body.title
    return {"ok": True, "session_id": session_id, "session": sess}


@router.get("")
async def list_sessions(limit: int = 50):
    """List recent sessions so a phone can find and continue one."""
    return {"sessions": mem.list_sessions(limit=max(1, min(limit, 200)))}


@router.get("/{session_id}")
async def get_session(session_id: str, limit: int = 40):
    """Fetch a session's metadata + recent messages (continue context)."""
    sess = mem.get_session(session_id)
    if not sess:
        raise HTTPException(404, f"Session '{session_id}' not found.")
    messages = mem.get_session_messages(session_id, limit=max(1, min(limit, 200)))
    return {"ok": True, "session": sess, "messages": messages}


@router.patch("/{session_id}/surface")
async def patch_surface(session_id: str, body: SessionSurfacePatch):
    """Re-tag a session for a handoff (e.g. house -> phone)."""
    sess = mem.set_session_surface(
        session_id,
        body.surface,
        body.room,
        body.device_id,
    )
    if not sess:
        raise HTTPException(404, f"Session '{session_id}' not found.")
    return {"ok": True, "session": sess}
