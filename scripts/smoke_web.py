#!/usr/bin/env python3
"""HTTP smoke for brain + sessions — run from repo root with brain on :8787.

Usage:
  python scripts/smoke_web.py
  python scripts/smoke_web.py --base http://127.0.0.1:8787
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = os.environ.get("JARVIS_BRAIN_URL", "http://127.0.0.1:8787").rstrip("/")


def _get(url: str, headers: dict[str, str] | None = None) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="Jarvis brain HTTP smoke")
    parser.add_argument("--base", default=DEFAULT_BASE, help="Brain base URL")
    parser.add_argument("--pair", action="store_true", help="POST /pair if JARVIS_PAIR_SECRET set")
    args = parser.parse_args()
    base = args.base.rstrip("/")
    fails = 0

    status, body = _get(f"{base}/health")
    if status != 200:
        print(f"FAIL health HTTP {status}")
        fails += 1
    else:
        print("OK  GET /health")
        try:
            data = json.loads(body)
            if "status" not in data and "ok" not in str(data).lower():
                print("WARN health JSON unexpected keys")
        except json.JSONDecodeError:
            print("WARN health response not JSON")

    status, body = _get(f"{base}/sessions?limit=5")
    if status != 200:
        print(f"FAIL sessions HTTP {status}")
        fails += 1
    else:
        print("OK  GET /sessions")
        try:
            payload = json.loads(body)
            if "sessions" not in payload:
                print("WARN sessions missing 'sessions' key")
        except json.JSONDecodeError:
            print("FAIL sessions not JSON")
            fails += 1

    secret = os.environ.get("JARVIS_PAIR_SECRET", "").strip()
    if args.pair and secret:
        req = urllib.request.Request(
            f"{base}/pair",
            data=json.dumps({"device_id": "smoke-web", "secret": secret}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    print("OK  POST /pair")
                else:
                    print(f"FAIL pair HTTP {resp.status}")
                    fails += 1
        except urllib.error.HTTPError as exc:
            print(f"FAIL pair HTTP {exc.code}")
            fails += 1
    elif args.pair:
        print("SKIP pair (set JARVIS_PAIR_SECRET)")

    print()
    if fails:
        print(f"smoke_web: {fails} failure(s) — is brain running? python scripts/run_brain.py")
        return 1
    print("smoke_web: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
