# Contributing to J.A.R.V.I.S. 🤖

Thank you for your interest in contributing to **J.A.R.V.I.S.** (Just A Rather Very Intelligent System)! Whether you are fixing a bug, adding a new modular tool connector, enhancing one of the presence clients (Web, Flutter, Windows), or improving documentation, your contributions are welcome.

We operate as a **co-building ecosystem** where humans and AI coding agents (Cursor, Antigravity, Claude, MiniMax) collaborate seamlessly.

---

## 🌟 Core Principles to Keep in Mind

1. **Zero-SaaS & Local Sovereignty:** Whenever possible, avoid hard vendor lock-in. We favor self-hostable, open-source models, local memory, and offline-resilient utilities.
2. **Modular Micro-Plugins (No Monoliths):** New capabilities should be added as isolated, self-contained plugins under `backend/plugins/` or `tools/` with standardized Pydantic/Hands registry declarations.
3. **Flat, AI-Friendly Code:**
   - Small, focused files (avoid 300+ line monster modules).
   - Flat control flow (return early; avoid deeply nested conditionals).
   - Clear developer docstrings explaining **why** a decision was made.
4. **Security & Privacy First:** API tokens are always brain-local (read via `.env` or system environment). Never commit secrets, and never pass raw keys in LLM tool parameters.

---

## 🛠️ Development Environment Setup

### 1. Prerequisites
- **Python:** 3.10+ (3.12 or 3.14 recommended)
- **Node.js:** 18+ (for Web PWA)
- **Git**
- *(Optional)* Flutter SDK (for mobile presence client)
- *(Optional)* Ollama or LM Studio (for local LLM inference)

### 2. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/J.A.R.V.I.S.git
cd J.A.R.V.I.S
git remote add upstream https://github.com/dr-week/J.A.R.V.I.S.git
```

### 3. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies including development tools
pip install -r requirements.txt
pip install -e .[dev]

# Configure environment
cp .env.example .env
```

### 4. Web Client Setup
```bash
cd clients/web
npm install
npm run dev
# Vite server starts at http://localhost:5173
```

---

## 🔄 Contribution Workflow & DevLoop

We use a synchronized issue-driven workflow called `devloop` to prevent parallel worker collisions:

### 1. Choose or Create an Issue
Check open issues or create one:
```bash
# See current board status
python scripts/devloop.py status

# Create an issue if working on something new
python scripts/devloop.py issue --title "Add Weather Forecast Tool" --phase 3 --priority P1
```

### 2. Claim Your Issue
Pick your stable owner identifier (e.g. your GitHub username):
```bash
python scripts/devloop.py claim ISSUE-XXX --owner your_username
```

### 3. Create a Feature Branch
```bash
git checkout -b feat/ISSUE-XXX-short-description
```

### 4. Implement Your Changes
Follow the architectural guidelines and ensure your code contains clear docstrings.

### 5. Verify & Run Test Suites
All tests must pass before submitting a PR:
```bash
# Backend pytest suite (190+ tests)
python -m pytest backend/tests/ -v

# Web client lint & build
cd clients/web
npm run lint
npm run build
cd ../..

# Dev environment check
python scripts/check_dev_env.py
```

### 6. Close Issue in DevLoop & Commit
```bash
# Mark issue done
python scripts/devloop.py done ISSUE-XXX

# Commit with conventional commit format
git add .
git commit -m "feat(connector): add weather forecast tool (ISSUE-XXX)"
git push origin feat/ISSUE-XXX-short-description
```

### 7. Open a Pull Request
Submit your PR against the `master` branch of `upstream`.

---

## 🧩 How to Create a New Tool Plugin

Adding a new tool takes zero modifications to `main.py`. Just create a new directory inside `backend/plugins/`:

```python
# backend/plugins/my_connector/__init__.py
"""My Modular Connector Plugin.

Detailed explanation of purpose and architecture rationale.
"""
from __future__ import annotations
import os
from typing import Any
from backend.app.hands import registry

def _my_tool_function(query: str = "") -> dict[str, Any]:
    """Execute the core logic."""
    if not query.strip():
        raise ValueError("query cannot be empty.")
    return {"status": "ok", "result": f"Processed {query}"}

# Register tool to Hands Registry
if "my_tool_name" not in registry.REGISTRY:
    registry.register(
        {
            "name": "my_tool_name",
            "description": "Clear explanation of what the tool does for the AI router.",
            "version": "1.0.0",
            "phase": 3,
            "risk_level": "auto",  # 'auto' | 'confirm_once' | 'confirm_always'
            "executor": "brain",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                },
                "required": ["query"],
            },
            "returns": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "result": {"type": "string"},
                },
            },
            "scopes": ["my_tool:read"],
            "tags": ["my_connector", "productivity"],
        },
        _my_tool_function,
    )
```

Write matching unit tests in `backend/tests/test_my_connector.py` with mock HTTP/service fixtures.

---

## 📋 Pull Request Quality Checklist

Before submitting:
- [ ] Unit tests added covering both success and error cases.
- [ ] All 190+ existing unit tests continue to pass (`python -m pytest backend/tests/`).
- [ ] Web client builds cleanly with zero linter errors (`npm run lint` & `npm run build`).
- [ ] No hardcoded secrets or sensitive environment variables committed.
- [ ] Documentation / README updated if new endpoints or tools were introduced.

---

## 💬 Community & Help

- **GitHub Discussions:** [Ask architecture questions or share ideas](https://github.com/dr-week/J.A.R.V.I.S./discussions)
- **GitHub Issues:** [Report bugs or suggest features](https://github.com/dr-week/J.A.R.V.I.S./issues)
- **Code of Conduct:** Please review and follow our [Code of Conduct](CODE_OF_CONDUCT.md).
