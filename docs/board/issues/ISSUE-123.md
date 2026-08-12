---
id: ISSUE-123
title: Setup alembic for SQLite
status: done
priority: P2
phase: 3
labels: [dev, backend]
owner: 
claimed_at: 
blocked_by: []
acceptance:
  - alembic in pyproject.toml
  - alembic.ini + env.py target brain.db
  - Baseline migration matches current schema
---

## Context

Phase 3 — schema will grow (memory, habits). **Not mini-first.** [LAB_STACK.md](../../dev/LAB_STACK.md).

## Lane

- `alembic/**`
- `pyproject.toml`

## Work

- [ ] alembic init + baseline migration

## Notes

- [2026-08-11T17:09:30Z] Marked done


- Released by unknown at 2026-08-11T17:06:52Z (was AI_Engineer)


- Claimed by AI_Engineer at 2026-08-11T17:06:39Z


Main `minimax` or cursor — not minimax2 first slice.
