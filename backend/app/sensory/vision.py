"""Visual Cortex (OpenCV + Tesseract) via MCP.

Provides 'Eyes' to see what is on the user's screen.
Runs a background loop to continuously capture the screen state.
Exposes 'Read Screen' as an MCP tool.
"""

import asyncio
import threading
import time

import cv2
import numpy as np
import pytesseract
from mcp.server.mcpserver import MCPServer
from PIL import ImageGrab

mcp = MCPServer("VisualCortex")

class VisualCortex:
    def __init__(self):
        self.latest_text = ""
        self.running = False
        self._thread = None

    def start_loop(self):
        """Start the background screen capture loop."""
        print("[Vision] Starting screen capture loop...")
        self.running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop_loop(self):
        """Stop the background screen capture loop."""
        print("[Vision] Stopping screen capture loop...")
        self.running = False
        if self._thread:
            self._thread.join()

    def _capture_loop(self):
        while self.running:
            try:
                # Capture screen using PIL ImageGrab
                screenshot = ImageGrab.grab()
                
                # Convert to numpy array for OpenCV
                img_np = np.array(screenshot)
                
                # Convert RGB to BGR for OpenCV (standard format)
                img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                
                # Preprocess for better OCR
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                
                # Extract text using Tesseract
                text = pytesseract.image_to_string(gray)
                
                self.latest_text = text.strip()
                
                # Sleep briefly to avoid high CPU usage
                time.sleep(2)
            except Exception as e:
                print(f"[Vision] Error capturing screen: {e}")
                time.sleep(5)

cortex = VisualCortex()

@mcp.tool()
def read_screen() -> str:
    """Read the current text/UI state from the user's screen.

    Returns the text extracted using OCR on the latest screen capture.
    """
    if not cortex.latest_text:
        return "No text detected or screen capture not ready."
    return cortex.latest_text

async def main():
    cortex.start_loop()
    try:
        await mcp.run_stdio_async()
    finally:
        cortex.stop_loop()

if __name__ == "__main__":
    asyncio.run(main())
