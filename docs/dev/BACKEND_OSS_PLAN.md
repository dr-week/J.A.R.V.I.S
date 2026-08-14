# Backend OSS leverage plan

Jarvis should spend its engineering time on Soul, intent, confirmations, and device execution. Mature open-source infrastructure should carry generic platform work.

## Implemented foundation

- Pydantic Settings is the configuration boundary.
- SQLModel provides an async persistence adapter with SQLite-by-default and `DATABASE_URL` override.
- Celery + Redis are isolated as an optional task-queue adapter; local API startup does not require a worker.
- Tenacity centralizes bounded retries for idempotent outbound HTTP calls.
- APScheduler is an optional in-process scheduler for reminders and polling.
- OpenTelemetry/Sentry are accessed through a no-op-safe telemetry boundary.
- Prometheus client metrics provide reusable tool-call counts and latency measurement.
- Existing plugin and API contracts remain the public integration surface.

## Next slices

1. Add FastAPI Users only when a durable user model and multi-user scope are approved.
2. Add OpenTelemetry after trace fields and privacy redaction are specified.
3. Add Tenacity around outbound sidecars with bounded retries and idempotency keys.
4. Add APScheduler only for local reminders; use Celery for durable distributed jobs.

Each slice needs a contract test, an ADR, an environment example, and a rollback path.

## Automation gate

Run `python scripts/check_backend_oss.py` before changing backend adapters. It catches missing code, tests, and canonical OSS documentation early.

Run `python scripts/verify_backend.py` for the fast chained agent check: consistency -> compile -> focused tests. Use `--full` before a release.

## Time-saving chain

API request -> validated settings -> domain/plugin contract -> queued or direct execution -> audit event -> client notification.
