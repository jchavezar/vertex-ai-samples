# Architecture Deep Dive

[<- Back to Main README](../README.md)

## System Overview

This architecture enables secure, identity-aware access to **SharePoint documents** (via Discovery Engine) and **ServiceNow ITSM** (via MCP) through an AI agent, with end-to-end JWT token propagation using Workforce Identity Federation.

## Complete Component Diagram

```
+-----------------------------------------------------------------------------------+
|                              USER BROWSER                                          |
|  +-----------------------------------------------------------------------------+  |
|  |                         REACT FRONTEND                                       |  |
|  |  +------------+  +------------+  +---------------------------------------+   |  |
|  |  |   MSAL     |  |  STS       |  |     Agent Engine Client               |   |  |
|  |  |   Auth     |  |  Exchange  |  |     (REST API calls)                  |   |  |
|  |  +-----+------+  +-----+------+  +------------------+--------------------+   |  |
|  +--------+---------------+-----------------------------+------------------------+  |
+-----------+---------------+-----------------------------+----------------------------+
            |               |                             |
            v               v                             v
+-----------------+ +-------------------+ +----------------------------------------+
|    ENTRA ID     | |   GCP STS         | |        VERTEX AI AGENT ENGINE          |
|    (Microsoft)  | |   (Token Exchange)| |                                        |
|                 | |                   | |  +----------------------------------+   |
|  - User Auth    | |  - WIF Pool       | |  |        ADK LlmAgent              |   |
|  - JWT Issuer   | |  - ID Mapping     | |  |                                  |   |
|                 | |  - GCP Token      | |  |  +-------------+  +------------+ |   |
+-----------------+ +-------------------+ |  |  | search_     |  | LazyMcp    | |   |
                                          |  |  | sharepoint  |  | Toolset    | |   |
                                          |  |  | (function)  |  | (SSE)      | |   |
                                          |  |  +------+------+  +-----+------+ |   |
                                          |  +---------|---------------|--------+   |
                                          +------------|---------------|------------+
                                                       |               |
                    +----------------------------------+               |
                    |                                                  |
                    v                                                  v
+-----------------------------------+           +-----------------------------------+
|       DISCOVERY ENGINE            |           |        CLOUD RUN MCP SERVER       |
|       (Gemini Enterprise)         |           |                                   |
|                                   |           |  +-----------------------------+  |
|  +-----------------------------+  |           |  |   FastMCP (SSE)             |  |
|  |  streamAssist API           |  |           |  |   - Header extraction       |  |
|  |  - Grounded responses       |  |           |  |   - ServiceNow client       |  |
|  |  - textGroundingMetadata    |  |           |  +-------------+---------------+  |
|  |  - Source citations         |  |           +---------------|-------------------+
|  +-------------+---------------+  |                           |
+---------------|-------------------+                           v
                |                             +-----------------------------------+
                v                             |        SERVICENOW                 |
+-----------------------------------+         |        (ITSM Platform)            |
|        SHAREPOINT ONLINE          |         |  - OIDC JWT validation            |
|  sockcop.sharepoint.com           |         |  - User identity mapping          |
|  - Financial Reports              |         |  - Table API access               |
|  - HR Documents                   |         +-----------------------------------+
|  - Contracts & Policies           |
+-----------------------------------+
```

## Tool Architecture

The agent has two distinct tool types for different data sources:

```
+------------------------------------------------------------------+
|                    AGENT TOOL ARCHITECTURE                        |
+------------------------------------------------------------------+
|                                                                  |
|  +-----------------------------------------------------------+  |
|  |                     LlmAgent                               |  |
|  |                (Gemini 2.5 Flash)                          |  |
|  +-----------------------------------------------------------+  |
|                               |                                  |
|              +----------------+----------------+                 |
|              |                                 |                 |
|              v                                 v                 |
|  +------------------------+      +---------------------------+  |
|  |   search_sharepoint    |      |     LazyMcpToolset        |  |
|  |   (Function Tool)      |      |     (ServiceNow)          |  |
|  +------------------------+      +---------------------------+  |
|  | - Direct Python call   |      | - SSE transport           |  |
|  | - WIF token exchange   |      | - header_provider         |  |
|  | - Discovery Engine API |      | - Pickle-safe wrapper     |  |
|  | - Returns grounded     |      | - Dynamic tool discovery  |  |
|  |   response + sources   |      |                           |  |
|  +------------------------+      +---------------------------+  |
|              |                                 |                 |
|              v                                 v                 |
|       [SharePoint via DE]            [ServiceNow via MCP]       |
|                                                                  |
+------------------------------------------------------------------+
```

## Data Flow

### 1. Authentication Flow

```
User -> MSAL Login -> Entra ID -> JWT Token
                                      |
                                      v
                       STS Token Exchange (WIF)
                                      |
                                      v
                              GCP Access Token
```

### 2. SharePoint Query Flow (Discovery Engine)

