"""Small shared HTTP policy for outbound OSS sidecars and APIs."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

T = TypeVar("T")


@retry(
    retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError)),
    wait=wait_exponential(multiplier=0.2, min=0.2, max=2),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def request_json(operation: Callable[[], Awaitable[httpx.Response]]) -> T:
    """Run an idempotent request with bounded retries and HTTP error checking."""
    response = await operation()
    response.raise_for_status()
    return response.json()


__all__ = ["request_json"]
