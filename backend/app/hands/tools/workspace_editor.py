"""Pre-validated atomic file editor with self-healing error envelopes."""
from __future__ import annotations

from typing import Any

from ...mind.ast_validator import validate_bracket_balance, validate_json_syntax, validate_python_syntax
from .workspace_tree import resolve_safe_path


def file_edit_strict(
    file_path: str,
    search: str,
    replace: str,
    start_line: int | None = None,
    end_line: int | None = None,
) -> dict[str, Any]:
    """Pre-validate syntax with AST and atomically apply search & replace edit."""
    try:
        p = resolve_safe_path(file_path)
        if not p.exists() or not p.is_file():
            return {"ok": False, "error": f"File '{file_path}' not found."}

        original = p.read_text(encoding="utf-8", errors="replace")

        # 1. Normalize line endings
        orig_norm = original.replace("\r\n", "\n")
        search_norm = search.replace("\r\n", "\n")
        replace_norm = replace.replace("\r\n", "\n")

        if search_norm not in orig_norm:
            total = len(orig_norm.splitlines())
            hint_start = max(1, (start_line or 1) - 5)
            hint_end = min(total, (end_line or hint_start) + 20)
            return {
                "ok": False,
                "status": "error",
                "error_code": "SEARCH_NOT_FOUND",
                "error": "Target search block not found. Exact whitespace and indentation must match.",
                "suggestion": (
                    f"Run file_read_chunk on '{file_path}' lines {hint_start}-{hint_end} "
                    "to inspect the exact text before retrying."
                ),
            }

        # 2. Check single occurrence
        count = orig_norm.count(search_norm)
        if count > 1 and start_line is None:
            return {
                "ok": False,
                "status": "error",
                "error_code": "AMBIGUOUS_MATCH",
                "error": f"Search block appears {count} times in file.",
                "suggestion": "Provide start_line and end_line to disambiguate the target occurrence.",
            }

        # 3. Perform atomic replacement
        new_content = orig_norm.replace(search_norm, replace_norm, 1)

        # 4. Pre-write AST / Syntax Validation Gate
        if p.suffix == ".py":
            is_valid, msg = validate_python_syntax(new_content)
            if not is_valid:
                return {
                    "ok": False,
                    "status": "error",
                    "error_code": "AST_SYNTAX_REJECTED",
                    "error": f"AST syntax validation failed: {msg}. Disk write aborted.",
                    "suggestion": "Fix the Python syntax error in your replace block before retrying.",
                }
        elif p.suffix == ".json":
            is_valid, msg = validate_json_syntax(new_content)
            if not is_valid:
                return {
                    "ok": False,
                    "status": "error",
                    "error_code": "JSON_SYNTAX_REJECTED",
                    "error": f"JSON syntax validation failed: {msg}. Disk write aborted.",
                    "suggestion": "Ensure your replace block produces valid JSON (check trailing commas or missing quotes).",
                }
        elif p.suffix in (".js", ".ts", ".tsx", ".jsx", ".html"):
            is_valid, msg = validate_bracket_balance(new_content)
            if not is_valid:
                return {
                    "ok": False,
                    "status": "error",
                    "error_code": "BRACKET_BALANCE_REJECTED",
                    "error": f"Bracket balance check failed: {msg}. Disk write aborted.",
                    "suggestion": "Count all opening/closing brackets, braces, and parens in your replace block.",
                }

        # 5. Write to disk
        p.write_text(new_content, encoding="utf-8")

        return {
            "ok": True,
            "file": file_path,
            "message": f"Successfully edited {file_path}",
            "lines_changed": len(replace_norm.splitlines()) - len(search_norm.splitlines()),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
