---
id: ISSUE-126
title: Prototype openwakeword wake listener
status: backlog
priority: P3
phase: 4
labels: [dev, windows, voice]
owner:
claimed_at:
blocked_by: []
acceptance:
  - clients/windows/wake.py prints on wake detection (dev prototype)
  - Document mic permission + Phase 4 gate in README
  - No production tray integration in this slice
---

## Context

Phase 4 voice — **not before Hands exit.** [LAB_STACK.md](../../dev/LAB_STACK.md).

## Lane

- `clients/windows/wake.py`
- `clients/windows/README.md`

## Work

- [ ] Minimal wake.py script
- [ ] README warning: prototype only

## Notes

Stark prototypes in the lab; ship to suit after Phase 4 board exit.
