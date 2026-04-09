# A2A Protocol Dojo

> Interactive tutorial for learning Google's Agent-to-Agent (A2A) protocol — the open standard for agent interoperability.

**Python 3.12** | **React 19** | **a2a-sdk** | **FastAPI**

## What is A2A?

A2A is an open protocol by Google that lets AI agents from different vendors, frameworks, and organizations communicate through a standard interface — built on HTTP, JSON-RPC 2.0, and Server-Sent Events.

## Architecture

```
Frontend (5173)          Backend Gateway (8000)        A2A Agents
┌──────────────┐        ┌──────────────────┐        ┌─────────────────┐
│ React 19     │───────►│ FastAPI          │───────►│ Echo Agent :8001│
│ Vite + TS    │        │ Lesson content   │        │ (pure Python)   │
│ 7 lessons    │        │ A2A proxy calls  │        ├─────────────────┤
│ Interactive  │        │ Agent management │───────►│ Gemini Agent    │
│ demos        │        │                  │        │ :8002 (Vertex)  │
└──────────────┘        └──────────────────┘        └─────────────────┘
```

## Quick Start

```bash
cd semiautonomous-agents/a2a-protocol-dojo

# 1. (Optional) Configure GCP for Gemini Agent
cp .env.example .env
# Edit .env with your PROJECT_ID — or skip for mock mode

# 2. Start everything
chmod +x start_all.sh
./start_all.sh

# 3. Open http://localhost:5173
```

**No API keys needed for lessons 1-4** — the Echo Agent is pure Python. Lessons 5-7 use the Gemini Agent (mock mode if no GCP project configured).

## Lessons

| # | Title | Type | What You Learn |
|---|-------|------|---------------|
| 1 | What is A2A? | Theory | Protocol overview, design principles, A2A vs MCP |
| 2 | Agent Cards — Discovery | Interactive | Fetch a real Agent Card, understand the schema |
| 3 | Tasks & Lifecycle | Interactive | Watch tasks progress through states in real-time |
| 4 | Messages & Parts | Interactive | Build JSON-RPC messages, send to Echo Agent |
| 5 | Streaming with SSE | Interactive | Stream Gemini responses, see raw SSE events |
| 6 | Artifacts & Skills | Interactive | Browse agent skills, invoke them |
| 7 | Multi-Agent Orchestration | Interactive | Orchestrator discovers and delegates to agents |

## Project Structure

```
a2a-protocol-dojo/
├── agents/
│   ├── echo_agent.py          # A2A agent: echoes messages (port 8001)
│   ├── gemini_agent.py        # A2A agent: Gemini 2.5 Flash (port 8002)
│   └── pyproject.toml         # a2a-sdk, google-genai
├── backend/
│   ├── main.py                # FastAPI gateway (port 8000)
│   ├── lessons/               # 7 lesson markdown files
│   └── pyproject.toml         # fastapi, httpx
├── frontend/
│   ├── src/
│   │   ├── App.tsx            # Main app with sidebar + lesson view
│   │   ├── App.css            # Dark dojo theme
│   │   └── components/        # 7 interactive demo components
│   ├── package.json           # React 19, Vite, TypeScript
│   └── vite.config.ts         # Proxy /api → backend
├── start_all.sh               # Launch all 4 services
├── .env.example
└── README.md
```

## Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| A2A Protocol | [a2a-sdk](https://pypi.org/project/a2a-sdk/) | Agent-to-Agent communication |
| Echo Agent | Pure Python + a2a-sdk | Demo agent, no API keys |
| Gemini Agent | google-genai + a2a-sdk | AI-powered agent with streaming |
| Backend | FastAPI + httpx | Lesson serving, A2A proxying |
| Frontend | React 19 + Vite + TypeScript | Interactive tutorial UI |

## Manual Start (Individual Services)

```bash
# Terminal 1: Echo Agent
cd agents && uv run python echo_agent.py

# Terminal 2: Gemini Agent
cd agents && uv run python gemini_agent.py

# Terminal 3: Backend
cd backend && uv run uvicorn main:app --port 8000

# Terminal 4: Frontend
cd frontend && npm run dev
```

## Resources

- [A2A Protocol Specification](https://a2a-protocol.org/latest/specification/)
- [A2A Python SDK](https://github.com/a2aproject/a2a-python)
- [Google Blog: A2A Announcement](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
