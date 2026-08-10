---
id: ISSUE-108
title: pre-commit hooks — doc links and dev env check
status: done
priority: P3
phase: D1
labels: [devloop, docs]
owner: cursor
claimed_at: 2026-08-09T19:05:00Z
blocked_by: []
acceptance:
  - .pre-commit-config.yaml runs verify_doc_links.py and check_dev_env.py
  - Documented in docs/dev/DEV_ENV.md
  - Contributors can skip with git commit --no-verify only when documented exception
---

## Context

[DEV_ENV.md](../../dev/DEV_ENV.md) script backlog — catch broken plan links before commit.

## Lane

- `.pre-commit-config.yaml`
- `docs/dev/DEV_ENV.md`

## Work

- [x] Local hooks config (pip install pre-commit && pre-commit install)

## Notes

Skip hook only for emergencies; document in commit message.
