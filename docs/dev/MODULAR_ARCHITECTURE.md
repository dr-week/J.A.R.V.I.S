# Modular Architecture & Reusable Codeblocks Specification

This document details the modular standards, directory topology, and reusable codeblock primitives for developing plugins and tools within the Jarvis ecosystem.

---

## 1. Directory Topology

Every subsystem and plugin must follow this exact 3-file or 4-file pattern:

```text
backend/plugins/<plugin_name>/
├── __init__.py      # Thin facade: re-exports public API and runs register_<plugin>()
├── client.py        # External REST/WebSocket network interfaces (zero business logic)
├── engine.py        # (Optional) Binary/subprocess runner or local ML execution
├── tools.py         # Tool handlers & registration schemas
└── models.py        # (Optional) Data structures or Pydantic models
```

---

## 2. Reusable Modular Codeblocks

### A. Resilient Async HTTP Client Pattern
```python
import httpx
from typing import Any

class ResilientHttpClient:
    def __init__(self, base_url: str, token: str = "", timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        h = {"Accept": "application/json", "User-Agent": "Jarvis-Brain"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    async def post_json(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload, headers=self.headers)
            resp.raise_for_status()
            return resp.json()
```

### B. Safe Asynchronous CLI Subprocess Runner Pattern
```python
import asyncio
import shutil
from typing import Any

class SafeCliRunner:
    @staticmethod
    def resolve_binary(*candidates: str) -> str:
        for name in candidates:
            found = shutil.which(name)
            if found:
                return found
        return ""

    @staticmethod
    async def run_command(cmd: list[str], timeout: float = 30.0) -> dict[str, Any]:
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return {
                "ok": proc.returncode == 0,
                "returncode": proc.returncode,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
            }
        except asyncio.TimeoutError:
            return {"ok": False, "error": f"Command timed out after {timeout}s"}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
```

### C. Self-Healing Error Diagnostics Envelope
```python
from typing import Any

def make_error_envelope(
    error_code: str,
    message: str,
    suggestion: str,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "status": "error",
        "ok": False,
        "error_code": error_code.upper(),
        "error": message,
        "suggestion": suggestion,
        **extra,
    }
```

---

## 3. Strict Development Rules

1. **Max File Size**: No file shall exceed **200 lines**. Target is **80–120 lines**.
2. **Output Truncation**: All tool results must respect the 1,400 character / 40 line ceiling.
3. **No Monolithic Registries**: Tools must never be declared inline inside large single files. They must be registered via `tools.py` or the `@tool` decorator.
