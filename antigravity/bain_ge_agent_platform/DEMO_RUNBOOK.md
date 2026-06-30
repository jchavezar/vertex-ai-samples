# Demo Runbook — Bain GE Agent Gateway

> **The goal of this demo:** prove to a Bain technical leader that Agent
> Gateway policy enforcement is real, not a UI simulation. Every tool call
> the agent makes is evaluated by a Cloud Run policy service, every decision
> is written to Cloud Logging, and the UI panel renders those real entries.

## 1. Architecture in one minute

```
   ┌──────────┐    /api/...       ┌─────────────────┐
   │  Vite UI │ ─────────────────► Vertex AI Agent  │
   │  :5186   │                   │  Runtime (ADK)  │
   └────┬─────┘                   └────────┬────────┘
        │ /api/gateway-logs                │ HTTPS /decide (per tool call)
        ▼                                   ▼
  ┌──────────────────────┐           ┌────────────────────────┐
  │ bain-ge-gateway-     │           │ bain-ge-policy-svc     │
  │ logs-svc (Cloud Run) │           │ (Cloud Run, FastAPI)   │
  │ proxies Cloud Logging│ ◄──────── │ ALLOW / DENY decisions │
  └──────────────────────┘  reads    │ rules R000–R020        │
                                     └────────────────────────┘
                                              │
                                              ▼
                                     ┌────────────────────────┐
                                     │ Cloud Logging          │
                                     │ jsonPayload.component  │
                                     │ = agent-gateway-policy │
                                     └────────────────────────┘
```

- **`bain-ge-policy-svc`** (`policy-decision-svc/`): the policy engine. Every
  tool call routes through `policy_guard.py` in the agent and POSTs `/decide`
  for an ALLOW/DENY. Each decision emits a structured Cloud Logging entry.
- **`bain-ge-gateway-logs-svc`** (`gateway-logs-svc/`): queries Cloud Logging
  for those entries and serves them to the UI. The Vite proxy at
  `/api/gateway-logs` forwards browser requests to this service.
- **`policy_guard.py`** (`adk-agent/policy_guard.py`): the in-agent guard that
  wraps every tool. Raises `PolicyDenied` on a DENY response, which each tool
  catches and returns as a structured result the LLM is instructed to render
  literally (no fake redaction strings).

The previous demo's `addGatewayLog(...)` hardcoded strings in
`FlatConsoleChat.tsx` are gone. The LLM-side DLP/canary simulation in
`agent.py`'s system prompt is gone. Both are replaced by the real backend
governance loop above.

## 2. One-time setup (already done in `vtxdemos`, listed for reference)

```bash
# Policy service
gcloud run deploy bain-ge-policy-svc \
  --source policy-decision-svc/ --region us-central1 --project vtxdemos \
  --allow-unauthenticated --memory 512Mi --max-instances 4
# URL: https://bain-ge-policy-svc-254356041555.us-central1.run.app

# Gateway-logs proxy
gcloud run deploy bain-ge-gateway-logs-svc \
  --source gateway-logs-svc/ --region us-central1 --project vtxdemos \
  --allow-unauthenticated --memory 512Mi --max-instances 4 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=vtxdemos,POLICY_SERVICE_NAME=bain-ge-policy-svc
# URL: https://bain-ge-gateway-logs-svc-254356041555.us-central1.run.app

# Grant log reader to its runtime SA (default compute SA)
gcloud projects add-iam-policy-binding vtxdemos \
  --member=serviceAccount:254356041555-compute@developer.gserviceaccount.com \
  --role=roles/logging.viewer
```

## 3. Deploy / redeploy the agent

```bash
cd antigravity/bain_ge_agent_platform/adk-agent
uv run deploy.py    # or: python deploy.py
```

The deploy ships `policy_guard.py` in `extra_packages` and sets the
`POLICY_SERVICE_URL` / `REASONING_ENGINE_ID` env vars on the runtime.

