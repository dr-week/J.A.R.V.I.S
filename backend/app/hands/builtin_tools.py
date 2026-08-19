"""Built-in tools bootstrap — registers all built-in tool groups at import time.

Each tool group lives in its own focused module under backend/app/hands/tools/:
  - core_tools.py        : hello_world, get_current_time, dangerous_demo
  - client_tools.py      : android_open, windows_open, windows_system_control
  - workspace_tools.py   : workspace_map_tree, file_ast_outline, file_read_chunk
  - workspace_schemas.py : file_edit_strict schema registration
  - velocity_build.py    : dev_eval_python, dev_run_tests
"""
from __future__ import annotations


def register_builtin_tools() -> None:
    """Bootstrap — calls each group register function in dependency order."""
    from .tools.core_tools import register_core_tools
    from .tools.client_tools import register_client_tools
    from .tools.velocity_build import register_velocity_build
    from .tools.workspace_schemas import register_workspace_tools

    register_core_tools()
    register_client_tools()
    register_velocity_build()
    register_workspace_tools()
