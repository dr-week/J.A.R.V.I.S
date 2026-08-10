---
id: ISSUE-083
title: tasks plugin scaffold and tasks_ping stub tool
status: done
priority: P1
phase: 3
labels: [life-tools, starter]
owner: antigravity
claimed_at: 2026-08-09T05:31:07Z
blocked_by: [ISSUE-030]
acceptance:
  - tools/tasks/ package exists with README
  - One stub tool tasks_ping registered and visible via GET /tools
  - No full task CRUD yet that is ISSUE-040
---

## Context

First slice of Phase 3 plugins for small AI before ISSUE-040 epic.

## Lane

- `tools/tasks/` only; wire register in `backend/app/hands/registry.py` minimal import

## Notes

- [2026-08-09T05:32:54Z] Marked done


- Claimed by antigravity at 2026-08-09T05:31:07Z


Part **H** in SMALL_AI_PARTS.md. ISSUE-030 done — unblocked.
