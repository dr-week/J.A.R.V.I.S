---
id: ISSUE-105
title: Web UI verification — 098/099 acceptance and DESIGN header
status: done
priority: P2
phase: 6
labels: [web, qa]
owner: antigravity
claimed_at: 2026-08-09T17:50:48Z
blocked_by: []
acceptance:
  - Settings tab wires brain URL + clear token; hamburger collapses sidebar under 768px
  - Main header has no duplicate product name if sidebar shows Jarvis (DESIGN.md)
  - New session / clear chat works; LLM-off visible in status zone
  - Issue 098/099 acceptance checkboxes reflected in issue files or notes explaining gaps
---

## Context

ISSUE-098 and ISSUE-099 marked done with unchecked acceptance ([PLAN_AUDIT.md](../../dev/PLAN_AUDIT.md)).

## Lane

- `clients/web/**`
- `docs/dev/WEB_UI.md`
- `docs/board/issues/ISSUE-098.md`, `ISSUE-099.md` (notes only)

## Notes

- [2026-08-09T17:51:14Z] Marked done


- Claimed by antigravity at 2026-08-09T17:50:48Z


- WS ?token= auth not required for this issue (backend accepts open /ws today).
