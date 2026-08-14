"""Chain the fast backend quality gates in one command for agents and CI."""

from __future__ import annotations

import subprocess
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(label: str, args: list[str]) -> None:
    print(f"[backend] {label}")
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="run the complete backend test suite")
    args = parser.parse_args()
    run("OSS consistency", [sys.executable, "scripts/check_backend_oss.py"])
    run("compile", [sys.executable, "-m", "compileall", "-q", "backend", "scripts"])
    run(
        "focused tests",
        [sys.executable, "-m", "pytest", *(["backend/tests"] if args.full else ["backend/tests/test_backend_oss_adapters.py", "backend/tests/test_telemetry.py", "backend/tests/test_metrics.py", "backend/tests/test_database.py", "backend/tests/test_health.py"]), "-q"],
    )
    print("[backend] verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
