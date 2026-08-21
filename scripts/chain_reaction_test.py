#!/usr/bin/env python3
"""
Chain Reaction Verification Script (Zero Dependencies)
Checks doc links, web frontend build artifact, and devloop sync state in a single chain.
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run_step(name: str, cmd: list[str], cwd: Path) -> bool:
    print(f"\n[CHAIN REACTION] Running Step: {name}...")
    try:
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        print(f"[OK] {name} PASSED")
        if res.stdout.strip():
            print(f"   Output summary: {res.stdout.strip().splitlines()[0]}")
        return True
    except subprocess.CalledProcessError as exc:
        print(f"[FAIL] {name} FAILED (Exit Code {exc.returncode})")
        if exc.stdout:
            print(f"   stdout: {exc.stdout}")
        if exc.stderr:
            print(f"   stderr: {exc.stderr}")
        return False
    except Exception as exc:
        print(f"[ERROR] {name} ERROR ({exc})")
        return False

def main() -> int:
    print("=" * 60)
    print("      JARVIS CHAIN REACTION SYSTEM INTEGRITY CHECK      ")
    print("=" * 60)

    # Step 1: Verify Doc Relative Links
    s1 = run_step(
        "1. Doc Relative Links Audit",
        [sys.executable, str(ROOT / "scripts" / "verify_doc_links.py")],
        ROOT
    )

    # Step 2: Devloop Board Synchronization
    s2 = run_step(
        "2. Devloop Board Synchronization",
        [sys.executable, str(ROOT / "scripts" / "devloop.py"), "sync"],
        ROOT
    )

    # Step 3: Web Frontend Bundle Verification
    web_dir = ROOT / "clients" / "web"
    s3 = False
    if (web_dir / "package.json").exists():
        s3 = run_step(
            "3. Web Presence Bundle Verification",
            ["cmd", "/c", "npm run build"],
            web_dir
        )

    # Step 4: AI Fine-Tuning Dataset Export
    s4 = run_step(
        "4. AI Fine-Tuning Dataset Export",
        [sys.executable, str(ROOT / "scripts" / "export_training_data.py")],
        ROOT
    )

    all_passed = s1 and s2 and s3 and s4
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] CHAIN REACTION SUCCESSFUL: ALL INTEGRITY CHECKS PASSED!")
        print("=" * 60)
        return 0
    else:
        print("[FAIL] CHAIN REACTION FAILED: CHECK ERRORS ABOVE.")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
