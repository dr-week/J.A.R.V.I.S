import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DevWatcherHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_run = 0
        self.debounce_seconds = 1.0

    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Only watch python files
        if not event.src_path.endswith('.py'):
            return

        # Ignore virtual environments and cache
        if '.venv' in event.src_path or '__pycache__' in event.src_path or '.ruff_cache' in event.src_path:
            return

        # Debounce multiple save events
        current_time = time.time()
        if current_time - self.last_run < self.debounce_seconds:
            return
            
        self.last_run = current_time
        self.run_linter(event.src_path)

    def run_linter(self, filepath):
        os.system('cls' if os.name == 'nt' else 'clear')
        filename = os.path.basename(filepath)
        print(f"\n[DEV WATCHER] [UPDATE] File saved: {filename}")
        print(f"[DEV WATCHER] [RUN] Running Ruff Linter on {filepath}...\n")
        
        try:
            # Run ruff check
            result = subprocess.run(
                ["uv", "run", "ruff", "check", filepath],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"[PASS] No linting errors found in {filename}.")
            else:
                print(f"[FAIL] Linting errors detected!\n")
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
        except Exception as e:
            print(f"[DEV WATCHER] Error running linter: {e}")
            
        print("\n[DEV WATCHER] [IDLE] Watching for file changes... (Press Ctrl+C to stop)")

def main():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    event_handler = DevWatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"[AUTONOMOUS UNIT 02] Dev Watcher Booting Up...")
    print(f"Watching directory: {path}")
    print("Listening for changes to .py files. Press Ctrl+C to terminate.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[STOP] Dev Watcher Terminated.")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
