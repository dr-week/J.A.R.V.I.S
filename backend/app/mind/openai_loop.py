"""OpenAI-compatible streaming loop (LM Studio, Ollama OpenAI shim, cloud OpenAI).

Single responsibility: stream chat.completions and handle tool call turns.
Connection config lives in llm_client.py; message formatting in message_builder.py.
"""
from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from .. import config
from ..hands.registry import run_tool
from .llm_client import base_url, auth_headers
from .message_builder import build_messages, build_tools

# Hard limit on agentic tool-call loops to prevent runaway VRAM usage.
MAX_TOOL_TURNS = 5


async def openai_stream(
    system_prompt: str,
    history: list[dict[str, Any]],
    user_text: str,
    session_id: str,
    device_id: str,
) -> AsyncGenerator[str, None]:
    """Stream chat.completions; run tool calls via Hands gate (max 5 turns)."""
    messages = build_messages(system_prompt, history, user_text)
    tools = build_tools(user_text)
    url = f"{base_url()}/chat/completions"

    async with httpx.AsyncClient(timeout=120.0) as client:
        for _turn in range(MAX_TOOL_TURNS):
            body: dict[str, Any] = {
                "model": config.LLM_MODEL,
                "messages": messages,
                "stream": True,
                "temperature": 0.7,
            }
            if tools:
                body["tools"] = tools

            try:
                async with client.stream("POST", url, headers=auth_headers(), json=body) as resp:
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
                            # Force string — never let structured chunks enter history
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
                    f"\n[LLM Error: cannot reach {base_url()}. "
                    "Start LM Studio server or set JARVIS_LLM_BASE_URL.]\n"
                )
                return
            except Exception as exc:
                yield f"\n[LLM Error: {exc}]\n"
                return

            # No tool calls → generation is complete
            if not tool_acc:
                return

            # Append plain-text assistant turn + tool_calls (template-safe)
            tc_list = [
                {
                    "id": slot["id"] or f"call_{slot['name']}",
                    "type": "function",
                    "function": {
                        "name": slot["name"],
                        "arguments": slot["arguments"] or "{}",
                    },
                }
                for slot in tool_acc.values()
            ]
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_text or "",
                    "tool_calls": tc_list,
                }
            )

            # Execute each tool and append its result
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
