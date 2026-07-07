# Handoff — `exploring_StreamAssist`

You (next LLM) are picking up work on a small web app whose only purpose is to make Gemini Enterprise's `streamAssist` API observable: every request, every streamed event, every grounding reference, every planner step, surfaced live in a two-pane UI. Read this whole doc before touching anything.

---

## 1. What you're inheriting

**Project root:** `/home/admin_jesusarguelles_altostrat_c/vertex-ai-samples/semiautonomous-agents/atlassian-jira-integration/exploring_StreamAssist/`

**Live deployment:** Cloud Run service `exploring-streamassist` in project `vtxdemos`, region `us-central1`.
URL: `https://exploring-streamassist-oyntfgdwsq-uc.a.run.app`
SA: `254356041555-compute@developer.gserviceaccount.com` (compute default; already has `discoveryengine.admin` in vtxdemos).
Deploy via `bash deploy.sh`.

**Backing GE engine:** `jira-testing_1778158449701` (Jira federated connector) in vtxdemos. The engine has ~15 datastores attached — relevant because streamAssist will not tell you which one(s) it consulted.

**Originating session (transcripts):** Claude session `092ff2b8-19ad-40de-a052-34630fac777d.jsonl` under `~/.claude/projects/-home-admin-jesusarguelles-altostrat-c/` — 52 MB, May 19–23 2026. That's where this app was designed and shipped. If you need to know *why* a decision was made, grep that file.

