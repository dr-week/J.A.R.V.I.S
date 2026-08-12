"""Tests for Hands MCP Client Integration."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from backend.app.hands.mcp_client import mcp_manager, load_mcp_config
from backend.app.hands.registry import REGISTRY, _execute_raw, run_tool


@pytest.fixture(autouse=True)
def cleanup_mcp_state():
    yield
    mcp_manager.servers.clear()
    mcp_manager.mock_executors.clear()


@pytest.mark.asyncio
async def test_mcp_mock_server_registration_and_execution():
    """Test that mock MCP servers register tools in REGISTRY and execute correctly."""
    
    def dummy_executor(tool_name: str, params: dict):
        if tool_name == "echo":
            return {"echo": params.get("text", "")}
        return {"error": "unknown tool"}

    mock_tools = [
        {
            "name": "echo",
            "description": "Echo back input text",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"]
            }
        }
    ]

    mcp_manager.register_mock_server("test_server", mock_tools, dummy_executor)

    assert "mcp_test_server_echo" in REGISTRY
    tool_def = REGISTRY["mcp_test_server_echo"]
    assert tool_def["runtime"] == "mcp"
    assert tool_def["mcp_server"] == "test_server"
    assert tool_def["mcp_tool_name"] == "echo"

    res = await _execute_raw("mcp_test_server_echo", {"text": "hello mcp"})
    assert res == {"result": {"echo": "hello mcp"}}


def test_load_mcp_config(tmp_path: Path):
    """Test loading MCP server configuration file."""
    config_file = tmp_path / "mcp_servers.json"
    config_data = {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "d:/CODES/jarvis"]
            }
        }
    }
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    loaded = load_mcp_config(config_file)
    assert "mcpServers" in loaded
    assert "filesystem" in loaded["mcpServers"]
    assert loaded["mcpServers"]["filesystem"]["command"] == "npx"
