"""Mind — LLM agent loop (orchestration only).

Provider-specific streaming lives in mind.gemini_loop.
"""
from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator

from .. import config
from ..hands.gate import get_pending_confirmation, user_confirmed
from ..hands.registry import run_tool
from ..soul.learner import observe
from ..soul.memory import append_message, get_or_create_session, get_session_messages
from ..soul.persona import build_system_prompt
from ..sync.manager import manager
from .gemini_loop import gemini_stream


async def stream_chat(
    session_id: str,
    user_text: str,
    device_id: str = "",
    client_msg_id: str | None = None,
    confirm_pending_tool: bool = False,
    surface: str = "",
    room: str = "",
) -> AsyncGenerator[str, None]:
    """Yield SSE-compatible chunks for a user turn."""
    get_or_create_session(session_id, device_id, surface, room)

    appended = append_message(session_id, "user", user_text, client_msg_id)
    if not appended:
        yield "Message deduplicated (already processed)."
        return

    pending = get_pending_confirmation(session_id)
    if pending and (confirm_pending_tool or user_confirmed(user_text)):
        result = await run_tool(
            pending["tool_name"],
            pending.get("parameters") or {},
            session_id=session_id,
            device_id=device_id,
            user_text=user_text,
            explicit_confirm=True,
        )
        reply = json.dumps(result)
        yield reply
        append_message(session_id, "assistant", reply)
        return

    updated_habits = observe(user_text, device_id=device_id)
    if updated_habits:
        for habit in updated_habits:
            asyncio.create_task(manager.push_habit_update(habit))

    history = get_session_messages(session_id, limit=30)
    system_prompt = build_system_prompt()

    if config.LLM_PROVIDER == "gemini" and config.GEMINI_API_KEY:
        gen = gemini_stream(system_prompt, history, user_text, session_id, device_id)
    else:
        gen = _fallback_stream(user_text)

    full_reply = ""
    async for chunk in gen:
        full_reply += chunk
        yield chunk

    append_message(session_id, "assistant", full_reply)


async def _fallback_stream(user_text: str) -> AsyncGenerator[str, None]:
    from ..soul.persona import get_assistant_name

    name = get_assistant_name()
    yield (
        f"[{name} — no LLM configured]\n\n"
        f"I received your message: \"{user_text}\"\n\n"
        f"To activate the AI, add GEMINI_API_KEY to your .env file.\n"
        f"Get a free key at: https://aistudio.google.com/app/apikey"
    )
