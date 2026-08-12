---
id: ISSUE-131
title: Create velocity_build Tool
status: done
priority: P1
phase: 3
labels: [backend, tools]
owner: cursor
claimed_at: 2026-08-11T17:57:46Z
blocked_by: []
acceptance:
  - Create backend/app/hands/tools/velocity_build.py
  - The tool will accept an app_description string, generate a JSON configuration payload, and send it to the Velocity engine.
---

## Context

Velocity Integration: Create the python tool schema and executor to bridge Jarvis and Velocity.

## Lane

- `backend/app/hands/tools/velocity_build.py`
- `backend/app/hands/builtin_tools.py`
- `backend/app/config.py`
- `docs/dev/LOCAL_LLM.md`

## Work

- [x] Create velocity_build.py tool
- [x] Connect to local velocity endpoint (`JARVIS_VELOCITY_URL`)
- [x] Mount `/internal/webhook/velocity` + broadcast
- [x] Document in docs/dev/LOCAL_LLM.md

## Notes

- [2026-08-11T17:58:10Z] Marked done


- Claimed by cursor at 2026-08-11T17:57:46Z


- [2026-08-11T17:57:36Z] Marked done


- [2026-08-11] Implemented by cursor (NOW was full — claim later / `done` when slot free).
- Released by unknown at 2026-08-11T17:53:23Z (was —)
- Released by unknown at 2026-08-11T17:53:21Z (was AI_SOFTWARE_ENGINEER)
- Claimed by AI_SOFTWARE_ENGINEER at 2026-08-11T17:52:04Z

Created for Cursor queue (Velocity Integration)
