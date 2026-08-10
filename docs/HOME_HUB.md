# Home hub — always-on brain host

**Doc map:** [DOCS_MAP.md](DOCS_MAP.md) · **Roadmap:** [ROADMAP.md](ROADMAP.md) (Phase 5 — House body)

This is the **run mode** for the always-on home host that keeps the Jarvis
brain awake. It is the Rick-layer foundation: the house stays up, reachable on
the LAN, and survives reboots so the assistant is ambient rather than on-demand.

## What "always-on" means

The brain is a central FastAPI service (SQLite + Soul/Mind/Hands). For the house
experience it must:

- **Run continuously** on one host (a home hub, Raspberry Pi, or an always-on PC)
- **Survive reboots** — started by the OS service manager, not by hand
- **Be reachable from the LAN** so a phone/tablet can hit `/health` and talk
  over WebSocket even when away from the service console

## Run modes

| Mode | Command | Use |
|------|---------|-----|
| Local dev | `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8787 --reload` | Iterating on code |
| Always-on host | `python scripts/run_brain.py` | Production; no `--reload`, clean shutdown |

The always-on launcher reads `HOST` / `PORT` from `backend/app/config.py`
(env or `.env`). The default `HOST=0.0.0.0` binds all interfaces so LAN
clients can reach it.

## House Hands (Home Assistant)

The brain exposes Home Assistant as Jarvis tools via the **house** executor
(plugin at `backend/plugins/homeassistant/`):

- `home_entity_list` (risk `auto`, read-only) — list HA entities and states.
- `home_entity_set` (risk `confirm_once`) — turn an entity on/off (e.g. a
  light) and optionally set brightness 0–255.

Configure in the hub's `.env`:

```env
JARVIS_HA_URL=http://192.168.1.10:8123
JARVIS_HA_TOKEN=<long-lived HA access token>
JARVIS_HA_ENTITY=light.living_room
```

If HA is unconfigured the tools fail **visibly** with a clear error — they never
silently pretend to succeed. Design decision: [ADR-0019](DECISIONS.md#adr-0019--home-assistant-bridge-for-house-hands-issue-061).

## Requirements (recap)

- Python 3.9+ and `pip install -r backend/requirements.txt`
- A `.env` in the repo root with at least `GEMINI_API_KEY` (see `.env.example`)
- A free port (default `8787`)

## Surviving a reboot

Install the launcher behind your operating system's service manager.

### Linux (systemd)

Create `/etc/systemd/system/jarvis-brain.service`:

```ini
[Unit]
Description=Jarvis Brain (always-on home host)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/path/to/jarvis
# Run the status-check CLI as-is; the brain runs in the foreground.
ExecStart=/usr/bin/python3 /path/to/jarvis/scripts/run_brain.py
Restart=on-failure
RestartSec=5
# Hardening
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now jarvis-brain
systemctl status jarvis-brain        # verify it is running
journalctl -u jarvis-brain -f        # follow logs
```

The service auto-starts on boot and restarts on failure.

### Windows (Task Scheduler)

1. Open **Task Scheduler** → **Create Task**.
2. **General:** name `Jarvis Brain`; "Run whether user is logged on or not".
3. **Triggers:** **At startup**.
4. **Actions:** *Start a program*
   - Program: `C:\path\to\python.exe`
   - Arguments: `C:\path\to\jarvis\scripts\run_brain.py`
   - Start in: `C:\path\to\jarvis`
5. Optional **Settings:** "If the task fails, restart every 1 minute" (up to 3 times).

The task runs at boot; the brain stays up until the host is powered off.

## Remote health check from a phone on LAN

The service exposes `GET /health` (see `backend/app/api/health.py`), which
returns status, assistant name, LLM provider/model, and `llm_ready`.

From a phone/tablet on the same LAN:

```bash
# On the hub, find its LAN IP (or the launcher prints it on startup)
ip a          # Linux
ipconfig      # Windows

# From the phone browser or curl:
curl http://192.168.1.50:8787/health
```

Expected response (JSON):

```json
{
  "status": "ok",
  "assistant_name": "Jarvis",
  "llm_provider": "gemini",
  "llm_model": "gemini-2.0-flash",
  "llm_ready": true,
  "learning_enabled": true,
  "version": "0.1.0"
}
```

`status: "ok"` means the brain process is alive. `llm_ready: true` means the
LLM provider is configured (a separate readiness signal).

### Notes on reachability

- The brain binds `0.0.0.0` by default, so it answers on all interfaces.
- If the phone cannot reach `/health`, allow inbound TCP on port `8787` in the
  hub's firewall (systemd `firewalld`/`ufw`, or Windows Firewall).
- WebSocket clients connect to `ws://<hub-ip>:8787/ws` for the chat + device
  bridge session (see [SYNC_PROTOCOL.md](SYNC_PROTOCOL.md)).

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `/health` unreachable from phone | Hub firewall blocking `8787`; host not on same subnet; wrong IP |
| Service shows `active (running)` but health fails | `llm_ready: false` → check `GEMINI_API_KEY` in `.env` |
| Brain stops after reboot | Service not enabled (`systemctl enable`) or Task Scheduler not "At startup" |
| Port already in use | Change `JARVIS_PORT` in `.env` and restart |
| Logs unavailable | `journalctl -u jarvis-brain -f` (systemd) or Task Scheduler history tab |

## ADR

Always-on run mode decision: [ADR-0018](DECISIONS.md#adr-0018--always-on-home-host-run-mode-issue-060).

## Related

- [ROADMAP.md](ROADMAP.md) — Phase 5 House body
- [ARCHITECTURE.md](ARCHITECTURE.md) — brain + bodies
- [SYNC_PROTOCOL.md](SYNC_PROTOCOL.md) — WebSocket client protocol
