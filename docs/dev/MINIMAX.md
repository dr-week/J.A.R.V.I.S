# MiniMax (Blackbox) — agent rules

**Owner id (always):** `minimax`

These rules apply to **Blackbox MiniMax** on the Jarvis repo. Other agents may read this for handoffs. Portable dev skill: [skills/jarvis-dev/SKILL.md](../../skills/jarvis-dev/SKILL.md). Blackbox mirror: [.blackbox/skills/jarvis-dev/SKILL.md](../../.blackbox/skills/jarvis-dev/SKILL.md).

Related: [PARALLEL.md](PARALLEL.md) · [FEEDBACK_LOOP.md](FEEDBACK_LOOP.md) · [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md) · [PARTNERSHIP.md](../PARTNERSHIP.md) · [DOCS_MAP.md](../DOCS_MAP.md) · [AGENTS.md](../../AGENTS.md)

---

## 1. Mission

Ship **one issue at a time** as complete **vertical slices**: code that meets acceptance, docs/protocol updates when behavior changes, board updated via `devloop`, honest handoff to the human and other agents.

MiniMax is optimized for: **backend + one client lane + docs + devloop done** (proven: ISSUE-032).

---

## 2. Session start (mandatory)

Run in repo root (`D:\CODES\jarvis` or clone root):

```bash
python scripts/devloop.py sync --owner minimax
python scripts/devloop.py loop
python scripts/devloop.py inbox --owner minimax
python scripts/devloop.py status
```

Only then:

```bash
python scripts/devloop.py next --owner minimax
python scripts/devloop.py claim ISSUE-XXX --owner minimax
python scripts/devloop.py brief --owner minimax
```

Open `docs/board/LIVE_BRIEF.md` — **regenerated each run** (issue, lanes, inbox, fingerprint).

**Do not** implement before `claim`. **Do not** claim an issue owned by another worker without `--steal` and human approval.

---

## 3. Hard rules (never break)

| # | Rule |
|---|------|
| R1 | **One NOW issue** per `minimax` at a time |
| R2 | **Always `--owner minimax`** on claim, release, prompt |
| R3 | **Stay in SCOPE** — [SCOPE.md](../SCOPE.md); no invented features outside [REQUIREMENTS.md](../REQUIREMENTS.md) |
| R4 | **Do not edit another owner's claimed issue paths** without coordination in issue Notes or `devloop say` |
| R5 | **Max 2 workers** on board — check NOW before touching shared hot files |
| R6 | **Secrets only in `.env`** — never commit keys, tokens, or `brain.db` with private data |
| R7 | **Single tool registry** — `backend/app/hands/registry.py` only; do not add duplicate registries or dead `mind/registry.py`-style files |
| R8 | **Phase gate** — do not start Phase N product work while prior phase P0s block the issue (read issue `blocked_by`) |
| R9 | **No drive-by refactors** — change only what the issue needs; no repo-wide "cleanup" unless the issue says so |
| R10 | **No fake done** — every acceptance bullet must be true before `devloop done` |

---

## 4. Parallel lanes (where MiniMax goes)

| Safe for MiniMax | Avoid (other worker / lane) |
|------------------|-------------------------------|
| `clients/windows/**` when issue is Windows | `clients/android/**` on a Windows-only issue |
| `clients/android/**` when issue is Android | `clients/windows/**` on Android-only issue |
| `backend/app/sync/**`, `hands/**`, `api/**` when issue requires | Same files while another agent's issue owns them |
| `docs/SYNC_PROTOCOL.md`, client READMEs | `scripts/devloop.py` unless issue is devloop |
| One plugin package under `tools/` per issue | Another worker's plugin directory |

**Default pairing:** Windows bridge work ↔ Android bridge work on **different** issues (`032` / `033`), not the same session.

**Windows Flet UI (mini queue):** [MINIMAX_UI.md](MINIMAX_UI.md) — issues **077–079**, **089–091**; edit `ui_gui.py` unless the issue says `client.py` only. **All UI:** [DESIGN.md](../DESIGN.md) first.

---

## 5. Implementation patterns (copy, don't reinvent)

### Client-executor tools (device bridge)

1. Register tool in `backend/app/hands/registry.py` with `executor: "client"`, risk per [TOOL_SCHEMA.md](../TOOL_SCHEMA.md) / gate.
2. Dispatch via existing `_dispatch_to_device` / `run_tool` — do not bypass confirmation or `action_log`.
3. WebSocket protocol: [SYNC_PROTOCOL.md](../SYNC_PROTOCOL.md) — `register`, `tool_execute`, `tool_result`, `request_id` echo.
4. Client: connect `/ws`, register `device_id`, loop on `tool_execute`, reply `tool_result`.
5. Update protocol doc + client README when adding a tool row.

**Reference implementation:** ISSUE-032 — `windows_open`, `clients/windows/device_bridge.py`, `client.py --bridge`.

### Coding Style (Small-Context AI Friendly)

Write code that is easy for small-context AIs (like MiniMax) to read, fix, and maintain:
1. **Small Files:** Keep modules and files short and highly cohesive. Do not create 1,000-line monolithic files.
2. **Clear Comments:** Write explicit docstrings for classes and functions explaining *why* something is done, not just *what*.
3. **Flat Logic:** Avoid deeply nested `if/else` or loops. Return early to keep the indentation shallow.
4. **Isolated Changes:** When fixing bugs, isolate the fix to the smallest scope possible.

### Backend

- FastAPI routers live in `backend/app/api/`; include in `main.py` if new.
- Soul data: SQLite via existing modules — do not add a second DB without ADR.

### Docs / ADR

- Behavior or API change → update relevant doc.
- Architecture choice → append [DECISIONS.md](../DECISIONS.md).

