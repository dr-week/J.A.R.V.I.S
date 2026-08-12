# OSS Steal Process: Cannibalizing the Open Source Community

**Why this exists:** The Open Source community has built hundreds of "Jarvis" clones and AI web tools. We do not need to reinvent the wheel. Instead, we surgically extract the best modules from these repositories and integrate them into our centralized Brain and Cross-Device Architecture.

## The Hitlist

### 1. `isair/jarvis` — MCP (Model Context Protocol)
*   **What it is:** A local assistant with a heavy emphasis on Model Context Protocol (MCP) support.
*   **The Steal:** Instead of writing custom plugins for everything (GitHub, Jira, SQLite, File System), we will implement an **MCP Client** in our `backend/app/hands/registry.py`. 
*   **Outcome:** Jarvis instantly gains access to the entire Anthropic open-source MCP ecosystem.

### 2. `unclecode/crawl4ai` (over `firecrawl`)
*   **What it is:** `crawl4ai` is a wildly popular, ultra-fast async web scraper designed specifically for LLMs. It extracts raw HTML into RAG-ready markdown. `firecrawl` does the same but is primarily a paid API/Service.
*   **The Steal:** We will integrate `crawl4ai` directly into our Phase 3 Life Tools as a `web_research` plugin.
*   **Outcome:** Jarvis can autonomously read web pages, bypass popups, and summarize long-form articles in seconds natively without relying on a paid API.

### 3. `anthropics/claude-code`
*   **What it is:** Anthropic's official terminal-based agentic coding tool.
*   **The Steal:** We use this for **Development Velocity**. We can integrate `claude-code` into our `scripts/devloop.py` pipeline, or wrap it as a background subprocess plugin so Jarvis can literally write and commit code to his own repository autonomously.
*   **Outcome:** Jarvis becomes a self-improving codebase.

### 4. Desktop Automations (`Gladiator07/JARVIS` & `alexylem/jarvis`)
*   **What it is:** Legacy Python and Bash-based voice assistants.
*   **The Steal:** These repos contain hundreds of OS-level automation scripts (muting volume, opening Spotify, changing brightness). We will copy-paste their raw automation commands into our `clients/windows/device_bridge.py`.
*   **Outcome:** Instant deep OS integration for the Windows and Linux clients without writing the gross OS-specific API calls ourselves.

### 5. `home-assistant/core`
*   **What it is:** The gold standard for open-source local home automation.
*   **The Steal:** We will NOT rewrite a smart home engine. Instead, for Phase 5 (House Body), we will build a `HomeAssistantPlugin` that talks directly to your local Home Assistant instance via its REST/WebSocket API. 
*   **Outcome:** Jarvis instantly controls lights, locks, and sensors across hundreds of brands, fully locally, and with context on your India-based locale and timezone.

### 6. `saltstack/salt`
*   **What it is:** Infrastructure automation and configuration management at scale.
*   **The Steal:** We can steal Salt's "minion" architecture concepts for managing multiple devices. If Jarvis is running on your PC, laptop, and phone, we use Salt-like states to keep them synced.

### 7. Desktop Control (`octalmage/robotjs` concepts)
*   **What it is:** Node.js library for controlling the mouse and keyboard.
*   **The Steal:** Since we use Python, we won't use RobotJS directly, but we will steal its *capabilities* via Python equivalents (like `pyautogui` or `pynput`) in the `device_bridge`.
*   **Outcome:** Jarvis can take over your mouse and keyboard to execute UI-driven macros on the Windows client.

### 8. `AtsushiSakai/PythonRobotics`
*   **What it is:** Python sample codes for robotics algorithms (path planning, SLAM).
*   **The Steal:** This is for Phase 6+ (Hardware Body). When we hook Jarvis into an Arduino or ROS2, we steal these localization and mapping algorithms so Jarvis can navigate physical space.

### 9. `localsend/localsend`
*   **What it is:** An open-source cross-platform alternative to AirDrop.
*   **The Steal:** For our **Phase 5/6 Device Sync**, we can cannibalize LocalSend's local network discovery and secure file transfer protocols. This allows Jarvis's Android, Windows, and House Body clients to sync state instantly over LAN without relying on a cloud server.

### 10. `cactus-compute/needle`
*   **What it is:** A 14MB foundation model for tiny devices (phones, wearables, smart home, robots).
*   **The Steal:** We can deploy this tiny model on our mobile (Flutter) and House Body (Raspberry Pi) satellites for zero-latency, local intent classification and wake-word verification.

