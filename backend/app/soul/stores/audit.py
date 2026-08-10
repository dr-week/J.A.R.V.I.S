"""Soul store — tool execution audit log."""
from __future__ import annotations

import json
from typing import Any

from ..db import _db, _utc


def log_action(
    tool_name: str,
    parameters: dict,
    result_summary: str = "",
    device_id: str = "",
    confirmed_by: str = "auto",
) -> None:
    with _db() as conn:
        conn.execute(
            "INSERT INTO action_log(ts,tool_name,parameters_json,result_summary,device_id,confirmed_by) VALUES(?,?,?,?,?,?)",
            (_utc(), tool_name, json.dumps(parameters), result_summary, device_id, confirmed_by),
        )


def list_action_log(limit: int = 50) -> list[dict[str, Any]]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, ts, tool_name, parameters_json, result_summary, device_id, confirmed_by "
            "FROM action_log ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        try:
            item["parameters"] = json.loads(item.pop("parameters_json") or "{}")
        except json.JSONDecodeError:
            item["parameters"] = {}
            item.pop("parameters_json", None)
        out.append(item)
    return out
