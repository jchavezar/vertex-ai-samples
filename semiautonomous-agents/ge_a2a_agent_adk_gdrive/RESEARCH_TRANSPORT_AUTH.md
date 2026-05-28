# Transport + Auth Research: GE → Agent Engine via A2A

**Date:** 2026-05-27  
**Decision gates:** Can Agent Runtime replace Cloud Run for the GE → Custom A2A → Drive demo?

---

## 1. JSONRPC-only claim: Confirmed

### Verdict: CONFIRMED by source code — not a rumour, not a version glitch

Two independent hard restrictions exist today, each in different codebases:

#### Restriction A — Vertex AI Agent Runtime rejects non-`http_json` cards (source code)

File: `vertexai/preview/reasoning_engines/templates/a2a.py`  
(all cached versions on this machine, latest at `.cache/uv/archive-v0/O-mij0KbAS3I8tWBD7iZg/`)

```python
# Line 186–192 of a2a.py in the vertexai SDK
if (
    agent_card.preferred_transport
    and agent_card.preferred_transport != TransportProtocol.http_json
):
    raise ValueError(
        "Only HTTP+JSON is supported for preferred transport on agent card "
    )
```

This is a hard `ValueError` in `A2aAgent.__init__`. There is no flag, no workaround, no environment variable that bypasses it. Any call to `A2aAgent(agent_card=...)` where `agent_card.preferred_transport` is `"JSONRPC"` will crash at local setup time, before the deployment API call is even attempted.

Furthermore, `create_agent_card(...)` hard-codes the transport:

```python
# Line 107 of a2a.py
preferred_transport=TransportProtocol.http_json,  # Http Only.
```

The comment "Http Only." is the SDK authors explicitly documenting the restriction.

The server-side code that AE actually runs (`set_up()`) only registers `RESTAdapter` and `RESTHandler` — there is no `JsonRpcDispatcher` or `JsonRpcRoutes` registered anywhere in the AE container path. AE's `/a2a` endpoint is physically HTTP+JSON only; it is not a configuration issue.

#### Restriction B — GE harpoon proxy only invokes `"JSONRPC"` cards (empirical + memory)

Memory file `ge_custom_a2a_jsonrpc.md` (recorded 2026-05-27 from live debugging session, ~3 hours of burn to confirm):

> Cards with `"HTTP+JSON"` produce an `Agent returned an error (404)` in the chat UI **without ever sending an HTTP request** — the 404 is fabricated client-side by harpoon.  
> Cloud Run logs show zero traffic.

The `cloud-run/register_ge_agent.py` in this repo explicitly hard-codes `"preferredTransport": "JSONRPC"` in the card it builds, with the inline comment:

> GE's harpoon proxy silently rejects any other transport (it returns a synthetic 404 with zero upstream egress).

External confirmation: The alphasec.io deployment guide, the Gemini Enterprise registration docs (docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-a2a-agent), and the A2A spec itself (default: JSONRPC) all confirm JSONRPC as the expected transport for GE Custom A2A.

#### Is this version-specific and fixable by upgrading?

The AE restriction is baked into the current `vertexai` SDK (`vertexai.preview.reasoning_engines.A2aAgent`). It is marked `preview` which means Google can change it without notice. However:

- The restriction is architecturally coherent: AE's managed proxy was designed around REST/HTTP+JSON (the newer A2A 1.0 interface standard). JSONRPC is the older 0.3 wire format.
- GE's harpoon is also locked to JSONRPC and is not user-configurable.
- The two products are on diverging protocol generations. AE moved to A2A 1.0 (`supported_interfaces` proto-based); GE is still on A2A 0.3 (`preferred_transport` pydantic field, `protocolVersion: "0.3.0"`).

There is no public roadmap item for AE adding JSONRPC support. The correct fix, if it comes, would be GE updating harpoon to support HTTP+JSON / A2A 1.0, not AE downgrading to JSONRPC.

