"""Lightweight smoke test (no Flet window — avoids orphaned flet.exe)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    import client  # noqa: F401
    import instance_lock  # noqa: F401
    import ui_gui

    for name in ("mount_jarvis_desktop", "launch_flet_desktop"):
        if not hasattr(ui_gui, name):
            print(f"SMOKE_FAIL: missing ui_gui.{name}")
            return 1
    instance_lock.acquire_gui_instance()
    instance_lock.release_gui_instance()
    print("SMOKE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
