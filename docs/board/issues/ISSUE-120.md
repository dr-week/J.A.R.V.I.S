---
id: ISSUE-120
title: GitHub Action dev-smoke workflow
status: backlog
priority: P3
phase: D1
labels: [dev, starter, scripts]
owner:
claimed_at:
blocked_by: []
acceptance:
  - .github/workflows/dev-smoke.yml runs on push/PR
  - Steps include verify_doc_links.py and check_dev_env.py
  - Optional smoke_web only when documented as skipped without brain
---

## Context

Wave Z in [OSS_DEV_PLAN.md](../../dev/OSS_DEV_PLAN.md). No brain in CI — do not fail on port 8787.

## Lane

- `.github/workflows/dev-smoke.yml`
- `docs/dev/DEV_ENV.md`

## Work

- [x] Workflow file with Python setup + doc links + env check
- [x] Ruff + pytest (health smoke, no live brain)
- [x] Note in DEV_ENV that full smoke_web is local only
