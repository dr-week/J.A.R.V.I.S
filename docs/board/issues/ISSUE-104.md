---
id: ISSUE-104
title: Backend — WS confirm_request when tool gate blocks
status: done
priority: P2
phase: 2
labels: [backend, sync, hands]
owner: antigravity
claimed_at: 2026-08-09T18:43:43Z
blocked_by: []
acceptance:
  - When run_tool blocks for confirm_once/confirm_always, brain sends confirm_request on device WS if session has registered bridge
  - Approve/deny path documented in SYNC_PROTOCOL.md and completes gate (or routes to pending session)
  - Web chat text confirm still works without regression
---

## Context

[SYNC_PROTOCOL.md](../../SYNC_PROTOCOL.md) documents `confirm_request` but today only [hands/gate.py](../../backend/app/hands/gate.py) + chat text applies (PLAN_AUDIT).

Enables Flutter Field approve UI (FR-M3 off-desktop).

## Lane

- `backend/app/hands/**`
- `backend/app/api/chat.py` or sync manager
- `docs/SYNC_PROTOCOL.md`

## Notes

- [2026-08-09T18:44:11Z] Marked done


- Claimed by antigravity at 2026-08-09T18:43:43Z


- Optional for ISSUE-101 v1; required for mobile push confirms.
