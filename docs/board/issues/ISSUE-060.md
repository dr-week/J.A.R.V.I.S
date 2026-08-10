---
id: ISSUE-060
title: Home hub hardening always-on brain host
status: done
priority: P0
phase: 5
labels: [house, hub]
owner: minimax
claimed_at: 2026-08-08T11:00:03Z
blocked_by: [ISSUE-010]
acceptance:
  - Documented run mode for always-on home host
  - Brain survives reboot via service/script notes
  - Health check remote from phone on LAN
---

## Context

Rick-layer foundation: house stays awake.

## Notes

- [2026-08-08T11:08:47Z] Marked done


- [2026-08-08T11:08:47Z] Verified acceptance already satisfied by existing docs/HOME_HUB.md (run modes, systemd/Task Scheduler reboot survival, remote /health check from phone on LAN) + scripts/run_brain.py + ADR-0018. Removed a redundant docs/HOUSE.md created during work; kept canonical HOME_HUB.md. run_brain.py passes py_compile.


- [2026-08-08T11:06:44Z] Marked done


- [2026-08-08T11:06:44Z] verified: doc links OK, py_compile OK, /health smoke test returns status ok


- Claimed by minimax at 2026-08-08T11:00:03Z
- [2026-08-08T11:05:00Z] Done by minimax: Added `docs/HOME_HUB.md` (always-on run mode, reboot survival via systemd + Windows Task Scheduler, remote LAN `/health` check + troubleshooting), `scripts/run_brain.py` (production launcher, no `--reload`), ADR-0018, and registered doc in DOCS_MAP + ROADMAP. Verified: `verify_doc_links.py` OK, `py_compile` OK, `/health` smoke test returns `status: ok`.
