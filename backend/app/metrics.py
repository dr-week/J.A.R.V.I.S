"""Optional Prometheus metrics with a no-op fallback for minimal installs."""

from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from collections.abc import Iterator

try:
    from prometheus_client import Counter, Histogram

    tool_calls = Counter("jarvis_tool_calls_total", "Tool calls", ["tool", "status"])
    tool_latency = Histogram("jarvis_tool_latency_seconds", "Tool latency", ["tool"])
except ImportError:  # pragma: no cover - exercised by minimal installations
    tool_calls = None
    tool_latency = None


@contextmanager
def measure_tool(tool: str) -> Iterator[None]:
    """Record success/failure and latency without making metrics mandatory."""
    started = perf_counter()
    status = "ok"
    try:
        yield
    except Exception:
        status = "error"
        raise
    finally:
        if tool_calls is not None:
            tool_calls.labels(tool=tool, status=status).inc()
        if tool_latency is not None:
            tool_latency.labels(tool=tool).observe(perf_counter() - started)


__all__ = ["measure_tool", "tool_calls", "tool_latency"]
