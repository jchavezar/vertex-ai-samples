# Phase 1: Local Testing

[<- Back to Main README](../README.md) | [Phase 2: Cloud Deployment](PHASE2_CLOUD_DEPLOYMENT.md)

**Goal:** Verify the JWT token flows correctly through all components before deploying to cloud.

---

## Testing Strategy

We test in **isolation** first, then **integration**:

```
Step 1: MCP Server alone (can it authenticate to ServiceNow?)
Step 2: Agent + MCP Server (can the agent call MCP tools with JWT?)
Step 3: Full stack (Backend → Agent → MCP → ServiceNow)
```

---

## Prerequisites

1. **JWT Token** from Entra ID
2. **ServiceNow instance** with OIDC configured
3. **Local environment** with uv and Node.js

---

## Step 1: Get a JWT Token

```bash
cd /path/to/light_ge_mcp_cloud_portal

# Start the token helper (opens browser)
uv run scripts/serve-token-page.py
```

1. Click **"Save Configuration"** (Client ID and Tenant ID are pre-filled)
2. Click **"Login with Microsoft"**
3. Click **"Get ID Token"**
4. Copy the token

**Set it as an environment variable:**
```bash
export TEST_JWT_TOKEN="eyJ0eXAiOiJKV1Qi..."
```

> **Note:** Token expires in ~1 hour. Re-run the helper to get a fresh one.

---

## Step 2: Test MCP Server Locally

### 2.1 Start the MCP Server

```bash
cd mcp-server
uv run python mcp_server.py
```

Expected output:
```
[MCP] Starting ServiceNow MCP Server
[MCP] Instance URL: https://dev289493.service-now.com
[MCP] Transport: streamable-http
[MCP] Port: 8081
Starting MCP server 'ServiceNow-MCP' on http://0.0.0.0:8081/mcp
```

### 2.2 Test with the Local Test Script

In a **new terminal**:
```bash
cd /path/to/light_ge_mcp_cloud_portal
export TEST_JWT_TOKEN="eyJ..."

uv run scripts/test-local.py --test mcp
```

**Expected result:**
- MCP server receives the JWT
- Calls ServiceNow API with Bearer token
- Returns incident list (or falls back to Basic Auth)

---

## Step 3: Test Agent Locally (Simulated)

Since Agent Engine runs in the cloud, we **simulate** the agent behavior locally:

```bash
uv run scripts/test-local.py --test agent-sim
```

This script:
1. Creates an ADK agent locally (same code as `agent/agent.py`)
2. Injects JWT into session state
3. Calls the local MCP server
4. Verifies the token reaches the MCP server

---

## Step 4: Test Full Integration

Run the complete test suite:

```bash
uv run scripts/test-local.py --test all
```

### Success Criteria

| Test | Pass Condition |
|------|----------------|
| MCP Server | Returns ServiceNow data with JWT auth |
| Agent Simulation | Tool calls include Authorization header |
| Token Flow | JWT appears in MCP server logs |

---

## Troubleshooting

### MCP Server won't start (port in use)
```bash
# Find and kill existing process
lsof -i :8081
kill -9 <PID>
```

### JWT Token Expired
```
Error: 401 Unauthorized from ServiceNow
```
→ Get a new token from the helper page

### ServiceNow OIDC Error
```
Error: Invalid audience claim
```
→ Verify ServiceNow OIDC Provider has correct Client ID

### MCP Server Missing Headers
```
Error: 'RequestContext' object has no attribute 'headers'
```
→ Ensure using `streamable-http` transport, not `sse`

---

## Next Steps

Once all tests pass:

📁 **Proceed to:** [`PHASE2_CLOUD_DEPLOYMENT.md`](PHASE2_CLOUD_DEPLOYMENT.md)
