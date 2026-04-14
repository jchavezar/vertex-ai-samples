# ServiceNow Agent Portal

Production-ready architecture connecting a React frontend to Google Agent Engine with ServiceNow via MCP.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React)                                │
│                          localhost:3000 / Cloud Run                          │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────────────────────────┐ │
│  │   MSAL      │───▶│  Entra ID   │───▶│  Workforce Identity Federation   │ │
│  │   Login     │    │   JWT       │    │  (STS Token Exchange)            │ │
│  └─────────────┘    └─────────────┘    └──────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ GCP Token + User JWT in session state
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENT ENGINE (Vertex AI)                             │
│                    Managed Google Cloud Infrastructure                       │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────────────────────────┐ │
│  │   ADK       │───▶│   Gemini    │───▶│   MCP Toolset                    │ │
│  │   Agent     │    │   2.5 Flash │    │   (SSE + header_provider)        │ │
│  └─────────────┘    └─────────────┘    └──────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ Cloud Run ID Token + X-User-Token header
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MCP SERVER (Cloud Run)                              │
│                    https://servicenow-mcp-xxx.run.app                        │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────────────────────────┐ │
│  │   FastMCP   │───▶│   Header    │───▶│   ServiceNow API Client          │ │
│  │   SSE       │    │   Extract   │    │   (JWT Bearer Auth)              │ │
│  └─────────────┘    └─────────────┘    └──────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ Bearer {User JWT}
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SERVICENOW (ITSM)                                 │
│                      https://instance.service-now.com                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │   OIDC Provider validates JWT → Maps to ServiceNow user → Returns data  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

## Documentation Index

### Setup Guides

| Guide | Description |
|-------|-------------|
| [Architecture Deep Dive](docs/architecture.md) | Detailed system design and component interactions |
| [Security & Auth Flow](docs/security-flow.md) | End-to-end token flow, WIF, OIDC details |
| [GCP Infrastructure](docs/gcp-setup.md) | Workforce Identity Federation, IAM, Cloud Run, Agent Engine |
| [Entra ID Configuration](docs/entra-id-setup.md) | Microsoft app registration and OIDC setup |
| [ServiceNow Configuration](docs/servicenow-setup.md) | OIDC provider and user mapping |
| [Deployment Guide](docs/deployment.md) | Step-by-step deployment instructions |

### Component Documentation

| Component | Path | Documentation |
|-----------|------|---------------|
| Frontend | [`frontend/`](frontend/) | [Frontend README](frontend/README.md) |
| Agent Engine | [`agent/`](agent/) | [Agent README](agent/README.md) |
| MCP Server | [`mcp-server/`](mcp-server/) | [MCP Server README](mcp-server/README.md) |

## Quick Start

```bash
# 1. Clone and setup
cd light_mcp_cloud_portal

# 2. Deploy MCP Server to Cloud Run
cd mcp-server
gcloud run deploy servicenow-mcp --source . --region us-central1 --no-allow-unauthenticated
# Grant invoker access to Agent Engine SA
gcloud run services add-iam-policy-binding servicenow-mcp \
  --member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/run.invoker" --region=us-central1

# 3. Deploy Agent Engine
cd ../agent
uv run python deploy.py

# 4. Run Frontend locally
cd ../frontend
npm install --registry=https://registry.npmjs.org
npm run dev
```

## Key Configuration Files

| File | Purpose | Key Settings |
|------|---------|--------------|
| [`frontend/src/authConfig.ts`](frontend/src/authConfig.ts) | MSAL + WIF config | `clientId`, `tenantId`, `workforcePoolId` |
| [`agent/agent.py`](agent/agent.py) | Agent definition | `MCP_URL`, `header_provider` |
| [`mcp-server/mcp_server.py`](mcp-server/mcp_server.py) | MCP tools | `SERVICENOW_INSTANCE_URL` |

## Environment Variables

### MCP Server (`mcp-server/.env`)
```bash
SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com
SERVICENOW_BASIC_AUTH_USER=admin          # Fallback only
SERVICENOW_BASIC_AUTH_PASS=password       # Fallback only
```

### Agent (`agent/.env`)
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
SERVICENOW_MCP_URL=https://servicenow-mcp-xxx.us-central1.run.app/sse
```

### Frontend (`frontend/src/authConfig.ts`)
```typescript
clientId: "your-entra-app-client-id"
authority: "https://login.microsoftonline.com/your-tenant-id"
workforcePoolId: "your-workforce-pool"
providerId: "your-provider-id"
```

## Token Flow Summary

```
1. User clicks "Sign in with Microsoft"
2. MSAL popup → Entra ID login → Returns ID Token (JWT)
3. Frontend exchanges Entra JWT for GCP token via STS (Workforce Identity Federation)
4. Frontend creates Agent Engine session with USER_TOKEN in state
5. User sends message → Agent Engine processes with Gemini
6. Agent calls MCP tool → header_provider adds:
   - Authorization: Bearer {Cloud Run ID token}
   - X-User-Token: {User's Entra JWT}
7. MCP Server extracts X-User-Token, calls ServiceNow API
8. ServiceNow validates JWT via OIDC, returns user's data
```

## Project Structure

```
light_mcp_cloud_portal/
├── README.md                      # This file
├── docs/
│   ├── architecture.md            # System architecture
│   ├── security-flow.md           # Authentication details
│   ├── gcp-setup.md               # GCP infrastructure
│   ├── entra-id-setup.md          # Microsoft Entra ID
│   ├── servicenow-setup.md        # ServiceNow OIDC
│   └── deployment.md              # Deployment guide
├── frontend/
│   ├── README.md
│   ├── src/
│   │   ├── authConfig.ts          # MSAL + WIF configuration
│   │   ├── agentService.ts        # Agent Engine API client
│   │   ├── App.tsx                # Main UI component
│   │   └── App.css                # Styling
│   └── package.json
├── agent/
│   ├── README.md
│   ├── agent.py                   # ADK agent with MCP toolset
│   ├── deploy.py                  # Deployment script
│   └── requirements.txt
└── mcp-server/
    ├── README.md
    ├── mcp_server.py              # FastMCP ServiceNow server
    ├── Dockerfile
    └── requirements.txt
```