**Summary:**  
Both restrictions are confirmed by source code (AE side) and live empirical observation with detailed logging (GE side). They are not a misconfiguration. As of 2026-05-27, GE ↔ AE is architecturally broken at the transport layer for direct A2A registration.

---

## 2. Dual-protocol server: Feasible on Cloud Run, not on Agent Runtime

### Can the a2a-sdk serve both JSONRPC and HTTP+JSON simultaneously?

**Yes — in the open-source a2a-sdk, and therefore on Cloud Run.**

The a2a-sdk (1.x / proto-based, newest cache entry `RnXbiWjVmP-ueBavZ4hTK`) ships separate factory functions:

- `create_jsonrpc_routes(request_handler, rpc_url)` — registers a single Starlette `Route` at `rpc_url` (default `/`) that accepts `{jsonrpc, method, params, id}` POST bodies and dispatches via `JsonRpcDispatcher`
- `create_rest_routes(request_handler)` — registers the HTTP+JSON REST routes (`/message:send`, `/message:stream`, etc.) via `RestDispatcher`

Both use the same `RequestHandler` / `AgentExecutor` underneath. A Starlette/FastAPI app can mount both route sets simultaneously without conflict (different URL paths and/or different content sniffing). The working Cloud Run implementation in `cloud-run/app/main.py` already implements the JSONRPC side manually (raw FastAPI POST `/`). Extending it to also answer REST requests is a 10-line addition.

The older a2a-sdk (0.x / pydantic-based, cache `82RoZfyVOaORrfLhOO3Kn`) also ships `A2AStarletteApplication` (JSONRPC server) and `A2AServer` (REST server) as separate classes. A custom Cloud Run app can instantiate both.

**On Agent Runtime, dual-protocol is not possible.** AE's `set_up()` method hardwires `RESTAdapter` and `RESTHandler`. There is no constructor argument, subclass hook, or environment variable that injects a `JsonRpcDispatcher` alongside the REST handler. The container framework is sealed.

### Can a Cloud Run endpoint advertise both transports in a single agent card?

**In the old a2a-sdk (0.x):** `AgentCard` has `preferred_transport` (a single string) plus `additional_interfaces` (a list of `AgentInterface(transport=..., url=...)`). A card can declare `preferred_transport: "JSONRPC"` at the main URL and list `additional_interfaces: [{transport: "HTTP+JSON", url: "..."}]`. GE reads `preferred_transport` and will route to the JSONRPC endpoint. An AE-side proxy or direct HTTP+JSON client would use the `additional_interfaces` entry.

**In the new a2a-sdk (1.x proto-based):** There is no `preferred_transport` field at all. Cards are entirely `supported_interfaces: [AgentInterface(protocol_binding, url, ...)]`. The client factory picks the best match based on what it supports. GE (which is on the 0.x wire format) will not interpret this correctly.

**Practical conclusion:** For GE compatibility you must stay on the 0.x card format with `preferred_transport: "JSONRPC"`. The JSONRPC endpoint is what GE calls. You can additionally expose HTTP+JSON routes on a different path for other callers (e.g., an AE bridge), but that does not help with getting AE itself to receive calls from GE.

---

## 3. Hybrid bridge architecture: Feasible — this is the recommended path

### Core concept

```
[user] → GE chat
           │  Authorization: Bearer <ya29.user_token>
           │  JSONRPC POST /
           ▼
    Cloud Run bridge (JSONRPC server — already working)
           │  1. Extracts user token from Authorization header
           │  2. Calls AE: create_session(state={"temp:user_token": tok})
           │  3. Calls AE: stream_query(session_id=..., message=text)
           ▼
    Vertex AI Agent Runtime (ADK agent)
           │  tools read tool_context.state["temp:user_token"]
           ▼
    Google Drive API (as the user)
```

### Does `create_session(state={"temp:KEY": tok})` work and survive to tool calls?

