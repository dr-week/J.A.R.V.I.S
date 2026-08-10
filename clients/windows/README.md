# Windows client — Jarvis desktop presence

**Role:** **Legacy lane** — Flet + Python: tray, voice, wake-word, device bridge, Windows-local tools.  
**Primary UI:** [clients/web](../web/) (Vite + TypeScript). **Experimental:** [clients/flutter](../flutter/).  
See [docs/dev/PRESENCE_STACKS.md](../../docs/dev/PRESENCE_STACKS.md).

## Setup

```bash
pip install -r clients/windows/requirements.txt
```

## Troubleshooting

**Task Manager shows many "Flet" processes / high RAM** — each extra
`python clients\windows\client.py --pair` used to spawn another Flet desktop.
Only **one** GUI instance is allowed now (Windows mutex). Clean up orphans first:

```powershell
cd D:\CODES\jarvis
.\clients\windows\kill_stale.ps1
```

Then start **one** client. If you launch again while it is running, the second
process exits (or tries to focus the existing **Jarvis** window). Always use
tray **Quit** to fully exit — not only closing the window (that hides to tray).

**Single instance:** mutex `Global\JarvisWindowsClient_v1` — second launch prints
a message and exits without starting another Flet app.

## Start the brain first

The Windows client talks to `http://localhost:8787` by default. If nothing is
listening, pairing and chat fail (WinError 10061 / connection refused).

```bash
cd backend
uvicorn app.main:app --reload --port 8787
```

## Pair (token stub)

```bash
python clients/windows/client.py --pair --once "ping"
# token saved to %USERPROFILE%\.jarvis\windows_token.json
```

Uses brain `POST /pair` with `JARVIS_PAIRING_SECRET` (must match backend `.env`).

## Chat

```bash
# One-shot CLI (good for scripts / CI)
python clients/windows/client.py --once "hello" --brain http://localhost:8787

# Interactive Flet desktop UI (default)
python clients/windows/client.py --brain http://localhost:8787

# Same UI, but hides to the Windows tray; use tray menu to reopen
python clients/windows/client.py --brain http://localhost:8787

# GUI + device bridge in background
python clients/windows/client.py --pair --bridge --brain http://localhost:8787

# Headless bridge only (servers / scripts)
python clients/windows/client.py --bridge-only --pair --brain http://localhost:8787
```

## Device bridge (ISSUE-032)

Run the device-bridge WebSocket loop so the brain can ask this PC to open
apps / URLs / files. The client registers a `device_id` and listens for
`tool_execute` requests, executing the local action and returning the result.

```bash
# with pairing (headless)
python clients/windows/client.py --bridge-only --pair --brain http://localhost:8787

# with an existing token file
python clients/windows/client.py --bridge-only --brain http://localhost:8787
```

When a user asks the assistant to "open notepad" or "open <URL>" or "open
<file path>", the brain dispatches the `windows_open` tool to this bridge.

Requires `websockets` (already in `clients/windows/requirements.txt`).

## Tray presence (ISSUE-051)

The desktop UI now starts with a tray icon when `pystray` and `Pillow` are
installed. Minimize or close the window to hide it; then use the tray icon to
reopen Jarvis from the "Open Jarvis" menu item.

If the tray libraries are missing, the client still runs normally without the
tray affordance.

## Memory sync (ISSUE-022)

While the bridge is running, the client mirrors memory pushes from the brain
into a local cache at `~/.jarvis/windows_sync_cache.json`. A memory written on
another device becomes visible here in near-real-time, and the reverse happens
on other devices when this one writes.

```bash
# run the bridge (which also mirrors memory pushes)
python clients/windows/client.py --bridge --brain http://localhost:8787
```

- The brain is the source of truth; this file is a best-effort local mirror.
- A `push_memory` with an empty value deletes the key from the local cache.
- Inspect the mirror manually: the file is human-readable JSON.

## Voice (ISSUE-050)

Speak a turn and get a spoken reply, while the text transcript is still
streamed/synced through the normal `/chat` SSE path.

```bash
# Capture your spoken question from the mic, then speak the reply
python clients/windows/client.py --voice --brain http://localhost:8787

# Same, but with an explicit typed prompt that gets spoken aloud
python clients/windows/client.py --voice --once "hello" --brain http://localhost:8787
```

- `--voice` with no `--once` captures the prompt from the microphone (STT).
- `--voice --once "..."` speaks the assistant's reply (TTS) after the text
  streams in.
- Requires optional deps: `pyttsx3` (offline TTS) and `speech_recognition`
  (STT). If they're missing, the client logs a note and falls back to
  text-only, so existing use is unaffected.

## Wake word (ISSUE-052)

Hands-free summon is **opt-in** and disabled by default. When enabled, the
client keeps listening in the background; saying the wake phrase starts a one
turn spoken session with the brain, then it loops back to idle.

```bash
# Enable wake word "jarvis" (headless loop; Ctrl+C to stop)
python clients/windows/client.py --wake-word jarvis --brain http://localhost:8787

# Same via env
set JARVIS_WAKE_WORD=jarvis
python clients/windows/client.py --brain http://localhost:8787
```

- Requires the same optional voice deps as `--voice` (`speech_recognition` + a
  microphone). If they're missing, the client notes it and refuses to start
  the wake loop.
- Uses the `listen()` STT path to detect the phrase, so it degrades gracefully
  like the rest of the voice layer.
- **Privacy:** the microphone is active only while the wake loop runs. See
  `docs/SECURITY.md` → *Wake word privacy notes* for details. No audio is
  recorded or stored.

## Env

| Var | Meaning |
|-----|---------|
| `JARVIS_BRAIN_URL` | Brain base URL |
| `JARVIS_DEVICE_ID` | Device id sent on each message |
| `JARVIS_PAIRING_SECRET` | Must match brain `.env` |
| `JARVIS_TOKEN_FILE` | Where paired token is stored |
| `JARVIS_SYNC_CACHE` | Where the local memory sync mirror is stored |
| `JARVIS_WAKE_WORD` | Wake phrase for `--wake-word` mode (default from CLI) |
| `JARVIS_WAKE_ENABLED` | `true`/`1`/`yes` to enable wake word from env |
