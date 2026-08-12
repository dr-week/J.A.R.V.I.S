"""System vitals tool.

Returns CPU, RAM, and disk summary using psutil.
"""
from __future__ import annotations

from typing import Any
import psutil

from backend.app.hands import registry

def system_vitals() -> dict[str, Any]:
    """Return CPU, RAM, and disk summary."""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    
    vm = psutil.virtual_memory()
    ram_total_gb = vm.total / (1024**3)
    ram_used_gb = vm.used / (1024**3)
    ram_percent = vm.percent

    disk = psutil.disk_usage('/')
    disk_total_gb = disk.total / (1024**3)
    disk_used_gb = disk.used / (1024**3)
    disk_percent = disk.percent

    return {
        "cpu": {
            "usage_percent": cpu_percent
        },
        "ram": {
            "total_gb": round(ram_total_gb, 2),
            "used_gb": round(ram_used_gb, 2),
            "usage_percent": ram_percent
        },
        "disk": {
            "total_gb": round(disk_total_gb, 2),
            "used_gb": round(disk_used_gb, 2),
            "usage_percent": disk_percent
        }
    }

registry.register(
    {
        "name": "system_vitals",
        "description": "Get system vitals (CPU, RAM, Disk usage).",
        "version": "1.0.0", 
        "phase": 2, 
        "risk_level": "auto", 
        "executor": "brain",
        "parameters": {
            "type": "object", 
            "properties": {}, 
            "required": []
        },
        "returns": {
            "type": "object", 
            "properties": {
                "cpu": {"type": "object"},
                "ram": {"type": "object"},
                "disk": {"type": "object"}
            }
        },
        "scopes": ["system:read"], 
        "tags": ["system", "vitals"]
    },
    system_vitals
)
