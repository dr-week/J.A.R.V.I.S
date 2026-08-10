---
id: ISSUE-110
title: Ruff config and backend lint habit
status: done
priority: P3
phase: D1
labels: [devloop, starter, docs]
owner: cursor
claimed_at: 2026-08-09T19:05:00Z
blocked_by: []
acceptance:
  - ruff.toml at repo root targets backend and scripts
  - backend/README.md documents pip install ruff and ruff check backend
  - No mass reformat required in this issue
---

## Context

[DEV_ENV.md](../../dev/DEV_ENV.md) OSS table · [MINIMAX_QUEUE.md](../../dev/MINIMAX_QUEUE.md).

## Lane

- `ruff.toml`
- `backend/README.md`

## Work

- [x] Add minimal ruff.toml
- [x] Add README Lint section
