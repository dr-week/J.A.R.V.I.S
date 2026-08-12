import sys
from lupa import LuaRuntime

def execute_lua(script_path: str):
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    lua = LuaRuntime(unpack_returned_tuples=True)
    
    try:
        result = lua.execute(code)
        return result
    except Exception as e:
        print(f"Error executing Lua script: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lua_executor.py <script.lua>")
        sys.exit(1)
        
    script_file = sys.argv[1]
    res = execute_lua(script_file)
    print("Result:", res)
