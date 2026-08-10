# Task / issue schema

Each issue is `docs/board/issues/ISSUE-NNN.md` with YAML frontmatter:

```yaml
---
id: ISSUE-001
title: Short imperative title
status: backlog   # backlog | now | blocked | done
priority: P0      # P0 | P1 | P2
phase: D0         # D0 | D1 | 0 | 1 | 2 | 3 | 4 | 5 | 6
labels: [docs, agents]
owner: ""         # cursor | antigravity | claude | human id
claimed_at: ""
blocked_by: []
acceptance:
  - Measurable outcome 1
  - Measurable outcome 2
---
```

## Body sections (recommended)

```markdown
## Context
Why this exists.

## Work
- [ ] Step

## Notes
Progress log (also via `devloop update`).

## Links
Related docs / PRs.
```

## Status meanings

| Status | Meaning |
|--------|---------|
| `backlog` | Ranked later |
| `now` | Active focus |
| `blocked` | Waiting on `blocked_by` or external |
| `done` | Acceptance met; listed in DONE.md |

## Priority

- **P0** — phase gate / blocker
- **P1** — important inside phase
- **P2** — polish / optional
