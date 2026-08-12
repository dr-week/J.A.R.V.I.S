---
id: ISSUE-103
title: Flutter — strip legacy chat UI; Field home only
status: done
priority: P2
phase: 2
labels: [flutter, cleanup]
owner: 
claimed_at: 
blocked_by: [ISSUE-101]
acceptance:
  - Remove or gate SSE chat screen and composer from default route
  - Default route is Field Body home per FLUTTER_FIELD.md
  - README and FLUTTER_LAYERS.md reflect L3/L4 Field focus
  - flutter analyze and test pass
---

## Context

Chat belongs in web only. Flutter chat code was a spike.

## Lane

- `clients/flutter/lib/**`
- `docs/dev/FLUTTER_LAYERS.md`

## Notes

- [2026-08-11T17:55:04Z] Marked done


- Released by unknown at 2026-08-11T17:53:27Z (was —)


- Released by unknown at 2026-08-11T17:53:22Z (was AI Agent)


- Claimed by AI Agent at 2026-08-11T17:53:06Z


- Blocked until ISSUE-101 lands minimal Field path.
- [SYNC_PLAN.md](../../dev/SYNC_PLAN.md)
