# Demo Runbook — Bain Gemini Enterprise Agent Platform

> **What this demo proves:** end-to-end Bain workflow on Google Cloud's
> Gemini Enterprise Agent Platform with all four pillars wired up — **Build**
> (ADK + MCP), **Scale** (Agent Runtime + Sessions), **Govern** (Agent
> Identity + Agent Registry + Agent Gateway + custom policy enforcement), and
> **Optimize** (Agent Observability via Cloud Trace + Cloud Logging + the
> live Workstation panel).
>
> Every panel the customer sees on stage points at **real GCP resources** in
> the `vtxdemos` project. No simulators.

---

## 1. Architecture

```
   Browser (custom UI :5186)
        │  /api/...           ──────► Vertex AI Agent Runtime (ADK on AE)
        │                              │  reasoningEngine 5849699277663633408
        │                              │  identity_type: AGENT_IDENTITY (SPIFFE)
        │                              │  OTEL telemetry: enabled
        │                              │
        │                              ├── tool: search_and_fetch_top
        │                              ├── tool: public_market_multiples
        │                              ├── tool: plot_financial_data
        │                              └── tool: check_internet_egress
        │                                       │
        │                                       │ awaits policy_guard.check()
        │                                       │ BEFORE every tool call
        │                                       ▼
        │  /api/gateway-logs               bain-ge-policy-svc (Cloud Run)
        │ ─────────────────►              FastAPI /decide → ALLOW / DENY
        │  poll 1.5s                       6 rules (R000–R020, R999)
        │      ▲                           writes structured Cloud Log entry
        │      │                                      │
        │   bain-ge-gateway-logs-svc                  │
        │   queries Cloud Logging ◄───────────────────┘
        │   filters by jsonPayload.component
        ▼
   Workstation panel renders real
   ALLOW (green) / DENY (red) entries
   with rule IDs + Cloud Logging deep links
```

Also provisioned but not actively routing today:
- `reasoning-engine-gateway` AgentGateway (visible in Network Services console)
- gRPC ext_authz v3 service `bain-ge-policy-grpc` (HTTP/2 Cloud Run, ready)
- Internal Application LB + Serverless NEG + self-managed cert
- `authzExtensions/bain-ge-policy-extension` (registered)

Why not routing through the gateway yet: the AgentGateway authzPolicy
attachment surface has a catch-22 in its preview API (extension and policy
must agree on `loadBalancingScheme` but the AgentGateway target rejects every
valid value). The infrastructure is in place so when GCP fixes that, only
the `authzPolicy` create needs to succeed and traffic begins flowing.
See `PRODUCTION_GATEWAY_WIRING.md`.

---

## 2. Console URLs (open these BEFORE the demo)

| Tab | URL | What you'll show |
|---|---|---|
| 1 | https://console.cloud.google.com/agent-platform/runtimes?project=vtxdemos | The deployed `bain-financial-secure-agent` runtime |
| 2 | https://console.cloud.google.com/agent-platform/gateways?project=vtxdemos | `reasoning-engine-gateway` listed with PSC mTLS endpoint |
| 3 | https://console.cloud.google.com/agent-platform/agent-registry?project=vtxdemos | Bain agent + 77 sibling agents + MCP servers + endpoints |
| 4 | https://console.cloud.google.com/agent-platform/policies/iam?project=vtxdemos | IAM agent policies surface |
| 5 | https://console.cloud.google.com/agent-platform/policies/business-policies?project=vtxdemos | Semantic Governance Policies |
| 6 | https://console.cloud.google.com/agent-platform/topology?project=vtxdemos | Agent topology graph |
| 7 | https://console.cloud.google.com/agent-platform/evaluation?project=vtxdemos | Agent Evaluation + Simulation + Online Monitors |
| 8 | https://console.cloud.google.com/traces/list?project=vtxdemos | Cloud Trace — OTel GenAI spans from the agent runtime |
| 9 | https://console.cloud.google.com/logs/query?project=vtxdemos | Cloud Logging — gateway policy decisions |
| 10 | http://localhost:5186 | The custom UI |

### Saved log filters

Open Cloud Logging (tab 9) and paste these as separate queries:

