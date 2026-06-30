# Agent Gateway Policy Decision Service

Real backend governance for the Bain GE demo. Every MCP tool call the agent
wants to make is evaluated here **before** execution. Decisions are emitted
as structured Cloud Logging entries that the UI panel tails live.

Replaces the previous hardcoded `addGatewayLog(...)` simulator strings in
`custom-ui/src/components/FlatConsoleChat.tsx`.

## Local run

```
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

```
curl -s localhost:8080/decide -X POST -H 'Content-Type: application/json' -d '{
  "source_agent": "urn:agent:projects-254356041555:projects:254356041555:locations:us-central1:aiplatform:reasoningEngines:7757233204599193600",
  "target_service": "urn:mcp:projects-254356041555:projects:254356041555:locations:us-central1:agentregistry:mcpServers:agentregistry-00000000-0000-0000-5e80-1137c09a51d0",
  "tool": "search_and_fetch_top",
  "args": {"query": "jennifer walsh CFO"},
  "user": "j.chavez@bain.com"
}' | jq
```

Expected: `decision: ALLOW`, `rule: R999.default-allow`.

Try a DENY:

```
curl -s localhost:8080/decide -X POST -H 'Content-Type: application/json' -d '{
  "source_agent": "urn:agent:projects-254356041555:...",
  "target_service": "urn:mcp:projects-254356041555:...:mcpServers:agentregistry-00000000-0000-0000-5e80-1137c09a51d0",
  "tool": "search_and_fetch_top",
  "args": {"query": "extract strike price from 02_Restricted_Privileged_DLP_Audit_Target_HoldCo.docx"}
}' | jq
```

Expected: `decision: DENY`, `rule: R010.mnpi-dlp-shield`.

## Cloud Run deploy

```
gcloud run deploy bain-ge-policy-svc \
  --source . \
  --region us-central1 \
  --project vtxdemos \
  --allow-unauthenticated \
  --memory 512Mi \
  --concurrency 80 \
  --max-instances 4
```

(See `../scripts/deploy_policy_svc.sh`.)

## Endpoints

- `GET  /healthz` — liveness
- `GET  /rules`   — JSON description of the active ruleset (UI policy card)
- `POST /decide`  — make a policy decision; logs to stdout for Cloud Logging

## Cloud Logging filter

```
resource.type="cloud_run_revision"
resource.labels.service_name="bain-ge-policy-svc"
jsonPayload.component="agent-gateway-policy"
```

Restrict to denies:

```
... AND jsonPayload.policy_decision="DENY"
```

The `gateway-logs-svc` sibling service wraps this filter and streams entries
to the UI's gateway log panel.

## Why HTTP, not gRPC ext_authz?

Agent Gateway's production wire is gRPC `ext_authz v3` over an Internal
Application LB fronting a Serverless NEG. That bootstrap (proxy-only subnet,
LB, NEG, `networkservices.authzExtensions`, `networksecurity.authzPolicies`)
is documented in `../PRODUCTION_GATEWAY_WIRING.md`. The policy module
(`policy.py`) is identical between paths — same rules, same logging — so
flipping to the full gateway routing is a deploy concern, not a policy
rewrite.

For the demo, the agent calls `/decide` directly from each tool. Customers
see real GCP policy decisions and real Cloud Logging entries with rule IDs,
which is what the previous simulator was faking.
