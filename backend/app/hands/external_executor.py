"""Hands — Polyglot ExternalExecutor interface."""
from __future__ import annotations

import asyncio
import json
from typing import Any


class ExternalExecutor:
    """Dispatches tool execution to external runtimes (subprocess, lua, etc)."""

    def __init__(self, registry: dict[str, dict[str, Any]]):
        self.registry = registry

    async def execute(self, tool_def: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        runtime = tool_def.get("runtime", "python")

        if runtime == "python":
            raise ValueError("ExternalExecutor should not handle 'python' runtime directly.")
            
        elif runtime == "subprocess":
            return await self._execute_subprocess(tool_def, params)
            
        elif runtime == "mcp":
            from .mcp_client import mcp_manager
            return await mcp_manager.execute_tool(tool_def, params)
            
        elif runtime == "lua":
            # Deferred to ISSUE-129
            return await self._execute_lua(tool_def, params)
            
        else:
            return {"error": f"Unsupported runtime: {runtime}"}

    async def _execute_subprocess(self, tool_def: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Execute a binary or script via subprocess, passing JSON params over stdin or argv."""
        argv_template = tool_def.get("argv_template")
        entry = tool_def.get("entry")
        timeout = tool_def.get("timeout_seconds", 30)

        if not entry and not argv_template:
            return {"error": "Subprocess tools require 'entry' or 'argv_template'"}

        cmd = argv_template if argv_template else [entry]
        # In a real implementation we would substitute {param} in cmd, but this is a stub.
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=json.dumps(params).encode("utf-8")),
                timeout=timeout
            )
            
            if proc.returncode != 0:
                return {"error": f"Subprocess exited with code {proc.returncode}", "stderr": stderr.decode("utf-8")}
                
            return {"result": json.loads(stdout.decode("utf-8"))}
        except TimeoutError:
            return {"error": f"Subprocess timed out after {timeout} seconds"}
        except Exception as exc:
            return {"error": f"Subprocess execution failed: {str(exc)}"}

    async def _execute_lua(self, tool_def: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        """Execute a Lua script using lupa. Deferred to ISSUE-129."""
        return {"error": "Lua execution is deferred to ISSUE-129"}