**Sibling context** (don't re-explore unless asked): the user benchmarked 6 architectures (Options A–F) for Jira→GE in the parent `atlassian-jira-integration/` directory. Headline: Option A (Custom MCP + ADK) wins at 94.7% accuracy, 0% hallucination. This exploring_StreamAssist app is the *observability tool*, not a benchmark option.

---

## 2. The user (read this before answering anything)

- Wants **terse** replies. One or two sentences per update. No headers/bullets unless asked.
- Never quote effort estimates, T-shirt sizes, LOC. They're paying for an LLM, not a junior dev.
- Never add `Co-Authored-By: Claude` or `🤖 Generated with Claude Code` to commits or PR descriptions.
- Default GCP project for *deployments* is `vtxdemos`. `cloud-llm-preview1` is ONLY the CLI quota project — never deploy there. Prefer auto-detection over hardcoded IDs.
- Default LLM picks: gemini-3-flash-preview (or gemini-3.1-pro-preview if reasoning needed), in the `global` region. 2.5 is being deprecated.
- For non-trivial parallel work, spawn background subagents — don't block the main chat.
- Single-line shell commands (no `\` line-continuations) when the user might copy-paste.

---

## 3. Architecture in one breath

```
User browser
  ├─ Google Sign-In (vtxdemos OAuth Web client)
  │   → POST /api/auth/verify → signed cookie carrying user_pseudo_id = sha256(sub)[:32]
  ├─ "Connect Jira" popup → /api/auth/jira-consent-url (GE-issued consent URL for jira-testing engine)
  │   → on consent, GE stores a per-user 3LO grant keyed by userPseudoId
  └─ Chat input → POST /api/assist (SSE)
        │
        ▼
FastAPI (main.py) on Cloud Run
  ├─ Pulls user's Google access token from cookie session (fallback: SA token, emits auth_mode: service_account SSE)
  ├─ Calls discoveryengine streamAssist with Authorization: Bearer <user_token>
  ├─ Response is a top-level JSON array streaming over a single HTTP body
  ├─ _scan_top_level_objects() incrementally parses array elements as they arrive
  ├─ For each element, _sse(event, data) re-emits to browser
  └─ _extract_chat_delta(chunk, include_thoughts) splits visible text vs thought:true deltas
        │
        ▼
Browser (static/app.js)
  ├─ Left pane: rendered chat (marked + highlight.js)
  └─ Right pane: raw inspector (planner steps, function calls, grounding refs with chunk preview)
```

GE engine: `jira-testing_1778158449701`. Federated connector requires `read:jira-work` + `read:user:jira` scopes on the Atlassian app.

---

## 4. File map

| File | Lines | Purpose |
|---|---:|---|
| `main.py` | 1172 | FastAPI app: SSE streaming, JSON-array parser, OAuth (Google + Jira consent), session cookies |
| `static/index.html` | 156 | Two-pane resizable layout, sign-in button, Jira connect button |
| `static/app.js` | 1248 | SSE client, chat renderer, inspector pane (planner steps + grounding chips) |
| `static/styles.css` | 448 | Layout / dark theme |
| `sample_event_capture.json` | 871 | Frozen `streamAssist` response for "List bugs in project SMP" (20 chunks). Source of truth for the observations doc. |
| `GROUNDING_OBSERVATIONS.md` | 34 | The findings — what `streamAssist` exposes vs hides |
| `Dockerfile` + `deploy.sh` + `requirements.txt` | — | Build/deploy |
| `README.md` | — | Quick-start + manual OAuth-client provisioning steps |

**Important `main.py` functions to know:**
- `_get_sa_token()` — fetches SA token via metadata server (Cloud Run) or `google.auth` (local).
- `_load_session()` / `_set_session_cookie()` — itsdangerous-signed session cookies.
- `_user_pseudo_id_from_sub(sub)` — hashes Google `sub` claim to 32-char id; this is what GE keys 3LO grants on.
- `_fetch_engine_meta(client)` — pulls engine + connector metadata for the UI.
- `_scan_top_level_objects(buf)` — the incremental JSON-array parser (DE returns one big array, not NDJSON).
- `_sse(event, data)` — formats a single SSE frame.
- `_extract_chat_delta(chunk, include_thoughts)` — walks a chunk and returns user-visible text, optionally including `thought:true` deltas.
- Routes: `/api/health`, `/api/engine`, `/api/auth/*`, `/api/jira/*`, `/api/assist` (the SSE one).

---

## 5. What `streamAssist` exposes — verbatim findings

(From `GROUNDING_OBSERVATIONS.md`. Sample basis: `sample_event_capture.json`. Cite this if asked.)

**Visible:**
- `answer.diagnosticInfo.plannerSteps[]` — full planner trace.
  - `queryStep.parts[].text` — user query as the planner saw it.
  - `planStep.parts[].functionCall.{functionName, args, functionId}` — every tool call, including args (we observed `selfawareness_agent({"request": ...})`).
  - `planStep.parts[].text` — the model's "thinking out loud" between tool calls.
  - `planStep.role` — `MODEL` for model-side steps.
- `answer.replies[].groundedContent.textGroundingMetadata` — when a reply is actually grounded:
  - `references[].documentMetadata.{uri, title, document, domain, pageIdentifier, mimeType}` — full source identity.
  - `references[].content` — **the actual chunk text the model saw**.
  - `segments[].{text, endIndex, referenceIndices[]}` — sentence-range → reference index map.
- `answer.replies[].groundedContent.content.thought: true` — chain-of-thought deltas, tagged separately so the UI can hide/show.
- `answer.intentClassifications[]` — e.g. `["SUPPORT"]`.
- `answer.adkAuthor` — which sub-agent produced the reply (`root_agent`, etc.).
- `assistToken` + `sessionInfo.{session, queryId}` — correlation handles.

**Missing (do not pretend otherwise):**
- No per-reference confidence / relevance score.
- No `functionResponse` — you see call args, never the return value.
- No JQL / native query the sub-agent built.
- No datastore-routing decision trace (with 15 datastores attached).
- No raw retrieval candidates — only the references that survived into the final answer.
- No per-step latency field (must derive from `createTime`).
- No Gemini-native `citationMetadata` / `groundingMetadata` — GE uses its own `textGroundingMetadata` shape.

---

## 6. Critical context from prior memory — DO NOT relearn these

These are documented in `~/.claude/projects/-home-admin-jesusarguelles-altostrat-c/memory/` — cited so you know they exist.

- **`streamassist_request_shape.md`** — `streamAssist` body MUST use `toolsSpec` (not `tools`), `query.parts: [{text}]` (not `query.text`), `assistSkippingMode: "REQUEST_ASSIST"`, and `answerGenerationMode: "NORMAL"`. The "right" shape is copied verbatim from what the GE Console UI sends in DevTools Network. Trust that, not the v1alpha schema docs.
- **`ge_adk_agent_gotchas.md`** — Four silent-failure modes when calling streamAssist from an ADK agent:
  1. Agentspace injects V1 Azure tokens, not V2 (need V1-issuer WIF provider).
  2. GE chat data-source toggle is a client-side filter on `dataStoreSpecs` — don't fetch from `widget_config`; hardcode entity datastores.
  3. streamAssist silently SKIPs short queries — fix by combining `query.parts` shape + wrapping bare keywords into a full sentence at the tool layer + `assistSkippingMode: REQUEST_ASSIST`.
  4. Deployed `env_vars` don't appear in the Reasoning Engine GET response — verify via Cloud Logging instead.
- **`feedback_adc_quota_project.md`** — Never mutate global ADC quota project. Use inline `GOOGLE_CLOUD_QUOTA_PROJECT=` per-process. The user depends on `cloud-llm-preview1` being intact.
- **`feedback_project_id_separation.md`** — `cloud-llm-preview1` = CLI quota project only. Everything DEPLOYED goes to `vtxdemos`.
- **`atlassian_mcp_gemini_enterprise.md`** — When wiring Atlassian MCP into GE, token URL must be `cf.mcp.atlassian.com/v1/token`; use DCR (`/v1/register`), not developer.atlassian.com credentials.
- **`ge_custom_mcp_confirmation_fix.md`** — Five-part recipe to suppress the per-call permission popup on BYO-MCP while keeping grounding: full `Tool` serialization in `/mcp` handler + protocolVersion `2025-06-18` + `ToolAnnotations` + `outputSchema` + canonical `search(query)`/`fetch(id)` tools.

---

## 7. Manual setup (the one part deploy.sh can't do)

The OAuth Web client must be created by hand in the vtxdemos console:

1. https://console.cloud.google.com/apis/credentials?project=vtxdemos
2. **+ CREATE CREDENTIALS → OAuth client ID**, type **Web application**, name `exploring-streamassist`.
3. **Authorized JavaScript origins:** `https://exploring-streamassist-254356041555.us-central1.run.app`
4. **Authorized redirect URIs:** `https://exploring-streamassist-254356041555.us-central1.run.app/api/auth/callback` (Google requires one even though we don't use it).
5. `echo 'CLIENT_ID_HERE' > .oauth_client_id && bash deploy.sh`

The Atlassian-side federated connector consent app (the one consent popup opens) also needs `read:jira-work` and `read:user:jira` scopes registered.

---

## 8. Run locally

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
GOOGLE_CLOUD_QUOTA_PROJECT=cloud-llm-preview1 .venv/bin/uvicorn main:app --port 8080
```
Open `http://localhost:8080`. The local instance still hits the real Cloud Run-deployed GE engine and federated Jira; only the FastAPI is local.

---

## 9. Likely next asks (be ready)

The user typically continues in these directions — none has been started yet, so don't claim progress:

- **Per-reference latency / score** — would require client-side derivation from `createTime` (no native field). Be honest about this.
- **Exposing tool RESPONSE** — currently unreachable through streamAssist; would need a connector-side log shim or a future GE feature.
- **Datastore-routing visibility** — same: not exposed; would need GE product change or logging on connector.
- **Compare grounding visibility across the 6 Jira options (A–F)** — the comparison-site at `../eval/comparison-site/` already exists but doesn't show event-level data; could be wired up.
- **Reuse this app for the SharePoint engine** — sibling deployment pattern already exists at `semiautonomous-agents/streamassist-oauth-flow/` and `streamassist-oauth-flow-us/`. Mostly an engine-id swap + connector consent URL swap.
- **Publish the findings** — `GROUNDING_OBSERVATIONS.md` is currently the only writeup; user may want a blog/Confluence post.

---

## 10. Sanity checks before you change anything

1. `gcloud run services describe exploring-streamassist --region us-central1 --project vtxdemos` — confirm the deployment is still live and what revision is current.
2. `gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="exploring-streamassist"' --freshness=10m --limit=30 --project vtxdemos` — see recent traffic / errors.
3. Read `sample_event_capture.json` if you need to know the exact shape of a streamAssist event without making a live call.
4. Check `git status` / `git log` in `vertex-ai-samples/` before assuming the on-disk state matches what's deployed.
5. If memory cites a function/file/flag, verify it still exists before recommending it — memories are point-in-time.

---

## 11. Conventions for *your* output

- Terse. Status + next step. No preamble, no recap, no "let me know if…".
- Match scope to the ask. A yes/no question gets one line.
- If you make code changes for a UI feature, actually drive it in a browser (chrome-devtools MCP) before reporting success — type-check passing ≠ feature working.
- Use TaskCreate only for genuinely multi-step work (3+ non-trivial steps). Don't ceremony every tiny task.

That's everything. Open `main.py` and `GROUNDING_OBSERVATIONS.md` first; the rest follows.
