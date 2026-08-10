# Internal helpers — narrow agent tooling

**Not a second product.** Script-driven helpers so coding agents waste fewer tokens on search and board orientation.

**Start with two.** Ship others only if they save real time.

Related: [CODE_MAP.md](../CODE_MAP.md) · [DOCS_MAP.md](../DOCS_MAP.md) · [SMALL_AI_PARTS.md](SMALL_AI_PARTS.md) · [index_repo.py](../../scripts/index_repo.py)

---

## Hard rules

1. **Read-only by default** — helpers print advice; they do not edit product code
2. **One helper, one job** — no mega CLI
3. **No hidden long-term memory** — SQLite index is regenerable; board is source of truth
4. **Backed by repo** — index + board docs; no freeform guessing when data is missing
5. **Script-driven** — any agent can run the same commands

---

## Wave 1 (shipped)

### 1. Repo Navigator — `scripts/helpers/repo_nav.py`

| | |
|--|--|
| **Job** | Answer “where is X?” / “what touches Y?” with a short list |
| **Reads** | `data/repo_index.db` (from `index_repo.py`), `docs/CODE_MAP.md` fallback |
| **Does not** | Open whole files into stdout (paths + 1-line summary only) |

**CLI**

```bash
python scripts/index_repo.py rebuild   # if index stale
python scripts/helpers/repo_nav.py find "device bridge"
python scripts/helpers/repo_nav.py symbol windows_open
python scripts/helpers/repo_nav.py doc SYNC
```

**Output (stdout)** — max ~15 lines:

```text
query: device bridge
docs first: docs/SYNC_PROTOCOL.md
code:
  clients/windows/device_bridge.py — …
  backend/app/sync/manager.py — …
```

**Issue:** [ISSUE-085](../board/issues/ISSUE-085.md)

---

### 2. Board Copilot — `scripts/helpers/board_copilot.py`

| | |
|--|--|
| **Job** | Safest next issue + lane for an `--owner` |
| **Reads** | `docs/board/NOW.md`, `NEXT.md`, `LIVE_PLAN.md`, `LIVE_BRIEF.md` (if any), issue frontmatter, `agents.json` |
| **Does not** | Claim or steal issues |

**CLI**

```bash
python scripts/helpers/board_copilot.py --owner coder-003
python scripts/helpers/board_copilot.py --owner minimax2 --tier mini
```

**Output:**

```text
slots: 1/2 free
your NOW: (none)
suggest: ISSUE-085 — Lightweight …
lane: scripts/helpers/, docs/dev/INTERNAL_HELPERS.md
avoid: clients/windows/ (if another NOW owns it)
why: starter + unblocked + no path overlap with NOW owners
```

**Issue:** [ISSUE-086](../board/issues/ISSUE-086.md)

---

## Wave 2 (later — only if Wave 1 helps)

| Helper | Script (proposed) | Job |
|--------|-------------------|-----|
| Doc Sync | `helpers/doc_sync.py` | Flag DOCS_MAP mirrors / stale ADR pointers |
| UI Slice | `helpers/ui_slice.py` | Tiny Flet pattern hints (read-only snippets) |
| Test Helper | `helpers/test_hint.py` | Smallest verify: `py_compile`, smoke cmds |
| Context Summarizer | `helpers/summarize.py` | Folder/issue → ≤40-line brief |
| Discovery | fold into `repo_nav` | Do not split unless needed |

Do **not** open Wave 2 issues until Wave 1 has been used for a week and proves useful.

---

## Layout

```text
scripts/
  index_repo.py          # exists (ISSUE-084)
  helpers/
    __init__.py          # empty
    repo_nav.py          # ISSUE-085
    board_copilot.py     # ISSUE-086
data/
  repo_index.db          # gitignored regenerable
docs/
  CODE_MAP.md            # generated
  dev/INTERNAL_HELPERS.md  # this file
```

Ensure `data/` is in `.gitignore` if not already.

---

## Efficiency target

| Without helpers | With Wave 1 |
|-----------------|-------------|
| 5–15 greps / session start | 1–2 helper calls |
| Re-read whole modules for orientation | Paths + summaries only |
| Guess next issue | Board copilot + `who` |

Goal: **~20–30% fewer search/read tool calls** on agent sessions — not a new “AI platform.”

---

## Assign

| Issue | Tier | Parallel with |
|-------|------|----------------|
| **085** Repo Navigator | mini / starter | docs-only or board-only work |
| **086** Board Copilot | mini / starter | **085** (different files under `helpers/`) |

Safe pair: **085** + **086** once a NOW slot frees (or one after the other).