**Confirmed YES** — by both the `agent_engine_gotchas.md` memory (recorded 2026-04-28) and the live `adk-drive-ae` project (`vertex-ai-samples/semiautonomous-agents/adk-drive-ae/`):

Memory entry (exact quote):
> `agent.create_session(user_id=..., state={"temp:KEY": tok})` from the Vertex SDK *does* persist into `tool_context.state` on the deployed agent (read via `tool_context.state.get("temp:KEY")`).

The `adk-drive-ae` backend (`backend/main.py`) implements this pattern in production:
```python
state = {"temp:drive_access_token": body.access_token, "drive_access_token": body.access_token}
session = engine.create_session(user_id=body.user_id, state=state)
```

And the agent tool (`agent/agent.py`) reads it:
```python
token = state.get(f"temp:{TOKEN_KEY}") or state.get(TOKEN_KEY)
```

This is the same pattern already used by the `sharepoint_wif_portal` and `gemini-enterprise-sharepoint-agent` projects.

### Does `stream_query` accept user-delegated identity via the AE SDK?

**No direct mechanism.** There is no `stream_query(..., user_token=..., impersonate=...)` parameter. AE always calls the executor as the AE service account. The only supported bridge is session state, which works as documented above.

### Architecture sketch for the hybrid bridge

The Cloud Run bridge becomes slightly more complex than the current working demo:

1. Bridge receives `JSONRPC message/send` from GE with `Authorization: Bearer <ya29.user>`
2. Bridge extracts `user_token` from the `Authorization` header (identical to what the current `cloud-run/app/main.py` does)
3. Bridge calls `engine.create_session(user_id=context_id, state={"temp:user_token": user_token, "user_token": user_token})`
4. Bridge calls `engine.stream_query(user_id=context_id, session_id=sid, message=text)` and streams events back to GE
5. AE executes the ADK agent; tools read `tool_context.state["temp:user_token"]` to call Drive

The bridge holds the AE resource handle (`agent_engines.get(RESOURCE_NAME)`) and calls it with the AE service account's ADC. The user token never goes in the `Authorization` header to AE — it goes in session state.

**Caveats:**
- Token lifetime: `ya29.*` access tokens expire in 1 hour. If a GE session lasts longer, the bridge needs to either refresh the token or propagate a new token on each turn (since GE re-injects the fresh token on every JSONRPC call, the bridge can always call `create_session` or `update_session` at the start of each turn).
- State naming: `temp:` prefix keys are session-scoped ephemerals; use `user_token` (without prefix) as a fallback so the value survives session continuation across turns.
- The bridge adds ~1 network hop + AE session creation latency (~200ms) vs the direct Cloud Run path.

### Could the token go into the A2A message body instead?

GE's JSONRPC `params` contains the A2A `Message` object (parts, contextId, taskId). The bridge controls how it maps the message to AE. It could embed the token in `metadata` or as a special text part, but that is fragile and requires the AE agent to parse it out of the message body. The session state approach is clean and already proven.

---

## 4. Auth fix options ranked

### Option 1 — Session-state token injection (Cloud Run bridge → AE)

**Feasibility: High — confirmed working in adk-drive-ae**

Implementation sketch:

```python
# In the Cloud Run JSONRPC bridge (extends current cloud-run/app/main.py):

async def _handle_message_send(params, user_token):
    message = params.get("message") or {}
    text = _extract_text(message)
    context_id = message.get("contextId") or str(uuid.uuid4())

    # 1. Inject token into AE session state
    engine = _get_ae_engine()
    session = engine.create_session(
        user_id=context_id,
        state={"temp:user_token": user_token, "user_token": user_token}
    )
    sid = session.get("id")

    # 2. Query AE — the ADK agent reads user_token from tool_context.state
    reply_parts = []
    for event in engine.stream_query(
        user_id=context_id, session_id=sid, message=text
    ):
        # collect final response text
        ...

    return build_jsonrpc_result(reply_parts, context_id, ...)
```

