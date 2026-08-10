---
id: ISSUE-076
title: verify_doc_links script for README and AGENTS
status: done
priority: P2
phase: D0
labels: [docs, tooling, starter]
owner: minimax2
claimed_at: 2026-08-08T10:23:56Z
blocked_by: []
acceptance:
  - scripts/verify_doc_links.py checks relative markdown links in README.md AGENTS.md and docs/dev/*.md
  - Exits 0 when links resolve; prints broken paths on failure
  - docs/dev/PROCESS.md mentions how to run the script
---

## Context

Automates part of ISSUE-072. **Good second task for `minimax2`** — Python only, no product behavior change.

## Work

- [ ] Parse `](path)` style relative links from listed markdown files
- [ ] Resolve from repo root; skip http(s) and anchors-only
- [ ] `python scripts/verify_doc_links.py` from repo root

## Lane

- Touch only: `scripts/verify_doc_links.py`, `docs/dev/PROCESS.md` (one line)
- Optional: tick progress on ISSUE-072 Notes — do not mark 072 done unless all its acceptance met

## Notes

- [2026-08-08T10:26:55Z] Marked done


- [2026-08-08T10:26:47Z] Added scripts/verify_doc_links.py: checks relative markdown links in README.md AGENTS.md docs/dev/*.md from repo root; skips http(s), anchors, and .blackbox mirror; exits 0 when OK, prints broken paths (file:line) and exits 1 on failure. Added 'Verify doc links' section to docs/dev/PROCESS.md. Verified both exit paths; py_compile OK.


- Claimed by minimax2 at 2026-08-08T10:23:56Z


Created for parallel **minimax2** seat.
