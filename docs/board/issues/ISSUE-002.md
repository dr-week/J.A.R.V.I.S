---
id: ISSUE-002
title: Implement and verify scripts/devloop.py
status: done
priority: P0
phase: D1
labels: [devloop, tooling]
owner: 
claimed_at: 
blocked_by: []
acceptance:
  - CLI supports status, next, claim, issue, update, done, refresh, prompt, bootstrap
  - Commands read/write docs/board markdown correctly
  - `prompt` emits a MiniMax-ready brief for the top NOW/next issue
  - README documents how to run it
---

## Context

Internal AI app-dev feedback loop — deterministic orchestration around coding agents.

## Work

- [ ] Implement CLI
- [ ] Smoke: status → claim → update → done → refresh
- [ ] Document in README / PROCESS.md

## Notes

- [2026-08-06T19:33:29Z] Marked done


- [2026-08-06T19:33:29Z] CLI implemented with status/next/claim/issue/update/done/refresh/prompt/bootstrap.


Stub may ship with bootstrap; flesh out until acceptance passes.
