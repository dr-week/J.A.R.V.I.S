from backend.app.telemetry import capture_exception, span


def test_span_is_safe_without_exporter():
    with span("test.operation", surface="unit") as current:
        assert current is None or current.is_recording() is False or current.get_span_context()


def test_capture_exception_is_optional():
    capture_exception(RuntimeError("test-only"))
