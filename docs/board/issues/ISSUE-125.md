---
id: ISSUE-125
title: Integrate psutil — system_vitals tool
status: done
priority: P2
phase: 2
labels: [dev, starter, backend]
owner: subagent
claimed_at: 2026-08-11T22:39:15+05:30
blocked_by: []
acceptance:
  - psutil in pyproject.toml
  - Tool system_vitals returns CPU/RAM/disk summary
  - executor brain, risk auto, registered via existing plugin pattern
---

## Context

“Suit vitals” — brain knows host health. [LAB_STACK.md](../../dev/LAB_STACK.md) wave Z C1.

## Lane

- `pyproject.toml`
- `backend/plugins/**` or `tools/**` (one package only)

## Work

- [x] Add psutil
- [x] One tool module + registry discover

## Notes

Do not edit hands/registry.py core logic beyond discover path — use plugin package.
