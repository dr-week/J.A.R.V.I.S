from backend.app.metrics import measure_tool


def test_metrics_context_preserves_success():
    with measure_tool("test"):
        pass


def test_metrics_context_preserves_errors():
    try:
        with measure_tool("test"):
            raise ValueError("expected")
    except ValueError:
        pass
