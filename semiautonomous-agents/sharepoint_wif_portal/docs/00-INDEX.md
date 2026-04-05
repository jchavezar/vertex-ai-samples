# Documentation Index

**Version:** 2.1.0  
**Last Updated:** 2026-04-04

---

## Reading Order

```
+===========================================================================+
|                         DOCUMENTATION FLOW                                 |
|                                                                            |
|   PHASE 1: INFRASTRUCTURE                                                  |
|   +-----------+     +-----------+     +-----------+     +-----------+     |
|   |  01-GCP   | --> |  02-ENTRA | --> |  03-WIF   | --> |  04-DISCO |     |
|   +-----------+     +-----------+     +-----------+     +-----------+     |
|                                                                            |
|   PHASE 2: CUSTOM UI (Direct API - No Agent Required)                     |
|   +-----------+     +-----------+     +-----------+                       |
|   |  05-DEV   | --> |  06-ENGINE| --> |  07-FRONT |                       |
|   +-----------+     +-----------+     +-----------+                       |
|                                                                            |
|   PHASE 3: AGENT INTEGRATION                                              |
|   +-----------+     +-----------+                                          |
|   | 08-AGENT  | --> | 09-PANEL  |                                          |
|   +-----------+     +-----------+                                          |
|                                                                            |
|   PHASE 4: PRODUCTION DEPLOYMENT                                          |
|   +-----------+     +-----------+                                          |
|   | 10-DEPLOY | --> |  TESTING  |                                          |
|   +-----------+     +-----------+                                          |
|                                                                            |
+===========================================================================+
```

---

## Core Documents

| # | Document | Depends On | Description |
|---|----------|------------|-------------|
| 01 | [01-SETUP-GCP.md](01-SETUP-GCP.md) | - | GCP project, APIs, IAM |
| 02 | [02-SETUP-ENTRA.md](02-SETUP-ENTRA.md) | 01 | Microsoft Entra ID app |
| 03 | [03-SETUP-WIF.md](03-SETUP-WIF.md) | 01, 02 | Workforce Identity Federation |
| 04 | [04-SETUP-DISCOVERY.md](04-SETUP-DISCOVERY.md) | 01-03 | Discovery Engine + SharePoint |
| 05 | [05-LOCAL-DEV.md](05-LOCAL-DEV.md) | 01-04 | Backend + Frontend (direct API) |
| 06 | [06-AGENT-ENGINE.md](06-AGENT-ENGINE.md) | 05 | Agent Engine basics |
| 07 | [07-FRONTEND-FEATURES.md](07-FRONTEND-FEATURES.md) | 05-06 | Chat, /btw, sessions |
| 08 | [08-ADK-AGENT.md](08-ADK-AGENT.md) | 01-04 | Deploy InsightComparator agent |
| 09 | [09-AGENT-PANEL.md](09-AGENT-PANEL.md) | 05, 08 | Add Agent Panel to custom UI |
| 10 | [10-CLOUD-DEPLOYMENT.md](10-CLOUD-DEPLOYMENT.md) | 01-09 | Cloud Run + GLB + IAP |
| - | [TESTING.md](TESTING.md) | 10 | Full testing workflow |

---

## Project Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Frontend** | `frontend/` | React UI (port 5173) - DO NOT MODIFY |
| **Backend** | `backend/` | FastAPI (port 8000) - streamAssist + Agent |
| **Agent** | `agent/` | ADK Agent for Agent Engine |
| **Scripts** | `scripts/` | Registration & testing scripts |
| **Test UI** | `test_ui/` | Token capture for testing |

---

## Backend Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | streamAssist + WIF (main chat) |
| `/api/quick` | POST | Gemini + Google Search |
| `/api/sessions` | GET/POST | Conversation management |
| `/api/agent` | POST | Agent Engine SDK query |
| `/api/agent/info` | GET | Agent information |

---

## Values Flow

```
01-SETUP-GCP.md
├── PROJECT_ID        → All docs
├── PROJECT_NUMBER    → 03, 04, 08
└── STAGING_BUCKET    → 08

02-SETUP-ENTRA.md
├── TENANT_ID         → 03, 08
├── OAUTH_CLIENT_ID   → 03, 04, 08
└── OAUTH_CLIENT_SECRET → 08

03-SETUP-WIF.md
├── WIF_POOL_ID       → 04, 08
├── ge-login-provider → GE login
└── entra-provider    → Agent WIF

04-SETUP-DISCOVERY.md
├── ENGINE_ID         → 08
└── DATA_STORE_ID     → 08

08-ADK-AGENT.md
├── REASONING_ENGINE_RES → backend, testing
└── AUTH_ID              → testing
```

---

## Quick Reference

| Task | Document |
|------|----------|
| Create GCP project | [01-SETUP-GCP.md](01-SETUP-GCP.md) |
| Register Entra app | [02-SETUP-ENTRA.md](02-SETUP-ENTRA.md) |
| Configure WIF | [03-SETUP-WIF.md](03-SETUP-WIF.md) |
| Connect SharePoint | [04-SETUP-DISCOVERY.md](04-SETUP-DISCOVERY.md) |
| Deploy agent | [08-ADK-AGENT.md](08-ADK-AGENT.md) |
| Test agent | [TESTING.md](TESTING.md) |
