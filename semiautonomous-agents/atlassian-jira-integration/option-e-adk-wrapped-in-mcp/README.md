# Option E — ADK Agent wrapped inside a Custom MCP

A Cloud Run service that, from GE's perspective, is an ordinary
**custom_mcp** data store (so it appears in the main chat surface with no
agent picker required). Internally, every tool call delegates to the
existing **Option A ADK agent on Vertex Agent Engine** via
`vertexai.agent_engines.get(...).stream_query(...)`. The ADK agent's
polished answer text becomes the MCP tool result that GE renders almost
unchanged.

The goal of this hack is to combine the **silent, low-cost main-chat
delivery of Option C** with the **multi-step orchestration, pagination
callback, and 3500-char system prompt of Option A** — without registering
an agent in the GE agent picker.

---

## Architecture

```mermaid
flowchart TB
  user(["👤 User in GE main chat"]):::user
  ge["🟦 Gemini Enterprise — auto-spawned custom_mcp_agent · no agent picker"]:::ge
  store[("📦 GE Custom MCP datastore<br/>mcp-adk-wrapper-*_mcp_data")]:::store
  wrapper["🟧 Cloud Run mcp-adk-wrapper<br/>StreamableHTTP /mcp · search + fetch"]:::wrapper
  ae["🟪 Vertex AI Agent Engine<br/>Option A ADK agent (jira-mcp-portal)"]:::ae
  mcp["🟧 Cloud Run jira-mcp-server<br/>7 Jira tools via SSE"]:::mcp
  jira[("🟦 Atlassian Jira REST<br/>api.atlassian.com")]:::jira

  user --> ge
  ge ==> store
  store -.->|OAuth 3LO on 1st call| jira
  store ==> wrapper
  wrapper ==>|create_session{temp:auth_id=bearer}| ae
  ae ==> mcp
  mcp ==>|Authorization: Bearer jira-oauth| jira

  classDef user fill:#FBBC04,stroke:#F29900,stroke-width:3px,color:#000
  classDef ge fill:#4285F4,stroke:#1967D2,stroke-width:3px,color:#fff
  classDef store fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff
  classDef wrapper fill:#FF6F00,stroke:#E65100,stroke-width:3px,color:#fff
  classDef ae fill:#7B1FA2,stroke:#4A0072,stroke-width:3px,color:#fff
  classDef mcp fill:#FF8F00,stroke:#E65100,stroke-width:2px,color:#fff
  classDef jira fill:#0052CC,stroke:#003D99,stroke-width:2px,color:#fff
  linkStyle 1,3,4,5,6 stroke:#FF6F00,stroke-width:3px
  linkStyle 2 stroke:#34A853,stroke-width:2px,stroke-dasharray:5 3
```

**Latency budget**: GE → wrapper (≈100 ms) + wrapper → AE
`create_session` (≈500 ms) + AE `stream_query` (15-180 s, depends on
question) + wrapper → GE return (≈100 ms). Expect **p50 ≈ 25-40 s** —
roughly Option A latency + one extra hop.

**Cost**: Option A's $0.17/1K (AE invocation + ADK API + Cloud Run for the
Jira MCP) plus an additional Cloud Run service (≈ $0.05/1K, idle most of
the time), so **≈ $0.22/1K** in the steady state. Cheaper than running a
new agent-fronted GE engine; more expensive than Option C alone.

---

## When to use Option E

| | Option A | **Option E** | Option C |
|---|---|---|---|
| MCP server | Custom | **Custom (wrapping ADK)** | Custom |
| Front layer | ADK on Agent Engine | **ADK behind MCP wrapper** | None — direct GE |
| GE consumption surface | Agent picker (sidebar) | **Main chat (no agent picker)** | Main chat (no agent picker) |
| Multi-step reasoning | Strong | **Strong (inherits from A)** | Weak |
| Hallucination | ~1 % | **inherits A** | 31 % |
| Cost / 1K | $0.17 | $0.22 | $0.05 |
| Latency p50 | 24 s | ≈ 25-40 s | 29 s |

**Pick Option E when:** you need Option A's accuracy AND main-chat delivery
(no agent picker) AND can afford the extra Cloud Run hop. Pick A directly
when the agent picker is acceptable. Pick C when you don't need
multi-step.

---

## The five-part recipe (preserved verbatim)

