#!/usr/bin/env python3
"""Verify relative markdown links in the key docs files.

Checks README.md, AGENTS.md, and every docs/dev/*.md from the repo root.
Exits 0 when all relative links resolve; prints broken paths and exits 1
otherwise. External (http/https/mailto) and anchor-only (#frag) links are
skipped, as are links that resolve into the gitignored .blackbox/ mirror.

Run from the repo root:
    python scripts/verify_doc_links.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Files to check, relative to the repo root.
PLAN_CLUSTER = [
    "docs/DESIGN.md",
    "docs/dev/SYNC_PLAN.md",
    "docs/dev/PRESENCE_STACKS.md",
    "docs/dev/PLAN_AUDIT.md",
    "docs/dev/STRATEGY_FORWARD.md",
    "docs/dev/OSS_DEV_PLAN.md",
    "docs/dev/OSS_ARSENAL.md",
    "docs/dev/LAB_STACK.md",
    "docs/dev/STARK_TIMELINE.md",
    "docs/dev/VENTURE_EARN_PLAN.md",
    "docs/dev/POLYGLOT_TOOLS.md",
    "docs/dev/DEV_ENV.md",
]
TARGET_FILES = list(
    dict.fromkeys(
        [
            "README.md",
            "AGENTS.md",
            *PLAN_CLUSTER,
            *sorted(
                str(p.relative_to(ROOT)) for p in (ROOT / "docs" / "dev").glob("*.md")
            ),
        ]
    )
)

# A markdown link: [text](url). The `!?` also matches image links, which are
# still resolved (a missing image is a real broken link too).
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")


def is_external(url: str) -> bool:
    return url.startswith(
        ("http://", "https://", "mailto:", "tel:", "//")
    )


def is_anchor(url: str) -> bool:
    return url == "" or url.startswith("#")


def is_ignored_mirror(resolved: Path) -> bool:
    """Links resolving into the gitignored .blackbox/ mirror are expected to
    be absent in a fresh clone and are not treated as broken."""
    return ".blackbox" in resolved.parts


def check_file(path: Path) -> list[str]:
    """Return a list of broken-link descriptions for one markdown file."""
    broken: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path}: cannot read ({exc})"]
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in LINK_RE.finditer(line):
            url = m.group(1)
            if is_external(url) or is_anchor(url):
                continue
            target = url.split("#", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if is_ignored_mirror(resolved):
                continue
            if not resolved.exists():
                rel = _safe_rel(resolved)
                broken.append(f"{_safe_rel(path)}:{lineno}: '{url}' -> {rel}")
    return broken


def _safe_rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def main() -> int:
    broken: list[str] = []
    for rel in TARGET_FILES:
        path = ROOT / rel
        if not path.exists():
            broken.append(f"{rel}: file not found")
            continue
        broken.extend(check_file(path))

    if broken:
        print(f"BROKEN LINKS ({len(broken)}):")
        for b in broken:
            print(f"  - {b}")
        print("\nFix the paths above, then re-run:")
        print("  python scripts/verify_doc_links.py")
        return 1

    print(f"OK — checked {len(TARGET_FILES)} files; all relative links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
