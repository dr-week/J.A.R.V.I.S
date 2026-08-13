"""n8n Workflow Automation Sidecar Plugin.

Enables full zero-code automation by delegating complex multi-app workflows
to a local self-hosted n8n instance via webhooks.
"""
from __future__ import annotations

import os
import json
import urllib.request
from typing import Any
from backend.app.hands import registry

N8N_WEBHOOK_BASE = os.environ.get("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/")


def _n8n_trigger_workflow(workflow_slug: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Trigger an automated workflow in n8n via webhook without writing Python code."""
    url = f"{N8N_WEBHOOK_BASE.rstrip('/')}/{workflow_slug.lstrip('/')}"
    payload_data = json.dumps(data or {}).encode("utf-8")
    
    try:
        req = urllib.request.Request(
            url,
            data=payload_data,
            headers={"Content-Type": "application/json", "User-Agent": "Jarvis-Brain"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw_res = resp.read().decode("utf-8")
            try:
                res_json = json.loads(raw_res)
            except Exception:
                res_json = {"raw": raw_res}
            return {"status": "triggered", "workflow": workflow_slug, "response": res_json}
    except Exception as exc:
        return {"error": f"n8n webhook call failed: {exc}. Ensure n8n is running at {N8N_WEBHOOK_BASE}"}


registry.register(
    {
        "name": "n8n_trigger_workflow",
        "description": "Trigger a full zero-code automated workflow (e.g. Gmail->Slack, Notion->Sheets) in n8n via webhook.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "confirm_once",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow_slug": {
                    "type": "string",
                    "description": "Webhook endpoint slug configured in n8n (e.g. 'send-slack-summary')",
                },
                "data": {
                    "type": "object",
                    "description": "Arbitrary key-value payload to pass into the workflow",
                },
            },
            "required": ["workflow_slug"],
        },
        "returns": {"type": "object", "properties": {"status": {"type": "string"}}},
        "scopes": ["automation:write"],
        "tags": ["n8n", "automation", "workflows", "zero-code"],
    },
    _n8n_trigger_workflow,
)
