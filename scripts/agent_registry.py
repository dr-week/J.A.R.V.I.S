"""Agent registry — names, tiers, and issue routing for new AI coders."""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "docs" / "board" / "agents.json"

# Issues suited for mini / low-scope coders (backlog, unclaimed)
MINI_ISSUE_QUEUE = (
    "ISSUE-115",
    "ISSUE-116",
    "ISSUE-122",
    "ISSUE-124",
    "ISSUE-125",
    "ISSUE-106",
)

STANDARD_PREFERRED_AFTER = (
    "ISSUE-022",
    "ISSUE-040",
    "ISSUE-041",
)


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.exists():
        return {"version": 1, "agents": []}
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def save_registry(data: dict[str, Any]) -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def list_agent_ids(data: dict[str, Any]) -> set[str]:
    return {str(a.get("id", "")).lower() for a in data.get("agents", [])}


def next_blackbox_id(data: dict[str, Any], prefix: str = "minimax") -> str:
    """minimax -> minimax2 -> minimax3 ... skip minimax-mini style unless prefix given."""
    used = list_agent_ids(data)
    nums = [1]
    for aid in used:
        m = re.match(rf"^{re.escape(prefix)}(\d*)$", aid)
        if m:
            tail = m.group(1)
            nums.append(int(tail) if tail else 1)
        if aid == prefix:
            nums.append(1)
    n = max(nums) + 1
    if n == 2:
        return f"{prefix}2"
    return f"{prefix}{n}"


def next_coder_id(data: dict[str, Any]) -> str:
    used = list_agent_ids(data)
    nums = [0]
    for aid in used:
        m = re.match(r"^coder-(\d+)$", aid)
        if m:
            nums.append(int(m.group(1)))
    return f"coder-{max(nums) + 1:03d}"


def register_agent(
    *,
    agent_id: str,
    display_name: str = "",
    tier: str = "standard",
    platform: str = "unknown",
    note: str = "",
) -> dict[str, Any]:
    data = load_registry()
    aid = agent_id.strip().lower()
    if not aid:
        raise ValueError("agent id required")
    for a in data.get("agents", []):
        if str(a.get("id", "")).lower() == aid:
            raise ValueError(f"agent '{aid}' already registered")
    entry = {
        "id": aid,
        "display_name": display_name or aid,
        "tier": tier,
        "platform": platform,
        "registered_at": utc_now(),
        "note": note,
        "active": True,
    }
    data.setdefault("agents", []).append(entry)
    save_registry(data)
    return entry


def suggest_issue_for_tier(
    tier: str,
    *,
    list_issues_fn: Any,
    open_issues_fn: Any,
    is_unblocked_fn: Any,
) -> tuple[dict[str, Any], Path] | None:
    """Pick backlog issue matching tier; returns (meta, path)."""
    issues = list_issues_fn()
    done_ids = {str(m.get("id")) for m, _ in issues if m.get("status") == "done"}
    by_id = {str(m.get("id")): (m, p) for m, p in issues}

    queue = MINI_ISSUE_QUEUE if tier == "mini" else STANDARD_PREFERRED_AFTER

    for iid in queue:
        pair = by_id.get(iid)
        if not pair:
            continue
        meta, path = pair
        if meta.get("status") == "done":
            continue
        if meta.get("status") == "now" and meta.get("owner"):
            continue
        blocked = meta.get("blocked_by") or []
        if isinstance(blocked, str):
            blocked = [blocked] if blocked else []
        if not all(str(b) in done_ids for b in blocked):
            continue
        return meta, path

    if tier == "mini":
        for m, p in open_issues_fn():
            labs = m.get("labels") or []
            if isinstance(labs, str):
                labs = [labs]
            if "starter" in [str(x).lower() for x in labs] and m.get("status") == "backlog":
                return m, p
        return None

    for m, p in open_issues_fn():
        if m.get("status") == "done":
            continue
        if m.get("status") == "now" and m.get("owner"):
            continue
        blocked = m.get("blocked_by") or []
        if isinstance(blocked, str):
            blocked = [blocked] if blocked else []
        if not all(str(b) in done_ids for b in blocked):
            continue
        if str(m.get("id")) in MINI_ISSUE_QUEUE and tier == "standard":
            continue
        return m, p
    return None