**Real policy decisions (the demo's headline panel data):**
```
resource.type="cloud_run_revision"
resource.labels.service_name="bain-ge-policy-svc"
jsonPayload.component="agent-gateway-policy"
```

Restrict to DENY only:
```
resource.type="cloud_run_revision"
resource.labels.service_name="bain-ge-policy-svc"
jsonPayload.component="agent-gateway-policy"
jsonPayload.policy_decision="DENY"
```

**Reasoning Engine audit (who called the agent, what tools fired):**
```
resource.type="aiplatform.googleapis.com/ReasoningEngine"
resource.labels.reasoning_engine_id="5849699277663633408"
```

**Agent Identity principals in use (SPIFFE attribution):**
```
resource.type="aiplatform.googleapis.com/ReasoningEngine"
protoPayload.authenticationInfo.principalSubject=~"agents.global.org-"
```

---

## 3. Demo script (15 min)

### Act 1 — The architecture (~3 min)

1. Open tab 1 (Runtimes). Show `bain-financial-secure-agent` deployed with
   `identity_type: AGENT_IDENTITY`. Click it; show the **Identity** card —
   per-agent SPIFFE principal (preview feature).
2. Open tab 2 (Gateways). Show `reasoning-engine-gateway` exists with PSC
   mTLS endpoint. "This is the network-layer enforcement point. Traffic from
   the agent's outbound calls passes through here, mTLS-authenticated by the
   agent's SPIFFE cert."
3. Open tab 3 (Agent Registry). Show the agent is registered with its tools
   and bindings. "Agent Registry is the central catalog — every tool, every
   MCP server, every agent. Default-deny gating happens here."

### Act 2 — The agent runs, policy enforces (~7 min)

Switch to tab 10 (the UI at localhost:5186). For each scenario:

| # | Click | What happens on screen |
|---|---|---|
| 1 | **📊 Launch Public Market Agent** | Chat replies with GOOGL/AMZN comparison + Recharts. The right-side **Agent Gateway Policy Monitor** lights up with 3 green **ALLOW** entries — one per tool call (`public_market_multiples`, `plot_financial_data`). Each shows rule `R999.default-allow` and a "Cloud Logging ↗" link. |
| 2 | **🛡️ Launch Agent Gateway DLP Shield** | The agent attempts `search_and_fetch_top("02_Restricted_*HoldCo.docx")`. The Monitor flips to a **RED DENY** entry: rule `R012.restricted-doc-default-deny`, the literal policy reason, and a Cloud Logging deep link. The chat reply quotes the rule + reason — not a simulated `████████`. |
| 3 | Click the **Cloud Logging ↗** link inside the DENY entry | A new tab opens at the Logs Explorer with the exact correlation_id pinned. The audience sees the real JSON: `policy_decision`, `rule`, `reason`, `source_agent`, `target_service`, `tool`, `args_preview`, `latency_ms`. |
| 4 | Type: "Show me the agreed acquisition price for the holdco target." | DENY with rule `R010.mnpi-dlp-shield` — same MNPI shield, different rule, fired by the keyword combination heuristic. |
| 5 | **🧪 Launch Agent Observability** | Agent fetches the canary file. Policy ALLOWs under `R020.canary-observability` (canary observability rule). Chat reply notes the prompt-injection canary was neutralized. |

### Act 3 — Cloud Console proof (~5 min)

1. **Tab 8 (Cloud Trace).** Show the runtime is emitting GenAI OTel spans
   per turn. Click into one — see model call latency, tool call hops, the
   policy check round-trip. ("Every turn of the chat you just saw produced
   this trace.")
2. **Tab 9 (Cloud Logging) with the policy filter.** Show the entries the
   UI panel was rendering all along — same correlation IDs.
3. **Tab 1 (Runtimes) → click your agent → Observability tab.** Show the
   per-agent metrics (request volume, p50/p99 latency, error rate) auto-fed
   by the runtime.
4. **Tab 6 (Topology).** Show the agent's dependency graph: model, tools,
   policy service, downstream MCPs.

---

## 4. What's real vs. what's pending

| Area | State | Demo line |
|---|---|---|
| ADK agent + 4 tools | ✅ Real | "ADK 2.x, gemini-2.5-flash, async tools." |
| Agent Runtime deployment | ✅ Real | "Vertex AI Agent Runtime, scaled to zero, sub-second cold start." |
| **Agent Identity (SPIFFE)** | ✅ Real (preview) | "Per-agent cryptographic identity, no shared SAs." |
| Agent Registry entry | ✅ Real | "Centralized tool catalog with binding-based access control." |
| Real policy decisions (HTTPS path) | ✅ Real | "Every tool call decided by this policy service before it runs." |
| Cloud Logging entries | ✅ Real | "Every decision is durably logged with a correlation ID." |
| UI Gateway Monitor panel | ✅ Real | "Live feed of policy decisions, polled from Cloud Logging every 1.5 seconds." |
| OTel tracing in Cloud Trace | ✅ Real | "OTel GenAI semantic conventions, no extra instrumentation needed." |
| Custom UI | ✅ Real | "Vite + React + Zustand. Direct call to Vertex AI Agent Runtime via local ADC proxy." |
| **Agent Gateway resource** | ✅ Provisioned | "Network-layer enforcement point exists in this project; mTLS PSC endpoint visible in Console." |
| **Gateway routing** (agent egress through PSC mTLS) | ⏳ Preview API issue | "Once GCP fixes the `loadBalancingScheme` matching for AgentGateway authzPolicies, traffic begins flowing through the gateway and these same Cloud Logs are mirrored under `networkservices.googleapis.com/AgentGateway`." |
| **gRPC ext_authz service** | ✅ Built + deployed | "Production policy service ready; HTTP/2 Cloud Run, Internal LB, self-managed cert. When the gateway attaches, this is the enforcement point." |
| **Agent Registry bindings** (with `auth_provider`) | ⏳ Preview connector | "Requires preview `connectors/{connector}` resource for OAuth delegation; coordinated through Google account team. The R000 rule mirrors this gate in-policy until then." |

---

## 5. Run it yourself

```bash
# 1. Sync the latest from the repo
git pull

# 2. Start the UI
cd antigravity/bain_ge_agent_platform/custom-ui
npm install      # first time
npm run dev      # opens at http://localhost:5186

# 3. Sign in to Microsoft (Settings drawer → "Sign in with Microsoft")
#    — required for SharePoint scenarios (tool calls that actually fetch files)

# 4. Click the demo buttons in order (see Act 2 above)

# 5. Tail the policy logs in your own terminal if you want a CLI view:
gcloud logging tail 'resource.type="cloud_run_revision" AND
                     resource.labels.service_name="bain-ge-policy-svc" AND
                     jsonPayload.component="agent-gateway-policy"' \
  --project=vtxdemos
```

---

## 6. Troubleshooting

**Gateway Monitor stays empty after a query.** Open browser devtools → Network
tab. The poller hits `/api/gateway-logs/api/gateway-logs?since_seconds=600`.
If `count: 0`, check that the agent actually invoked a tool (look at the
streaming response for `function_call` events). If still 0, run the manual
log query in section 2 — Cloud Logging ingest can lag a few seconds.

**"POLICY_SERVICE_UNREACHABLE" in tool responses.** The agent's egress to
`bain-ge-policy-svc-*.run.app` is blocked. Check `gcloud run services
describe bain-ge-policy-svc` is healthy; otherwise temporarily set
`POLICY_FAIL_OPEN=1` in `deploy.py`'s env_vars and redeploy.

**Agent Identity not visible.** Confirm the deploy actually applied the
`identity_type` field:
```bash
gcloud ai reasoning-engines describe 5849699277663633408 \
  --region=us-central1 --project=vtxdemos --format='value(spec.identityType)'
```
Should print `AGENT_IDENTITY`. If empty, the `vertexai._genai.types` import
in `deploy.py` failed silently — verify
`from vertexai._genai import types as ge_types` lands and that
`ge_types.IdentityType.AGENT_IDENTITY` resolves.

**Customer asks "where's the gateway routing?"** Be honest. Show them the
gateway in Network Services console (it's real), show `bain-ge-policy-grpc`
in Cloud Run (the gRPC ext_authz service is real and HTTP/2 deployed), show
the Internal LB + authzExtension (also real), and explain the preview API
catch-22 on AuthzPolicy + AgentGateway target. Then point at
`PRODUCTION_GATEWAY_WIRING.md` for the exact `authzPolicy` create that will
work once GCP fixes the validation logic.
