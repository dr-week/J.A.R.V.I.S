import re
import os
import glob
import subprocess

def add_typing_any(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Look for functions in the API layer that need typing.
    # It's easier if we just use a regex like `async def ([a-zA-Z0-9_]+)\((.*?)\):`
    # and replace `):` with `) -> Any:`
    # Wait, we need to import Any.

    new_content = re.sub(r'async def ([a-zA-Z0-9_]+)\(([^)]*)\):', r'async def \1(\2) -> typing.Any:', content)
    
    if new_content != content:
        if "import typing" not in new_content:
             new_content = "import typing\n" + new_content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

for filepath in glob.glob("backend/app/api/*.py"):
    add_typing_any(filepath)

print("Done")
