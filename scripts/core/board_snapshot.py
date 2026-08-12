from pathlib import Path
from typing import Any

from board_context import (
    LIVE_PLAN,
    build_snapshot,
    render_live_plan,
    snapshot_fingerprint,
)

from .board_io import (
    BOARD,
    MAX_PARALLEL,
    ROOT,
    list_issues,
    open_issues,
    owner_norm,
    sort_pair,
)


def pick_for_owner(owner: str | None) -> tuple[dict[str, Any], Path] | None:
    """Pick issue for a worker: their NOW first, else first unclaimed backlog."""
    opens = open_issues()
    if not opens:
        return None
    if not owner:
        now = [x for x in opens if x[0].get("status") == "now"]
        return (now or opens)[0]

    mine = [
        x
        for x in opens
        if x[0].get("status") == "now" and owner_norm(x[0].get("owner")) == owner_norm(owner)
    ]
    if mine:
        return mine[0]

    for m, p in opens:
        if m.get("status") == "now":
            # Skip other workers' active claims
            if owner_norm(m.get("owner")) and owner_norm(m.get("owner")) != owner_norm(owner):
                continue
        if m.get("status") in {"backlog", "todo"}:
            return m, p
        if m.get("status") == "now" and owner_norm(m.get("owner")) in {"", owner_norm(owner)}:
            return m, p
    return None


def rebuild_board() -> None:
    items = list_issues()
    now = [(m, p) for m, p in items if m.get("status") == "now"]
    done = [(m, p) for m, p in items if m.get("status") == "done"]
    open_ = open_issues(include_blocked=True)
    open_ = [(m, p) for m, p in open_ if m.get("status") != "done"]

    now_lines = [
        "# NOW",
        "",
        f"Active focus — **max {MAX_PARALLEL} parallel workers** (people or AIs).",
        "See [docs/dev/PARALLEL.md](../dev/PARALLEL.md).",
        "",
        "| ID | Title | Phase | Priority | Owner |",
        "|----|-------|-------|----------|-------|",
    ]
    if not now:
        now_lines.append("| — | _(none claimed)_ | — | — | — |")
    else:
        for m, _ in sorted(now, key=sort_pair):
            now_lines.append(
                f"| [{m.get('id')}](issues/{m.get('id')}.md) | {m.get('title')} | "
                f"{m.get('phase')} | {m.get('priority')} | {m.get('owner') or '—'} |"
            )
    now_lines.append("")
    now_lines.append("Generated plan: [LIVE_PLAN.md](LIVE_PLAN.md) (`devloop sync`).")
    now_lines.append("")
    (BOARD / "NOW.md").write_text("\n".join(now_lines) + "\n", encoding="utf-8")

    actionable = open_issues()
    next_candidates = [m for m, _ in actionable if m.get("status") in {"now", "backlog", "todo"}][:12]
    next_lines = [
        "# NEXT",
        "",
        "Refreshed by `python scripts/devloop.py refresh`.",
        "Two workers: use `next --owner YOU` so you skip the other's claim.",
        "",
    ]
    for i, m in enumerate(next_candidates, 1):
        own = m.get("owner") or "—"
        next_lines.append(
            f"{i}. **{m.get('id')}** (phase {m.get('phase')}, {m.get('priority')}, "
            f"owner={own}) — {m.get('title')}"
        )
    next_lines.append("")
    (BOARD / "NEXT.md").write_text("\n".join(next_lines) + "\n", encoding="utf-8")

    backlog_lines = [
        "# BACKLOG",
        "",
        "Open work ranked by status then priority. Source: issue frontmatter.",
        "",
        "| ID | Title | Phase | Priority | Status | Owner |",
        "|----|-------|-------|----------|--------|-------|",
    ]
    for m, _ in sorted(
        [(m, p) for m, p in items if m.get("status") != "done"],
        key=sort_pair,
    ):
        backlog_lines.append(
            f"| {m.get('id')} | {m.get('title')} | {m.get('phase')} | "
            f"{m.get('priority')} | {m.get('status')} | {m.get('owner') or '—'} |"
        )
    backlog_lines.append("")
    (BOARD / "BACKLOG.md").write_text("\n".join(backlog_lines) + "\n", encoding="utf-8")

    done_lines = ["# DONE", "", "Completed issues (newest first).", ""]
    if not done:
        done_lines.append("_None yet._")
    else:
        for m, _ in sorted(done, key=lambda x: str(x[0].get("id")), reverse=True):
            done_lines.append(f"- [{m.get('id')}](issues/{m.get('id')}.md) — {m.get('title')}")
    done_lines.append("")
    (BOARD / "DONE.md").write_text("\n".join(done_lines) + "\n", encoding="utf-8")


def make_snapshot() -> dict[str, Any]:
    issues = list_issues()
    now_items = [m for m, _ in issues if m.get("status") == "now"]
    return build_snapshot(
        issues=issues,
        open_issues=open_issues(),
        now_items=now_items,
        pick_for_owner_fn=pick_for_owner,
    )


def write_live_plan_file() -> dict[str, Any]:
    snap = make_snapshot()
    snap["fingerprint"] = snapshot_fingerprint(snap)
    LIVE_PLAN.parent.mkdir(parents=True, exist_ok=True)
    LIVE_PLAN.write_text(render_live_plan(snap), encoding="utf-8")
    return snap


def refresh_code_map() -> None:
    """Regenerate the lightweight repo index and code map if available."""
    try:
        from index_repo import DEFAULT_DB, render_map, write_index
    except Exception:
        return

    entries = write_index(DEFAULT_DB)
    CODE_MAP = ROOT / "docs" / "CODE_MAP.md"
    CODE_MAP.parent.mkdir(parents=True, exist_ok=True)
    CODE_MAP.write_text(render_map(entries, limit=len(entries)), encoding="utf-8")
