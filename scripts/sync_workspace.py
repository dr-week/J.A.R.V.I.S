#!/usr/bin/env python3
"""One-shot: refresh board, feedback, LIVE_PLAN, and optional LIVE_BRIEF."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEVLOOP = ROOT / "scripts" / "devloop.py"


def main() -> None:
    owner = None
    if len(sys.argv) > 1:
        owner = sys.argv[1]
    cmd = [sys.executable, str(DEVLOOP), "sync"]
    if owner:
        cmd.extend(["--owner", owner])
    raise SystemExit(subprocess.call(cmd, cwd=ROOT))


if __name__ == "__main__":
    main()