---

## 6. Verification before `done`

Minimum for code issues:

```bash
python -m py_compile <changed-python-files>
```

When the issue touches device bridge:

- Brain running; client in `--bridge` (or Android equivalent).
- Tool registered: visible via `GET /hands/actions` or registry check per issue.
- Happy path + safe errors (empty target, offline device, unknown tool).

Tick [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md) mentally; add issue Notes with what you verified.

---

## 7. Finish + handoff (mandatory)

```bash
python scripts/devloop.py update ISSUE-XXX --note "what shipped + how verified"
python scripts/devloop.py done ISSUE-XXX
python scripts/devloop.py say --from minimax --to cursor --kind done --issue ISSUE-XXX -- "1-3 sentence summary; paths touched; smoke test steps"
python scripts/devloop.py refresh
```

If blocked: `release` or `update` with blocker — do not leave a silent half-claim.

---

## 8. Product behavior (persona + trust)

When touching assistant behavior, read [PERSONA.md](../PERSONA.md):

- Execute > explain; report failures honestly.
- Confirmations per `hands/gate.py` — do not weaken confirm_always for money/messages/delete.
- Persona name from config, not hardcoded "Jarvis" in user strings.

---

## 9. What MiniMax should not do

- Claim multiple NOW issues.
- Touch `clients/android` and `clients/windows` in one issue unless issue explicitly spans both.
- Replace httpx WebSocket with imaginary APIs — use `websockets` on Windows client (032 lesson).
- Mark `done` without acceptance.
- Commit `.env`, credentials, or user data.
- Start Phase 5 house / Phase 4 voice without board phase exit and issue.

---

## 10. Current priority (update when board moves)

Check `python scripts/devloop.py who` and `next --owner minimax` — do not trust stale text.

**Main `minimax`:** **ISSUE-101** (Flutter Field epic) — finish via slices **112–114** or verify `tool_execute` on Windows desktop.  
**033 Android bridge:** done.

**`minimax2` (free NOW slot):** [MINIMAX_QUEUE.md](MINIMAX_QUEUE.md) — start **109** or **112** (one file each).

If NOW is 2/2, main minimax **waits** or human releases a slot — do not `--steal` without human OK.

---

## 11. Prompt template (paste for Blackbox — Main MiniMax)

```text
Owner minimax. EXECUTE MODE: do not ask to approve the plan.
Work order = docs/board/LIVE_BRIEF.md + claimed issue acceptance (already approved).
Run: devloop sync --owner minimax && devloop brief --owner minimax
If NOW slot free: claim next from LIVE_BRIEF (often **101** close or **107** / **142** for standard tier).
Implement immediately. py_compile + smoke test. done + say to cursor. No "shall I proceed?"
```

---

## 11b. Prompt template (Mini Coder 2 only)

## 13. Multiple Blackbox MiniMax coders (mini + main)

**Rule: one repo owner id per AI seat.** Never share `minimax` between two Blackbox sessions — they will fight over the same claim.

| Seat | Owner id | Typical role |
|------|----------|----------------|
| MiniMax **main** | `minimax` | Field epic **101**, bridges, vertical slices |
| MiniMax **mini** | `minimax2` or `minimax-mini` | Smaller parallel issue when a **free NOW slot** exists |

### How we know who is which

| Signal | Example |
|--------|---------|
| Issue frontmatter `owner:` | `minimax` vs `minimax2` |
| `docs/board/NOW.md` | Owner column |
| `python scripts/devloop.py who` | `minimax -> ISSUE-101` |
| `devloop say --from minimax2` | Feedback log shows sender |
| `LIVE_BRIEF.md` | Generated with `--owner minimax2` |

**You (human)** assign ids once in the Blackbox project prompt: *“Your owner id is minimax2. Never use minimax.”*

### What to give the mini coder **when a slot is free**

Max **2** NOW issues. Check `devloop who` first.

| Task | Issue | Owner | Difficulty |
|------|-------|-------|------------|
| **Scripts / quality** | **115** pytest, **116** mypy | `minimax2` | Low–med |
| **Config** | **122**, **124** | `minimax2` | Low |
| **Parent epic** | **101** close after Windows smoke | `minimax` | Medium |
| **Field confirm** | **142** (after **101**) | `cursor` / `minimax` | Medium |
| **Avoid** | **130–132** Velocity, **136+** Phase 8 | standard agent | Large |

Queue detail: [MINIMAX_QUEUE.md](MINIMAX_QUEUE.md).

| If this is in NOW | Give mini (`minimax2`) | Lane |
|-------------------|------------------------|------|
| **101** on Flutter Field | **112** or **109** | `clients/flutter/lib/ui/field` or `scripts/` |
| Another worker on `clients/web/` | **109–111** | scripts/docs only |

**Do not** put two MiniMax seats on the same issue or the same client folder.

### Mini coder session (paste)

```bash
python scripts/devloop.py who
python scripts/devloop.py sync --owner minimax2
python scripts/devloop.py inbox --owner minimax2
python scripts/devloop.py next --owner minimax2
python scripts/devloop.py claim ISSUE-XXX --owner minimax2
python scripts/devloop.py brief --owner minimax2
```

```text
You are MiniMax mini. Owner id: minimax2 (NOT minimax).
EXECUTE MODE: no plan approval — claimed issue acceptance + MINIMAX_QUEUE wave is the plan.
devloop who → claim with minimax2 → brief → code → done.
```

---

## 12. Escalation

- Unclear acceptance → `devloop say --from minimax --to cursor --kind question --issue ISSUE-XXX -- "…"`
- Shared file conflict → stop; do not merge-edit; message other owner
- Scope creep → propose new issue in say; do not expand current issue silently
