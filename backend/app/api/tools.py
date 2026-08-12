from __future__ import annotations

import typing

"""API — /tools endpoints."""
from fastapi import APIRouter

from ..hands.registry import list_tools

router = APIRouter(prefix="/tools")


@router.get("")
async def get_tools() -> typing.Any:
    return {"tools": list_tools(), "count": len(list_tools())}
