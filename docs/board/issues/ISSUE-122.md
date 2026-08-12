---
id: ISSUE-122
title: Integrate pydantic-settings
status: done
priority: P2
phase: 0
labels: [dev, starter, backend]
owner: 
claimed_at: 
blocked_by: [ISSUE-119]
acceptance:
  - backend/app/config.py Settings (or pydantic-settings BaseSettings) validates core env on startup
  - main.py uses Settings instead of scattered os.getenv for core vars
  - No unrelated refactors
---

## Context

Wave Y phase B2. [LAB_STACK.md](../../dev/LAB_STACK.md).

## Lane

- `backend/app/config.py`
- `backend/app/main.py`

## Work

- [ ] Create Settings with brain URL, assistant name, pairing flags as needed
- [ ] Wire main.py

## Notes

- [2026-08-11T17:08:36Z] Marked done


- Released by unknown at 2026-08-11T17:07:08Z (was subagent)


- Claimed by subagent at 2026-08-11T17:06:57Z


Dep in pyproject (**119** + main deps). Not blocked on Velocity **130**.
