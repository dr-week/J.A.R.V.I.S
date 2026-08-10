import time
import datetime
import os
import psutil

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("[AUTONOMOUS UNIT 01] System Monitor Booting Up...")
    print("Entering background loop. Press Ctrl+C to terminate.\n")
    time.sleep(2)

    try:
        while True:
            clear_terminal()
            
            # Gather metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Print dashboard
            print(f"=== JARVIS AUTONOMOUS SYSTEM MONITOR ===")
            print(f"Time: {timestamp}")
            print(f"-------------------------------------------")
            print(f"CPU Usage:  {cpu_percent}%")
            print(f"RAM Usage:  {mem.percent}% ({mem.used / (1024**3):.1f}GB / {mem.total / (1024**3):.1f}GB)")
            print(f"-------------------------------------------")
            print(f"Agent Status:  [ACTIVE] | Monitoring every 2s")
            
            # Simulate a "decision"
            if cpu_percent > 80:
                print("[WARNING] High CPU load detected! Consider terminating background tasks.")
            elif mem.percent > 90:
                print("[WARNING] Critical Memory usage! System may page.")
            else:
                print("[OK] System metrics are within normal parameters.")

            time.sleep(1) # wait a second before next loop

    except KeyboardInterrupt:
        print("\n\n[STOP] Autonomous Unit Terminated by User.")
        print("Shutting down safely...")

if __name__ == "__main__":
    main()

# Trigger watcher

# Trigger watcher again
