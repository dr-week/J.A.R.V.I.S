# Work parts — small AI / parallel lanes

**Rule:** Each row = **one claim**, **one session**, **listed files only**. Use `devloop onboard --tier mini` for new coders.

Manager: `python scripts/devloop.py who` · `python scripts/devloop.py agents`

Related: [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) · [PARALLEL.md](PARALLEL.md)

---

## How to assign

```bash
python scripts/devloop.py onboard --tier mini --platform blackbox --display-name "Coder N"
python scripts/devloop.py claim ISSUE-XXX --owner minimax3
python scripts/devloop.py brief --owner minimax3
```

Issue must have label **`starter`**. Big epics stay on standard tier (`minimax`, `cursor`, `antigravity`).

---

## Part map (current)

### Tier **mini** — docs, one file, tiny scripts

| Part | Issue | Touch only | Done when |
|------|-------|------------|-----------|
| A | **072** | `scripts/verify_doc_links.py`, docs | Links check passes |
| **N1** | **085** | `scripts/helpers/repo_nav.py` | find/symbol/doc CLI over index |
| **N2** | **086** | `scripts/helpers/board_copilot.py` | next issue + lane for `--owner` |
| B | **077** | `docs/DECISIONS.md` | ADR: Flet replaces Textual for Windows UI |
| C | **078** | `clients/android/README.md` | Bridge section mirrors Windows README (docs only) |
| D | **079** | `docs/ARCHITECTURE.md`, `docs/OSS.md` | Presence layer mentions Flet, not Textual TUI |
| E | **080** | `backend/app/api/hands.py` or `action_log` read | `GET` last N audit rows (read-only) |

### Tier **mini2** — helpers, docs, and one-file UI support

| Part | Issue | Touch only | Done when |
|------|-------|------------|-----------|
| M | **085** | `scripts/helpers/repo_nav.py` | find/symbol/doc over the repo index |
| N | **086** | `scripts/helpers/board_copilot.py` | next issue + lane for `--owner` |
| O | **079** | `docs/ARCHITECTURE.md`, `docs/OSS.md` | Flet Windows presence wording is current |
| P | **081** | `clients/windows/client.py` | device id + bridge status visible |
| Q | **082** | `clients/windows/ui_gui.py` | reconnect button if health fails — **done** |
| R | **089** | `clients/windows/client.py` (`bridge_loop` only) | Bridge: connected after WS ack |
| S | **090** | `clients/windows/ui_gui.py` | New chat → new session_id |
| T | **091** | `clients/windows/ui_gui.py` | LLM-off hint when `llm_ready` false |

### Tier **mini+** — one feature slice, still no core refactors

| Part | Issue | Touch only | Done when |
|------|-------|------------|-----------|
| F | **081** | `clients/windows/client.py` | Flet: show `device_id` + bridge thread alive in status bar |
| G | **082** | `clients/windows/ui_gui.py` | Reconnect — **done** |
| H | **083** | `tools/tasks/` scaffold | Empty plugin package + `register` one stub tool `tasks_ping` |

### Tier **standard** — full vertical slices (main MiniMax / Antigravity)

| Part | Issue | Who | Notes |
|------|-------|-----|-------|
| I | **040** | `minimax` / `antigravity` | Full tasks plugin — **not** mini |
| J | **041** | parallel plugin | Reminders sample |
| K | **051** | antigravity | Tray / quick tile (after Flet base) |
| L | **042** | standard | First connector slot |

---

## Parallel combos (safe at once)

| Slot 1 | Slot 2 | Why safe |
|--------|--------|----------|
| **085** (repo_nav) | **086** (board_copilot) | Different helper files |
| **072** (scripts/docs) | **077** (DECISIONS only) | No overlap |
| **078** (android README) | **081** (windows client) | Different trees |
| **080** (backend GET) | **079** (architecture docs) | API vs docs |
| **083** (`tools/tasks`) | **080** (hands API) | Different dirs |

**Avoid parallel:** two agents on `clients/windows/client.py` or both on `hands/registry.py`.

---

## Splitting a big issue (template)

When a P0/P1 is too large for mini AI:

1. Parent stays in backlog (e.g. **040**).
2. Add **starter** children: scaffold → one tool → tests → docs.
3. Parent `done` only when children + acceptance met.

---

## Queue for `devloop onboard --tier mini`

Updated in `scripts/agent_registry.py` → `MINI_ISSUE_QUEUE`.

Preferred order: **109** → **110** → **112** → **113** → **114** → **108** → legacy **077** wave.

Full waves: [MINIMAX_QUEUE.md](MINIMAX_QUEUE.md).

**Windows UI wave:** [MINIMAX_UI.md](MINIMAX_UI.md) (Flet lane for `minimax` / `minimax2`).

Helpers spec: [INTERNAL_HELPERS.md](INTERNAL_HELPERS.md).

Minimax 2 bias: prefer helper/doc/UI one-file issues before touching shared backend runtime. If a task can be split into a helper or docs slice, do that first.

---

## After each part

```bash
python scripts/devloop.py update ISSUE-XXX --note "verified: ..."
python scripts/devloop.py done ISSUE-XXX
python scripts/devloop.py sync
```
