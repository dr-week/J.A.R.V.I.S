"""Tests for mcp_installer plugin."""
from __future__ import annotations

from pathlib import Path
import pytest

from backend.app.hands.mcp_client import load_mcp_config
from backend.app.hands.registry import REGISTRY
from backend.plugins.mcp_installer import _mcp_install_server


@pytest.mark.asyncio
async def test_mcp_installer_tool_registered():
    """Verify tool registration in REGISTRY."""
    assert "mcp_install_server" in REGISTRY


@pytest.mark.asyncio
async def test_mcp_install_server_updates_config(tmp_path: Path):
    """Test installing an MCP server spec writes JSON config cleanly."""
    config_file = tmp_path / "mcp_servers.json"

    # We use a dummy command so it doesn't launch a real subprocess during unit test
    from backend.app.hands import mcp_client
    
    # Temporarily override default config path in test
    res = await mcp_client.install_and_connect_mcp_server(
        name="test_filesystem",
        command="dummy_cmd",
        args=["--test"],
        config_path=config_file,
    )

    assert res["ok"] is True
    assert res["name"] == "test_filesystem"

    loaded = load_mcp_config(config_file)
    assert "mcpServers" in loaded
    assert "test_filesystem" in loaded["mcpServers"]
    assert loaded["mcpServers"]["test_filesystem"]["command"] == "dummy_cmd"
    assert loaded["mcpServers"]["test_filesystem"]["args"] == ["--test"]
