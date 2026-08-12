#!/usr/bin/env python3
"""Verify issue ## Lane paths exist under repo root (read-only)."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ISSUES = ROOT / "docs" / "board" / "issues"
LANE_HEADING = re.compile(r"^##\s+Lane\s*$", re.MULTILINE)
BACKTICK_PATH = re.compile(r"`([^`]+)`")


def parse_lane_paths(issue_text: str) -> list[str]:
    """Return glob-ish paths from ## Lane section bullet list."""
    match = LANE_HEADING.search(issue_text)
    if not match:
        return []
    rest = issue_text[match.end() :]
    next_h2 = re.search(r"\n##\s+", rest)
    section = rest[: next_h2.start()] if next_h2 else rest
    paths: list[str] = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        for raw in BACKTICK_PATH.findall(line):
            p = raw.strip()
            if p and not p.startswith("http"):
                paths.append(p)
    return paths


def verify_lane_path(pattern: str) -> tuple[bool, str]:
    """Check one lane entry (file or glob with **)."""
    clean = pattern.replace("\\", "/").lstrip("/")
    if "**" in clean:
        prefix = clean.split("**", 1)[0].rstrip("/")
        base = ROOT / prefix
        if not base.exists():
            return False, f"missing directory: {prefix}"
        if base.is_file():
            return True, f"ok file: {prefix}"
        any_file = any(base.rglob("*"))
        if not any_file:
            return False, f"no files under: {prefix}"
        return True, f"ok under: {prefix}"
    path = ROOT / clean
    if path.exists():
        return True, f"ok: {clean}"
    return False, f"missing: {clean}"


def is_file_in_lane(changed_file: str, lanes: list[str]) -> bool:
    """Return True if changed_file matches any pattern in lanes."""
    for pattern in lanes:
        clean = pattern.replace("\\", "/").lstrip("/")
        if "**" in clean:
            prefix = clean.split("**", 1)[0].rstrip("/")
            if prefix == "" or changed_file == prefix or changed_file.startswith(prefix + "/"):
                return True
        else:
            if changed_file == clean:
                return True
    return False


def verify_issue(issue_id: str, check_diff: bool = False) -> tuple[int, list[str]]:
    path = ISSUES / f"{issue_id}.md"
    if not path.exists():
        return 1, [f"issue file not found: {path}"]
    text = path.read_text(encoding="utf-8")
    lanes = parse_lane_paths(text)
    if not lanes:
        return 1, ["no ## Lane paths found (add `- \\`path\\`` bullets)"]
    lines: list[str] = []
    fails = 0
    for pattern in lanes:
        ok, msg = verify_lane_path(pattern)
        lines.append(("OK " if ok else "FAIL ") + msg)
        if not ok:
            fails += 1
            
    if check_diff and fails == 0:
        diff_fails = 0
        try:
            # Check staged and unstaged changes
            result = subprocess.run(
                ["git", "diff", "HEAD", "--name-only"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False
            )
            changed_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
            
            for changed_file in changed_files:
                if not is_file_in_lane(changed_file, lanes):
                    lines.append(f"FAIL diff out of lane: {changed_file}")
                    diff_fails += 1
                    
            if diff_fails > 0:
                fails += diff_fails
                lines.append(f"Blocked: {diff_fails} changed files fall outside the defined Lane.")
            else:
                lines.append(f"OK diff matches lane bounds ({len(changed_files)} files).")
                
        except Exception as e:
            lines.append(f"FAIL git diff check failed: {e}")
            fails += 1
            
    return fails, lines


# --- Tests ---

def test_parse_lane_paths():
    text = """
Some text
## Lane
- `scripts/helpers/issue_lane_verify.py`
- `tests/**`
- `http://example.com`
"""
    assert parse_lane_paths(text) == ["scripts/helpers/issue_lane_verify.py", "tests/**"]
    assert parse_lane_paths("No lane here") == []

def test_is_file_in_lane():
    lanes = ["scripts/helpers/issue_lane_verify.py", "tests/**"]
    
    assert is_file_in_lane("scripts/helpers/issue_lane_verify.py", lanes) is True
    assert is_file_in_lane("scripts/helpers/other.py", lanes) is False
    
    assert is_file_in_lane("tests/foo.py", lanes) is True
    assert is_file_in_lane("tests/nested/bar.py", lanes) is True
    assert is_file_in_lane("tests2/foo.py", lanes) is False
    
    lanes_all = ["**"]
    assert is_file_in_lane("anything.py", lanes_all) is True
    assert is_file_in_lane("foo/bar.py", lanes_all) is True
