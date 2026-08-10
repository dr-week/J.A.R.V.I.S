---
id: ISSUE-075
title: Warn when default pairing secret in use
status: done
priority: P1
phase: 0
labels: [auth, security, backend, starter]
owner: minimax2
claimed_at: 2026-08-08T10:00:37Z
blocked_by: []
acceptance:
  - Brain logs a clear WARNING at startup when JARVIS_PAIRING_SECRET is still the default change-me
  - SECURITY.md documents the warning and how to set a real secret in .env
---

## Context

Small security hygiene — helps operators not run production with the stub secret. **Good first task for `minimax2` (low scope, one backend file + one doc).**

## Work

- [ ] In `backend/app/main.py` lifespan (or `config.py` on import), detect default `PAIRING_SECRET`
- [ ] Log WARNING to console (not a secret value)
- [ ] Short SECURITY.md subsection

## Lane

- Touch only: `backend/app/main.py` and/or `backend/app/config.py`, `docs/SECURITY.md`
- Do **not** edit `clients/android/`, `hands/registry.py`, or pairing logic beyond the warning

## Notes

- [2026-08-08T10:06:31Z] Marked done


- [2026-08-08T10:06:22Z] Implemented startup SECURITY WARNING in backend/app/main.py lifespan (_warn_default_secrets) when JARVIS_PAIRING_SECRET or JARVIS_JWT_SECRET is still the default 'change-me'. Added 'Default pairing secret warning' subsection to docs/SECURITY.md with .env setup example. Verified: py_compile passes; smoke test shows warning on default, silent on custom secret.


- Claimed by minimax2 at 2026-08-08T10:00:37Z


Created for parallel **minimax2** seat while main agents ship larger issues.
