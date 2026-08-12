"""Board snapshot and dynamic agent briefs — variable output from live issue state."""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BOARD = DOCS / "board"
LIVE_PLAN = BOARD / "LIVE_PLAN.md"
LIVE_BRIEF = BOARD / "LIVE_BRIEF.md"

KNOWN_OWNERS = (
    "cursor",
    "antigravity",
    "claude",
    "minimax",
    "minimax2",
    "minimax-mini",
    "alice",
    "bob",
)

# Phase focus blurbs (roadmap-aligned)
PHASE_FOCUS: dict[str, str] = {
    "D0": "Docs OS — specs and agent contracts",
    "D1": "Devloop — issue lifecycle CLI",
    "0": "Skeleton — brain + clients chat",
    "1": "Soul — memory, persona, sync identity",
    "2": "Hands — tools, device bridges, audit",
    "3": "Life tools — domain plugins",
    "4": "Voice — STT/TTS, tray, wake word",
    "5": "House — hub, HA, room presence",
    "6": "Expand — tool SDK",
}

LANE_HINTS: list[tuple[set[str], dict[str, str]]] = [
    ({"android"}, {"allow": "clients/android/", "avoid": "clients/windows/", "note": "Android lane only"}),
    ({"windows"}, {"allow": "clients/windows/", "avoid": "clients/android/", "note": "Windows lane only"}),
    ({"hands", "tools"}, {"allow": "backend/app/hands/", "avoid": "", "note": "Registry + gate; one registry file"}),
    ({"soul", "sync"}, {"allow": "backend/app/soul/, backend/app/sync/", "avoid": "", "note": "Soul/sync — coordinate if NOW has bridge work"}),
    ({"skeleton", "backend"}, {"allow": "backend/", "avoid": "", "note": "Backend core"}),
]


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def labels_set(meta: dict[str, Any]) -> set[str]:
    raw = meta.get("labels") or []
    if isinstance(raw, str):
        raw = [raw]
    return {str(x).lower().strip() for x in raw}


def lane_for_issue(meta: dict[str, Any]) -> dict[str, str]:
    labs = labels_set(meta)
    for keys, hint in LANE_HINTS:
        if keys & labs:
            return hint
    phase = str(meta.get("phase", ""))
    if phase == "2":
        return {"allow": "backend/, clients/, docs/SYNC_PROTOCOL.md", "avoid": "scripts/devloop.py", "note": "Phase 2 Hands"}
    return {"allow": "paths in issue acceptance", "avoid": "other worker NOW paths", "note": "See PARALLEL.md"}


def owner_rules(owner: str) -> list[str]:
    o = owner.lower().strip()
    base = [
        f"Owner id for devloop: `{o}`",
        "Session: `devloop loop` -> `inbox --owner " + o + "` -> claim -> brief/prompt -> done -> say",
    ]
    if o == "minimax" or o.startswith("minimax"):
        base.extend(
            [
                "Read: `.blackbox/RULES.md`, `docs/dev/MINIMAX.md`",
                "Mirror device bridge: `docs/SYNC_PROTOCOL.md` + ISSUE-032 pattern",
                f"Handoff: `say --from {o} --to cursor --kind done`",
                "You are a Blackbox MiniMax seat — use YOUR owner id on every devloop command.",
            ]
        )
    elif o == "cursor":
        base.extend(
            [
                "Integration + review; Soul/Hands core when bridges stable",
                "Pair with minimax on 033 or antigravity on soul/sync lanes",
            ]
        )
    elif o == "antigravity":
        base.extend(["Parallel P0 slices; sync/dashboard/memory style issues"])
    else:
        base.append("Read: `AGENTS.md`, `skills/jarvis-dev/SKILL.md`")
    return base


