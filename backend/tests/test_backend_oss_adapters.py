import httpx
import pytest

from backend.plugins.http_resilience import request_json
from backend.plugins.scheduler import build_scheduler


@pytest.mark.asyncio
async def test_http_policy_retries_transient_connect_errors():
    calls = 0

    async def operation():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise httpx.ConnectError("temporary")
        return httpx.Response(200, json={"ok": True}, request=httpx.Request("GET", "http://test"))

    assert await request_json(operation) == {"ok": True}
    assert calls == 3


def test_scheduler_dependency_is_optional():
    try:
        scheduler = build_scheduler()
    except RuntimeError as exc:
        assert "scheduler" in str(exc)
    else:
        scheduler.shutdown(wait=False)
