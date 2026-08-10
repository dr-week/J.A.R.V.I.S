"""Soul — SQLite persistence (stable import surface).

Implementation is split under `soul.db` and `soul.stores.*` so agents can edit
one concern per file. External code should keep importing from `soul.memory`.
"""
from __future__ import annotations

from .db import init_db
from .stores.audit import list_action_log, log_action
from .stores.config_kv import get_config, set_config
from .stores.devices import delete_expired_tokens, get_device_by_token, save_device_token
from .stores.learning_store import archive_habit, list_habits, log_interaction, upsert_habit
from .stores.memories import delete_memory, get_memory, list_memories, upsert_memory
from .stores.sessions import (
    append_message,
    get_or_create_session,
    get_session,
    get_session_messages,
    list_sessions,
    set_session_surface,
    set_session_title,
)

__all__ = [
    "init_db",
    "get_config",
    "set_config",
    "upsert_memory",
    "get_memory",
    "list_memories",
    "delete_memory",
    "log_interaction",
    "upsert_habit",
    "list_habits",
    "archive_habit",
    "get_or_create_session",
    "list_sessions",
    "get_session",
    "set_session_surface",
    "set_session_title",
    "append_message",
    "get_session_messages",
    "log_action",
    "list_action_log",
    "save_device_token",
    "get_device_by_token",
    "delete_expired_tokens",
]
