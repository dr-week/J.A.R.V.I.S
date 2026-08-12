"""Hands — Tool registry.

Tools register here on startup. The Mind uses this registry to build
tool declarations for the LLM and to execute tool calls.

Tool schema: see docs/TOOL_SCHEMA.md
Plugin scan: hands.plugin_loader.discover_plugins()
Built-ins: hands.builtin_tools.register_builtin_tools()
"""
from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from ..soul.memory import log_action
from .gate import (
    RISK_CONFIRM_ALWAYS,
    RISK_CONFIRM_ONCE,
    allowlist_tool,
    check_and_prepare,
    clear_pending_confirmation,
    is_allowlisted,
    redact_parameters,
    user_confirmed,
)

REGISTRY: dict[str, dict[str, Any]] = {}
_EXECUTORS: dict[str, Callable[..., Any]] = {}


def register(tool_def: dict[str, Any], executor: Callable[..., Any] | None = None) -> None:
    """Register a tool definition and optional Python executor."""
    name = tool_def["name"]
    if name in REGISTRY:
        raise ValueError(f"Tool '{name}' already registered")
    REGISTRY[name] = tool_def
    if executor:
        _EXECUTORS[name] = executor


async def _execute_raw(name: str, params: dict[str, Any]) -> dict[str, Any]:
    """Execute a registered tool by name with params (no gate)."""
    tool_def = REGISTRY.get(name)
    if not tool_def:
        return {"error": f"Unknown tool '{name}'"}

    runtime = tool_def.get("runtime", "python")
    
    if runtime == "python":
        if name not in _EXECUTORS:
            return {"error": f"Tool '{name}' has no executor registered on this brain."}
        try:
            result = _EXECUTORS[name](**params)
            if hasattr(result, "__await__"):
                result = await result
            return {"result": result}
        except Exception as exc:
            return {"error": str(exc)}
    else:
        from .external_executor import ExternalExecutor
        executor = ExternalExecutor(REGISTRY)
        return await executor.execute(tool_def, params)


async def run_tool(
    name: str,
    params: dict[str, Any],
    *,
    session_id: str = "",
    device_id: str = "",
    user_text: str = "",
    explicit_confirm: bool = False,
) -> dict[str, Any]:
    """Execute through confirmation gate and write action_log."""
    tool_def = REGISTRY.get(name)
    if not tool_def:
        return {"error": f"Unknown tool '{name}'"}

    safe_params = redact_parameters(params)
    may_run, block_reason = check_and_prepare(
        tool_def,
        name,
        params,
        session_id=session_id,
        device_id=device_id,
        explicit_confirm=explicit_confirm,
        user_text=user_text,
    )
    if not may_run:
        if device_id:
            import asyncio
            import uuid

            from ..sync.manager import manager

            payload = {
                "type": "confirm_request",
                "tool": name,
                "params": params,
                "request_id": str(uuid.uuid4()),
            }
            asyncio.create_task(manager.send_to_device(device_id, payload))

        return {"error": block_reason, "requires_confirmation": True}

    risk = tool_def.get("risk_level", "auto")
    confirmed_by = "auto"
    if risk == RISK_CONFIRM_ALWAYS and (explicit_confirm or user_confirmed(user_text)):
        confirmed_by = "user"
    elif risk == RISK_CONFIRM_ONCE:
        if explicit_confirm or user_confirmed(user_text):
            allowlist_tool(device_id, name)
            confirmed_by = "user"
        elif is_allowlisted(device_id, name):
            confirmed_by = "allowlist"

    if tool_def.get("executor") == "client":
        result = await _dispatch_to_device(name, params, device_id, session_id)
    else:
        result = await _execute_raw(name, params)

    clear_pending_confirmation(session_id)

    summary = json.dumps(result)[:500]
    log_action(
        name,
        safe_params,
        result_summary=summary,
        device_id=device_id,
        confirmed_by=confirmed_by,
    )
    return result


async def _dispatch_to_device(
    tool_name: str,
    params: dict[str, Any],
    device_id: str,
    session_id: str,
) -> dict[str, Any]:
    """Send a client-executor tool to `device_id` and await its result."""
    from ..sync.manager import manager

    if not device_id:
        return {"error": f"Tool '{tool_name}' is client-executor but no device_id was provided."}

    result = await manager.request(
        device_id,
        {
            "type": "tool_execute",
            "session_id": session_id,
            "tool": tool_name,
            "params": params,
        },
    )
    if result.get("status") == "ok":
        return {"result": result.get("result", {})}
    return {"error": result.get("error", "device execution failed")}


async def execute(name: str, params: dict[str, Any], **ctx: Any) -> dict[str, Any]:
    """Backward-compatible execute with optional gate context."""
    if ctx:
        return await run_tool(
            name,
            params,
            session_id=str(ctx.get("session_id", "")),
            device_id=str(ctx.get("device_id", "")),
            user_text=str(ctx.get("user_text", "")),
            explicit_confirm=bool(ctx.get("explicit_confirm", False)),
        )
    return await _execute_raw(name, params)


def list_tools() -> list[dict[str, Any]]:
    return list(REGISTRY.values())


def discover_plugins() -> None:
    """Re-export for main.py lifespan."""
    from .plugin_loader import discover_plugins as _discover

    _discover()


from .builtin_tools import register_builtin_tools  # noqa: E402 — after tool defs

register_builtin_tools()
