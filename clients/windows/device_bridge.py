"""Jarvis Windows client — device bridge (ISSUE-032).

Executes local 'open app / URL / file' actions on behalf of the brain.
Called by the client's WebSocket tool-execution loop when it receives a
`windows_open` tool_execute request.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Any

_URL_RE = re.compile(r"^(https?|ftp)://", re.I)
_WINDOWS = sys.platform.startswith("win")


def _looks_like_path(target: str) -> bool:
    """Guess whether a string is an absolute path or a path-like target."""
    if not _WINDOWS:
        return Path(target).expanduser().is_absolute()
    # Windows absolute paths: C:/..., C:\..., \\server\share, or a drive letter
    return bool(
        re.match(r"^([a-zA-Z]:[\\/]|\\\\|\.\\|\.\.)", target)
        or Path(target).exists()
    )


def _expand_path(target: str) -> str:
    """Expand user home and environment variables in a path."""
    expanded = os.path.expandvars(os.path.expanduser(target))
    return expanded


def open_with_default(target: str) -> dict[str, Any]:
    """Open target with the OS default handler. Returns a structured result."""
    target = target.strip()
    if not target:
        return {"ok": False, "error": "empty target"}

    # 1. URL → default browser
    if _URL_RE.match(target):
        opened = webbrowser.open(target)
        return {
            "ok": opened,
            "kind": "url",
            "target": target,
            "result": "opened in browser" if opened else "failed to open browser",
        }

    # 2. Path exists → explorer / default handler
    path = _expand_path(target)
    if Path(path).exists():
        if _WINDOWS:
            try:
                # os.startfile uses the default handler (app, explorer, etc.)
                os.startfile(path)  # type: ignore[attr-defined]
                return {
                    "ok": True,
                    "kind": "file",
                    "target": path,
                    "result": f"opened '{path}'",
                }
            except Exception as exc:  # noqa: BLE001
                return {"ok": False, "kind": "file", "target": path, "error": str(exc)}

    # 3. Looks like a path but doesn't exist → report clearly
    if _looks_like_path(target):
        return {"ok": False, "kind": "file", "target": path, "error": f"path not found: {path}"}

    # 4. Otherwise treat as an app name → try to launch it
    return _launch_app(target)


def _launch_app(name: str) -> dict[str, Any]:
    """Launch an installed application by name/command."""
    if _WINDOWS:
        # Common Windows app names map to executables via `start`.
        try:
            subprocess.Popen(["cmd", "/c", "start", "", name], shell=False)
            return {"ok": True, "kind": "app", "target": name, "result": f"launched '{name}'"}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "kind": "app", "target": name, "error": str(exc)}

    # Non-Windows fallback (dev/testing on other OSes)
    exe = shutil.which(name)
    if not exe:
        return {"ok": False, "kind": "app", "target": name, "error": f"app not found: {name}"}
    try:
        subprocess.Popen([exe])
        return {"ok": True, "kind": "app", "target": name, "result": f"launched '{name}'"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "kind": "app", "target": name, "error": str(exc)}


def _system_control(command: str) -> dict[str, Any]:
    """Execute simple OS-level commands (volume, lock)."""
    if not _WINDOWS:
        return {"ok": False, "error": "system control only supported on Windows"}
    
    cmd_lower = command.lower()
    try:
        if cmd_lower in ["mute", "unmute"]:
            # Toggle mute (VK_VOLUME_MUTE = 173)
            subprocess.Popen(["powershell", "-c", "$obj = new-object -com wscript.shell; $obj.SendKeys([char]173)"], shell=True)
            return {"ok": True, "kind": "system", "command": cmd_lower, "result": "toggled mute"}
        elif cmd_lower == "volume_up":
            # VK_VOLUME_UP = 175
            subprocess.Popen(["powershell", "-c", "$obj = new-object -com wscript.shell; $obj.SendKeys([char]175)"], shell=True)
            return {"ok": True, "kind": "system", "command": cmd_lower, "result": "volume increased"}
        elif cmd_lower == "volume_down":
            # VK_VOLUME_DOWN = 174
            subprocess.Popen(["powershell", "-c", "$obj = new-object -com wscript.shell; $obj.SendKeys([char]174)"], shell=True)
            return {"ok": True, "kind": "system", "command": cmd_lower, "result": "volume decreased"}
        elif cmd_lower == "lock_screen":
            subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"], shell=True)
            return {"ok": True, "kind": "system", "command": cmd_lower, "result": "screen locked"}
        else:
            return {"ok": False, "error": f"unknown system command: {command}"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def execute_tool(tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
    """Dispatch a tool request to the local bridge. Returns a result dict."""
    if tool_name == "windows_open":
        target = (params or {}).get("target", "")
        return open_with_default(target)
    elif tool_name == "windows_system_control":
        command = (params or {}).get("command", "")
        return _system_control(command)
    return {"ok": False, "error": f"unsupported device tool: {tool_name}"}
