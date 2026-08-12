from __future__ import annotations

import typing

"""API — /hands/* audit and tool safety.

Read-only audit endpoints for Hands debugging.

Secrets policy (see docs/dev/DEFINITION_OF_DONE.md): these endpoints only
REPORT history — nothing here deletes or mutates. Sensitive parameter keys
(api_key, token, password, ...) are redacted before being returned, using
the same rules as the confirmation gate (backend/app/hands/gate.py).
"""
from fastapi import APIRouter

from ..hands.gate import redact_parameters
from ..hands.registry import list_tools
from ..soul.memory import list_action_log

router = APIRouter(prefix="/hands")


@router.get("/actions")
async def get_action_log(limit: int = 20) -> typing.Any:
    """Return the last `limit` action_log rows, newest first (default 20).

    Read-only: fetch history only. Parameters are redacted with the same
    sensitive-key rules as the confirmation gate, so secrets never leak
    through the API.
    """
    rows = list_action_log(limit=min(limit, 200))
    for row in rows:
        row["parameters"] = redact_parameters(row.get("parameters", {}))
    return {"actions": rows, "count": len(rows)}


@router.get("/tools")
async def get_hands_tools() -> typing.Any:
    return {"tools": list_tools(), "count": len(list_tools())}
