---
id: ISSUE-142
title: Flutter Field — handle WS confirm_request and approve/deny
status: done
priority: P2
phase: 2
labels: [flutter, bridge, hands]
owner: 
claimed_at: 
blocked_by: [ISSUE-101]
acceptance:
  - bridge_client handles confirm_request messages and surfaces pending tool in FieldController
  - User can approve or deny; denial does not execute tool; approval completes gate per SYNC_PROTOCOL
  - Documented in FLUTTER_FIELD.md and flutter/README.md (remove "backlog" for confirm UI)
---

## Context

**ISSUE-104** shipped backend `confirm_request` push when the gate blocks. Flutter Field still only handles `tool_execute`. End-to-end Field confirm is a separate slice.

## Lane

- `clients/flutter/lib/data/bridge_client.dart`
- `clients/flutter/lib/state/field_controller.dart`
- `clients/flutter/lib/ui/field/field_screen.dart`

## Work

- [ ] Parse `confirm_request` in bridge_client
- [ ] Populate `pending` + approve/deny actions
- [ ] Wire approve to brain (chat confirm or dedicated WS message per protocol)

## Notes

- [2026-08-11T17:56:29Z] Marked done


- Released by unknown at 2026-08-11T17:53:41Z (was subagent)


- Claimed by subagent at 2026-08-11T17:53:34Z


Parent: FR-M3 off-desktop. Do not duplicate web chat thread.
