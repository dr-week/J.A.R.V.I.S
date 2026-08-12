"""Motor Cortex (PyAutoGUI) via MCP.

Provides 'Fingers' to control the Windows machine autonomously.
Implements Level 0-5 permission checks before clicking or typing.
"""
import os

import pyautogui
from mcp.server.mcpserver import MCPServer

# Initialize MCP server
mcp = MCPServer("MotorCortex")

# Level 0: Safe (No action, just observation)
# Level 1: Non-destructive moves
# Level 2: Clicks
# Level 3: Non-destructive typing
# Level 4: Destructive typing/keys (Enter, Delete)
# Level 5: Full unrestricted (e.g. formatting, sensitive apps)

def get_allowed_level() -> int:
    """Get the currently allowed permission level (0-5)."""
    return int(os.environ.get("MOTOR_PERMISSION_LEVEL", "5"))

def check_permission(required_level: int):
    """Enforce Level 0-5 permission checks."""
    allowed = get_allowed_level()
    if allowed < required_level:
        raise PermissionError(
            f"Action requires Level {required_level} permission, "
            f"but current level is {allowed}."
        )

@mcp.tool()
def get_screen_size() -> str:
    """Get the current screen resolution. Level 0."""
    check_permission(0)
    w, h = pyautogui.size()
    return f"Screen size: {w}x{h}"

@mcp.tool()
def get_mouse_position() -> str:
    """Get the current mouse coordinates. Level 0."""
    check_permission(0)
    x, y = pyautogui.position()
    return f"Mouse position: {x}, {y}"

@mcp.tool()
def mouse_move(x: int, y: int) -> str:
    """Move the mouse to absolute coordinates. Level 1."""
    check_permission(1)
    pyautogui.moveTo(x, y)
    return f"Mouse moved to {x}, {y}"

@mcp.tool()
def mouse_click(button: str = "left", clicks: int = 1) -> str:
    """Click the mouse button ('left', 'middle', 'right'). Level 2."""
    check_permission(2)
    pyautogui.click(button=button, clicks=clicks)
    return f"Clicked {button} button {clicks} times"

@mcp.tool()
def mouse_drag(x: int, y: int, button: str = "left") -> str:
    """Drag the mouse to absolute coordinates. Level 2."""
    check_permission(2)
    pyautogui.dragTo(x, y, button=button)
    return f"Mouse dragged to {x}, {y} with {button} button"

@mcp.tool()
def keyboard_type(text: str) -> str:
    """Type text on the keyboard. Level 3."""
    check_permission(3)
    pyautogui.write(text)
    return "Typed text successfully."

@mcp.tool()
def keyboard_press(key: str) -> str:
    """Press a specific key (e.g. 'enter', 'ctrl'). Level 4."""
    check_permission(4)
    pyautogui.press(key)
    return f"Pressed key: {key}"

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_stdio_async())
