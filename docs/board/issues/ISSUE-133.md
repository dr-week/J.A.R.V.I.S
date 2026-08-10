---
id: ISSUE-133
title: R subprocess plugin template
status: backlog
priority: P3
phase: 6
labels: [dev, starter, backend]
owner:
claimed_at:
blocked_by: [ISSUE-128]
acceptance:
  - Example plugin runs Rscript with fixed script path and JSON I/O
  - README documents R install on host
  - confirm_once or confirm_always on tool
---

## Context

[POLYGLOT_TOOLS.md](../../dev/POLYGLOT_TOOLS.md) — pattern A for R.

## Lane

- `backend/plugins/r_demo/**`

## Work

- [ ] `run.R` stub + Python wrapper
