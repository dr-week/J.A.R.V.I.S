---
id: ISSUE-119
title: Pytest dev dependencies only (micro-slice)
status: done
priority: P3
phase: D1
labels: [dev, starter, scripts]
owner: cursor
claimed_at: 2026-08-09T19:09:00Z
blocked_by: []
acceptance:
  - pytest and pytest-asyncio added to pyproject.toml optional-dependencies dev
  - backend/README.md or DEV_ENV.md documents pip install -e ".[dev]" and pytest command
  - No test files required in this slice
---

## Context

Parent chain: **119** → **115** full test migration. [OSS_DEV_PLAN.md](../../dev/OSS_DEV_PLAN.md).

## Lane

- `pyproject.toml`
- `backend/README.md`

## Work

- [x] Add `pytest`, `pytest-asyncio` to `[project.optional-dependencies] dev`
- [x] Document install + `pytest backend/tests` (tests land in **115**)

## Notes

Smallest possible MiniMax win before **115**.
