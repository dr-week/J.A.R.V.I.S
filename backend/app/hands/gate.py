"""Hands — confirmation gate before tool execution."""
from __future__ import annotations

import json
import re
from typing import Any

from ..soul.memory import get_config, log_action, set_config

RISK_AUTO = "auto"
RISK_CONFIRM_ONCE = "confirm_once"
RISK_CONFIRM_ALWAYS = "confirm_always"

SENSITIVE_KEY_RE = re.compile(
    r"(password|secret|token|api[_-]?key|authorization|credential)",
    re.I,
)

CONFIRM_PHRASES = (
    "confirm",
    "yes, confirm",
    "yes confirm",
    "go ahead",
    "approved",
    "do it",
)


def redact_parameters(params: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, val in params.items():
        if SENSITIVE_KEY_RE.search(str(key)):
            out[key] = "***REDACTED***"
        elif isinstance(val, dict):
            out[key] = redact_parameters(val)
        else:
            out[key] = val
    return out


def user_confirmed(text: str) -> bool:
    t = text.strip().lower()
    return t in CONFIRM_PHRASES or t.startswith("confirm ")


def _allowlist_key(device_id: str, tool_name: str) -> str:
    return f"tool_allowlist:{device_id or 'default'}:{tool_name}"


def is_allowlisted(device_id: str, tool_name: str) -> bool:
    return get_config(_allowlist_key(device_id, tool_name), "0") == "1"


def allowlist_tool(device_id: str, tool_name: str) -> None:
    set_config(_allowlist_key(device_id, tool_name), "1")


def _pending_key(session_id: str) -> str:
    return f"pending_tool:{session_id}"


def get_pending_confirmation(session_id: str) -> dict[str, Any] | None:
    raw = get_config(_pending_key(session_id), "")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def set_pending_confirmation(session_id: str, tool_name: str, params: dict[str, Any]) -> None:
    set_config(
        _pending_key(session_id),
        json.dumps({"tool_name": tool_name, "parameters": params}),
    )


def clear_pending_confirmation(session_id: str) -> None:
    set_config(_pending_key(session_id), "")


def needs_confirmation(tool_def: dict[str, Any], device_id: str) -> bool:
    risk = tool_def.get("risk_level", RISK_AUTO)
    name = tool_def.get("name", "")
    if risk == RISK_AUTO:
        return False
    if risk == RISK_CONFIRM_ALWAYS:
        return True
    if risk == RISK_CONFIRM_ONCE:
        return not is_allowlisted(device_id, name)
    return True


def check_and_prepare(
    tool_def: dict[str, Any],
    tool_name: str,
    params: dict[str, Any],
    *,
    session_id: str,
    device_id: str,
    explicit_confirm: bool,
    user_text: str,
) -> tuple[bool, str | None]:
    """Return (may_execute, block_reason)."""
    if not needs_confirmation(tool_def, device_id):
        return True, None

    confirmed = explicit_confirm or user_confirmed(user_text)
    if confirmed:
        return True, None

    set_pending_confirmation(session_id, tool_name, params)
    risk = tool_def.get("risk_level", RISK_AUTO)
    log_action(
        tool_name,
        redact_parameters(params),
        result_summary="blocked: awaiting user confirmation",
        device_id=device_id,
        confirmed_by="pending",
    )
    return False, (
        f"Tool '{tool_name}' requires confirmation (risk={risk}). "
        f"Reply with 'confirm' to run it, or enable confirm in the client."
    )
