"""Offline verification for the ISSUE-042 GitHub connector."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["JARVIS_GITHUB_TOKEN"] = "test-token-kept-on-brain"


class _Response:
    def raise_for_status(self) -> None:
        return None

    def json(self):
        return [
            {"number": 7, "title": "An issue", "state": "open", "html_url": "https://github.com/acme/jarvis/issues/7", "updated_at": "2030-01-01T00:00:00Z"},
            {"number": 8, "title": "A pull request", "state": "open", "html_url": "https://github.com/acme/jarvis/pull/8", "updated_at": "2030-01-01T00:00:00Z", "pull_request": {}},
        ]


async def main() -> None:
    from backend.app.hands import registry
    import backend.plugins.github as github

    captured: dict = {}

    def fake_get(url, *, headers, params, timeout):
        captured.update(url=url, headers=headers, params=params, timeout=timeout)
        return _Response()

    github.httpx.get = fake_get
    result = await registry.execute("github_issues_list", {"repo": "acme/jarvis"})
    assert result["result"]["count"] == 1
    assert result["result"]["issues"][0]["number"] == 7
    assert captured["headers"]["Authorization"] == "Bearer test-token-kept-on-brain"
    assert "test-token-kept-on-brain" not in str(result)
    print("github connector smoke test: OK")


asyncio.run(main())
