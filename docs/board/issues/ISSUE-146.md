---
id: ISSUE-146
title: HA home_scene tool — run Home Assistant scenes
status: done
priority: P1
phase: 5
labels: [house, homeassistant, hands]
owner: cursor
claimed_at: 2026-08-11T18:10:00Z
blocked_by: []
acceptance:
  - home_scene tool registered confirm_once calling HA scene/turn_on
  - Fails clearly when HA not configured
  - pytest mocks HA HTTP for home_scene
---

## Context

Phase 5 house — run a named HA scene. **Lane avoids Antigravity web/Flutter.**

## Lane

- `backend/plugins/homeassistant/**`
- `backend/tests/test_homeassistant_scene.py`
- `.env.example` (HA scene note only if needed)

## Work

- [ ] `home_scene` tool + executor
- [ ] Clear error without JARVIS_HA_* 
- [ ] Pytest with httpx mock

## Notes

- [2026-08-11T18:08:02Z] Marked done


cursor lane — antigravity stay on web/Flutter.