def dynamic_reads(meta: dict[str, Any]) -> list[str]:
    reads = ["AGENTS.md", "docs/SCOPE.md", "docs/board/issues/" + str(meta.get("id")) + ".md"]
    labs = labels_set(meta)
    phase = str(meta.get("phase", ""))
    if "android" in labs or "hands" in labs:
        reads.append("docs/SYNC_PROTOCOL.md")
    if "windows" in labs:
        reads.append("docs/SYNC_PROTOCOL.md")
        reads.append("clients/windows/README.md")
    if "soul" in labs or "persona" in labs:
        reads.append("docs/PERSONA.md")
        reads.append("docs/LEARNING.md")
    if phase == "2":
        reads.append("docs/TOOL_SCHEMA.md")
    if "auth" in labs or "sync" in meta.get("title", "").lower():
        reads.append("docs/SECURITY.md")
    reads.append("docs/dev/PARALLEL.md")
    reads.append("docs/dev/DEFINITION_OF_DONE.md")
    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for r in reads:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def phase_summary(issues: list[tuple[dict[str, Any], Path]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for meta, _ in issues:
        ph = str(meta.get("phase", "?"))
        summary.setdefault(ph, {"done": 0, "open": 0, "now": 0})
        st = str(meta.get("status", "backlog"))
        if st == "done":
            summary[ph]["done"] += 1
        elif st == "now":
            summary[ph]["now"] += 1
            summary[ph]["open"] += 1
        elif st != "done":
            summary[ph]["open"] += 1
    return summary


def snapshot_fingerprint(snap: dict[str, Any]) -> str:
    blob = json.dumps(snap, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def build_snapshot(
    *,
    issues: list[tuple[dict[str, Any], Path]],
    open_issues: list[tuple[dict[str, Any], Path]],
    now_items: list[dict[str, Any]],
    pick_for_owner_fn: Any,
) -> dict[str, Any]:
    done = [m for m, _ in issues if m.get("status") == "done"]
    phases = phase_summary(issues)
    sorted(
        [p for p, c in phases.items() if c.get("now") or (c.get("open") and p in ("1", "2", "3"))],
        key=lambda x: (x == "D0", x == "D1", x),
    )
    focus_phase = "2"
    for p in ("2", "1", "3", "0", "4", "5", "6"):
        if phases.get(p, {}).get("now") or (
            phases.get(p, {}).get("open", 0) > phases.get(p, {}).get("done", 0) and p in ("1", "2")
        ):
            focus_phase = p
            break

    per_owner: dict[str, Any] = {}
    for oid in KNOWN_OWNERS:
        picked = pick_for_owner_fn(oid)
        if picked:
            m, p = picked
            per_owner[oid] = {
                "id": m.get("id"),
                "title": m.get("title"),
                "status": m.get("status"),
                "owned_by_me": m.get("status") == "now"
                and str(m.get("owner", "")).lower() == oid,
            }
        else:
            per_owner[oid] = None

    return {
        "generated_at": utc_now(),
        "now": [
            {
                "id": m.get("id"),
                "title": m.get("title"),
                "owner": m.get("owner"),
                "phase": m.get("phase"),
                "priority": m.get("priority"),
            }
            for m in now_items
        ],
        "next_open": [
            {"id": m.get("id"), "title": m.get("title"), "phase": m.get("phase"), "priority": m.get("priority")}
            for m, _ in open_issues[:8]
        ],
        "done_count": len(done),
        "open_count": len(open_issues),
        "phase_stats": phases,
        "focus_phase": focus_phase,
        "focus_blurb": PHASE_FOCUS.get(str(focus_phase), "See ROADMAP.md"),
        "per_owner_next": per_owner,
    }


def render_live_plan(snap: dict[str, Any]) -> str:
    fp = snapshot_fingerprint(snap)
    lines = [
        "# LIVE PLAN (generated — do not edit)",
        "",
        f"_Generated: {snap['generated_at']} UTC · fingerprint `{fp}`_",
        "",
        "Regenerate: `python scripts/devloop.py sync` · Who: `devloop who`",
        "",
        "## Who is working on what",
        "",
    ]
    if snap["now"]:
        lines.append("| Owner | Issue | Phase | Priority | Title |")
        lines.append("|-------|-------|-------|----------|-------|")
        for item in snap["now"]:
            lines.append(
                f"| **{item.get('owner') or '?'}** | {item['id']} | {item.get('phase')} | "
                f"{item.get('priority')} | {item['title']} |"
            )
        lines.append("")
        free = max(0, 2 - len(snap["now"]))
        if free:
            lines.append(f"**Free parallel slots:** {free} / 2")
            lines.append("")
    else:
        lines.append("_No claims — both slots free._")
        lines.append("")

    lines.extend([
        "## Board state",
        "",
        f"- NOW slots: **{len(snap['now'])}/2**",
        f"- Open (unblocked): **{snap['open_count']}**",
        f"- Done total: **{snap['done_count']}**",
        f"- Focus phase: **{snap['focus_phase']}** — {snap['focus_blurb']}",
        "",
    ])
    if snap["now"]:
        lines.append("### In progress (detail)")
        for item in snap["now"]:
            lines.append(
                f"- **{item['owner']}** -> [{item['id']}](issues/{item['id']}.md) "
                f"({item['priority']}, phase {item['phase']}) — {item['title']}"
            )
        lines.append("")
    else:
        lines.append("### In progress (detail)\n\n_(none)_\n")

    lines.append("### Next actionable")
    for i, item in enumerate(snap["next_open"][:6], 1):
        lines.append(f"{i}. **{item['id']}** (phase {item['phase']}, {item['priority']}) — {item['title']}")
    lines.append("")

    lines.append("## Per-agent next issue")
    lines.append("")
    for oid in KNOWN_OWNERS:
        nxt = snap["per_owner_next"].get(oid)
        if nxt:
            tag = " **[IN NOW]**" if nxt.get("owned_by_me") else ""
            lines.append(f"- **{oid}**: {nxt['id']} — {nxt['title']}{tag}")
        else:
            lines.append(f"- **{oid}**: _(no pick — slot full or backlog empty)_")
    lines.append("")

    lines.append("## Phase progress (issue counts)")
    lines.append("")
    lines.append("| Phase | Done | Open+NOW |")
    lines.append("|-------|------|----------|")
    for ph in sorted(snap["phase_stats"].keys(), key=lambda x: (len(x) > 1, x)):
        c = snap["phase_stats"][ph]
        lines.append(f"| {ph} | {c.get('done', 0)} | {c.get('open', 0)} |")
    lines.append("")

    lines.append("## North star (static links)")
    lines.append("")
    lines.append("- [FUTURE.md](../FUTURE.md) · [PARTNERSHIP.md](../PARTNERSHIP.md) · [DOCS_MAP.md](../DOCS_MAP.md)")
    lines.append("")
    return "\n".join(lines)


def render_brief(
    *,
    snap: dict[str, Any],
    owner: str,
    meta: dict[str, Any],
    body: str,
    path: Path,
    inbox: list[dict[str, Any]],
) -> str:
    fp = snapshot_fingerprint(snap)
    iid = str(meta.get("id"))
    lane = lane_for_issue(meta)
    reads = dynamic_reads(meta)
    rules = owner_rules(owner)
    blocked = meta.get("blocked_by") or []
    acc = meta.get("acceptance") or []

    lines = [
        "# LIVE BRIEF (generated — do not edit)",
        "",
        f"_Generated: {snap['generated_at']} UTC · owner `{owner}` · issue `{iid}` · `{fp}`_",
        "",
        "Regenerate: `python scripts/devloop.py brief --owner " + owner + "`",
        "",
        "## Situation (this run)",
        "",
        f"- Board fingerprint `{fp}` — if unchanged, another agent may have stale chat context; re-run `sync`.",
        f"- Focus phase **{snap['focus_phase']}**: {snap['focus_blurb']}",
        f"- NOW occupied: {', '.join(n['id'] + '=' + str(n['owner']) for n in snap['now']) or 'none'}",
        "",
        "## Your assignment",
        "",
        f"### {iid}: {meta.get('title')}",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| phase | {meta.get('phase')} |",
        f"| priority | {meta.get('priority')} |",
        f"| status | {meta.get('status')} |",
        f"| claimed owner | {meta.get('owner') or '—'} |",
        f"| file | `{path.relative_to(ROOT)}` |",
        "",
    ]
    if blocked:
        lines.append(f"- blocked_by (must be done): {blocked}")
        lines.append("")

    lines.append("### Acceptance (verify each before `done`)")
    lines.append("")
    for a in acc:
        lines.append(f"- [ ] {a}")
    lines.append("")

    lines.append("### Lane")
    lines.append("")
    lines.append(f"- {lane.get('note', '')}")
    if lane.get("allow"):
        lines.append(f"- **Prefer paths:** `{lane['allow']}`")
    if lane.get("avoid"):
        lines.append(f"- **Avoid paths:** `{lane['avoid']}`")
    lines.append("")

    lines.append("### Owner rules")
    lines.append("")
    for r in rules:
        lines.append(f"- {r}")
    lines.append("")

    if inbox:
        lines.append("### Inbox (messages to you)")
        lines.append("")
        for ev in inbox:
            lines.append(
                f"- [{ev.get('ts')}] **{ev.get('from')}** `{ev.get('kind')}` "
                f"{ev.get('issue') or ''}: {ev.get('body')}"
            )
        lines.append("")

    lines.append("### Required reads (issue-specific)")
    lines.append("")
    for r in reads:
        lines.append(f"- `{r}`")
    lines.append("")

    lines.append("### Issue notes / body")
    lines.append("")
    lines.append(body.strip())
    lines.append("")

    lines.append("### Finish")
    lines.append("")
    lines.append("```bash")
    lines.append(f"python scripts/devloop.py update {iid} --note \"verified: ...\"")
    lines.append(f"python scripts/devloop.py done {iid}")
    lines.append(f"python scripts/devloop.py say --from {owner} --to cursor --kind done --issue {iid} -- \"summary\"")
    lines.append("python scripts/devloop.py sync")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)
