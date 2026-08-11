import json
from pathlib import Path
from typing import Any
from .board_io import utc_now, owner_norm

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / "docs" / "board"
FEEDBACK_JSONL = BOARD / "feedback.jsonl"
FEEDBACK_MD = BOARD / "FEEDBACK.md"

VALID_KINDS = ("claim", "done", "note", "ask", "block", "handoff")

def load_feedback(limit: int | None = None) -> list[dict[str, Any]]:
    if not FEEDBACK_JSONL.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in FEEDBACK_JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if limit is not None:
        return rows[-limit:]
    return rows


def post_feedback(
    *,
    from_owner: str,
    to_owner: str,
    kind: str,
    body: str,
    issue: str = "",
) -> dict[str, Any]:
    kind = kind.lower().strip()
    if kind not in VALID_KINDS:
        raise SystemExit(f"Invalid kind '{kind}'. Use one of: {', '.join(VALID_KINDS)}")
    event = {
        "ts": utc_now(),
        "from": owner_norm(from_owner) or "unknown",
        "to": owner_norm(to_owner) or "*",
        "kind": kind,
        "issue": (issue or "").upper(),
        "body": body.strip(),
    }
    FEEDBACK_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with FEEDBACK_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    render_feedback_md()
    return event


def feedback_for_owner(owner: str, limit: int = 15) -> list[dict[str, Any]]:
    me = owner_norm(owner)
    out: list[dict[str, Any]] = []
    for ev in reversed(load_feedback()):
        to = owner_norm(ev.get("to"))
        frm = owner_norm(ev.get("from"))
        if frm == me:
            continue
        if to in {me, "*", "all", "broadcast", ""}:
            out.append(ev)
        if len(out) >= limit:
            break
    return list(reversed(out))


def render_feedback_md() -> None:
    events = load_feedback(limit=40)
    lines = [
        "# Cross-agent feedback loop",
        "",
        "Shared channel between **Cursor** (`cursor`) and **Google Antigravity** (`antigravity`).",
        "",
        "Machine log: [`feedback.jsonl`](feedback.jsonl) (append-only).",
        "",
        "## Ritual",
        "",
        "```bash",
        "python scripts/devloop.py loop",
        "python scripts/devloop.py inbox --owner cursor",
        "python scripts/devloop.py inbox --owner antigravity",
        "python scripts/devloop.py say --from cursor --to antigravity --kind note -- \"message\"",
        "```",
        "",
        "Full protocol: [docs/dev/FEEDBACK_LOOP.md](../dev/FEEDBACK_LOOP.md)",
        "",
        "## Latest messages",
        "",
    ]
    if not events:
        lines.append("_No messages yet. Use `devloop say` or claim/done to post._")
        lines.append("")
    else:
        for ev in reversed(events):
            issue = ev.get("issue") or "-"
            lines.append(
                f"### {ev.get('ts')} | {ev.get('from')} → {ev.get('to')} | "
                f"`{ev.get('kind')}` | {issue}"
            )
            lines.append("")
            lines.append(ev.get("body") or "")
            lines.append("")
    FEEDBACK_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