The AE-side tool is unchanged from the `adk-drive-ae` pattern:
```python
def drive_search_files(tool_context: ToolContext, query: str) -> dict:
    token = tool_context.state.get("temp:user_token") or tool_context.state.get("user_token")
    ...
```

**Trade-offs:**
- Token is plaintext in AE session state. AE session storage is GCP-managed and isolated per project, so this is acceptable for a demo, though not for a SOC2-audited production system.
- Requires Cloud Run bridge to hold AE SDK credentials (ADC / SA). The AE SA must have `roles/aiplatform.user`.
- Adds ~200–400ms latency per session creation. Can be mitigated by caching `session_id` per GE `contextId` across turns.

### Option 2 — Domain-wide delegation (SA impersonates user for Drive)

**Feasibility: Medium — works for demo, significant GWS admin overhead**

A GWS admin grants the AE service account DWD for the `drive.readonly` scope. The AE agent exchanges the SA token for a user-impersonating token using the GWS Admin SDK / `google.auth.impersonated_credentials.Credentials`:

```python
from google.auth import impersonated_credentials, default

source_creds, _ = default()
target_creds = impersonated_credentials.Credentials(
    source_credentials=source_creds,
    target_principal=user_email,   # obtained from the OAuth token's userinfo
    target_scopes=["https://www.googleapis.com/auth/drive.readonly"],
)
svc = build("drive", "v3", credentials=target_creds, cache_discovery=False)
```

The user email must still reach the AE agent. It can be passed via session state (Option 1 pattern) since it is not a secret: the bridge calls the OAuth2 userinfo endpoint to resolve the email from the `ya29.*` token, then injects `user_email` into session state. No raw token needed in state.

**GWS admin steps required:**
1. Create a dedicated SA for AE (do not use the default AE P4SA — see the April 2026 security advisory about P4SA over-privilege).
2. Go to GWS Admin Console → Security → API Controls → Domain-wide delegation.
3. Add the SA's client ID with scope `https://www.googleapis.com/auth/drive.readonly`.
4. Pass the SA to AE at deployment using BYOSA.

**Trade-offs:**
- GWS admin action required — cannot be done by the GCP project owner alone if they don't have GWS admin rights.
- DWD is a high-privilege grant: the SA can read any user's Drive in the org. Even with `drive.readonly` it's a significant blast radius. Security teams will flag this.
- The user does not go through a consent screen — invisible to the user. This may be acceptable or desired (SSO-style experience) but removes user agency.
- Works for demo without token injection complexity.

### Option 3 — External UI → Cloud Run bridge → AE (no GE)

**Feasibility: High — proven in adk-drive-ae**

For a customer demo that doesn't require GE chat, deploy the `adk-drive-ae` pattern directly: custom Next.js UI handles Google sign-in, passes the token to the FastAPI bridge, bridge injects into AE session. This is the most flexible path and eliminates both blockers entirely.

Not a solution if the GE chat interface is a requirement.

### Option 4 — Token forwarding via WIF / token exchange

**Feasibility: Low for this use case**

Workload Identity Federation can exchange a third-party OIDC token for a GCP access token (SA impersonation), but a `ya29.*` user access token is not an OIDC ID token — it's an opaque OAuth access token. WIF does not accept it as an input credential. You would need to obtain the user's OIDC ID token (`openid` scope) and exchange that, which is a different token than what GE forwards (GE forwards the access token, not the ID token). Even if obtained, WIF token exchange results in SA credentials, not user credentials — so Drive access would still be SA-scoped, not user-scoped. This path collapses into DWD (Option 2).

### Option 5 — Waiting for GE harpoon to support HTTP+JSON

**Feasibility: Unknown / no public roadmap**

