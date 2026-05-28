# Briefing for Next Session — GE + A2A + Agent Runtime

This document was written by a separate Claude session after deep research.
Read `RESEARCH_TRANSPORT_AUTH.md` in this same folder for full evidence and
source-code citations. This file is the actionable summary.

---

## Where we left off

The Cloud Run variant (`cloud-run/`) is working end-to-end:

```
GE chat → harpoon (JSONRPC) → Cloud Run FastAPI → ADK agent → Drive (as user)
```

The Agent Runtime variant (`agent-runtime/`) was documented as blocked. The
question was: is it really blocked, and can we fix it?

---

## Research verdict: both blockers are real, but there is a clean path forward

### Blocker 1 — Transport mismatch (confirmed by source code)

**GE side:** harpoon only invokes endpoints whose agent card advertises
`preferredTransport: "JSONRPC"`. If the card says `HTTP+JSON`, harpoon
fabricates a 404 client-side — zero HTTP request ever leaves GE. This was
confirmed empirically during the 3-hour debug session on 2026-05-27.

**AE side:** `vertexai/preview/reasoning_engines/templates/a2a.py` line ~186
raises a hard `ValueError` if `agent_card.preferred_transport != http_json`.
The helper `create_agent_card()` hard-codes `http_json` with a comment "Http
Only." Only a `RESTAdapter` + `RESTHandler` is mounted — no JSON-RPC
dispatcher exists anywhere in the AE container code.

Root cause: the two products are on diverging A2A spec versions. AE moved to
A2A 1.0 (`supported_interfaces`). GE is still on A2A 0.3
(`preferred_transport` / `protocolVersion: "0.3.0"`). No public roadmap
to reconcile them at the platform layer.

**This is not a config knob. You cannot fix it by changing the agent card or
an environment variable.**

### Blocker 2 — User OAuth stripping (confirmed architectural)

AE's managed proxy validates the inbound bearer token (the `ya29.*` GE
forwards), strips it, and re-signs the inner request as the AE service
account. The ADK executor sees an AE SA JWT, not the user token. Per-user
Drive access breaks.

---

## The dual-protocol idea (serve both JSONRPC and http_json)

The open-source `a2a-sdk` ships two separate route factories:
`create_jsonrpc_routes()` and `create_rest_routes()`. They share one
`RequestHandler`. A Cloud Run FastAPI app can mount both on the same server
simultaneously — GE gets JSONRPC, direct callers get http_json.

AE's managed container has no injection point for a `JsonRpcDispatcher`.
You cannot add JSONRPC to an AE-hosted endpoint without putting something
in front of it.

---

## The recommended path: Cloud Run JSONRPC bridge → AE via session-state token injection

This solves both blockers without changing the GE registration and without
needing GWS admin / domain-wide delegation.

### How it works

```
GE chat
  │  JSONRPC (A2A 0.3)
  ▼
Cloud Run bridge  ← already exists as cloud-run/
  │  1. Extract user ya29.* from Authorization header
  │  2. engine.create_session(state={"temp:user_token": "ya29...."})
  │  3. engine.stream_query(session_id, message)
  ▼
Vertex AI Agent Runtime (Agent Engine)
  │  ADK LlmAgent runs here
  │  tool reads tool_context.state["temp:user_token"]
  │  calls Drive API as the user
  ▼
Google Drive (per-user, ACL-enforced)
```

### Why this works

- **Transport:** Cloud Run speaks JSONRPC to GE (already done). Cloud Run
  speaks http_json internally to AE via the Python SDK (`stream_query`).
  No protocol conflict.
- **User token:** GE sends a fresh `ya29.*` on every JSONRPC call. The bridge
  extracts it and stores it in AE session state using the `temp:` prefix. ADK
  tool functions retrieve it via `tool_context.state["temp:user_token"]`.
- **Proven pattern:** `adk-drive-ae` project (AE resource ID
  `5114827487100010496`) already proves `create_session(state={"temp:KEY":
  val})` persists across the `stream_query` call and is readable by tool
  functions. See memory file `agent_engine_gotchas.md`.

### What needs to be built

The delta from the current `cloud-run/` is small:

1. Add `vertexai` SDK dependency to `cloud-run/requirements.txt`
2. In `cloud-run/app/main.py`, after extracting the user token from the
   Authorization header, replace the local ADK runner with:
   ```python
   import vertexai
   from vertexai import agent_engines

   engine = agent_engines.get(REASONING_ENGINE_RESOURCE_NAME)
   session = engine.create_session(state={"temp:user_token": user_token})
   for event in engine.stream_query(
       session_id=session["id"],
       message=user_message,
   ):
       yield event
   ```
3. In the AE-side ADK agent (`agent-runtime/agent/agent.py`), update the
   Drive tool function to read:
   ```python
   def search_drive(query: str, tool_context) -> str:
       token = tool_context.state.get("temp:user_token", "")
       # use token as Bearer for Drive API calls
   ```
4. Redeploy only the Cloud Run service — the AE agent deployment stays the
   same.

### What does NOT need to change

- GE registration (agent card, Authorization resource, agent binding)
- AE deployment (Reasoning Engine resource)
- OAuth client / scopes
- The JSONRPC request/response handling in Cloud Run

---

## Other options considered (and why they rank lower)

| Option | Feasibility | Notes |
|--------|------------|-------|
| Session-state token injection (above) | High | Zero GWS admin, genuine per-user consent, already proven |
| Domain-wide delegation (SA impersonates user) | Medium | Requires GWS admin, high-privilege SA, removes user consent story |
| External UI → AE directly (bypass GE) | High | Works but loses GE chat UX |
| WIF / token exchange | Not applicable | `ya29.*` access tokens are not accepted as WIF OIDC inputs |

---

## Files to read for full context

- `RESEARCH_TRANSPORT_AUTH.md` — source code citations, sdk version checks, full evidence chain
- `agent-runtime/README.md` — current AE variant layout and deploy steps
- `cloud-run/README.md` — working variant (starting point for the bridge extension)
- Memory: `agent_engine_gotchas.md` — AE session state `temp:KEY` confirmed working
- Memory: `adk_drive_ae_project.md` — the existing project that proves the token injection pattern
