#!/usr/bin/env python3
"""Quick dev environment check — run from repo root before coding.

Exits 0 when core requirements pass; prints fixes for failures.
"""
from __future__ import annotations

import importlib.util
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _ok(msg: str) -> None:
    print(f"  OK  {msg}")


def _warn(msg: str) -> None:
    print(f"  WARN {msg}")


def _fail(msg: str) -> None:
    print(f"  FAIL {msg}")


def port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def main() -> int:
    print(f"Jarvis dev check — {ROOT}")
    fails = 0

    _ok(f"Python {sys.version.split()[0]}")

    env_file = ROOT / ".env"
    if env_file.exists():
        _ok(".env present")
    else:
        _warn(".env missing — copy .env.example and set keys")

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        spec = importlib.util.find_spec("backend.app.main")
        if spec is None:
            raise ImportError("backend.app.main not found")
        _ok("backend.app.main importable from repo root")
    except Exception as exc:
        _fail(f"brain import: {exc} — run from repo root; pip install -r backend/requirements.txt")
        fails += 1

    if port_open("127.0.0.1", 8787):
        _ok("brain port 8787 listening")
    else:
        _warn("brain not on :8787 — run: python scripts/run_brain.py")

    node = shutil_which("node")
    if node:
        _ok("node on PATH")
    else:
        _warn("node not found — needed for clients/web")

    flutter = shutil_which("flutter")
    if flutter:
        _ok("flutter on PATH (Field lane)")
    else:
        _warn("flutter not on PATH — optional unless doing ISSUE-101")

    print()
    if fails:
        print(f"{fails} hard failure(s). Fix before backend work.")
        return 1
    print("Ready for dev (warnings are OK).")
    return 0


def shutil_which(cmd: str) -> str | None:
    import shutil

    return shutil.which(cmd)


if __name__ == "__main__":
    sys.exit(main())
