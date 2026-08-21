"""AST Syntax Pre-Validator.

Adopted from Velocity engine (E:\\CODES\\velocity) to ensure 0-token waste,
validating Python, JavaScript, JSON, and HTML balance before disk writes.
"""
import ast
import json
import re
from typing import Tuple

def validate_python_syntax(code_str: str) -> Tuple[bool, str]:
    """Validates Python code syntax in <2ms using the native ast parser."""
    try:
        ast.parse(code_str)
        return True, "Valid Python syntax"
    except SyntaxError as e:
        return False, f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}"

def validate_json_syntax(json_str: str) -> Tuple[bool, str]:
    """Validates JSON formatting in <1ms."""
    try:
        json.loads(json_str)
        return True, "Valid JSON"
    except Exception as e:
        return False, f"Invalid JSON: {str(e)}"

def validate_bracket_balance(code_str: str) -> Tuple[bool, str]:
    """Fast check for matching parentheses, brackets, and braces in JS/TS/HTML."""
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    # Strip string literals to avoid false positives inside quotes
    cleaned = re.sub(r'(["\'])(?:(?=(\\?))\2.)*?\1', '', code_str)
    
    for idx, char in enumerate(cleaned):
        if char in "([{":
            stack.append((char, idx))
        elif char in ")]}":
            if not stack:
                return False, f"Unmatched closing bracket '{char}' at position {idx}"
            last_char, _ = stack.pop()
            if pairs[char] != last_char:
                return False, f"Mismatched bracket: expected '{pairs[char]}', got '{char}'"
                
    if stack:
        unclosed, pos = stack[-1]
        return False, f"Unclosed bracket '{unclosed}' opened at position {pos}"
        
    return True, "Balanced brackets"