GE's transition from A2A 0.3 (JSONRPC) to A2A 1.0 (REST/HTTP+JSON) is a prerequisite for direct AE registration. This would eliminate Blocker 1 without any application code change. Blocker 2 (token stripping) would still require DWD or a bridge pattern. No public ETA available.

---

## 5. Recommended path

### Use the hybrid Cloud Run bridge (Option 1 + existing Cloud Run JSONRPC server)

**Concrete recommendation:** Split the work into two pieces that can be developed and tested independently.

**Piece 1 — Keep the current Cloud Run JSONRPC handler (already working)**

The `cloud-run/` variant already handles the full GE → Cloud Run → Drive flow. For a demo that only needs Cloud Run as the final executor, this is done. No changes needed.

**Piece 2 — If AE execution is required, add a minimal AE bridge layer to the Cloud Run server**

Extend `cloud-run/app/main.py` to optionally forward to AE when `USE_AE=true`:

```
GE → Cloud Run JSONRPC → (if USE_AE) → AE stream_query → Drive tools in AE
                          (if not)    → local ADK runner → Drive API directly
```

The Cloud Run server already extracts the user token and resolves userinfo. To bridge to AE:

1. Add `AGENT_ENGINE_RESOURCE` env var.
2. In `_handle_message_send`, call `engine.create_session(state={"temp:user_token": token, "user_token": token, "user_email": email})` once per `contextId`.
3. Call `engine.stream_query(...)` instead of the local `_runner.run_async(...)`.
4. The AE agent's Drive tool reads from session state exactly as in `adk-drive-ae/agent/agent.py`.

This approach:
- Requires zero GWS admin actions.
- Requires zero changes to the GE registration (the card stays `JSONRPC`, GE keeps calling the Cloud Run bridge).
- The user token is the user's actual token, not a service account — genuine per-user Drive access, not DWD.
- Is already fully proven: `adk-drive-ae` proves session state injection, `cloud-run/` proves the JSONRPC bridge and token extraction. Combining them is straightforward.
- The only new risk is token lifetime. Mitigate by re-injecting the token on every turn (GE sends a fresh `ya29.*` on each JSONRPC call; the bridge can call `create_session` each turn or `update_session` if the AE SDK exposes it).

**Rationale for not recommending DWD:** For a live customer demo, explaining "we gave a service account blanket read access to everyone's Drive" is a harder sell than "the user logs in and consents, and the token flows through to Drive." The true per-user delegation story is stronger and the implementation is not significantly more complex given the existing `adk-drive-ae` reference.

**If the GE chat interface is not required** (e.g., a custom web app is acceptable), use `adk-drive-ae` directly — it is simpler, has no Cloud Run dependency, and is already deployed to AE resource `5114827487100010496`.

---

## Evidence sources

| Claim | Evidence type | Location |
|---|---|---|
| AE only accepts `http_json` | Source code (hard ValueError) | `vertexai/preview/reasoning_engines/templates/a2a.py` line 186–192 |
| GE harpoon only invokes JSONRPC | Empirical (3-hour debug session) + in-repo comments | `memory/ge_custom_a2a_jsonrpc.md`, `cloud-run/register_ge_agent.py` comment |
| AE strips user bearer | Source code (set_up creates RESTAdapter only) + README | `a2a.py` set_up(), `agent-runtime/README.md` "Known limitations" |
| Session state survives to tool calls | Memory + live project | `memory/agent_engine_gotchas.md`, `adk-drive-ae/backend/main.py` |
| a2a-sdk supports both JSONRPC and REST server routes | Source code | `a2a/server/routes/jsonrpc_routes.py`, `rest_routes.py` |
| GE requires `protocolVersion: "0.3.0"` in card | Registration docs + in-repo register scripts | `docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-a2a-agent` |
| New a2a-sdk (1.x) uses `supported_interfaces` not `preferred_transport` | Source code (proto) | `a2a/types/a2a_pb2.py` (AgentCard proto), `client_factory.py` |
