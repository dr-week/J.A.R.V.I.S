"""File Manager plugin — CLI-based fast file search wrapper.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import os
import subprocess
from typing import Any
from backend.app.hands import registry


def _file_search(query: str, root_dir: str = ".") -> dict[str, Any]:
    """Fast file search using system find / fd CLI."""
    try:
        if os.name == "nt":
            cmd = ["where", "/r", root_dir, f"*{query}*"]
        else:
            cmd = ["find", root_dir, "-name", f"*{query}*"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        matches = [line.strip() for line in res.stdout.splitlines() if line.strip()][:20]
        return {"count": len(matches), "files": matches}
    except Exception as exc:
        return {"error": str(exc)}


registry.register(
    {
        "name": "file_search",
        "description": "Fast system file search by keyword/pattern.",
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "auto",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "root_dir": {"type": "string"},
            },
            "required": ["query"],
        },
        "returns": {"type": "object", "properties": {"count": {"type": "integer"}, "files": {"type": "array"}}},
        "scopes": ["files:read"],
        "tags": ["files", "search"],
    },
    _file_search,
)
