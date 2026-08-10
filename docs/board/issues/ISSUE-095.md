---
id: ISSUE-095
status: done
phase: 6
owner: antigravity
claimed_at: 2026-08-09T15:22:02Z
---

# Fix Backend Connection

The web UI is showing an "Offline" status and "Failed to fetch" errors. This is because the Jarvis Python backend (`backend/app/main.py`) is not currently running.

## Acceptance Criteria
- [ ] Launch the backend using `uvicorn backend.app.main:app --host 0.0.0.0 --port 8787` as a background task.
- [ ] Ensure the web UI connects and shows a "Connected" or "Ready" status without fetch errors.

## Notes

- [2026-08-09T15:23:21Z] Marked done


- Claimed by antigravity at 2026-08-09T15:22:02Z


- Claimed by antigravity at 2026-08-09T15:21:30Z


- Claimed by antigravity at 2026-08-09T15:21:07Z
