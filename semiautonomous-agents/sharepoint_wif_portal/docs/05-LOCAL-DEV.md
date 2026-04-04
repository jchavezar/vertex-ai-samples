# Local Development

> **Version**: 1.0.0 | **Last Updated**: 2026-04-03

**Navigation**: [README](../README.md) | [GCP Setup](01-SETUP-GCP.md) | [Entra ID](02-SETUP-ENTRA.md) | [WIF](03-SETUP-WIF.md) | [Discovery](04-SETUP-DISCOVERY.md) | **Local Dev** | [Agent Engine](06-AGENT-ENGINE.md)

---

## Overview

Local development setup for testing the full StreamAssist + WIF + Discovery Engine flow.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOCAL ARCHITECTURE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Frontend (:5173)          Backend (:8000)           External Services     │
│   ┌─────────────┐           ┌─────────────┐          ┌─────────────────┐   │
│   │  React App  │◄─────────►│  FastAPI    │◄────────►│ Discovery Engine│   │
│   │  - Chat UI  │  /api/*   │  - WIF      │   API    │ - streamAssist  │   │
│   │  - Sources  │           │  - Search   │          │ - SharePoint    │   │
│   └─────────────┘           └──────┬──────┘          └─────────────────┘   │
│                                    │                                        │
│                                    │ STS Token Exchange                     │
│                                    ▼                                        │
│                             ┌─────────────────┐                             │
│                             │ Google STS      │                             │
│                             │ - WIF Pool      │                             │
│                             │ - Token Exchange│                             │
│                             └─────────────────┘                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Flow: Direct StreamAssist (No Agent Engine)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STREAMASSIST DIRECT FLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. User Query                                                             │
│      Browser → POST /api/search { query: "..." }                            │
│                                                                             │
│   2. Backend Processing                                                     │
│      ├── Get access token (service account or WIF exchange)                 │
│      ├── Fetch datastores dynamically from widget config                    │
│      └── Build streamAssist payload with dataStoreSpecs                     │
│                                                                             │
│   3. StreamAssist API Call                                                  │
│      POST discoveryengine.googleapis.com/.../streamAssist                   │
│      {                                                                      │
│        "query": {"text": "user query"},                                     │
│        "toolsSpec": {                                                       │
│          "vertexAiSearchSpec": {                                            │
│            "dataStoreSpecs": [...]  ← REQUIRED for SharePoint grounding     │
│          }                                                                  │
│        }                                                                    │
│      }                                                                      │
│                                                                             │
│   4. Response Processing                                                    │
│      ├── Extract answer text (skip thought/thinking parts)                  │
│      ├── Extract grounding sources (textGroundingMetadata.references)       │
│      └── Return formatted response with citations                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.12+ (for backend)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- GCP project with Discovery Engine configured
- All previous setup steps completed (Entra ID, WIF, Discovery)

---

## Step 1: Configure Environment

```bash
cd semiautonomous-agents/sharepoint_wif_portal
cp .env.example .env
```

Edit `.env` with your values:

```env
# GCP
PROJECT_NUMBER=545964020693
LOCATION=global

# Discovery Engine
ENGINE_ID=gemini-enterprise

# WIF (optional - for user-level ACLs)
WIF_POOL_ID=sp-wif-pool-v2
WIF_PROVIDER_ID=entra-provider

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

---

## Step 2: Start Backend

```bash
cd backend

# Install dependencies with uv
uv sync

# Start FastAPI server
uv run python main.py

# Or with hot reload for development
uv run uvicorn main:app --reload --port 8000
```

**Verify:**

```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"sharepoint-wif-portal"}

curl http://localhost:8000/api/config
# {"project_number":"545964020693","engine_id":"gemini-enterprise",...}
```

---

## Step 3: Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

**Verify:** Open http://localhost:5173 - you should see the Enterprise Search Portal UI.

---

## Step 4: Test Search

1. Open http://localhost:5173
2. Enter a query: "What documents do I have access to?"
3. Check the response includes SharePoint sources

**Expected backend logs:**

```
INFO - [Search] Using 5 datastore(s)
INFO - [Search] Calling StreamAssist API: https://discoveryengine.googleapis.com/v1alpha/...
INFO - [Search] Found 3 source(s)
```

---

## Project Structure

```
sharepoint_wif_portal/
├── frontend/
│   ├── package.json          # Dependencies
│   ├── vite.config.ts        # Vite config with /api proxy
│   ├── tsconfig.json         # TypeScript config
│   ├── index.html            # Entry HTML
│   ├── public/
│   │   └── favicon.svg       # App icon
│   └── src/
│       ├── main.tsx          # React entry
│       ├── App.tsx           # Main component with chat UI
│       └── index.css         # Styling (dark theme)
│
├── backend/
│   ├── pyproject.toml        # Python dependencies
│   ├── main.py               # FastAPI server
│   └── tools/
│       ├── __init__.py
│       └── stream_assist.py  # StreamAssist client with WIF
│
├── docs/                     # Setup documentation
├── assets/                   # Screenshots for docs
├── .env.example              # Environment template
└── .secrets.md               # Credentials (git-ignored)
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/config` | GET | Current configuration (non-sensitive) |
| `/api/search` | POST | Search via StreamAssist |

### Search Request

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "financial reports"}'
```

### Search Response

```json
{
  "answer": "Based on SharePoint documents...\n\n---\n**Sources:**\n1. **[Financial Report Q4](https://sharepoint.com/...)**\n",
  "sources": [
    {
      "title": "Financial Report Q4",
      "url": "https://sharepoint.com/...",
      "snippet": "Quarterly financial summary..."
    }
  ]
}
```

---

## Development Commands

```bash
# Backend
cd backend
uv sync                           # Install dependencies
uv run python main.py             # Start server
uv run pytest                     # Run tests

# Frontend
cd frontend
npm install                       # Install dependencies
npm run dev                       # Start dev server
npm run build                     # Production build
npm run preview                   # Preview production build
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| CORS error | Backend not running | Start backend on :8000 |
| "No dataStoreSpecs" warning | Engine not configured | Check ENGINE_ID in .env |
| Empty response | SharePoint not indexed | Wait for sync or check connector |
| 403 Forbidden | Missing IAM roles | Add discoveryengine roles to service account |
| WIF exchange fails | Wrong provider | Use agent provider with api:// prefix |

### Debug Mode

```bash
# Backend verbose logging
LOG_LEVEL=DEBUG uv run python main.py

# Check Discovery Engine response
# Look for "[Search] Response (first 500 chars):" in logs
```

---

## Architecture Notes

### Why Direct StreamAssist?

This implementation calls StreamAssist directly without Agent Engine:

| Aspect | Direct StreamAssist | Via Agent Engine |
|--------|---------------------|------------------|
| Latency | Lower (1 hop) | Higher (2 hops) |
| Complexity | Simpler | More features |
| Cost | Base API cost | + Agent Engine cost |
| Best for | Simple search | Complex workflows |

### dataStoreSpecs is REQUIRED

The most critical part of the StreamAssist integration:

```python
# WITHOUT dataStoreSpecs - Generic LLM response (no SharePoint)
payload = {"query": {"text": query}}

# WITH dataStoreSpecs - Grounded response from SharePoint
payload = {
    "query": {"text": query},
    "toolsSpec": {
        "vertexAiSearchSpec": {
            "dataStoreSpecs": [
                {"dataStore": "projects/.../dataStores/sharepoint-..."}
            ]
        }
    }
}
```

---

## Next Step

→ [06-AGENT-ENGINE.md](06-AGENT-ENGINE.md) - Optional: Deploy to Vertex AI Agent Engine for advanced orchestration

---

## Related Documentation

- [README.md](../README.md) - Project overview and quick start
- [02-SETUP-ENTRA.md](02-SETUP-ENTRA.md) - Entra ID configuration for OAuth
- [03-SETUP-WIF.md](03-SETUP-WIF.md) - WIF pool setup
- [04-SETUP-DISCOVERY.md](04-SETUP-DISCOVERY.md) - SharePoint connector and federated search
- [backend/main.py](../backend/main.py) - FastAPI server implementation
- [backend/tools/stream_assist.py](../backend/tools/stream_assist.py) - StreamAssist client with WIF
- [frontend/src/App.tsx](../frontend/src/App.tsx) - React UI component
