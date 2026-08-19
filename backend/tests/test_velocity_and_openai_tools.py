"""Smoke: velocity_build registers; openai tools builder is importable."""
from backend.app.hands.registry import REGISTRY


def test_velocity_build_registered():
    assert "velocity_build" in REGISTRY
    tool = REGISTRY["velocity_build"]
    assert tool["risk_level"] == "confirm_always"
    assert "app_description" in tool["parameters"]["properties"]


def test_openai_tools_shape():
    # build_tools lives in message_builder after monolith decomposition
    from backend.app.mind.message_builder import build_tools

    # Use a coding-domain prompt so the router returns tool schemas
    tools = build_tools("run python code")
    assert isinstance(tools, list)
    assert any(t["function"]["name"] == "velocity_build" for t in tools)
