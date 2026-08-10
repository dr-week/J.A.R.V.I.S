---
id: ISSUE-041
title: Plugin reminders and plan-today sample
status: done
priority: P1
phase: 3
labels: [life-tools, example]
owner: coder-003
claimed_at: 2026-08-08T11:45:23Z
blocked_by: [ISSUE-030]
acceptance:
  - Set/list/cancel reminder
  - plan-today produces ordered plan from available context
---

## Context

More execution samples.

## Lane (parallel with ISSUE-040)

- **Package:** `tools/reminders/` (or `backend/plugins/reminders/`) — **not** `tools/tasks/` (minimax owns 040)
- Register tools only via `backend/app/hands/registry.py` — coordinate imports; no duplicate registries
- Read `docs/TOOL_SCHEMA.md`, existing plugin pattern if any under `tools/` or `backend/plugins/`

## Notes

- [2026-08-08T11:48:23Z] Marked done


- [2026-08-08T11:48:23Z] Acceptance complete: set/list/cancel reminders, ordered plan_today using active reminders plus relevant memory context; smoke test and startup discovery both pass.


- [2026-08-08T11:48:06Z] Verified reminder create/list/cancel confirmation flow and chronological plan_today output with memory context using scratch/test_reminders.py.


- [2026-08-08T11:47:39Z] Implemented backend/plugins/reminders self-registering tools: reminder_set/list/cancel and plan_today, with durable SQLite storage and brain-memory context. Offline smoke test passing.


- Claimed by coder-003 at 2026-08-08T11:45:23Z
