# agent-gateway-demo

End-to-end interactive demo of Google's **Agent Gateway + Agent Identity +
Agent Runtime** with **3LO Microsoft Entra OAuth**. A chatbot UI, a deployed
ADK agent, an MCP "tool" server on Cloud Run, and the full governance stack —
both Door 1 (`iap.egressor` on the Registry resource) and Door 2 (per-user
3LO token decrypted by Auth Manager and injected at the gateway).

```
Browser (Next.js + MSAL.js) ── Entra sign-in ──▶ Microsoft
       │
       │ POST /chat { message, entra_access_token }
       ▼
Backend (FastAPI / Cloud Run)
       │ create AE session: state["temp:sharepoint_3lo"] = entra_access_token
       │ async_stream_query → SSE → browser
       ▼
Agent Engine (identity_type=AGENT_IDENTITY,
              agent_gateway_config bound to my-agent-gateway)
       │ McpToolset.search_documents → SPIFFE x509 + DPoP egress
       ▼
Agent Gateway (Google-managed, AGENT_TO_ANYWHERE)
       │ IAP: roles/iap.egressor on agentregistry service?  (Door 1)
       │ Auth Manager: decrypt → Authorization: Bearer <user_token>
       ▼
MCP Server (FastAPI / Cloud Run)
       │ STUB (default): echo {agent_spiffe, user_token_claims, query}
       │ REAL (DEMO_REAL_MCP=1): call Microsoft Graph /me/drive/root/search
       ▼
Microsoft Graph              (Door 2: SharePoint ACLs filter the result)
```

## Verified vs original spec

The original build spec (LLM-generated) had several wrong call shapes. This
implementation uses **only verified** shapes, sourced from:

- `vertexai/_genai/agent_engines.py` (1.151.0) — real `client.agent_engines.create(config={...})` with `identity_type` + `agent_gateway_config`
- `google.adk.integrations.agent_identity` package — real `GcpAuthProvider`, `GcpAuthProviderScheme`
- `agentregistry.googleapis.com/v1alpha/.../services` — real MCP-server registration API (NOT `aiplatform.googleapis.com/.../agentRegistries/default/mcpServers`)
- Token-pre-injection pattern (`state["temp:<KEY>"]`) — matches `adk-drive-ae/backend/main.py`. There is no `submit_auth_response` method.
- IAP CEL attribute is `mcp.resourceName` (not `resource.name`).
- `service_account` and `identity_type=AGENT_IDENTITY` are **mutually exclusive**.

Full table in `~/.claude/plans/foamy-drifting-honey.md`.

## Layout

```
agent-gateway-demo/
├── infra/         shell + Python: APIs, Gateway, connector, registry, IAM
├── mcp_server/    FastAPI tool (stub | real Microsoft Graph)
├── agent/         ADK LlmAgent + McpToolset + GcpAuthProviderScheme
├── backend/       FastAPI chat backend (token-pre-injection + SSE)
├── frontend/      Next.js chat UI with MSAL.js Entra sign-in
└── scripts/       local + remote test runners, log tailing
```

## Manual prerequisite — Microsoft Entra app registration

(Skip this section if you already have an Entra app with Graph delegated
permissions and a redirect URI you can update.)

1. Go to <https://entra.microsoft.com> → **App registrations** → **New registration**.
2. Name: `agent-gateway-demo`. Account types: single-tenant.
3. **Redirect URI** (Web): leave empty for now — we add the real URLs after
   the frontend is deployed. For local dev: `http://localhost:3000/auth/callback`.
4. After creation note `Application (client) ID` and `Directory (tenant) ID`.
5. **Certificates & secrets → New client secret** — copy the *Value*. This is
   `ENTRA_CLIENT_SECRET`.
6. **API permissions → Add a permission → Microsoft Graph → Delegated**:
   `Files.Read`, `openid`, `profile`, `offline_access`. Click **Grant admin
   consent** if you have the rights.
7. Drop `ENTRA_TENANT_ID`, `ENTRA_CLIENT_ID`, `ENTRA_CLIENT_SECRET` into `.env`.
8. After the frontend Cloud Run URL exists, come back and add it as a redirect URI.

## Build order

See `~/.claude/plans/foamy-drifting-honey.md` for the full plan. Short version:

1. APIs → 2. MCP server → 3. Agent (no gateway, local) → 4. Backend +
frontend (local) → 5. Cloud Run deploys for MCP + backend + frontend → 6.
Re-deploy agent without gateway → 7. **Provision gateway (PERMANENT)** → 8.
Connector → 9. Registry → 10. Re-deploy agent with gateway + grant egressor
→ 11. Validate audit logs → 12. Flip enforce mode.

The gateway-bind step (#7+) is **irreversible in vtxdemos us-central1**. Do
NOT run `infra/10_create_gateway.sh` until everything else works without it.

## Reuses from sibling projects (cribbed, not copied wholesale)

| Pattern | Source |
|---|---|
| `vertexai.Client + agent_engines.create(config={...})` deploy | `observability-orchestra/agent/deploy.py:49-107` |
| Backend pre-injects token + streams events as SSE | `adk-drive-ae/backend/main.py:86-179` |
| Microsoft Entra 3LO + WIF | `streamassist-oauth-flow-sharepoint/backend/{main,auth_sharepoint}.py` |
| FastAPI MCP server template | `gworkspace-mcp-server/server.py` |
| SSE consumer in browser | `adk-drive-ae/frontend/lib/api.ts:42-73` |

## Testing every part

| Layer | How to test |
|---|---|
| MCP server (stub) | `curl https://MCP/mcp/tools/search_documents -H 'Authorization: Bearer fake' -d '{"query":"x"}'` |
| Agent locally (no gateway) | `python scripts/test_agent_local.py "find docs about X"` (uses InMemoryRunner + a stub MCP) |
| Agent remotely (no gateway) | `python scripts/test_agent_remote.py "..."` (calls deployed AE) |
| Backend SSE | `curl -N https://BACKEND/chat -H 'Content-Type: application/json' -d '{...}'` |
| Frontend chat UI | open `https://FRONTEND/`, sign in with Microsoft, ask a question |
| Door 1 (Gateway/IAP) | `bash scripts/tail_iap_logs.sh` while sending a request — look for ALLOW with `mcp.resourceName=...` |
| Door 1 negative | revoke `roles/iap.egressor` from the agent SA → next request returns 403 |
| Door 2 (per-user data) | Send same query from two different users, observe different results from Graph |
| Door 2 negative | omit token / send empty token → MCP returns 401, agent reports "auth required" |
