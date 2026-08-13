"""PDF Generation plugin — PDF document creation via fpdf2.

Self-registers when ``discover_plugins`` scans this package.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from backend.app.hands import registry

try:
    from fpdf import FPDF
    _HAS_FPDF = True
except ImportError:
    _HAS_FPDF = False

_REPORTS_DIR = Path(os.environ.get("JARVIS_REPORTS_DIR", "reports"))
_REPORTS_DIR.mkdir(exist_ok=True)


def _pdf_create_report(title: str, content: str, filename: str = "report.pdf") -> dict[str, Any]:
    """Create a styled PDF report."""
    if not _HAS_FPDF:
        return {"error": "fpdf2 is not installed. Run: pip install fpdf2"}
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 7, content)
        
        filepath = _REPORTS_DIR / filename
        pdf.output(str(filepath))
        return {"status": "created", "filepath": str(filepath.resolve())}
    except Exception as exc:
        return {"error": str(exc)}


registry.register(
    {
        "name": "pdf_create_report",
        "description": "Generate a PDF document/report from title and text content.",
        "version": "1.0.0",
        "phase": 6,
        "risk_level": "confirm_once",
        "executor": "brain",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "filename": {"type": "string"},
            },
            "required": ["title", "content"],
        },
        "returns": {"type": "object", "properties": {"filepath": {"type": "string"}}},
        "scopes": ["documents:write"],
        "tags": ["pdf", "documents"],
    },
    _pdf_create_report,
)
