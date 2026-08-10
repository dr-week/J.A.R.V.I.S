# Definition of done

**Doc sync:** [DOCS_MAP.md](../DOCS_MAP.md)

Before `devloop done`:

## Required

- [ ] All issue `acceptance` items true
- [ ] No new secrets committed
- [ ] SCOPE respected
- [ ] If public behavior/API/architecture changed: docs and/or ADR updated
- [ ] Progress notes captured on the issue
- [ ] Related checklist items in issue body ticked

## For UI / Presence (`clients/web`, `clients/flutter`, `clients/windows` GUI)

- [ ] Read [DESIGN.md](../DESIGN.md) + lane surface doc before coding
- [ ] No duplicate brand, status zone, or primary send control
- [ ] Issue **Lane** lists the surface doc path

## For code issues (Phase 0+)

- [ ] Preflight + gate checklist: [dev/AI_CODER_AUTOMATION.md](AI_CODER_AUTOMATION.md) §12
- [ ] `python scripts/devloop.py verify ISSUE-XXX` before editing (lane paths exist)
- [ ] `python scripts/check_dev_env.py` passes (or warnings only)
- [ ] `python scripts/verify_doc_links.py` if docs touched
- [ ] Obvious happy-path verified
- [ ] Failures are visible (errors not swallowed)

## For docs issues

- [ ] Links resolve inside repo
- [ ] AGENTS.md still accurate if entrypoints changed
- [ ] Mirrored files updated per [DOCS_MAP.md](../DOCS_MAP.md) (skills, MINIMAX, `.blackbox/RULES.md`)