```
+------------------------------------------------------------------+
|  USER: "What is the CFO salary?"                                  |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|  AGENT ENGINE                                                     |
|  - Selects search_sharepoint tool                                 |
|  - Passes query and tool_context                                  |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|  search_sharepoint() FUNCTION                                     |
|  1. Extract USER_TOKEN from tool_context.state                    |
|  2. Exchange JWT via WIF/STS -> GCP token (user identity)         |
|  3. Fetch datastores using service account (admin operation)      |
|  4. Call streamAssist API with user's GCP token                   |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|  DISCOVERY ENGINE (streamAssist)                                  |
|  - Searches SharePoint datastores                                 |
|  - Respects ACLs via user identity                                |
|  - Returns grounded answer + textGroundingMetadata                |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|  RESPONSE                                                         |
|  "According to the Financial Audit Report for FY2024, the CFO     |
|   Jennifer Walsh receives $3,855,000 in total compensation."      |
|                                                                   |
|  Sources: 01_Financial_Audit_Report_FY2024.pdf                    |
+------------------------------------------------------------------+
```

### 3. ServiceNow Query Flow (MCP)

```
+------------------------------------------------------------------+
|  USER: "List my open incidents"                                   |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|  AGENT ENGINE                                                     |
|  - Selects query_table tool (from MCP)                            |
|  - header_provider callback invoked                               |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|  header_provider()                                                |
|  1. Generate Cloud Run ID token (service auth)                    |
|  2. Extract USER_TOKEN from session.state                         |
|  3. Return: {Authorization: CR token, X-User-Token: JWT}          |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|  MCP SERVER (Cloud Run)                                           |
|  - IAM validates Cloud Run token                                  |
|  - Extract X-User-Token header                                    |
|  - Call ServiceNow with user JWT                                  |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|  SERVICENOW                                                       |
|  - OIDC validates JWT signature                                   |
|  - Maps email claim to sys_user                                   |
|  - Returns user-scoped incidents                                  |
+------------------------------------------------------------------+
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
| [`agent.py`](../agent/agent.py) | ADK agent with LazyMcpToolset + search_sharepoint |
| [`tools/discovery_engine.py`](../agent/tools/discovery_engine.py) | Discovery Engine client with WIF |
| [`deploy.py`](../agent/deploy.py) | Deployment to Vertex AI |

**Key Components:**
- `LlmAgent` with Gemini 2.5 Flash
- `LazyMcpToolset` - Pickle-safe MCP wrapper
- `search_sharepoint` - Function tool for Discovery Engine
- `header_provider` callback for dynamic headers

**LazyMcpToolset Pattern:**
```python
class LazyMcpToolset(BaseToolset):
    """Defers McpToolset creation to runtime, avoiding pickle issues."""

    def __getstate__(self):
        return {"_url": self._url, "_header_provider": self._header_provider, "_toolset": None}

    def __setstate__(self, state):
        self.__init__(state["_url"], state["_header_provider"])
```

### Discovery Engine Client ([`agent/tools/`](../agent/tools/))

| File | Purpose |
|------|---------|
| [`discovery_engine.py`](../agent/tools/discovery_engine.py) | SharePoint search via streamAssist |

**Key Functions:**
- `exchange_wif_token()` - JWT to GCP token exchange
- `_get_dynamic_datastores()` - Auto-discover SharePoint datastores
- `search()` - Call streamAssist with grounded responses

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
+------------------------------------------------------------------+
|                    PUBLIC INTERNET                                |
|  +--------------+                                                |
|  |  Frontend    |  (No secrets - all in browser)                 |
|  +--------------+                                                |
+------------------------------------------------------------------+
                              |
                              | HTTPS + OAuth
                              v
+------------------------------------------------------------------+
|                    GOOGLE CLOUD (IAM Protected)                   |
|                                                                  |
|  +-------------+  +-------------+  +--------------------------+  |
|  |   STS       |  |   Agent     |  |   Discovery Engine       |  |
|  |   Endpoint  |  |   Engine    |  |   (streamAssist)         |  |
|  +-------------+  +-------------+  +--------------------------+  |
|                         |                      |                 |
|                         |                      | WIF User Token  |
|                         | Cloud Run IAM        v                 |
|                         v          +--------------------------+  |
|  +--------------------------------+|   SharePoint Connector   |  |
|  |         MCP SERVER             |+--------------------------+  |
|  |  (IAM authenticated)           |            |                 |
|  +--------------------------------+            | Graph API       |
|                   |                            v                 |
+-------------------|-------------------+---------------------------+
                    |                   |
                    | HTTPS + JWT       | User ACLs
                    v                   v
+---------------------------+   +---------------------------+
|        SERVICENOW         |   |    SHAREPOINT ONLINE      |
|    (OIDC Protected)       |   |  (Microsoft 365)          |
|  - Validates JWT          |   |  - Per-document ACLs      |
|  - User identity mapping  |   |  - Federated identity     |
+---------------------------+   +---------------------------+
```

## Identity Flow Summary

| Component | Auth Method | User Identity Source |
|-----------|-------------|---------------------|
| Frontend -> Agent Engine | WIF GCP Token | Entra ID JWT |
| Agent Engine -> MCP Server | Cloud Run IAM | Service Account |
| MCP Server -> ServiceNow | JWT (X-User-Token) | Entra ID JWT |
| Agent Engine -> Discovery Engine | WIF GCP Token | Entra ID JWT |
| Discovery Engine -> SharePoint | Graph API + ACLs | Federated User |

## Related Documentation

- [Security Flow Details](security-flow.md)
- [Discovery Engine Setup](discovery-engine-setup.md)
- [LazyMcpToolset Pattern](lazy-mcp-pattern.md)
- [GCP Infrastructure Setup](gcp-setup.md)
- [Entra ID Configuration](entra-id-setup.md)
- [ServiceNow Configuration](servicenow-setup.md)
- [Troubleshooting](troubleshooting.md)
