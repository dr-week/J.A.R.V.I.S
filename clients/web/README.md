# Jarvis Web (Vite + React)

**Role:** **Primary** presence UI — build product/design here first.  
**Stack:** TypeScript only (not Flutter). See [docs/dev/PRESENCE_STACKS.md](../../docs/dev/PRESENCE_STACKS.md).

Browser UI on `http://localhost:5173`. Talks to the brain at `http://localhost:8787`.

**Design (required):** [docs/dev/WEB_UI.md](../../docs/dev/WEB_UI.md) · [docs/DESIGN.md](../../docs/DESIGN.md)

## Run

**Terminal 1 — brain (from repo root):**

```bash
cd D:\CODES\jarvis
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8787
```

**Terminal 2 — web UI:**

```bash
cd clients/web
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). If you see **Offline** / **Failed to fetch**, the brain is not running or not on port 8787.

Pairing uses `JARVIS_PAIRING_SECRET` from the repo `.env` (default in `.env.example` matches the web client stub).

## Source layout (for agents)

```text
src/
├── api/           brainApi, syncSocket
├── hooks/         useJarvisApp (state + connection)
├── components/    AppSidebar, ChatView, Settings
├── types/         chat types
└── App.tsx        shell only
```

See [docs/dev/AI_CODE_STRUCTURE.md](../../docs/dev/AI_CODE_STRUCTURE.md).
