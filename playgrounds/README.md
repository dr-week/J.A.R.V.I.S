# 🛝 The Autonomous Playground

Welcome to the Playground. This directory is specifically designed for the **"Test As You Build"** architectural pattern. 

## The Rules of the Playground

1. **100% Modular:** Scripts in this folder must have **zero dependencies** on the main Jarvis `backend/` or `scripts/` directories. 
2. **Autonomous Units:** Every script must be able to run independently as a standalone process (e.g., `python 01_system_monitor.py`).
3. **Instant Feedback:** The purpose of the playground is live, instant testing. Scripts should output clear, readable feedback directly to the terminal.
4. **Promotion to Core:** Once a playground script is perfected and validated by the user, it can be migrated and integrated into the central Jarvis Brain (via the `SYNC_PROTOCOL`).

*Use this space to build autonomous robots, plugins, and prototypes quickly and safely without destabilizing the core brain.*
