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

<br/>

```
      ▲
     / \     "Allow me to introduce myself. I am J.A.R.V.I.S., 
    /   \     your personal AI operator. Operating silently in the background,
   /  |  \    orchestrating 87+ tools, 23 open-source microservices,
  /   |   \   and anticipating your every move across your entire digital realm."
 /____|____\
```

</div>

---

## 📖 The Origin & Narrative: "The Stark Protocol"

> *"Sir, I have configured the workshop, synchronized your devices, connected the local neural models, and bypassed external SaaS dependencies. We are fully self-sufficient."*

**J.A.R.V.I.S.** is built on a single core philosophy: **True AI agency requires an omnipresent mind, reliable hands, and complete local independence.**

Rather than locking your workflows inside expensive proprietary API subscriptions, Jarvis acts as your **personal AI chief of staff**. It runs on your local hardware, communicates seamlessly with your phone, desktop, and smart home, and leverages the world's most powerful open-source projects to perform complex real-world tasks.

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

## 🔮 The 4 Pillars of J.A.R.V.I.S.

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 User / Operator
    participant Voice as 🎙️ Voice & Telegram Presence
    participant Brain as 🧠 Central Brain (FastAPI)
    participant Hands as ✋ Hands Execution Engine
    participant OSS as 🌐 23+ Open Source Plugins

    User->>Voice: "Jarvis, summarize the latest tech news & update my calendar"
    Voice->>Brain: Streamed Audio / Intent Routing
    Brain->>Hands: Validate Tool Permissions (Confirmation Gate)
    Hands->>OSS: Execute feedparser + icalendar (0-SaaS)
    OSS-->>Brain: Structured Output Data
    Brain-->>User: Synced Audio Response + Glassmorphism UI Update
```

1. 👻 **The Soul (Memory & Identity)**: Persistent SQLite semantic memory with vector ranking. Remembers facts, preferences, habits, and user context across device restarts.
2. 💭 **The Mind (Cognition & Routing)**: LLM gateway with strict scope enforcement, multi-turn dialogue, and dynamic tool orchestration.
3. ✋ **The Hands (Action & Safety)**: A confirmation-gated execution engine that controls local apps, browsers, devices, and files safely.
4. 🌐 **The Body (Omnipresent Presence)**: Live presence across iPhone/Web Glassmorphism UI, Windows system tray voice loop, and Telegram mobile bridge.

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

## 📦 Zero-SaaS Open Source Engine Matrix

| Category | Integrated Library / Tool | Replaced Proprietary Service | Monthly Cost Saved |
|---|---|---|---|
| **Speech-to-Text** | `faster-whisper` (Local ML) | OpenAI Whisper API | ~$50 / mo |
| **Translation** | `argostranslate` (Offline Neural) | Google Translate API | ~$20 / mo |
| **Web Search** | `SearXNG` (Self-Hosted Sidecar) | SerpAPI / Google Custom Search | ~$50 / mo |
| **Automation** | `n8n` (Self-Hosted Webhooks) | Zapier / Make | ~$30 / mo |
| **Stealth Web** | `CloakBrowser` + `Playwright` | Paid Scraping Proxies | ~$40 / mo |
| **Finance** | Plain-Text Ledger Engine | Mint / YNAB SaaS | ~$15 / mo |
| **Total Saved** | **23+ Integrated OSS Projects** | **All Paid APIs & Cloud Lock-in** | **~$205+ / month** |

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
