#!/usr/bin/env python3
"""Always-on launcher for the Jarvis Brain (home hub / always-on host).

Unlike `uvicorn --reload` (which is fine for local dev), this script starts the
brain in a production-oriented way:

  * reads HOST / PORT from `backend/app/config.py` (env or .env)
  * binds 0.0.0.0 by default so phones/other clients on the LAN can reach it
  * never uses --reload (survives reboots cleanly under a service manager)
  * prints the LAN health-check URL so you know where to point your phone

Run from the repo root:

    python scripts/run_brain.py

Install behind your OS service manager for reboot survival — see
docs/HOME_HUB.md for systemd (Linux) / Task Scheduler (Windows) examples.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make `backend.app` importable when run straight from the repo root.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _approximate_ip() -> str:
    """Best-effort LAN IP for the health-check hint (no external deps)."""
    import socket

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        # UDP connect does not send packets; it just picks a route.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "<your-hub-ip>"


def main() -> int:
    import uvicorn
    from backend.app import config

    host = config.HOST
    port = config.PORT

    print("=" * 50)
    print("  Jarvis Brain — always-on launcher")
    print(f"  Binding: {host}:{port}")
    print(f"  LAN health check: http://{'' if host != '0.0.0.0' else _approximate_ip()}:{port}/health")
    print("  (shown from repo root; run: python scripts/run_brain.py)")
    print("  Install behind a service manager for reboot survival — docs/HOME_HUB.md")
    print("=" * 50)

    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        log_level="info",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

