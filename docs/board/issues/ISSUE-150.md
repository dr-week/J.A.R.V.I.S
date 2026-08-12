---
id: ISSUE-150
title: M-Android Presence UI — pair, bridge status, confirm, open web
status: done
priority: P0
phase: 2
labels: [android, ui, presence, hands]
owner: cursor
claimed_at: 2026-08-11T18:30:00Z
blocked_by: []
acceptance:
  - Field-style Presence UI: brain URL, pair, health, bridge status
  - confirm_request shown with Approve/Deny wired to chat confirm
  - Open full assistant launches web URL
  - DeviceBridge uses token on WS register; README+MAJOR_WORK_PLAN updated
---

## Context

Complete **Kotlin Android** presence (not a second chat product). Align with Flutter Field + PRESENCE_STACKS.
Plan: [MAJOR_WORK_PLAN.md](../../dev/MAJOR_WORK_PLAN.md)

## Lane

- `clients/android/**`
- `docs/dev/MAJOR_WORK_PLAN.md`
- `docs/dev/PRESENCE_STACKS.md`
- `docs/DEMO.md` (one Android line if needed)

## Work

- [x] Presence UI (pair / health / bridge / confirm / open web)
- [x] Bridge token + confirm_request
- [x] Docs / plan update

## Notes

- [2026-08-11T18:33:26Z] Marked done


cursor — PresenceScreen + PresenceViewModel + BridgeHub; ChatScreen kept unused for reference.
M-Android marked shipped in MAJOR_WORK_PLAN.
