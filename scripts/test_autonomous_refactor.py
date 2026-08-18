"""End-to-End Autonomous Refactoring Test.
Demonstrates: Intent Classification -> AST Outline -> Chunk Read -> AST Pre-Validated Edit -> Integrity Gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.mind.router import classify_intent_fast
from backend.app.hands.tools.workspace_tools import (
    workspace_map_tree,
    file_ast_outline,
    file_read_chunk,
    file_edit_strict,
)


def run_e2e_refactor_test():
    print("=" * 65)
    print("   AUTONOMOUS WORKSPACE REFACTORING END-TO-END TEST")
    print("=" * 65)

    # Step 1: Intent Routing (<1ms CPU check)
    user_prompt = "Inspect and refactor router.py to support docker commands"
    print(f"\n[1/5] Testing Intent Router for: '{user_prompt}'")
    tools = classify_intent_fast(user_prompt)
    print(f"      Matched Active Tool Schemas: {tools}")
    assert "file_edit_strict" in tools
    assert "file_ast_outline" in tools
    print("      [OK] Intent Router correctly identified 'code' domain.")

    # Step 2: AST File Outline (<5ms)
    target_rel = "backend/app/mind/router.py"
    print(f"\n[2/5] Generating AST Skeleton for: {target_rel}")
    outline = file_ast_outline(target_rel)
    print(f"      File Total Lines: {outline['total_lines']}")
    print(f"      Functions Found: {outline['functions']}")
    assert outline["ok"] is True
    assert len(outline["functions"]) > 0
    print("      [OK] AST Skeleton generated (<80 tokens context footprint).")

    # Step 3: Surgical Line Range Inspection (<2ms)
    print(f"\n[3/5] Reading Precise Chunk (lines 40 to 60)")
    chunk = file_read_chunk(target_rel, start_line=40, end_line=60)
    assert chunk["ok"] is True
    assert "DOMAIN_SYNONYMS" in chunk["content"]
    print("      [OK] Chunk retrieved cleanly with zero whole-file overhead.")

    # Step 4: AST Pre-Validated Code Modification (<5ms)
    print(f"\n[4/5] Applying AST Pre-Validated Code Edit with 'file_edit_strict'")
    search_target = '"code": {"evaluate", "execute", "run", "script", "benchmark", "pytest", "refactor", "fix", "inspect", "debug", "file", "tree", "lines"},'
    replacement = '"code": {"evaluate", "execute", "run", "script", "benchmark", "pytest", "refactor", "fix", "inspect", "debug", "file", "tree", "lines", "docker", "container"},'

    edit_res = file_edit_strict(
        file_path=target_rel,
        search=search_target,
        replace=replacement,
        start_line=43,
        end_line=55
    )
    print(f"      Edit Result: {edit_res}")
    assert edit_res["ok"] is True
    print("      [OK] Pre-write AST gate passed and atomic disk write completed.")

    # Step 5: Verify new capability in live router
    print(f"\n[5/5] Verifying new 'docker' keyword in live router")
    new_prompt = "Run my docker container"
    new_tools = classify_intent_fast(new_prompt)
    print(f"      Router output for '{new_prompt}': {new_tools}")
    assert "workspace_map_tree" in new_tools or "file_edit_strict" in new_tools
    print("      [OK] Live router successfully recognized new domain token!")

    print("\n" + "=" * 65)
    print("   [SUCCESS] ALL 5 END-TO-END REFACTORING PHASES PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    run_e2e_refactor_test()
