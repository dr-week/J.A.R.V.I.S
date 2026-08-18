"""OpenAI-compatible streaming loop (LM Studio, Ollama OpenAI shim, cloud OpenAI).

Assistant content is always plain text strings so Jinja chat templates that
reject non-text chunks (Ministral/Devstral) still work.
"""
from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from .. import config
from .router import classify_intent_fast
from ..hands.registry import REGISTRY, run_tool


def _base_url() -> str:
    raw = (config.LLM_BASE_URL or "").rstrip("/")
    if not raw:
        # LM Studio default
        return "http://127.0.0.1:1234/v1"
    if raw.endswith("/v1"):
        return raw
    return f"{raw}/v1"


def _headers() -> dict[str, str]:
    key = config.LLM_API_KEY or "lm-studio"
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _openai_tools(current_prompt: str = "") -> list[dict[str, Any]]:
    active_tools = classify_intent_fast(current_prompt)
    if not active_tools:
        return []

    tools = []
    for name in active_tools:
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


MAX_CONTEXT_TURNS = 6


def _history_messages(
    system_prompt: str, history: list[dict[str, Any]], user_text: str
) -> list[dict[str, Any]]:
    msgs: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    pruned_history = history[-MAX_CONTEXT_TURNS:] if len(history) > MAX_CONTEXT_TURNS else history
    for msg in pruned_history[:-1]:
        role = msg.get("role") or "user"
        if role not in ("user", "assistant", "system"):
            role = "user"
        content = msg.get("content") or ""
        if not isinstance(content, str):
            content = json.dumps(content)
        msgs.append({"role": role, "content": content})
    msgs.append({"role": "user", "content": user_text})
    return msgs


async def openai_stream(
    system_prompt: str,
    history: list[dict[str, Any]],
    user_text: str,
    session_id: str,
    device_id: str,
) -> AsyncGenerator[str, None]:
    """Stream chat.completions; run tool calls via Hands gate (max 5 turns)."""
    messages = _history_messages(system_prompt, history, user_text)
    tools = _openai_tools(user_text)
    url = f"{_base_url()}/chat/completions"

    async with httpx.AsyncClient(timeout=120.0) as client:
        for _turn in range(5):
            body: dict[str, Any] = {
                "model": config.LLM_MODEL,
                "messages": messages,
                "stream": True,
                "temperature": 0.7,
            }
            if tools:
                body["tools"] = tools

            try:
                async with client.stream("POST", url, headers=_headers(), json=body) as resp:
                    if resp.status_code >= 400:
                        err = (await resp.aread()).decode("utf-8", errors="replace")[:500]
                        yield f"\n[LLM Error HTTP {resp.status_code}: {err}]\n"
                        return

                    assistant_text = ""
                    tool_acc: dict[int, dict[str, str]] = {}

                    async for line in resp.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        choice = (chunk.get("choices") or [{}])[0]
                        delta = choice.get("delta") or {}
                        if delta.get("content"):
                            piece = delta["content"]
                            # Force string — never structured chunks into history
                            if not isinstance(piece, str):
                                piece = str(piece)
                            assistant_text += piece
                            yield piece
                        for tc in delta.get("tool_calls") or []:
                            idx = int(tc.get("index", 0))
                            slot = tool_acc.setdefault(idx, {"id": "", "name": "", "arguments": ""})
                            if tc.get("id"):
                                slot["id"] = tc["id"]
                            fn = tc.get("function") or {}
                            if fn.get("name"):
                                slot["name"] = fn["name"]
                            if fn.get("arguments"):
                                slot["arguments"] += fn["arguments"]
            except httpx.ConnectError:
                yield (
                    f"\n[LLM Error: cannot reach {_base_url()}. "
                    "Start LM Studio server or set JARVIS_LLM_BASE_URL.]\n"
                )
                return
            except Exception as exc:
                yield f"\n[LLM Error: {exc}]\n"
                return

            if not tool_acc:
                return

            # Plain-text assistant message + separate tool_calls (template-safe)
            tc_list = []
            for slot in tool_acc.values():
                tc_list.append(
                    {
                        "id": slot["id"] or f"call_{slot['name']}",
                        "type": "function",
                        "function": {
                            "name": slot["name"],
                            "arguments": slot["arguments"] or "{}",
                        },
                    }
                )
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_text or "",
                    "tool_calls": tc_list,
                }
            )

            for slot in tool_acc.values():
                name = slot["name"]
                try:
                    params = json.loads(slot["arguments"] or "{}")
                except json.JSONDecodeError:
                    params = {}
                yield f"\n[Calling tool: {name}...]\n"
                result = await run_tool(
                    name,
                    params if isinstance(params, dict) else {},
                    session_id=session_id,
                    device_id=device_id,
                    user_text=user_text,
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": slot["id"] or f"call_{name}",
                        "content": json.dumps(result),
                    }
                )
