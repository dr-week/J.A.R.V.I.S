---
id: ISSUE-085
title: Repo Navigator helper CLI over code index
status: done
priority: P2
phase: D1
labels: [tooling, starter, helpers]
owner: coder-003
claimed_at: 2026-08-08T17:02:18Z
blocked_by: [ISSUE-084]
acceptance:
  - scripts/helpers/repo_nav.py supports find / symbol / doc against data/repo_index.db
  - Output is short (paths + one-line summaries); no full file dumps
  - README or INTERNAL_HELPERS.md documents the three commands
---

## Context

Wave 1 internal helper. Index already exists (`scripts/index_repo.py`, ISSUE-084). This wraps it for agents.

## Lane

- `scripts/helpers/repo_nav.py` (new)
- `scripts/helpers/__init__.py` (empty ok)
- `docs/dev/INTERNAL_HELPERS.md` (usage only)
- Do **not** rewrite `index_repo.py` unless a one-line import fix is required

## Notes

- [2026-08-08T17:03:09Z] Marked done


- [2026-08-08T17:03:09Z] Added read-only repo navigator CLI at scripts/helpers/repo_nav.py; it supports find/symbol/doc against the SQLite index and prints compact path + summary output only.


- Claimed by coder-003 at 2026-08-08T17:02:18Z


Spec: [INTERNAL_HELPERS.md](../dev/INTERNAL_HELPERS.md)
