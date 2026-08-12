---
id: ISSUE-145
title: Phase 1 Soul exit — proactive habits in prompt + memory recall proof
status: done
priority: P0
phase: 1
labels: [soul, learning]
owner: cursor
claimed_at: 2026-08-11T18:01:00Z
blocked_by: []
acceptance:
  - get_proactive_context injected into system prompt when habits are confident
  - pytest proves memory upsert appears in build_system_prompt (cross-session recall)
  - LEARNING.md + ROADMAP Phase 1 exit note updated
---

## Context

Phase 1 Soul exit criteria: memory injection works; proactive habits surface without being asked.
Do **not** rebuild Soul stores — wire existing `learner.get_proactive_context`.

## Lane

- `backend/app/soul/persona.py`
- `backend/app/soul/learner.py`
- `backend/tests/test_soul_phase1.py`
- `docs/LEARNING.md`
- `docs/ROADMAP.md`

## Work

- [x] Inject proactive suggestions into `build_system_prompt`
- [x] Pytest: upsert memory → prompt contains it; habit → proactive block
- [x] Docs: Phase 1 exit note

## Notes

- [2026-08-11T18:03:46Z] Marked done


- [2026-08-11T18:03:20Z] Marked done


- [2026-08-11] Implemented by cursor — no greenfield swarm; wired existing learner into persona.
