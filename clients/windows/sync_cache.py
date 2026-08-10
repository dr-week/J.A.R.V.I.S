"""Jarvis Windows client — local memory sync cache (ISSUE-022).

Maintains a small on-disk mirror of the brain's memories so that a memory
written on another device (and pushed over the brain WebSocket) is visible
here in near-real-time. This is an edge cache: the brain remains the source
of truth; this file only mirrors what the brain broadcasts.

The file is human-readable JSON so a user or agent can inspect what the client
currently knows. It is best-effort — if the file can't be written, the client
keeps running (sync is non-fatal).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_CACHE_PATH = Path(
    os.environ.get(
        "JARVIS_SYNC_CACHE",
        str(Path.home() / ".jarvis" / "windows_sync_cache.json"),
    )
)


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save(path: Path, data: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except Exception:
        # Non-fatal: sync cache is best-effort.
        return


def apply_push(key: str, value: str, path: Path | None = None) -> bool:
    """Apply a brain `push_memory` message to the local cache.

    A value of `""` (empty string) means the memory was deleted on the brain,
    so it is removed locally. Returns True if the cache changed.
    """
    p = path or DEFAULT_CACHE_PATH
    data = _load(p)
    if value == "":
        if key in data:
            del data[key]
            _save(p, data)
            return True
        return False
    data[key] = value
    _save(p, data)
    return True


def list_cached(path: Path | None = None) -> dict[str, Any]:
    """Return the current local memory mirror."""
    return _load(path or DEFAULT_CACHE_PATH)
