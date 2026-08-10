---
id: ISSUE-061
title: Home Assistant or equivalent tool bridge
status: done
priority: P0
phase: 5
labels: [house, iot]
owner: minimax
claimed_at: 2026-08-08T11:26:10Z
blocked_by: [ISSUE-030, ISSUE-060]
acceptance:
  - At least one home entity controllable via tool (e.g. light)
  - Risk/confirm rules applied
  - Chosen bridge recorded in DECISIONS.md
---

## Context

House Hands.

## Notes

- [2026-08-08T11:37:30Z] Marked done


- [2026-08-08T11:37:30Z] HA plugin verified: home_entity_list (auto) + home_entity_set (confirm_once) load via discover_plugins. Acceptance met. Redundant home_bridge.py + config block reverted; ADR-0019 stands. Docs: HOME_HUB.md House Hands section added. test: scratch/test_home_bridge.py offline gate verification passed.


- Claimed by minimax at 2026-08-08T11:26:10Z


- Claimed by minimax at 2026-08-08T11:26:01Z
