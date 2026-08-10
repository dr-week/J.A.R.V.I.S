# Strategy forward — plan, scripts, and MiniMax-sized work

**Horizon doc:** ties [FUTURE.md](../FUTURE.md) (why) · [STRATEGY.md](../STRATEGY.md) (how we win) · [board/LIVE_PLAN.md](../board/LIVE_PLAN.md) (now).

Regenerate live numbers: `python scripts/devloop.py sync`

---

## 1. Where we are (L3 — Hands)

| Pillar | State |
|--------|--------|
| **One chat UI** | Web (Vite) — sessions shipped (**102**) |
| **Field Body** | Flutter `FieldScreen` + bridge (**112–114** done); **101** closes after Windows `tool_execute` smoke |
| **Device bridges** | Windows (**032**) + Kotlin Android (**033**) |
| **Dev factory** | devloop, smoke_web, ruff, pre-commit, `devloop verify` (**108–111**) |
| **Gaps** | Field confirm UI (**142**), WS auth (**107**), Flutter chat removal (**103**), pytest/mypy (**115–116**) |

**Phase 2 exit (level-up to L4 / Phase 3):** **101** done + **104** done (backend) + **142** (Field confirm) + audited multi-step action (action_log + gate).

---

## 2. Three horizons

### Now (0–2 weeks) — max 2 NOW slots

| Slot | Issue | Owner | Outcome |
|------|-------|-------|---------|
| A | **101** | `minimax` | Field epic closed (Windows smoke) |
| B | *(free)* | `cursor` / `claude` | **115**, **107**, or **142** after **101** |

Parallel mini: **115**, **116**, **106** via `minimax2`.

### Next (phase 2 tail → phase 3 door)

| Order | Issue | Theme |
|-------|-------|--------|
| 1 | **103** | Remove Flutter chat spike files |
| 2 | **107** | Enforce device token on `/ws` |
| 3 | **106** | PWA — web as desktop daily driver |
| 4 | Life plugins | Phase 3 per [ROADMAP.md](../ROADMAP.md) |

### Later (L4–L7)

See [FUTURE.md](../FUTURE.md) level ladder: **Phase 3 Life** (tasks, connectors, semantic memory) → **Voice** → **House** → **SDK**.

**Do not** start Phase 5 house product code until board phase gate clears.

---

## 3. Agent routing (who codes what)

| Agent | Owner id | NOW-sized | Mini / one-file |
|-------|----------|-----------|-----------------|
| Cursor | `cursor` | **107**, **142**, architecture | Review, doc sync |
| Antigravity | `antigravity` | Web polish | `clients/web` slices |
| MiniMax main | `minimax` | **101**, plugins, bridges | **117–118** devloop split |
| MiniMax mini | `minimax2` | — | **115**, **116**, **106**, Flet **077+** |
| Claude | `claude` | Second standard seat | Same lanes as cursor |

```bash
python scripts/devloop.py next --owner minimax2 --tier mini
python scripts/devloop.py verify ISSUE-115
```

Queue tables: [MINIMAX_QUEUE.md](MINIMAX_QUEUE.md) · [MINIMAX.md](MINIMAX.md)

---

## 4. Script & dev-environment roadmap

| Wave | Status | Items |
|------|--------|--------|
| **U** Dev factory | ✅ | smoke_web, ruff, pre-commit, verify |
| **X** Quality | 🔲 | **115** pytest, **116** mypy API |
| **Y-devloop** | Split | **117** core, **118** cmds | [MODULARITY_PLAN.md](MODULARITY_PLAN.md) |
| **Y-config** | 🔲 | **122**, **124** (see [MINIMAX_QUEUE.md](MINIMAX_QUEUE.md) Wave Y) |
| **Z** CI (optional) | Future | **120** GitHub Action; local `smoke_web` stays human/always-on |

**Daily human path:** [DEV_ENV.md](DEV_ENV.md) — `dev_up.ps1` → web dev → `smoke_web.py`.

**Performance rules:** one brain `:8787`, repo-root uvicorn, one chat UI for manual test, `devloop sync` after board edits.

---

## 5. Open-source integrate (don’t reinvent)

| Tool | Purpose | When |
|------|---------|------|
| **pytest** + **pytest-asyncio** | Brain tests | **115** |
| **mypy** | API safety | **116** |
| **Ruff** | Lint/format | ✅ habit |
| **pre-commit** | Doc + env gate | ✅ optional install |
| **uv** | Fast deps | Document in README; use in 115 acceptance |
| **Vite + Oxlint** | Web | ✅ |
| **FastAPI + Uvicorn** | Brain | ✅ |

Locked versions: [OSS.md](../OSS.md).

---

## 6. Dividing work for MiniMax (rules)

1. **One issue = one lane** — `devloop verify ISSUE-XXX` before edit.
2. **`starter` label** + queue entry in `agent_registry.MINI_ISSUE_QUEUE`.
3. **Use `--tier mini`** on `devloop next` — avoids random P1 picks.
4. **Split parents** — template in [SMALL_AI_PARTS.md](SMALL_AI_PARTS.md); example **101** → **112–114**.
5. **No `devloop.py` edits** for mini unless issue says so (**117/118** = main minimax only).

### Suggested mini sequence (Wave X)

1. **119** — pytest deps in `pyproject.toml` only (~15 min)
2. **115** — `backend/tests/test_brain.py`
3. **116** — mypy on `backend/app/api/` only
4. **106** — PWA manifest (web-only)
5. **120** — GitHub dev-smoke (no brain in CI)

---

## 7. Documentation sync (when plan moves)

| Event | Update |
|-------|--------|
| Board / issue done | `devloop sync`, tick acceptance, [board/CHANGELOG.md](../board/CHANGELOG.md) if user-facing |
| Presence change | `PRESENCE_STACKS`, `SYNC_PLAN`, ADR in `DECISIONS.md` |
| Mini queue change | `MINIMAX_QUEUE`, `MINIMAX.md` §10, `agent_registry` queue |
| Strategy shift | This file + `STRATEGY.md` “Where we are” |

Checklist: [DOCS_MAP.md](../DOCS_MAP.md) · links: `verify_doc_links.py`

---

## 8. Risks & anti-patterns

- Duplicate chat in Flutter/Flet — **103** + product Don't in jarvis-product skill.
- Marking `done` with unchecked `- [ ]` — use `update` + verify, or `--force` only when children satisfied.
- `devloop next` without `--tier mini` for **minimax2** — may suggest large **107**/**130** work.
- Brain started from `backend/` only — breaks `tools.*` plugins.

---

## Related

[PLAN_AUDIT.md](PLAN_AUDIT.md) · [SYNC_PLAN.md](SYNC_PLAN.md) · [ROADMAP.md](../ROADMAP.md) · [LAB_STACK.md](LAB_STACK.md) · [PARTNERSHIP.md](../PARTNERSHIP.md)

---

## 9. Further ahead (12–24 months)

| Window | Focus | OSS / outcomes |
|--------|--------|----------------|
| **2026 H2** | Phase 2 exit → Phase 3 | **142** Field confirm, memory search (sqlite-vec), first life plugins |
| **2027 H1** | Voice + PWA default | Whisper/Piper, **106**, wake **126** after Phase 4 gate |
| **2027 H2** | House | HA scenes, room presence sketch |
| **2028+** | SDK + scale | Plugin forge; **127** only if ADR approves queue |

Stark rule: **instrument → harden → then ambient** — see [LAB_STACK.md](LAB_STACK.md).
