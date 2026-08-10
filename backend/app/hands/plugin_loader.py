"""Load backend/plugins and repo-root tools/ into the tool registry."""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path


def discover_plugins() -> None:
    """Scan backend/plugins/ and repo-root tools/ and import plugin modules."""
    plugins_dir = Path(__file__).resolve().parent.parent.parent / "plugins"
    if plugins_dir.exists():
        backend_dir = str(plugins_dir.parent)
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)

        for entry in os.scandir(plugins_dir):
            if entry.is_dir() and not entry.name.startswith("__"):
                init_file = Path(entry.path) / "__init__.py"
                if init_file.exists():
                    module_name = f"backend.plugins.{entry.name}"
                    try:
                        importlib.import_module(module_name)
                        print(f"[registry] Loaded plugin: {entry.name}")
                    except Exception as exc:
                        print(f"[registry] Failed to load plugin {entry.name}: {exc}", file=sys.stderr)

    repo_root = Path(__file__).resolve().parents[3]
    tools_dir = repo_root / "tools"
    if not tools_dir.is_dir():
        return

    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    for entry in os.scandir(tools_dir):
        if entry.is_dir() and not entry.name.startswith("__"):
            init_file = Path(entry.path) / "__init__.py"
            if init_file.exists():
                module_name = f"tools.{entry.name}"
                try:
                    importlib.import_module(module_name)
                    print(f"[registry] Loaded tool plugin: {entry.name}")
                except Exception as exc:
                    print(f"[registry] Failed to load tool plugin {entry.name}: {exc}", file=sys.stderr)
