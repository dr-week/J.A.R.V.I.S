# Jarvis — live demo (barebone)

**Audience:** anyone who should see the product, not the dev factory.  
**Time:** ~5 minutes live · ~2 minutes if you only show UI + `/health`.

---

## What you are showing

| Piece | One-liner |
|-------|-----------|
| **Brain** | FastAPI on `:8787` — memory, tools, LLM (server-side keys only) |
| **Web** | Primary chat UI (Vite) — pairs once, then talks over HTTP + sync socket |
| **Story** | One brain, many bodies — this repo is the spine; house/phone clients plug in later |

Skip in a pitch: `devloop`, board issues, Flutter Field experiments, Windows Flet unless asked.

---

## Before the room

1. **Machine:** Python 3.11+, Node 20+, repo cloned.
2. **Secrets:** Copy `.env.example` → `.env` and set `GEMINI_API_KEY` (or your provider). Without it, UI still **pairs** and status shows **LLM off** — fine for architecture-only demos.
3. **Deps (once):**
   ```bash
   pip install -e .
   cd clients/web && npm install
   ```
4. **Dry run:** `python scripts/smoke_web.py` after brain is up.
5. **Browser:** Use a fresh profile or clear site data if pairing acted weird (Settings → Reset Token).

---

## Fastest path (Windows)

```powershell
.\scripts\demo_up.ps1
```

Then open the URL it prints (usually `http://localhost:5173`).

**macOS / Linux:**

```bash
./scripts/demo_up.sh
```

---

## Manual path (two terminals)

**Terminal 1 — brain (repo root):**

```bash
python scripts/run_brain.py
```

**Terminal 2 — web:**

```bash
cd clients/web
npm run dev
```

Open `http://localhost:5173`. Health check for slides: `http://localhost:8787/health`.

---

## Suggested talk track (90 seconds)

1. **Vision** — personal AI that *executes*, same mind at home and on the go ([VISION.md](VISION.md)).
2. **Live** — show green connection + “LLM on” in the header; send one message.
3. **Architecture** — browser never holds API keys; brain owns LLM + SQLite soul + tool gate.
4. **Honest status** — Phase 2 hands/bridge in progress; this demo is the **vertical slice**, not the finished house.

---

## Demo prompts (safe defaults)

Use these if you want predictable replies (depends on persona + API):

- “Who are you, in one paragraph?”
- “What can you actually do for me today versus later on the roadmap?”
- “Remember that my favorite drink is coffee.” then “What did I just tell you?” (session/memory smoke)

Avoid live tool demos unless you rehearsed them (confirm flows, Windows bridge, etc.).

---

## If something breaks

| Symptom | Fix |
|---------|-----|
| Red / Offline in header | Brain not running → `run_brain.py` or `demo_up` |
| `(LLM Offline)` | Set `GEMINI_API_KEY` in `.env`, restart brain |
| Pairing 401 | Settings → pairing secret matches `JARVIS_PAIRING_SECRET` in `.env` |
| Port in use | Kill old uvicorn on 8787; one brain only |
| Blank web | `npm install` in `clients/web`; check terminal for Vite URL |

---

## After the demo

- **Builders:** [README.md](../README.md) → agents → [docs/board/NOW.md](board/NOW.md)
- **Depth:** [ARCHITECTURE.md](ARCHITECTURE.md) · [ROADMAP.md](ROADMAP.md)

---

## Checklist (printable)

- [ ] `.env` with LLM key (if showing chat)
- [ ] `demo_up` or brain + `npm run dev`
- [ ] Browser on chat tab, sidebar shows **Jarvis**
- [ ] One rehearsed user message
- [ ] `/health` tab ready for JSON slide optional
