"""Core tools for the Soul (memory)."""
from __future__ import annotations

from typing import Any

from ..hands import registry
from . import memory


def _save_memory(key: str = "", value: str = "", device_id: str = "") -> dict[str, Any]:
    """Upsert an explicit memory to the database."""
    if not key or not value:
        return {"error": "Both 'key' and 'value' are required."}
    
    success = memory.upsert_memory(key=key, value=value, source="explicit", device_id=device_id)
    if success:
        return {"result": f"Memory saved: {key} = {value}"}
    return {"result": "Memory rejected (newer version exists)."}


def _list_memories() -> dict[str, Any]:
    """Retrieve all explicitly saved memories."""
    memories = memory.list_memories()
    if not memories:
        return {"result": "No explicit memories stored yet."}
    return {"memories": memories}


def _forget_memory(key: str = "") -> dict[str, Any]:
    """Delete a memory from the database."""
    if not key:
        return {"error": "A 'key' is required to delete a memory."}
    
    success = memory.delete_memory(key)
    if success:
        return {"result": f"Memory '{key}' deleted."}
    return {"result": f"Memory '{key}' not found."}


registry.register(
    {
        "name": "save_memory",
        "description": "Save a piece of information about the user (e.g. preferences, facts, routines) for long-term recall.",
        "version": "1.0.0",
        "phase": 1,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "A short, unique identifier for the memory (e.g., 'favorite_food')."},
                "value": {"type": "string", "description": "The information to remember."}
            },
            "required": ["key", "value"],
        },
        "returns": {"type": "object", "properties": {"result": {"type": "string"}}},
        "scopes": [],
        "tags": ["memory", "soul"],
    },
    _save_memory,
)

registry.register(
    {
        "name": "list_memories",
        "description": "List all explicit long-term memories saved about the user.",
        "version": "1.0.0",
        "phase": 1,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "returns": {"type": "object", "properties": {"memories": {"type": "array"}}},
        "scopes": [],
        "tags": ["memory", "soul"],
    },
    _list_memories,
)

registry.register(
    {
        "name": "forget_memory",
        "description": "Delete a long-term memory about the user.",
        "version": "1.0.0",
        "phase": 1,
        "risk_level": "confirm_always",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "The short identifier for the memory to delete."}
            },
            "required": ["key"],
        },
        "returns": {"type": "object", "properties": {"result": {"type": "string"}}},
        "scopes": [],
        "tags": ["memory", "soul", "destructive"],
    },
    _forget_memory,
)
