"""Hands — Model Context Protocol (MCP) Client Adapter.

Connects Jarvis to external MCP servers (stdio/SSE/custom) and registers
their exposed tools directly into the central tool registry.
"""
from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Callable

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPManager:
    """Manages MCP server connections and tool registration."""

    def __init__(self) -> None:
        self.servers: dict[str, dict[str, Any]] = {}
        self.sessions: dict[str, ClientSession] = {}
        self.transports: dict[str, Any] = {}
        self.mock_executors: dict[str, Callable[..., Any]] = {}

    def register_mock_server(self, name: str, tools: list[dict[str, Any]], executor: Callable[..., Any]) -> None:
        """Register an in-memory mock MCP server for testing and local zero-process tools."""
        from .registry import register

        self.servers[name] = {"type": "mock"}
        self.mock_executors[name] = executor

        for tool_info in tools:
            tool_name = tool_info["name"]
            prefixed_name = f"mcp_{name}_{tool_name}" if not tool_name.startswith("mcp_") else tool_name
            tool_def = {
                "name": prefixed_name,
                "description": tool_info.get("description", f"MCP tool from {name}"),
                "version": "1.0.0",
                "phase": 3,
                "risk_level": tool_info.get("risk_level", "auto"),
                "executor": "brain",
                "runtime": "mcp",
                "mcp_server": name,
                "mcp_tool_name": tool_name,
                "parameters": tool_info.get("parameters", {"type": "object", "properties": {}}),
                "returns": {"type": "object"},
                "scopes": ["mcp"],
                "tags": ["mcp", name],
            }
            register(tool_def)

    async def connect_stdio_server(
        self,
        name: str,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> list[str]:
        """Connect to an external stdio MCP server, discover tools, and register them."""
        from .registry import register

        params = StdioServerParameters(
            command=command,
            args=args or [],
            env=env,
        )

        try:
            client_ctx = stdio_client(params)
            read_stream, write_stream = await client_ctx.__aenter__()
            self.transports[name] = client_ctx

            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            await session.initialize()
            self.sessions[name] = session

            tools_res = await session.list_tools()
            registered_tools = []

            for tool in tools_res.tools:
                prefixed_name = f"mcp_{name}_{tool.name}"
                tool_def = {
                    "name": prefixed_name,
                    "description": tool.description or f"MCP tool {tool.name} from {name}",
                    "version": "1.0.0",
                    "phase": 3,
                    "risk_level": "auto",
                    "executor": "brain",
                    "runtime": "mcp",
                    "mcp_server": name,
                    "mcp_tool_name": tool.name,
                    "parameters": tool.inputSchema if hasattr(tool, "inputSchema") else {"type": "object", "properties": {}},
                    "returns": {"type": "object"},
                    "scopes": ["mcp"],
                    "tags": ["mcp", name],
                }
                register(tool_def)
                registered_tools.append(prefixed_name)

            self.servers[name] = {
                "type": "stdio",
                "command": command,
                "args": args or [],
                "tools": registered_tools,
            }
            return registered_tools
        except Exception as exc:
            logger.error("Failed to connect stdio MCP server %s: %s", name, exc)
            return []

    async def execute_tool(self, tool_def: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Execute an MCP tool call."""
        server_name = tool_def.get("mcp_server", "")
        tool_name = tool_def.get("mcp_tool_name", "")

        if not server_name or not tool_name:
            return {"error": f"Invalid MCP tool definition for '{tool_def.get('name')}'"}

        if server_name in self.mock_executors:
            try:
                res = self.mock_executors[server_name](tool_name, params)
                if hasattr(res, "__await__"):
                    res = await res
                return {"result": res}
            except Exception as exc:
                return {"error": f"Mock MCP execution failed: {exc}"}

        session = self.sessions.get(server_name)
        if not session:
            return {"error": f"MCP server '{server_name}' is not connected."}

        try:
            res = await session.call_tool(tool_name, params)
            output_content = []
            if hasattr(res, "content") and res.content:
                for block in res.content:
                    if hasattr(block, "text"):
                        output_content.append(block.text)
                    else:
                        output_content.append(str(block))
            return {"result": "\n".join(output_content) if output_content else "Success"}
        except Exception as exc:
            return {"error": f"MCP execution error: {exc}"}

    async def close_all(self) -> None:
        """Close all active MCP sessions and transports."""
        for name, session in list(self.sessions.items()):
            try:
                await session.__aexit__(None, None, None)
            except Exception:
                pass
        for name, transport in list(self.transports.items()):
            try:
                await transport.__aexit__(None, None, None)
            except Exception:
                pass
        self.sessions.clear()
        self.transports.clear()


mcp_manager = MCPManager()


def load_mcp_config(config_path: Path | str) -> dict[str, Any]:
    """Load MCP server configurations from JSON file."""
    path = Path(config_path)
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error("Error reading MCP config %s: %s", path, exc)
        return {}


def save_mcp_config(config_data: dict[str, Any], config_path: Path | str) -> None:
    """Save MCP server configurations to JSON file."""
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)


async def install_and_connect_mcp_server(
    name: str,
    command: str,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
    config_path: Path | str = "backend/config/mcp_servers.json",
) -> dict[str, Any]:
    """Install/register a new MCP server spec in config and attempt stdio connection."""
    existing_config = load_mcp_config(config_path)
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}

    existing_config["mcpServers"][name] = {
        "command": command,
        "args": args or [],
    }
    if env:
        existing_config["mcpServers"][name]["env"] = env

    save_mcp_config(existing_config, config_path)

    # Attempt connecting to discover tools
    registered_tools = await mcp_manager.connect_stdio_server(
        name=name, command=command, args=args, env=env
    )

    return {
        "ok": True,
        "name": name,
        "command": command,
        "args": args or [],
        "tools_registered": registered_tools,
        "config_saved": str(config_path),
    }
