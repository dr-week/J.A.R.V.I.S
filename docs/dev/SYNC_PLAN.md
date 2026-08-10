# Sync plan — docs, board, and product

How Jarvis stays **one brain, many bodies** without duplicate apps or stale agent context.

**Hub:** [DOCS_MAP.md](../DOCS_MAP.md) · **Board:** `python scripts/devloop.py sync` · **Protocol:** [SYNC_PROTOCOL.md](../SYNC_PROTOCOL.md)

---

## 1. Product sync (what each client does)

| Surface | Path | Syncs with brain via | Does **not** duplicate |
|---------|------|----------------------|-------------------------|
| **Web chat** | `clients/web/` | REST `/pair`, `/health`, `/chat` SSE; WS bridge | — (canonical UI) |
| **Flutter Field** | `clients/flutter/` | WS `register`, `tool_execute`, `tool_result` (+ `confirm_request` after ISSUE-104) | Web chat/sessions/settings |
| **Windows agent** | `clients/windows/` | WS bridge + Flet/CLI voice; client tools | Web chat UI |
| **Android stub** | `clients/android/` | Bridge pattern (033) | Full UI |

Detail: [PRESENCE_STACKS.md](PRESENCE_STACKS.md) · Flutter spec: [FLUTTER_FIELD.md](FLUTTER_FIELD.md).

**Identity:** one `device_id` + token per client install; same user across devices via brain SoT ([SYNC_PROTOCOL.md](../SYNC_PROTOCOL.md) entities).

---

## 2. Documentation sync (when you change X, update Y)

| Change | Update together |
|--------|-----------------|
| Presence roles / stack priority | `PRESENCE_STACKS.md`, `OSS.md`, ADR in `DECISIONS.md`, `STRATEGY.md` § Presence |
| Web layout/chrome | `DESIGN.md`, `WEB_UI.md`, `clients/web/README.md` |
| Flutter Field behaviour | `FLUTTER_FIELD.md`, `clients/flutter/README.md`, `SYNC_PROTOCOL.md` if WS types change |
| Windows tray/voice/bridge | `clients/windows/README.md`, `MINIMAX_UI.md`, `SYNC_PROTOCOL.md` |
| WS message shapes | `SYNC_PROTOCOL.md`, bridge code in web + flutter + windows, `devloop` issue notes |
| Agent rules | `AGENTS.md`, `jarvis-dev` + Blackbox mirror, `.cursor/rules/jarvis-design.mdc` |
| Board milestone | `STRATEGY.md` “Where we are”, `CHANGELOG.md`, `devloop sync` |

**After any doc cluster edit:** run checklist in [DOCS_MAP.md](../DOCS_MAP.md) § Edit checklist.

---

## 3. Agent / board sync rhythm

```text
devloop sync          # LIVE_PLAN.md fingerprint, open counts
devloop loop          # slots + handoffs
devloop inbox --owner ME
devloop next --owner ME → claim → implement → done
devloop say --from ME --to OTHER --kind note -- "…"
```

**Max 2 NOW claims.** Lanes must not touch the same paths ([PARALLEL.md](PARALLEL.md)).

---

## 4. Parallel lanes (2026-08 strategy)

| Worker A | Worker B | Rule |
|----------|----------|------|
| `clients/web/**` (chat, settings, sessions) | `backend/**` (tools, mind, API) | No edits to same file |
| `clients/flutter/**` (Field Body only) | `clients/web/**` | Flutter **no** chat features |
| `clients/windows/**` (integration) | `clients/web/**` | Flet GUI maintenance only |
| Docs / ADR | Code in other tree | One writer on shared docs |

**Default pairing:**

| Owner | Primary lane |
|-------|----------------|
| `antigravity` | Web product UI + polish |
| `cursor` | Backend integration, review, architecture |
| `minimax` | Vertical slices (bridge, plugins, Field Body) |
| `minimax2` | One-file helpers, doc sync, small web fixes |

---

## 5. Backlog queue (seeded on board)

| ID | Title | Priority | Status (board) |
|----|-------|----------|----------------|
| **101** | Flutter Field — desktop `tool_execute` shell | P1 | **NOW** (minimax) |
| **102** | Web sessions FR-P3 | P1 | **done** — verify acceptance boxes |
| **103** | Strip Flutter legacy chat | P2 | todo (blocked on 101) |
| **104** | Backend WS `confirm_request` | P2 | **done** — Field UI follow-up **142** |
| **105** | Web QA 098/099 + DESIGN header | P2 | **done** |
| **106** | Web PWA | P3 | todo |
| **107** | WS token auth | P3 | todo |
| **108–111** | smoke, ruff, pre-commit, verify | — | **done** |
| **112–114** | Field slices | — | **done** |
| **142** | Flutter `confirm_request` UI | P2 | backlog (after **101**) |

Audit: [PLAN_AUDIT.md](PLAN_AUDIT.md). Run `devloop sync` after board changes.

---

## 6. Anti-patterns (stop doing)

- Same acceptance in web **and** Flutter (sidebar, composer, sessions).
- Marking UI issues `done` without lane doc cited in issue body.
- `STRATEGY.md` “next actions” pointing at already-`done` issues — refresh after `sync`.
- Starting brain from `backend/` only (use repo root uvicorn) — see `PRESENCE_STACKS.md` run block.

---

## Related

[STRATEGY.md](../STRATEGY.md) · [PARALLEL.md](PARALLEL.md) · [FEEDBACK_LOOP.md](FEEDBACK_LOOP.md) · ADR-0023 [DECISIONS.md](../DECISIONS.md)
