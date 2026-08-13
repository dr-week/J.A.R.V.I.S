<div align="center">

![J.A.R.V.I.S. Banner](./docs/assets/banner.jpg)

# 🤖 J.A.R.V.I.S.
### Just A Rather Very Intelligent System
**Autonomous Personal AI Operator · Multi-Agent Swarm · Zero-SaaS Local Engine**

[![Tests](https://img.shields.io/badge/pytest-59%20passed-success?style=for-the-badge&logo=pytest&logoColor=white)](#-testing--quality)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](#-license)
[![Python](https://img.shields.io/badge/python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#-tech-stack)
[![React](https://img.shields.io/badge/frontend-Vite%20%2B%20React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](#-web-interface)
[![Telegram](https://img.shields.io/badge/presence-Telegram%20Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](#-multi-presence)

</div>

---

## ⚡ Overview

**J.A.R.V.I.S.** is a close personal AI assistant designed to know the user (Soul), execute real-world system and web operations (Hands), and remain accessible across all devices (Presence). 

Built with **Zero-Code OSS Acceleration**, Jarvis integrates over **23 open-source libraries** and exposes **87+ executable tools** without relying on expensive SaaS APIs.

---

## 🌐 System Architecture

![J.A.R.V.I.S. Architecture](./docs/assets/architecture_hud.jpg)

```mermaid
graph TD
    A["👤 User (Voice / Web / Telegram)"] --> B["🧠 J.A.R.V.I.S. Central Brain (FastAPI)"]
    
    subgraph Brain ["Central Mind & Memory"]
        B --> C["👻 Soul: Persona & SQLite Semantic Memory"]
        B --> D["💭 Mind: Reasoning & Multi-Agent Router"]
        B --> E["✋ Hands: Confirmation Gate & Tool Registry"]
    end
    
    subgraph Ecosystem ["Zero-Code Open Source Plugins (87+ Tools)"]
        E --> F["📅 Core Tools: Calendar, Email, Contacts, Notes"]
        E --> G["🛠️ System Tools: Media, Screenshot OCR, Clipboard, Files"]
        E --> H["🤖 Automation: n8n Webhooks, MCP Protocol, CloakBrowser"]
        E --> I["🗣️ Presence: Faster-Whisper STT, Telegram Bot, Flet Tray"]
    end
```

---

## ✨ Features & Capabilities

### 📱 Multi-Presence & Voice
- **iPhone & Web Desktop Client**: Modern frosted glassmorphism interface built with Vite, React, and `100dvh` mobile responsiveness.
- **Hands-Free Voice Loop**: Opt-in background wake-word listener (`jarvis`) with system tray controls.
- **Telegram Bot Bridge**: Send text or voice notes to Jarvis directly from your phone.

### ✋ Autonomous Operations (Hands)
- **Stealth Web Scraping & Action**: `CloakBrowser` stealth Playwright engine bypasses anti-bot verification smoothly.
- **System Control**: Native volume & mute control (`pycaw`), clipboard manager (`pyperclip`), and OCR screen capture (`mss` + `pytesseract`).
- **Productivity Ecosystem**: Offline translation (`argostranslate`), PDF report generator (`fpdf2`), RSS news feedparser, Pomodoro focus timer, and habit streak tracker.

### ⚡ Zero-Code Automation
- **n8n Workflow Engine**: Trigger complex multi-app visual workflows (Gmail, Slack, Notion) via a single webhook tool.
- **MCP Server Discovery**: Auto-detects Anthropic Model Context Protocol tools (`npx` Github, Postgres, Brave Search).

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ (for Web Client & MCP)

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/dr-week/J.A.R.V.I.S.git
cd J.A.R.V.I.S

# Install dependencies
pip install -r requirements.txt

# Start the Brain server
python -m uvicorn backend.app.main:app --reload --port 8787
```

### 3. Web Client Setup
```bash
cd clients/web
npm install
npm run dev
```

---

## 🧪 Testing & Quality

Run the comprehensive pytest suite covering all 23 plugins and endpoints:

```bash
python -m pytest backend/tests/ -v
```

> **59 passed tests cleanly** across Brain, Soul, Hands, Webhooks, and Plugins.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
