"""Optional in-process scheduler adapter for local reminders and polling."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def build_scheduler() -> Any:
    """Create APScheduler only when the optional dependency is installed."""
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except ImportError as exc:
        raise RuntimeError("Install the 'scheduler' extra to enable background jobs") from exc
    return AsyncIOScheduler()


def add_interval_job(scheduler: Any, job: Callable[[], Any], seconds: int, job_id: str) -> Any:
    """Register a replaceable interval job without leaking scheduler details."""
    return scheduler.add_job(job, "interval", seconds=seconds, id=job_id, replace_existing=True)


__all__ = ["add_interval_job", "build_scheduler"]
