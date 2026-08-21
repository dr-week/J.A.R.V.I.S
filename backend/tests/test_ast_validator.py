import unittest
from backend.app.mind.ast_validator import (
    validate_python_syntax,
    validate_json_syntax,
    validate_bracket_balance
)

class TestAstValidator(unittest.TestCase):
    def test_valid_python_syntax(self):
        valid_code = "def hello():\n    return 'world'\n"
        is_valid, msg = validate_python_syntax(valid_code)
        self.assertTrue(is_valid)

    def test_invalid_python_syntax(self):
        invalid_code = "def broken(:\n    pass\n"
        is_valid, msg = validate_python_syntax(invalid_code)
        self.assertFalse(is_valid)
        self.assertIn("SyntaxError", msg)

    def test_valid_json_syntax(self):
        valid_json = '{"name": "Jarvis", "version": 1}'
        is_valid, msg = validate_json_syntax(valid_json)
        self.assertTrue(is_valid)

    def test_bracket_balance_valid(self):
        js_code = "function test() { const arr = [1, 2, 3]; return arr.map(x => (x * 2)); }"
        is_valid, msg = validate_bracket_balance(js_code)
        self.assertTrue(is_valid)

    def test_bracket_balance_unclosed(self):
        broken_js = "function broken() { const arr = [1, 2, 3; return arr; }"
        is_valid, msg = validate_bracket_balance(broken_js)
        self.assertFalse(is_valid)

if __name__ == "__main__":
    unittest.main()
