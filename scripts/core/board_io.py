import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / "docs" / "board"
ISSUES = BOARD / "issues"

STATUS_ORDER = {"now": 0, "backlog": 1, "todo": 1, "blocked": 2, "done": 3}
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}
MAX_PARALLEL = 2  # designed for 2 people / 2 AIs at once

def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, Any] = {}
    body = parts[2].lstrip("\n")
    lines = parts[1].strip("\n").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if raw == "" and i + 1 < len(lines) and lines[i + 1].startswith("  -"):
            items: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith("-"):
                items.append(lines[i].strip()[1:].strip().strip('"'))
                i += 1
            meta[key] = items
            continue
        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            meta[key] = (
                [x.strip().strip('"') for x in inner.split(",") if x.strip()] if inner else []
            )
        else:
            meta[key] = raw.strip('"')
        i += 1
    return meta, body


def dump_frontmatter(meta: dict[str, Any]) -> str:
    order = [
        "id",
        "title",
        "status",
        "priority",
        "phase",
        "labels",
        "owner",
        "claimed_at",
        "blocked_by",
        "acceptance",
    ]
    lines = ["---"]
    keys = [k for k in order if k in meta] + [k for k in meta if k not in order]
    for key in keys:
        val = meta[key]
        if isinstance(val, list):
            if key in {"acceptance"} or (val and not all(len(str(x)) < 40 for x in val)):
                lines.append(f"{key}:")
                for item in val:
                    lines.append(f"  - {item}")
            else:
                inner = ", ".join(str(x) for x in val)
                lines.append(f"{key}: [{inner}]")
        else:
            lines.append(f"{key}: {val}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def issue_path(issue_id: str) -> Path:
    return ISSUES / f"{issue_id.upper()}.md"


def load_issue(issue_id: str) -> tuple[dict[str, Any], str, Path]:
    path = issue_path(issue_id)
    if not path.exists():
        raise SystemExit(f"Issue not found: {path}")
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    return meta, body, path


def save_issue(meta: dict[str, Any], body: str, path: Path) -> None:
    path.write_text(dump_frontmatter(meta) + "\n" + body.lstrip("\n"), encoding="utf-8")


def list_issues() -> list[tuple[dict[str, Any], Path]]:
    if not ISSUES.exists():
        return []
    out: list[tuple[dict[str, Any], Path]] = []
    for path in sorted(ISSUES.glob("ISSUE-*.md")):
        meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        if meta:
            out.append((meta, path))
    return out


def sort_key(meta: dict[str, Any]) -> tuple:
    return (
        STATUS_ORDER.get(str(meta.get("status", "backlog")), 9),
        PRIORITY_ORDER.get(str(meta.get("priority", "P2")), 9),
        str(meta.get("id", "")),
    )


def sort_pair(item: tuple[dict[str, Any], Path]) -> tuple:
    return sort_key(item[0])


def is_unblocked(meta: dict[str, Any], done_ids: set[str]) -> bool:
    blocked = meta.get("blocked_by") or []
    if isinstance(blocked, str):
        blocked = [blocked] if blocked else []
    return all(str(b) in done_ids or str(b) == "" for b in blocked)


def open_issues(include_blocked: bool = False) -> list[tuple[dict[str, Any], Path]]:
    done_ids = {str(m.get("id")) for m, _ in list_issues() if m.get("status") == "done"}
    items = []
    for m, p in list_issues():
        if str(m.get("status")) == "done":
            continue
        if str(m.get("status")) == "blocked" and not include_blocked:
            continue
        if not include_blocked and not is_unblocked(m, done_ids):
            continue
        items.append((m, p))
    return sorted(items, key=sort_pair)


def owner_norm(value: Any) -> str:
    return str(value or "").strip().lower()


def append_note(body: str, note: str) -> str:
    if "## Notes" in body:
        return body.replace("## Notes", "## Notes\n" + note, 1)
    return body + "\n## Notes\n" + note


def unchecked_task_lines(body: str) -> list[str]:
    """Markdown `- [ ]` lines in the issue body (Work / Acceptance sections)."""
    return [
        line.strip()
        for line in body.splitlines()
        if re.match(r"^-\s*\[\s\]", line.strip())
    ]
