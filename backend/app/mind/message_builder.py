"""Message list builder for chat.completions requests.

Single responsibility: given a system prompt, conversation history, and
current user text, produce the messages[] array and the filtered tools[]
list to send to the LLM. No HTTP or streaming logic here.
"""
from __future__ import annotations

import json
from typing import Any

from .router import classify_intent_fast
from ..hands.registry import REGISTRY

# Sliding window: keep only the last N turns to protect the KV cache
# on 4GB VRAM (GTX 1050 Ti) from overflowing.
MAX_CONTEXT_TURNS = 6


def build_tools(user_text: str) -> list[dict[str, Any]]:
    """Return only the tool schemas relevant to this prompt (0 VRAM waste)."""
    active = classify_intent_fast(user_text)
    if not active:
        return []

    tools = []
    for name in active:
        tool = REGISTRY.get(name)
        if tool:
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters") or {"type": "object", "properties": {}},
                    },
                }
            )
    return tools


def build_messages(
    system_prompt: str,
    history: list[dict[str, Any]],
    user_text: str,
) -> list[dict[str, Any]]:
    """Build a pruned message list safe for the 4096 context window."""
    msgs: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    pruned = history[-MAX_CONTEXT_TURNS:] if len(history) > MAX_CONTEXT_TURNS else history
    for msg in pruned[:-1]:
        role = msg.get("role") or "user"
        if role not in ("user", "assistant", "system"):
            role = "user"
        content = msg.get("content") or ""
        if not isinstance(content, str):
            content = json.dumps(content)
        msgs.append({"role": role, "content": content})

    msgs.append({"role": "user", "content": user_text})
    return msgs
