---
id: ISSUE-129
title: Implement Embedded Lua Engine
status: backlog
priority: P3
phase: "6"
labels:
  - dev
  - backend
owner: ""
claimed_at: ""
blocked_by: ["ISSUE-128"]
acceptance:
  - Add lupa to pyproject.toml.
  - Create a simple Lua executor that reads a script.lua and executes it safely.
---
## Context

Polyglot Plugins: Execute fast, lightweight .lua scripts directly inside the Python memory space using lupa.

## Work

- [ ] Add lupa
- [ ] Create lua executor

## Notes

Created for Minimax queue
