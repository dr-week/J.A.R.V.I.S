---
id: ISSUE-087
title: Implement security and robustness fixes from MiniMax review
status: done
priority: P1
phase: 0
labels: [security, tech-debt]
owner: antigravity
claimed_at: 2026-08-08T17:22:38Z
blocked_by: []
acceptance:
  - CORS origins restricted or made configurable
  - Default secrets in config.py throw an explicit error or warning in prod
  - int() cast in config.py for port handles ValueError safely
---

## Context
MiniMax performed a code review and identified several low-hanging security and robustness improvements:
1. Wildcard CORS in `main.py` is risky.
2. Default JWT/Pairing secrets in `config.py` can leak into prod.
3. Unvalidated `int()` cast on port env var crashes ungracefully.

## Notes

- [2026-08-08T17:23:26Z] Marked done


- [2026-08-08T17:23:19Z] Fixed CORS wildcard, default secrets, and port int() casting as per MiniMax review


- Claimed by antigravity at 2026-08-08T17:22:38Z
