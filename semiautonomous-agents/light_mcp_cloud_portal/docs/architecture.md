# Architecture Deep Dive

[← Back to Main README](../README.md)

## System Overview

This architecture enables secure, identity-aware access to ServiceNow through an AI agent, with end-to-end JWT token propagation.

## Component Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                 USER BROWSER                                │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         REACT FRONTEND                                │  │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────────────────────────┐ │  │
│  │  │   MSAL     │  │  STS       │  │     Agent Engine Client         │ │  │
│  │  │   Auth     │  │  Exchange  │  │     (REST API calls)            │ │  │
│  │  └─────┬──────┘  └─────┬──────┘  └──────────────┬──────────────────┘ │  │
│  └────────┼───────────────┼────────────────────────┼────────────────────┘  │
└───────────┼───────────────┼────────────────────────┼────────────────────────┘
            │               │                        │
            ▼               ▼                        ▼
┌───────────────────┐ ┌───────────────────┐ ┌────────────────────────────────┐
│    ENTRA ID       │ │   GCP STS         │ │      VERTEX AI                 │
│    (Microsoft)    │ │   (Token Exchange)│ │      AGENT ENGINE              │
│                   │ │                   │ │  ┌─────────────────────────┐   │
│  - User Auth      │ │  - WIF Pool       │ │  │    ADK LlmAgent         │   │
│  - JWT Issuer     │ │  - ID Mapping     │ │  │  ┌─────────────────┐    │   │
│                   │ │  - GCP Token      │ │  │  │   McpToolset    │    │   │
└───────────────────┘ └───────────────────┘ │  │  │  (SSE transport)│    │   │
                                            │  │  └────────┬────────┘    │   │
                                            │  └───────────┼─────────────┘   │
                                            └──────────────┼─────────────────┘
                                                           │
                                                           ▼
                                            ┌─────────────────────────────────┐
                                            │        CLOUD RUN                │
                                            │        MCP SERVER               │
                                            │  ┌─────────────────────────┐    │
                                            │  │   FastMCP (SSE)         │    │
                                            │  │   - Header extraction   │    │
                                            │  │   - ServiceNow client   │    │
                                            │  └───────────┬─────────────┘    │
                                            └──────────────┼──────────────────┘
                                                           │
                                                           ▼
                                            ┌─────────────────────────────────┐
                                            │        SERVICENOW               │
                                            │        (ITSM Platform)          │
                                            │  - OIDC JWT validation          │
                                            │  - User identity mapping        │
                                            │  - Table API access             │
                                            └─────────────────────────────────┘
```

## Data Flow

### 1. Authentication Flow

```
User → MSAL Login → Entra ID → JWT Token
                                   │
                                   ▼
                    STS Token Exchange (WIF)
                                   │
                                   ▼
                           GCP Access Token
```

### 2. Query Flow

```
User Message → Agent Engine API
                     │
                     ├─ Creates/uses session (USER_TOKEN in state)
                     ├─ Processes with Gemini 2.5 Flash
                     └─ Calls MCP tools via header_provider
                                   │
                                   ▼
                    MCP Server (Cloud Run)
                     │
                     ├─ Validates Cloud Run ID token
                     ├─ Extracts X-User-Token header
                     └─ Calls ServiceNow with user JWT
                                   │
                                   ▼
                         ServiceNow API Response
```

## Component Details

### Frontend ([`frontend/`](../frontend/))

| File | Purpose |
|------|---------|
| [`src/authConfig.ts`](../frontend/src/authConfig.ts) | MSAL and WIF configuration |
| [`src/agentService.ts`](../frontend/src/agentService.ts) | STS exchange + Agent Engine API |
| [`src/App.tsx`](../frontend/src/App.tsx) | React UI with streaming |

**Key Functions:**
- `exchangeTokenForGcp()` - STS token exchange
- `createSession()` - Agent Engine session with USER_TOKEN
- `queryStream()` - Streaming query with chunk updates

### Agent Engine ([`agent/`](../agent/))

| File | Purpose |
|------|---------|
| [`agent.py`](../agent/agent.py) | ADK agent definition with MCP toolset |
| [`deploy.py`](../agent/deploy.py) | Deployment to Vertex AI |

**Key Components:**
- `LlmAgent` with Gemini 2.5 Flash
- `McpToolset` with SSE transport
- `header_provider` callback for dynamic headers

### MCP Server ([`mcp-server/`](../mcp-server/))

| File | Purpose |
|------|---------|
| [`mcp_server.py`](../mcp-server/mcp_server.py) | FastMCP server with ServiceNow tools |

**Key Functions:**
- `_extract_token_from_context()` - Header extraction for SSE
- `query_table()` - Generic ServiceNow table query
- `FallbackSession` - Basic auth fallback for testing

## Security Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                    PUBLIC INTERNET                               │
│  ┌─────────────┐                                                │
│  │  Frontend   │  (No secrets - all in browser)                 │
│  └─────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS + OAuth
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE CLOUD (IAM Protected)                  │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │   STS       │  │   Agent     │  (WIF + Service Account)      │
│  │   Endpoint  │  │   Engine    │                               │
│  └─────────────┘  └─────────────┘                               │
│                         │                                        │
│                         │ Cloud Run IAM                          │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    MCP SERVER                            │    │
│  │  (IAM authenticated - requires Cloud Run ID token)       │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS + JWT
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICENOW (OIDC Protected)                   │
│  (Validates JWT signature, checks user identity)                 │
└─────────────────────────────────────────────────────────────────┘
```

## Related Documentation

- [Security Flow Details](security-flow.md)
- [GCP Infrastructure Setup](gcp-setup.md)
- [Entra ID Configuration](entra-id-setup.md)
- [ServiceNow Configuration](servicenow-setup.md)
