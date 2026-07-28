# 🧭 Jetski Nav: Deployment Indexer & Session Context Hub

An automated navigation, indexing, and session context recovery engine for **Jetski**. `jetski-nav` scans all daily autonomous agent projects deployed under `semiautonomous-agents/`, monitors active background server ports, harvests conversation transcript histories, and instantly builds LLM context bundles.

---

## 🌟 Key Features

- **🧭 Central Deployment Indexer (`jetski_indexer.py`)**:
  - Automatically scans 80+ project folders under `semiautonomous-agents/`.
  - Extracts titles, descriptions, `SKILL.md` blueprints, `start.sh` scripts, and GitHub URLs.
  - Matches active background server ports (`lsof -i`) to detect running daemons in real-time.
  - Links Jetski brain conversation IDs (`<appDataDir>/brain/<conversation-id>`) to project folders.

- **💻 Interactive CLI (`./jetski-nav`)**:
  - `./jetski-nav`: Interactive terminal menu displaying top active & recent deployments with one-click prompt loading.
  - `./jetski-nav list`: Styled table view of all indexed deployments, running ports, and SKILL statuses.
  - `./jetski-nav load <project-id>`: Formats and outputs the complete LLM context bundle for immediate session resumption.

- **🖥️ IDE Web Sidecar Pane (`server.py` & `sidecar.json`)**:
  - Embedded sidecar tab inside Jetski IDE displaying live status badges (`🟢 8001: ONLINE`, `🟢 5173: ONLINE`).
  - Search filter across all deployments.
  - One-click **"📋 Copy Context Bundle"** button to inject full history into any new chat.

---

## 🚀 Quick Usage

### 1. Interactive Terminal Navigation
```bash
cd semiautonomous-agents/jetski-nav
./jetski-nav
```

### 2. Output Context Bundle for a Specific Project
```bash
./jetski-nav load pulse-spend-ai-galaxy-dashboard
```

### 3. Re-index All Projects & Transcripts
```bash
./jetski-nav --refresh
```

---

## 🏗️ Architecture & Project Files

```
jetski-nav/
├── jetski_indexer.py     # Core metadata harvester & active port detector
├── jetski-nav            # Executable terminal CLI & prompt bundle builder
├── server.py             # Lightweight sidecar web server (port 8099)
├── PROJECT_INDEX.json    # Generated JSON index database
└── README.md
```

---

## 🔌 Sidecar Integration

Configured automatically via `<configDir>/sidecars/jetski-nav/sidecar.json`:
- **Sidecar Display Name**: `Deployments & Context`
- **Web UI Entrypoint**: Full Pane Served on `ANTIGRAVITY_SIDECAR_WEB_PORT` (default `8099`)
