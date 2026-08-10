---
id: ISSUE-130
title: Establish Velocity Plugin Submodule
status: backlog
priority: P1
phase: "3"
labels:
  - dev
  - plugins
owner: ""
claimed_at: ""
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

Created for Minimax queue (Velocity Integration)
