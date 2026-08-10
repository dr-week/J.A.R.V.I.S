# MiniMax — Windows UI lane (Flet)

**Role:** **Legacy Windows lane** (tray/voice/bridge) — not the primary product UI. See [PRESENCE_STACKS.md](PRESENCE_STACKS.md).

**Design (required):** [DESIGN.md](../DESIGN.md) · Flet details in this file.
**Parity Note:** Windows Flet uses the footer as its single status zone per DESIGN anti-duplication rules (do not duplicate status in the header).

**Owner:** `minimax` or `minimax2` (one issue at a time). **Execute mode:** claim + brief = go; no re-approval ([MINIMAX.md](MINIMAX.md), [.blackbox/EXECUTE.md](../../.blackbox/EXECUTE.md)).

UI code lives mainly in **`clients/windows/ui_gui.py`**. Do **not** grow `client.py` unless the issue says so.

---

## Session start

```bash
python scripts/devloop.py sync --owner minimax
python scripts/devloop.py who
python scripts/devloop.py claim ISSUE-XXX --owner minimax
python scripts/devloop.py brief --owner minimax
```

Read `docs/board/issues/ISSUE-XXX.md` and **only** edit paths listed under **Lane**.

---

## UI wave queue (do in order when unclaimed)

| Order | Issue | Touch only | Done when |
|-------|-------|------------|-----------|
| 1 | **077** | `docs/DECISIONS.md` | ADR: Windows presence uses Flet; Textual ADR superseded |
| 2 | **079** | `docs/ARCHITECTURE.md`, `docs/OSS.md` | Presence docs say Flet desktop, not Textual TUI |
| 3 | **078** | `clients/android/README.md` | Bridge section mirrors Windows README (docs) |
| 4 | **089** | `clients/windows/client.py` (`bridge_loop` only) | Footer shows `Bridge: connected` after WS register ack |
| 5 | **090** | `clients/windows/ui_gui.py` | “New chat” clears list + new `session_id`; chat still works |
| 6 | **091** | `clients/windows/ui_gui.py` | When `llm_ready` is false, footer shows short “add API key” hint |

**Already done (do not reclaim):** 081, 082 (reconnect), 088 (aesthetics), single-instance (`instance_lock.py`).

---

## Rules for UI issues

1. **One file** when possible (`ui_gui.py`).
2. **No `ft.run` in tests** — use `clients/windows/test_ui_smoke.py` (import-only).
3. **Verify:** `python -m py_compile clients/windows/ui_gui.py` (and any other touched `.py`).
4. **Window title** stays `WINDOW_TITLE` in `ui_gui.py` for single-instance focus — do not rename OS window.
5. **Done:** `python scripts/devloop.py update ISSUE-XXX --note "..."` then `done ISSUE-XXX` then `sync`.

---

## Reference (read, don’t rewrite)

- Pairing / brain URL: `clients/windows/README.md`
- Kill orphans: `clients/windows/kill_stale.ps1`
- Design tokens: top of `ui_gui.py` (`BG`, `ACCENT`, …)

---

## Handoff to human

After `done`, user runs:

```powershell
.\clients\windows\kill_stale.ps1
cd backend; python -m uvicorn app.main:app --port 8787
cd ..; python clients\windows\client.py --pair
```