### 11. Productivity & Agent Frameworks (`hugohe3/ppt-master`, `infiniflow/ragflow`, `paperclipai/paperclip`)
*   **What they are:** Tools for generating native PowerPoints, advanced RAG engines, and agent management workspaces.
*   **The Steal:** 
    *   We will wrap `ppt-master` into a Phase 3 Productivity Plugin so Jarvis can generate native `.pptx` files.
    *   We will adopt `ragflow`'s document chunking strategies to upgrade Jarvis's semantic memory (`sqlite-vec`).
    *   We will analyze `paperclip` and `orca` to inform how we orchestrate multiple parallel AIs in the background.

### 12. Workflow Automation (`n8n-io/n8n`, `langgenius/dify`)
*   **What they are:** Visual workflow automation platforms for AI and APIs.
*   **The Steal:** We won't rewrite a visual node editor. Instead, we can build a plugin that allows Jarvis to trigger your existing `n8n` or `dify` webhooks. If you have a complex 50-step automation built in n8n, Jarvis can just trigger it and wait for the response, acting as the ultimate front-end for your automations.

### 13. Browser Automation (`puppeteer/puppeteer`, `microsoft/playwright`, `SeleniumHQ/selenium`)
*   **What it is:** The gold standard for browser automation.
*   **The Steal:** We already stole `crawl4ai` (which uses Playwright) for extracting Markdown. We can extend this to allow Jarvis to take over a headless browser to actually click buttons, fill forms, and navigate sites that don't have APIs.

### 14. The MCP Ecosystem (`HKUDS/nanobot`, `ComposioHQ/awesome-claude-skills`, `Panniantong/Agent-Reach`)
*   **What they are:** Frameworks and lists of pre-built MCP (Model Context Protocol) servers and skills.
*   **The Steal:** Instead of building scraping plugins, GitHub plugins, or SQL plugins from scratch, we build the **MCP Client** (Step 2). Once built, we just download `Agent-Reach` or tools from `awesome-claude-skills` and plug them straight into Jarvis. This outsources 90% of our tool development to the open-source community.

### 15. Advanced Voice & TTS (`RVC-Boss/GPT-SoVITS`, `microsoft/VibeVoice`, `CorentinJ/Real-Time-Voice-Cloning`)
*   **What they are:** Cutting-edge, open-source Text-to-Speech (TTS) and voice cloning models.
*   **The Steal:** Our Phase 4 Voice Exit currently uses `pyttsx3`, which works entirely offline but sounds like a 1990s robot. We can cannibalize GPT-SoVITS or VibeVoice to give Jarvis a hyper-realistic, human-like voice (perhaps even cloning Paul Bettany's voice from Iron Man) that runs fully locally and in real-time on your GPU.

### 16. Local NLU (`RasaHQ/rasa`)
*   **What it is:** An open-source machine learning framework for conversational AI.
*   **The Steal:** If we want to move away from relying on cloud LLMs (like Gemini/Claude) for simple commands ("turn on the lights"), we can use Rasa's NLU engine locally to classify user intent with zero latency.

### 17. Autonomous Coding (`bin123apple/AutoCoder`, `w4n9H/autocoder-nano`, `10Nates/ollama-autocoder`)
*   **What they are:** Frameworks and CLI tools that allow AI agents to autonomously write, edit, and run code.
*   **The Steal:** We combine these concepts with `claude-code` to build the **Velocity Upgrade**. We can give Jarvis a `code_executor` plugin that allows him to literally write his own plugins, run tests, and commit them to this repository. Jarvis becomes self-improving.

## Execution Strategy

1. **Step 1: (COMPLETED)** Implement `crawl4ai` as a `backend/plugins/web` tool.
2. **Step 2:** Implement the MCP Client inside the tool registry. This fundamentally changes how we add tools.
3. **Step 3:** Port OS-level scripts and PyAutoGUI (RobotJS equivalent) into the `device_bridge`.
4. **Step 4:** Integrate `home-assistant/core` API for Phase 5 (House Body), utilizing your local India timezone/context.
5. **Step 5:** Implement LocalSend network discovery for seamless LAN syncing between devices.
6. **Step 6:** Upgrade Jarvis's voice engine using `GPT-SoVITS` or `VibeVoice`.
7. **Step 7:** Build the AutoCoder/Velocity plugin so Jarvis can write his own code.
