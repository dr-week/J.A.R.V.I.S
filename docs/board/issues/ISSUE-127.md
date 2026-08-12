---
id: ISSUE-127
title: Evaluate background queue (Celery) — ADR required
status: done
priority: P3
phase: 3
labels: [dev, backend]
owner: subagent
claimed_at: 2026-08-11T17:52:03Z
blocked_by: []
acceptance:
  - ADR in DECISIONS.md compares APScheduler vs Celery+Redis for Jarvis
  - No Celery code until ADR accepted and Phase 3 exit
  - If rejected, issue closed with note prefer in-process + APScheduler
---

## Context

**127 is decision-first**, not “add Celery because Iron Legion sounds cool.” [LAB_STACK.md](../../dev/LAB_STACK.md).

## Lane

- `docs/DECISIONS.md`
- `docs/dev/LAB_STACK.md`

## Work

- [x] Write ADR with recommendation
- [x] Human approves before any celery_app.py

## Notes

- [2026-08-11T17:52:46Z] Marked done


- Claimed by subagent at 2026-08-11T17:52:03Z
- **Resolution**: Rejected Celery in favor of in-process `APScheduler`. Added ADR-0026 to DECISIONS.md.

Replaces premature Celery implementation issue.
