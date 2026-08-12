"""R Demo Plugin.

Demonstrates running an R script as a subprocess using the ExternalExecutor.
"""
from __future__ import annotations

import os

from backend.app.hands import registry

plugin_dir = os.path.dirname(os.path.abspath(__file__))
r_script_path = os.path.join(plugin_dir, "run.R")

registry.register(
    {
        "name": "r_demo_stats",
        "description": "Calculates summary statistics using an R subprocess.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "confirm_always",
        "executor": "brain",
        "runtime": "subprocess",
        "argv_template": ["Rscript", r_script_path],
        "timeout_seconds": 15,
        "parameters": {
            "type": "object",
            "properties": {
                "numbers": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "An array of numbers to calculate stats for."
                }
            },
            "required": ["numbers"],
        },
        "returns": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "object",
                    "properties": {
                        "mean": {"type": "number"},
                        "median": {"type": "number"},
                        "sd": {"type": "number"},
                        "min": {"type": "number"},
                        "max": {"type": "number"},
                        "count": {"type": "number"}
                    }
                }
            }
        },
        "scopes": [],
        "tags": ["plugin", "r", "demo", "subprocess"],
    }
)
