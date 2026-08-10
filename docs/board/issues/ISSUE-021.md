---
id: ISSUE-021
title: Memory CRUD and injection
status: done
priority: P0
phase: 1
labels: [soul, memory]
owner: antigravity
claimed_at: 2026-08-07T19:33:47Z
blocked_by: [ISSUE-020]
acceptance:
  - Create/list/update/delete memories via API or tools
  - Relevant memories injected into agent context
---

## Context

Long-term personalization.

## Notes

- [2026-08-07T19:36:14Z] Marked done


- [2026-08-07T19:36:01Z] Memory CRUD API (GET, PUT, DELETE) and SQLite persistence were implemented in prior PRs (ISSUE-010). Memories are successfully loaded and injected into the LLM context via build_system_prompt in persona.py. Integration tests pass.


- Claimed by antigravity at 2026-08-07T19:33:47Z
