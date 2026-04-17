# sockagent

Terminal-aesthetic mobile PWA for chatting with Vertex AI Gemini.

```
┌─────────────────────────────┐
│        sockagent v0.1       │
│   vertex ai terminal chat   │
└─────────────────────────────┘
```

## Stack

- **Backend**: FastAPI + google-genai SDK (Vertex AI)
- **Frontend**: React 18 + TypeScript + Vite + Zustand
- **Style**: JetBrains Mono, phosphor green on black, box-drawing chars
- **PWA**: Installable on mobile, works offline for cached assets

## Setup

### 1. Environment

```bash
cp .env.example .env
# Edit .env with your GCP project ID
```

### 2. Backend

```bash
cd backend
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### Both at once

```bash
chmod +x scripts/dev.sh
./scripts/dev.sh
```

Open `http://localhost:5173`

## Architecture

```
sockagent/
  backend/
    main.py          # FastAPI — REST + WebSocket
    config.py        # env vars
    pyproject.toml   # uv project
  frontend/
    src/
      App.tsx        # main layout
      components/    # ChatView, InputBar, MessageBubble, ThinkingState, ModelPicker, SessionList
      stores/        # Zustand chat store
      api/           # fetch + WebSocket client
      styles/        # terminal.css
    public/
      manifest.json  # PWA manifest
      sw.js          # service worker
  scripts/
    dev.sh           # start both servers
```

## Features (Phase 1)

- Streaming chat via WebSocket
- Model switching: gemini-2.5-flash / gemini-2.5-pro
- In-memory session management
- Terminal-style UI with spinning cursor thinking state
- Optional API key auth (X-API-Key header)
- PWA installable on mobile
