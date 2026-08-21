---
name: jarvis-ui-builder
description: Autonomous UI builder, design system enforcer, and token-saving template generator for Jarvis Presence clients.
---

# Jarvis UI Builder & Token-Saving Architecture Skill

This skill governs the generation, testing, and optimization of user interfaces across Vite Web, Flutter, and Desktop.

## 1. Core Principles
- **One Screen, One Truth:** Keep the chat hero unobstructed; collapse secondary menus.
- **AST Pre-Validation:** Check syntax balance before filesystem writes (0 broken builds).
- **Zero-Drift Template Caching:** Pull pre-validated components from local cache to save 80% token cost.
- **India Market Optimization:** Integrate UPI 1-tap intent, clear rupee pricing (`₹`), and bottom thumb navigation.

## 2. Canonical Tech Stack
- **Web Presence:** Vite + React 18 + Tailwind CSS + Zustand + Lucide Icons
- **Mobile Presence:** Flutter + Riverpod + WebSocket Brain Bridge
- **Backend Bridge:** FastAPI + Tool Registry Gate (`hands/gate.py`)

## 3. Execution Verification
- Web bundle size must remain `< 250 KB`.
- Cold start load time must remain `< 400 ms`.
