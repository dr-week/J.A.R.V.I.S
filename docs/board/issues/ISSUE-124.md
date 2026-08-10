---
id: ISSUE-124
title: Integrate loguru for observability
status: backlog
priority: P2
phase: "0"
labels: [dev, starter, backend]
owner:
claimed_at:
blocked_by: []
acceptance:
  - backend/app/logger.py configures loguru (or thin wrapper)
  - main.py uses logger instead of print for startup paths
  - At least 3 log lines in main.py migrated
---

## Context

Wave Y phase B4. [LAB_STACK.md](../../dev/LAB_STACK.md).

## Lane

- `backend/app/logger.py`
- `backend/app/main.py`

## Work

- [ ] logger.py
- [ ] Replace prints in main.py

## Notes

loguru already in `pyproject.toml`. Not blocked on Velocity **131**.
