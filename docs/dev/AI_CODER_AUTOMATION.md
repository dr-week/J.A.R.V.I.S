# AI coder — what agents forget + what Jarvis automates

**Principle:** The coding AI is not the safety system. **Orchestrator + gates + reviewer** are. Aligns with [SELF_IMPROVEMENT_LOOP.md](SELF_IMPROVEMENT_LOOP.md) (mutator ≠ evaluator) and [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md).

**Read first:** [AGENTS.md](../../AGENTS.md) · [ARCHITECTURE.md](../ARCHITECTURE.md) · [AI_CODE_STRUCTURE.md](AI_CODE_STRUCTURE.md) · issue **Lane** · `devloop brief --owner YOU`

---

## 1. Forty common gaps → Jarvis automation map

| # | Often forgotten | Automate with (Jarvis today) | Backlog / issue |
|---|----------------|------------------------------|-----------------|
| 1 | Read architecture first | **Skill read order** + `ARCHITECTURE.md`, `SCOPE.md` | — |
| 2 | Check utilities before duplicating | `python scripts/index_repo.py map` → [CODE_MAP.md](../CODE_MAP.md) | Repo Navigator **085** ✅ |
| 3 | Update documentation | `verify_doc_links.py`; [DOCS_MAP.md](../DOCS_MAP.md) checklist | pre-commit **108** ✅ |
| 4 | Update types/interfaces | `mypy backend/app/api` | **116** |
| 5 | Update imports/exports | `ruff check` | **110** ✅ |
| 6 | Remove dead code | `ruff` (partial) | manual review |
| 7 | Unused imports | `ruff check` | **110** ✅ |
| 8 | Error states | pytest + manual smoke | **115** |
| 9–10 | Loading / empty UI | Web/Field manual; no E2E yet | **106** PWA; Playwright later |
| 11 | Null/undefined | TS `tsc`; mypy API | **116** |
| 12 | Input validation | Pydantic on API bodies | extend **116** |
| 13–14 | Edge + regression tests | `pytest backend/tests` | **115** |
| 15 | Responsive UI | [DESIGN.md](../DESIGN.md); manual | browser MCP optional |
| 16 | Accessibility | not automated | future a11y issue |
| 17 | Performance | not automated | eval/ fitness later |
| 18 | Security | [SECURITY.md](../SECURITY.md); no secrets in repo | review-agent skill; **107** WS auth |
| 19 | Env vars | `check_dev_env.py`; **122** Settings | **122**, **124** |
| 20 | Dependencies | `pyproject.toml` / lockfiles; human PR | **127** ADR before Celery |
| 21 | Build check | `npm run build` (web); `flutter analyze` | **120** CI |
| 22 | Console errors | `smoke_web.py` (API only) | Playwright later |
| 23 | Network failures | smoke_web connection hints | **115** httpx tests |
| 24 | DB migrations | SQLite `init_db` in lifespan; no alembic yet | **123** |
| 25 | Seed/test data | pytest fixtures | **115** |
| 26 | API docs | FastAPI `/docs` from code | keep routers thin |
| 27 | Changelog | `devloop done` → [CHANGELOG.md](../board/CHANGELOG.md) (manual append) | optional bot |
| 28 | Git diff | Human or Bugbot / review-agent skill | — |
| 29 | Unrelated file edits | Issue **## Lane** + `devloop verify` | **scope diff** (below) |
| 30 | Duplicate functionality | CODE_MAP + grep; reviewer AI | similarity scan future |
| 31 | Break APIs | pytest contract tests | **115**+ |
| 32 | Temp files | `.gitignore`; review | — |
| 33 | Logging | **124** loguru | **124** |
| 34 | Telemetry | action_log, health | **125** vitals |
| 35 | Rollback | git branch; no auto-revert | experiment branches |
| 36 | Over-engineering | [SCOPE.md](../SCOPE.md); small slices | task packet size |
| 37 | Large files | [AI_CODE_STRUCTURE.md](AI_CODE_STRUCTURE.md) &lt;200 LOC target | split in review |
| 38 | Context limits | Mini queue, **SMALL_AI_PARTS.md** | `devloop next --tier mini` |
| 39 | Naming | `ruff`; conventions in lane docs | — |
| 40 | Final verification | **Definition of done** + commands below | pre-commit **108** ✅ |

---

## 2. Before coding (automate this sequence)

```text
devloop sync --owner YOU
devloop brief --owner YOU          # LIVE_BRIEF + inbox
Read ISSUE-XXX + ARCHITECTURE + lane surface doc
devloop verify ISSUE-XXX           # paths exist
index_repo / CODE_MAP              # find existing symbols
devloop claim ISSUE-XXX --owner YOU
```

| Automation | Script / doc |
|--------------|----------------|
| Repository inspection | `scripts/index_repo.py`, [CODE_MAP.md](../CODE_MAP.md) |
| Task decomposition | Board issues + [SMALL_AI_PARTS.md](SMALL_AI_PARTS.md) |
| Architecture mapping | [ARCHITECTURE.md](../ARCHITECTURE.md), [backend/app/README.md](../../backend/app/README.md) |
| Impact / risk | `devloop verify`; human for cross-lane |
| Next task pick | `devloop next` / Board Copilot **086** ✅ |

---

## 3. During coding — scope enforcement (task packet)

Issue **Lane** = allowed edit surface. Today:

```bash
python scripts/devloop.py verify ISSUE-XXX   # lane paths exist (not: diff ⊆ lane)
```

