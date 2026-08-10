---
id: ISSUE-127
title: Evaluate background queue (Celery) — ADR required
status: backlog
priority: P3
phase: 3
labels: [dev, backend]
owner:
claimed_at:
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

- [ ] Write ADR with recommendation
- [ ] Human approves before any celery_app.py

## Notes

Replaces premature Celery implementation issue.
