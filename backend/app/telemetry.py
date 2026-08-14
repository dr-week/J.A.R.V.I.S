"""Optional OpenTelemetry/Sentry boundary; telemetry must never block Jarvis."""

from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator
from typing import Any


@contextmanager
def span(name: str, **attributes: Any) -> Iterator[Any]:
    """Yield a best-effort span while remaining usable without telemetry extras."""
    try:
        from opentelemetry import trace
    except ImportError:
        yield None
        return

    tracer = trace.get_tracer("jarvis")
    with tracer.start_as_current_span(name) as current:
        for key, value in attributes.items():
            current.set_attribute(key, str(value))
        yield current


def capture_exception(error: BaseException) -> None:
    """Report an exception when Sentry is configured; otherwise stay silent."""
    try:
        import sentry_sdk
    except ImportError:
        return
    if sentry_sdk.Hub.current.client is not None:
        sentry_sdk.capture_exception(error)


__all__ = ["capture_exception", "span"]
