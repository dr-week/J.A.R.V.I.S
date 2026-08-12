---
id: ISSUE-115
title: Pytest Integration
status: done
priority: P1
phase: 0
labels: [dev, starter, scripts]
owner: 
claimed_at: 
blocked_by: [ISSUE-119]
acceptance:
  - pytest and pytest-asyncio in pyproject.toml dev optional-deps
  - backend/tests/test_brain.py exists and passes with pytest
  - Document run command in backend/README.md or DEV_ENV.md
---

## Context

Replace scratch tests with pytest. **Mini slice:** do deps + one test file only.

[MINIMAX_QUEUE.md](../../dev/MINIMAX_QUEUE.md) wave X · [STRATEGY_FORWARD.md](../../dev/STRATEGY_FORWARD.md)

## Lane

- `pyproject.toml`
- `backend/tests/**`

## Work

- [x] Add pytest + pytest-asyncio to pyproject.toml `[project.optional-dependencies] dev`
- [x] Move or recreate `test_brain.py` under `backend/tests/`
- [x] `pytest backend/tests` passes from repo root

## Notes

- [2026-08-11T17:08:22Z] Marked done


- Released by unknown at 2026-08-11T17:06:56Z (was —)


- Released by unknown at 2026-08-11T17:06:34Z (was —)


- Released by unknown at 2026-08-11T17:06:28Z (was Agent)


- Claimed by Agent at 2026-08-11T17:06:15Z


Created by devloop. Prefer `uv run pytest` if uv installed; else `pip install -e ".[dev]"`.
