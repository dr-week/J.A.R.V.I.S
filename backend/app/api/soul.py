"""API — /soul/* endpoints for memories, habits, and persona config."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..soul import memory as mem
from ..soul.memory import set_config
from ..soul.persona import build_system_prompt, get_assistant_name, get_persona_profile
from ..sync.manager import manager

router = APIRouter(prefix="/soul")


# ── Memories ──────────────────────────────────────────────────────────────────

class MemoryUpsert(BaseModel):
    value: str
    source: str = "explicit"
    device_id: str = ""
    updated_at: str | None = None


@router.get("/memories")
async def list_memories():
    return {"memories": mem.list_memories()}


@router.put("/memories/{key}")
async def upsert_memory(key: str, body: MemoryUpsert):
    applied = mem.upsert_memory(
        key,
        body.value,
        body.source,
        body.device_id,
        body.updated_at,
    )
    # Broadcast asynchronously without waiting for clients
    asyncio.create_task(manager.push_memory_update(key, body.value))
    return {"ok": True, "key": key, "applied": applied}


@router.delete("/memories/{key}")
async def delete_memory(key: str):
    deleted = mem.delete_memory(key)
    if not deleted:
        raise HTTPException(404, f"Memory key '{key}' not found.")
    # Broadcast deletion as empty string or null (we'll push empty string)
    asyncio.create_task(manager.push_memory_update(key, ""))
    return {"ok": True, "key": key}


# ── Habits ────────────────────────────────────────────────────────────────────

@router.get("/habits")
async def list_habits(active_only: bool = True):
    return {"habits": mem.list_habits(active_only=active_only)}


@router.delete("/habits/{habit_id}")
async def archive_habit(habit_id: int):
    archived = mem.archive_habit(habit_id)
    if not archived:
        raise HTTPException(404, f"Habit {habit_id} not found.")
    asyncio.create_task(manager.push_habit_update({"id": habit_id, "active": 0}))
    return {"ok": True, "habit_id": habit_id, "action": "archived"}


# ── Config / Persona ──────────────────────────────────────────────────────────

class ConfigPatch(BaseModel):
    name: str | None = None


@router.get("/persona")
async def get_persona():
    profile = get_persona_profile()
    prompt = build_system_prompt()
    return {
        "assistant_name": get_assistant_name(),
        "role": profile.role,
        "tone": profile.tone,
        "rules": list(profile.rules),
        "trust_summary": profile.trust_summary,
        "system_prompt_preview": prompt if len(prompt) <= 800 else prompt[:800] + "...",
        "aligned_with": "docs/PERSONA.md",
    }


@router.patch("/persona")
async def patch_persona(body: ConfigPatch):
    if body.name is not None:
        if not body.name.strip():
            raise HTTPException(400, "Name cannot be empty.")
        set_config("assistant_name", body.name.strip())
    return {"ok": True, "assistant_name": get_assistant_name()}
