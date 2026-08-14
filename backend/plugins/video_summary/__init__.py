"""Video Summarization plugin — yt-dlp CLI subprocess wrapper.

Self-registers when ``discover_plugins`` scans this package.
Pattern 2: CLI Subprocess per docs/OSS.md
"""
from __future__ import annotations

import json
import subprocess
from typing import Any

from backend.app.hands import registry


def _video_summarize(url: str) -> dict[str, Any]:
    """Extract video metadata and information for summarization using yt-dlp CLI."""
    if not url:
        return {"error": "Missing required 'url' parameter."}

    try:
        cmd = ["yt-dlp", "--dump-json", "--skip-download", url]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(res.stdout) if res.stdout else {}
        return {
            "title": info.get("title", ""),
            "description": (info.get("description") or "")[:1000],
            "uploader": info.get("uploader", ""),
            "duration": info.get("duration", 0),
            "url": url,
        }
    except Exception as exc:
        return {"error": f"yt-dlp execution failed: {exc}. Ensure yt-dlp is installed."}


if "video_summarize" not in registry.REGISTRY:
    registry.register(
        {
            "name": "video_summarize",
            "description": "Extract video metadata and info for summarization using yt-dlp CLI.",
            "version": "1.0.0",
            "phase": 6,
            "risk_level": "auto",
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
            "returns": {"type": "object", "properties": {"title": {"type": "string"}}},
            "scopes": ["video:read"],
            "tags": ["video", "youtube", "media"],
        },
        _video_summarize,
    )
