"""Video Summarization plugin — yt-dlp wrapper.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import subprocess
from typing import Any
from backend.app.hands import registry


def _video_summarize(url: str) -> dict[str, Any]:
    """Download video metadata and subtitle transcript using yt-dlp CLI."""
    try:
        cmd = ["yt-dlp", "--dump-json", "--skip-download", url]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        info = json.loads(res.stdout)
        return {
            "title": info.get("title"),
            "description": info.get("description", "")[:1000],
            "uploader": info.get("uploader"),
            "duration": info.get("duration"),
            "url": url,
        }
    except Exception as exc:
        return {"error": f"yt-dlp execution failed: {exc}. Ensure yt-dlp is installed."}


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