**Planned:** `devloop verify ISSUE-XXX --diff` — fail if `git diff --name-only` leaves lane (see **ISSUE-111** extension or new mini issue).

Task packet fields (venture or improve):

```yaml
edit_paths: [...]
do_not_edit: [...]
```

Same idea as [BUSINESS_OPERATOR.md](../BUSINESS_OPERATOR.md) Layer 7 · [SELF_IMPROVEMENT_LOOP.md](SELF_IMPROVEMENT_LOOP.md) IMPROVE-* packets.

---

## 4. Test gate pipeline (target state)

```text
CODE CHANGE
    ↓
ruff check backend scripts          # today
    ↓
pytest backend/tests                # ISSUE-115
    ↓
mypy backend/app/api                # ISSUE-116
    ↓
verify_doc_links (if docs)          # today
    ↓
smoke_web (if brain/API)            # local, brain up
    ↓
devloop done ISSUE-XXX              # blocks on unchecked [ ]
```

**CI (no brain on runner):** [ISSUE-120](../board/issues/ISSUE-120.md) — `verify_doc_links` + `check_dev_env` only.

---

## 5. Bug-fix loop (max 3 attempts)

```text
TEST FAIL → read traceback → patch → re-run → (×3) → escalate human
```

Jarvis does **not** auto-loop fixes in CI yet. Agents should:

1. Run pytest/ruff locally after each fix.
2. Post `devloop say --kind block` if stuck after 3 tries.
3. Never `--force` `done` to hide failing tests.

---

## 6. Coder ≠ reviewer

| Role | Jarvis |
|------|--------|
| **Coder** | Claimed agent (`cursor`, `minimax`, …) |
| **Reviewer** | Second agent, `devloop say` handoff, or Cursor **Bugbot** / review-agent skill |
| **Evaluator** (self-improve) | pytest/smoke/fitness — not the mutator ([ADR-0024](../DECISIONS.md)) |

Do not merge your own issue without a second pass when changing security, auth, or gate code.

---

## 7. Git / PR automation

| Step | Today | Automated later |
|------|--------|-----------------|
| Branch | Agent creates `experiment/*` or feature branch | — |
| Commit message | Human/agent; user rule: commit when asked | — |
| Push/PR | `.github/workflows/dev-smoke.yml` (docs, env, ruff, pytest) | web `npm run build` |
| PR | `gh pr create` when user asks | review bots |
| Board | `devloop done` → sync → LIVE_PLAN | orchestrator draft issues (future) |

---

## 8. Documentation automation

After behavior/API change:

- [ ] Issue acceptance + notes
- [ ] [DOCS_MAP.md](../DOCS_MAP.md) cluster if mirrored docs touched
- [ ] `python scripts/verify_doc_links.py`
- [ ] ADR in [DECISIONS.md](../DECISIONS.md) if architecture changed

**Generated (do not hand-edit):** `LIVE_PLAN.md`, `LIVE_BRIEF.md`, `BACKLOG.md` — `devloop sync`.

---

## 9. Project management automation (already partial)

```text
devloop refresh → next → claim → implement → verify → done → sync
         ↓
FEEDBACK.md / feedback.jsonl (say / claim / done)
```

Venture packets: `docs/venture/experiments/` (when used) · CEO loop Phase **8** — not product NOW.

---

## 10. Self-healing factory (north star)

```text
ORCHESTRATOR (devloop + board + human CEO)
        ↓
TASK PACKET (ISSUE-XXX)
        ↓
CODER AGENT
        ↓
SCOPE (Lane + verify)
        ↓
LINT / TEST / DOCS
        ↓
REVIEWER (separate agent)
        ↓
PASS → devloop done → CHANGELOG / sync
FAIL → fix (≤3) or escalate
```

Full mutation/evolution: [SELF_IMPROVEMENT_LOOP.md](SELF_IMPROVEMENT_LOOP.md) · `eval/` harness.

---

## 11. Priority build order (Jarvis repo)

### Critical (do first)

1. **115** pytest + happy-path API tests  
2. **116** mypy API  
3. **120** GitHub Action (docs/env/lint/pytest) ✅ workflow in repo  
4. **Scope diff** on `devloop verify`  
5. **122/124** config + logging  
6. **142** Field confirm (product gate)  

### Very useful

7. pre-commit optional **ruff** hook  
8. `npm run build` in CI for web  
9. Independent review on PRs (Bugbot / second agent)  
10. Secret scan in CI (gitleaks or similar) — ADR if added  

### Advanced

11. Auto task packets from eval failures  
12. Playwright smoke for web  
13. n8n / webhooks (**127** ADR)  
14. Self-improvement `run_eval.py`  

---

## 12. Agent preflight (copy-paste)

```bash
python scripts/devloop.py sync --owner YOUR_ID
python scripts/devloop.py brief --owner YOUR_ID
python scripts/devloop.py verify ISSUE-XXX
python scripts/check_dev_env.py
# after code:
ruff check backend scripts
pytest backend/tests
python scripts/verify_doc_links.py
python scripts/smoke_web.py
python scripts/devloop.py done ISSUE-XXX
```

---

## Related

[FEEDBACK_LOOP.md](FEEDBACK_LOOP.md) · [PROCESS.md](PROCESS.md) · [OSS_DEV_PLAN.md](OSS_DEV_PLAN.md) · [skills/jarvis-dev/SKILL.md](../../skills/jarvis-dev/SKILL.md)