The wrapper applies the [Option C silent-dispatch recipe](../option-c-custom-mcp-direct/FINDINGS.md#3-the-five-part-recipe)
so GE treats the connector as retrieval-shaped and dispatches `search` /
`fetch` without per-call confirmation popups:

1. `/mcp` StreamableHTTP handler returns `t.model_dump(by_alias=True, exclude_none=True)` for every Tool.
2. `initialize` response declares `protocolVersion: "2025-06-18"`.
3. Both tools declare `ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=True)`.
4. Both tools have an `outputSchema` matching the canonical `SearchResultPage` / `FetchResult` shapes.
5. The two tools ARE the canonical `search(query)` + `fetch(id)` primitives — there is no domain-specific surface that GE could expose individually.

---

## Tool surface

```python
@mcp.tool
search(query: str) -> SearchResultPage:
    """The user's question, verbatim. Returns the ADK agent's full polished
    answer wrapped as a single SearchResultPage result. GE renders the
    `text` field unchanged."""

@mcp.tool
fetch(id: str) -> FetchResult:
    """Issue key, e.g. SMP-912. Synthesizes a 'give me details for {id}'
    prompt, sends it to the ADK agent, returns the answer."""
```

The MCP wrapper does **not** expose Jira's domain primitives
(`searchJiraIssuesUsingJql`, `getIssueComments`, etc.) — they're hidden
behind the ADK agent, which is the entire point. GE's auto-MCP-agent only
sees two tools, picks `search` for everything that isn't a single-key
lookup, and forwards the user's question untouched.

---

## OAuth token flow

GE injects the user's Jira OAuth bearer into `Authorization: Bearer <jira-oauth>`
on every `/mcp` POST. The wrapper:

1. Captures it in FastAPI middleware (same pattern as
   `option-a-custom-mcp-portal/jira_server/server.py:30-47`).
2. Creates a fresh AE session with `state={"temp:jira-mcp-portal-auth": <bearer>}`
   (key matches `AGENTSPACE_AUTH_ID` in `option-a-custom-mcp-portal/adk_agent/agent.py:29`).
3. Streams the agent's answer back.

The Option A agent's `mcp_header_provider` reads
`tool_context.state.get("jira-mcp-portal-auth")` (or `temp:` variant) and
attaches the bearer to its outgoing MCP/SSE call to the Jira tool server —
so the per-user identity is preserved end-to-end without an extra OAuth
roundtrip.

Per `~/.claude/.../memory/agent_engine_gotchas.md`: state keys with the
`temp:` prefix **do** sync through `agent.create_session(state=...)` —
this was specifically confirmed for the Vertex SDK path used here.

---

## Setup

### Prerequisites

- Option A is already deployed (ADK agent on Vertex Agent Engine and the
  Jira MCP Cloud Run). The wrapper points at the existing AE resource.
- Atlassian OAuth client used for Options B and C (same `client_id` /
  `client_secret`, in `eval/.env`).
- GE engine `jira-testing_1778158449701` (project `vtxdemos`).

### Step 1 — Deploy the wrapper Cloud Run service

```bash
cd option-e-adk-wrapped-in-mcp/server

gcloud run deploy mcp-adk-wrapper \
  --source . \
  --region us-central1 \
  --project vtxdemos \
  --allow-unauthenticated \
  --port 8080 --memory 1Gi --cpu 2 --timeout 600
```

Service URL on first deploy: `https://mcp-adk-wrapper-254356041555.us-central1.run.app`.

`--allow-unauthenticated` is safe: every `/mcp` POST is gated by the
per-user Jira OAuth bearer GE injects in the `Authorization` header. The
service rejects calls with no auth indirectly — the ADK agent answers with
a refusal because its `mcp_header_provider` finds no token in state.

Service identity needs `roles/aiplatform.user` on the project so the
runtime can call `agent_engines.get(...).stream_query(...)`. The Cloud
Run default SA usually has it; if not:

```bash
gcloud projects add-iam-policy-binding vtxdemos \
  --member="serviceAccount:254356041555-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Step 2 — Register the custom MCP datastore on GE

```bash
cd option-e-adk-wrapped-in-mcp
GCLOUD_ACCOUNT=admin@jesusarguelles.altostrat.com \
  python register_datastore.py
```

The script clones Option B's `register_datastore.py` but:
- `instance_uri` points at the wrapper's `/mcp` endpoint
- OAuth uses the **standard** `auth.atlassian.com` endpoints (same as
  Option C — NOT the `cf.mcp.atlassian.com` endpoints, those are for
  Atlassian's hosted Remote MCP)
- Collection id defaults to `mcp-adk-wrapper-<timestamp>`

Note the printed `OPTION_I_DATASTORE_ID=...` line.

### Step 3 — Enable tools + complete OAuth (console only)

The Discovery Engine REST API does not expose the per-tool enable flow
or the OAuth re-auth dialog. These remain UI-only — same as Options B and
C:

1. Console → AI Applications → Engine `jira-testing_1778158449701` →
   **Data stores** → click `mcp-adk-wrapper-<ts>` → **Actions** tab.
2. Click **Reload custom actions** (waits ~5 s, populates `dynamicTools`).
3. Check `search` and `fetch`. Click **Enable actions**.
4. The console opens a **Re-authenticate** dialog. Paste the same
   `ATLASSIAN_CLIENT_ID` / `ATLASSIAN_CLIENT_SECRET` from `eval/.env`,
   click **Connect**.
5. Approve the Atlassian consent, pick the `sockcop.atlassian.net` site.
6. Connector flips to ACTIVE; tools are now callable from GE main chat.

**Verification**: open the engine's chat surface (no agent picked) and
ask `How many issues are in SMP?`. The expected answer is `There are 910
issues in the SMP project. Status: Done 452 / To Do 426 / In Progress
32.` — produced entirely by the ADK agent and rendered verbatim by GE.

### Step 4 — Set the eval env var

```bash
# in eval/.env
OPTION_I_DATASTORE_ID=mcp-adk-wrapper-<ts>_mcp_data
```

### Step 5 — Run the eval

```bash
cd eval
nohup env GCLOUD_ACCOUNT=admin@jesusarguelles.altostrat.com \
  ./.venv/bin/python -m runners.orchestrator \
    --questions questions/main.json --only i \
    --out runs/$(date +%Y%m%d-%H%M%S)-option-i-full --concurrency 4 \
    > /tmp/option-i.log 2>&1 &
```

`--concurrency 4` (vs 6 for Options A/G) because each request now traverses
two Cloud Run hops and the ADK agent has its own concurrency limit on
Agent Engine.

### Step 6 — Judge + report

```bash
cd eval
./.venv/bin/python judge.py runs/<ts>-option-i-full/responses_i.jsonl \
  --pipeline i --questions runs/<ts>-option-i-full/questions.json \
  --out runs/<ts>-option-i-full/judged_i.json

./.venv/bin/python report.py --run runs/<ts>-option-i-full \
  --questions runs/<ts>-option-i-full/questions.json
```

Findings + per-bucket / per-category tables: [FINDINGS.md](./FINDINGS.md).

---

## Risks and failure modes (be honest)

| Risk | Mitigation |
|---|---|
| **Extra latency hop** — GE → wrapper → AE → MCP → Jira; ADK agent's `stream_query` can take 60-120 s on multi-step questions; GE has a per-call timeout. | `AGENT_STREAM_TIMEOUT_S=300` env var. If the AE stream times out, return whatever partial text we got plus a note. |
| **Two layers of OAuth** — GE wraps Jira OAuth around the MCP call AND the ADK agent's `mcp_header_provider` re-attaches it on its outgoing call. If the `temp:auth_id` key doesn't sync into the AE session, the ADK agent silently falls back to its env-var Basic auth — which may point at a different Jira site. | The Option A agent logs the chosen auth path (`[DEBUG] Using OAuth token (...)` vs `[DEBUG] Using Basic auth for ...`). Cloud Run logs of the wrapper + AE logs together pin down where the token was lost. |
| **Cloud Run cold start** of the wrapper. | First request after idle adds ~3 s. Tolerable for a chat workload. |
| **Cost addition** — extra Cloud Run service on top of Option A's stack (≈ $0.05/1K added). | Disable / delete the wrapper service when the experiment is over; Option A continues to work via the agent picker. |
| **Tool result truncation** — GE applies its own length limits to MCP tool results before rendering. Very long ADK answers (multi-page tables) may be cut off. | The wrapper does not chunk; if you hit this, switch the workload back to Option A's agent-picker surface. |

---

## Cleanup

```bash
gcloud run services delete mcp-adk-wrapper --region us-central1 --project vtxdemos

# Detach + delete the datastore (console: Data stores → … → Delete)
```

---

## Files

| Path | Purpose |
|---|---|
| `server/server.py` | FastAPI app, auth middleware, MCP server, AE-bridge tool implementations |
| `server/Dockerfile` | Cloud Run container |
| `server/requirements.txt` | `fastapi`, `mcp`, `google-cloud-aiplatform[agent_engines]` |
| `register_datastore.py` | GE datastore creation + engine attachment |
| `FINDINGS.md` | Eval results, per-bucket + per-category tables, comparison vs A/B/C |

## Related

- **Option A** (`../option-a-custom-mcp-portal/`) — the underlying ADK agent this wrapper delegates to.
- **Option C** (`../option-c-custom-mcp-direct/`) — the silent-dispatch recipe inherited verbatim here.
- **Option B** (`../option-b-direct-remote-mcp/`) — register-datastore template.
