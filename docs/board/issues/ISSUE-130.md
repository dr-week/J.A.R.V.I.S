---
id: ISSUE-130
title: Establish Velocity Plugin Submodule
status: done
priority: P1
phase: 3
labels: [dev, plugins]
owner: 
claimed_at: 
blocked_by: []
acceptance:
  - Document or symlink Velocity app into `plugins/velocity_builder/` (path via env e.g. `JARVIS_VELOCITY_ROOT`, not a fixed drive letter)
  - Ensure pnpm install and the Velocity dev server can be booted via a single script from the Jarvis root.
---

## Context

Velocity Integration: Bring the Velocity codebase into the Jarvis repo structure so the devloop daemon can manage both.

## Work

- [ ] Symlink or copy e:\CODES\velocity to plugins/velocity_builder/
- [ ] Create wrapper script in scripts/ to boot Velocity

## Notes

- [2026-08-11T17:06:20Z] Marked done


- Released by unknown at 2026-08-11T17:06:05Z (was velocity_plugin_agent)


- Claimed by velocity_plugin_agent at 2026-08-11T17:05:09Z


Created for Minimax queue (Velocity Integration)