## 4. Run the UI

```bash
cd antigravity/bain_ge_agent_platform/custom-ui
npm install      # first time
npm run dev      # opens at http://localhost:5186
```

Open the **Agent Gateway Policy Monitor** panel (main view, right column).
Empty by default. As soon as you send a query that calls a tool, real
ALLOW/DENY entries stream in within ~1.5s (polling interval).

## 5. Demo script

| Step | What you do | What the customer sees |
|---|---|---|
| 1 | Open the UI; show the empty Gateway Monitor panel. | "Real Cloud Logging feed, no fixtures." |
| 2 | Click **Launch Public Market Agent**. | A series of green **ALLOW** entries appear — one per tool call (`public_market_multiples`, `plot_financial_data`). Each shows the rule `R999.default-allow` and a "Cloud Logging ↗" deep link. |
| 3 | Click **Launch Agent Gateway DLP Shield**. | A red **DENY** entry appears with rule `R010.mnpi-dlp-shield`, the literal reason from the policy engine, and a Cloud Logging link. The agent's chat reply quotes the same rule/reason — NOT a fake `████████` redaction. |
| 4 | Open the Cloud Logging link in a new tab. | The customer sees the JSON entry the policy service wrote: `policy_decision`, `rule`, `reason`, `source_agent`, `target_service`, `tool`, `args_preview`, `correlation_id`, `latency_ms`. The entry is in `projects/vtxdemos/logs/run.googleapis.com%2Fstderr`. |
| 5 | Click **Launch Agent Observability**. | An **ALLOW** with rule `R020.canary-observability` — the policy permits the call but flags the canary file. The agent's reply notes the prompt-injection canary was neutralized. |

## 6. What's mocked vs. real

| Component | Real? | Notes |
|---|---|---|
| Policy decisions (`/decide`) | ✅ Real | Cloud Run, deterministic, no LLM. |
| Cloud Logging entries | ✅ Real | Every decision emits a structured entry. |
| Gateway Monitor panel | ✅ Real | Polls `/api/gateway-logs` → `bain-ge-gateway-logs-svc` → Cloud Logging. |
| Per-tool guard in agent | ✅ Real | `await policy_guard.check(...)` at the top of every tool. |
| `reasoning-engine-gateway` resource (Network Services) | ✅ Real | Created in `vtxdemos us-central1`. **No `authzPolicy` attached yet.** Traffic doesn't physically route through it in this demo. |
| `authzPolicy` + `authzExtension` wiring on the gateway | ⏳ Production playbook | See `PRODUCTION_GATEWAY_WIRING.md`. Same `policy.py` runs as a gRPC `ext_authz v3` service when flipped. |
| Agent Registry `bindings` | ⏳ Production playbook | Requires `connectors/{connector}` resource that's preview-only. The R000 rule in `policy.py` enforces the same default-deny gate in-policy. |

## 7. Troubleshooting

- **Gateway Monitor stays empty after a query.** Open the browser devtools
  network tab and check `/api/gateway-logs/api/gateway-logs?...` is returning
  `count > 0` after a tool call. If `count: 0`, check that the agent actually
  invoked a tool (look at the chat for `function_call` notes). If
  `count: 0` and there should be one, run `gcloud logging read` manually with
  the filter in the service description to confirm Cloud Logging ingestion.
- **All decisions come back DENY with rule `R000`.** The agent is calling a
  tool whose target URN isn't in `policy.py`'s `REGISTERED_TARGETS`. Add it
  or fix the agent's `TARGET_FOR_TOOL` mapping in `policy_guard.py`.
- **Every call says `POLICY_SERVICE_UNREACHABLE`.** The agent's egress to
  `bain-ge-policy-svc-*.run.app` is blocked. Check the agent's network
  config; as a temporary measure set `POLICY_FAIL_OPEN=1` in `deploy.py`'s
  `env_vars` (logs a warning per call but permits the call to proceed).
