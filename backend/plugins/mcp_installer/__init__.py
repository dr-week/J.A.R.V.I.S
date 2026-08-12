"""MCP Installer Plugin (Phase 3 — Automated GitHub Tool Integration).

Enables Jarvis (and the user) to register and auto-load external MCP servers
and open-source GitHub tool packages with zero manual code writing.
"""
from __future__ import annotations

from typing import Any

from backend.app.hands import registry
from backend.app.hands.mcp_client import install_and_connect_mcp_server


async def _mcp_install_server(
    name: str,
    command: str,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Install and configure a new MCP server specification."""
    clean_name = (name or "").strip()
    clean_cmd = (command or "").strip()

    if not clean_name:
        return {"ok": False, "error": "name parameter is required"}
    if not clean_cmd:
        return {"ok": False, "error": "command parameter is required"}

    try:
        res = await install_and_connect_mcp_server(
            name=clean_name,
            command=clean_cmd,
            args=args or [],
            env=env,
        )
        return res
    except Exception as exc:
        return {"ok": False, "error": f"Failed to install MCP server '{clean_name}': {exc}"}


registry.register(
    {
        "name": "mcp_install_server",
        "description": (
            "Download and integrate an open-source MCP tool server (e.g. from GitHub/NPM/PyPI). "
            "Pass server name, CLI command (npx/uvx), and arguments."
        ),
        "version": "1.0.0",
        "phase": 3,
        "risk_level": "confirm_once",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Identifier name for the MCP server (e.g. 'github', 'filesystem', 'sqlite')",
                },
                "command": {
                    "type": "string",
                    "description": "CLI executable to launch server (e.g. 'npx', 'uvx', 'python')",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Command line arguments (e.g. ['-y', '@modelcontextprotocol/server-filesystem'])",
                },
            },
            "required": ["name", "command"],
        },
        "returns": {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "name": {"type": "string"},
                "tools_registered": {"type": "array"},
            },
        },
        "scopes": ["mcp:admin"],
        "tags": ["mcp", "installer", "github"],
    },
    _mcp_install_server,
)
