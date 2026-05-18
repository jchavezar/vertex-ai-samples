# agent-gateway-handson

**A console-first walkthrough that builds the public `agent-gateway` demo by hand — no Terraform, no helper scripts.** Every step is either a Cloud Console click path or a single `gcloud`/`curl` command. The only "magic" is the one-time IAP IAM binding, which we do with raw `curl` so you can see exactly what the docs are asking for.

## Who this is for

You have **Owner on a GCP project** (so we can skip the granular IAM that the upstream demo's Terraform sets up) and you want to *understand* the Agent Gateway path well enough to debug it. You will deploy:

- one **MCP server** (FastMCP on Cloud Run, internal-LB ingress)
- one **Agent Gateway** with two authz extensions (IAP + Model Armor)
- one **ADK agent** deployed to Vertex AI Agent Runtime
- one entry in **Agent Registry**, with an IAP IAM binding that gates which agent can call which tool

That's the smallest set that proves the governance path. Adding more MCP servers is just repeating step 6 with different names.

## What you'll have at the end

```
You (browser)
  └── Vertex AI Agent Runtime (your ADK agent)
         └── Agent Gateway  ──► IAP authz ext       (REQUEST_AUTHZ: identity)
                            └─► Model Armor authz   (CONTENT_AUTHZ: content)
                            └─► PSC interface → your VPC
                                    └─► Internal ALB (URL-mask SNEG)
                                            └─► Cloud Run MCP server (/mcp)
```

If anything in that diagram is unfamiliar, open `/home/admin_jesusarguelles_altostrat_c/code/agent-gateway-manual.html` — every box has a deep-dive with raw payloads and an "Ask Gemini" button.

## A note on "MCP"

Throughout this guide **MCP = Model Context Protocol** (the open spec for tool-calling between agents and tool servers). The `mcp-*` prefix on resource names just means "this resource is part of an MCP server's plumbing" — it isn't a Google product called "MCP".

---

## 0. Environment

Pick a project and stick the env vars in your shell. Every command below references these.

```bash
# Use any project where you have Owner. Examples on this machine:
#   cloud-llm-preview1   (works with current ADC identity)
#   vtxdemos             (works with your gcloud auth account)
export PROJECT_ID="cloud-llm-preview1"
export PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
export ORG_ID="$(gcloud projects describe "$PROJECT_ID" --format='value(parent.id)')"
export REGION="us-central1"
export NAME="agw"                                # short prefix for resource names
export MCP_DOMAIN="mcp.internal.example.com"     # private domain for MCP services
export MCP_ZONE_NAME="mcp-internal"

gcloud config set project "$PROJECT_ID"
gcloud config set compute/region "$REGION"
```

> **Why a domain you don't own?** This is for the *private* DNS zone, resolvable only inside your VPC. Nothing leaves your network. You can pick `mcp.example.test` or any string; the Cloud Run url_mask just splits on the first dot.

---

## 1. Enable the APIs

**Console:** APIs & Services → Library → enable each, OR run this once:

```bash
gcloud services enable \
  compute.googleapis.com \
  servicenetworking.googleapis.com \
  networkservices.googleapis.com \
  networksecurity.googleapis.com \
  certificatemanager.googleapis.com \
  dns.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  iap.googleapis.com \
  agentregistry.googleapis.com \
  modelarmor.googleapis.com \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com \
  cloudtrace.googleapis.com
```

Verify (Console): **APIs & Services → Enabled APIs & services** should list all of them.

---

## 2. VPC + subnets

The gateway needs to land traffic somewhere private. You need four subnets in one region: primary (workloads), proxy-only (Envoy for the internal ALB), LB (forwarding-rule VIP), and PSC interface (network attachment).

**Console:** VPC network → VPC networks → **Create VPC network**, name `agw-vpc`, mode `custom`, then add four subnets in `us-central1` with the CIDRs below.

**gcloud:**

```bash
gcloud compute networks create "${NAME}-vpc" --subnet-mode=custom

# primary — workloads / future use
gcloud compute networks subnets create "${NAME}-primary" \
  --network="${NAME}-vpc" --region="$REGION" --range="10.10.0.0/24"

# proxy-only — REQUIRED for any regional internal ALB in this region
gcloud compute networks subnets create "${NAME}-proxy" \
  --network="${NAME}-vpc" --region="$REGION" --range="10.10.1.0/24" \
  --purpose=REGIONAL_MANAGED_PROXY --role=ACTIVE

# LB subnet — where the LB's forwarding rule VIP lives
gcloud compute networks subnets create "${NAME}-lb" \
  --network="${NAME}-vpc" --region="$REGION" --range="10.10.2.0/24"

# PSC interface subnet — consumed by the network attachment
gcloud compute networks subnets create "${NAME}-psc-i" \
  --network="${NAME}-vpc" --region="$REGION" --range="10.10.3.0/24" \
  --purpose=PRIVATE
```

**Verify:** Console → VPC network → Subnets → filter by network `agw-vpc` should show four rows.

---

## 3. Cloud NAT (so Cloud Build and any future VPC workloads have egress)

**Console:** Network services → Cloud NAT → **Get started** → name `agw-nat`, router `agw-router`, network `agw-vpc`, region `us-central1`, NAT mapping = all subnets.

**gcloud:**

```bash
gcloud compute routers create "${NAME}-router" --network="${NAME}-vpc" --region="$REGION"
gcloud compute routers nats create "${NAME}-nat" \
  --router="${NAME}-router" --region="$REGION" \
  --nat-all-subnet-ip-ranges --auto-allocate-nat-external-ips
```

---

## 4. Artifact Registry

One Docker repo for the MCP image we'll build next.

**Console:** Artifact Registry → **Create repository** → name `gateway-docker`, format Docker, region `us-central1`.

**gcloud:**

```bash
gcloud artifacts repositories create "gateway-docker" \
  --location="$REGION" --repository-format=docker
```

---

## 5. Build + push the MCP server image

The `mcp_server/` folder in this directory has a minimal FastMCP service with one tool (`lookup_document`). Build and push it.

```bash
cd mcp_server
gcloud builds submit \
  --tag="${REGION}-docker.pkg.dev/${PROJECT_ID}/gateway-docker/legacy-dms:v1"
cd ..
```

**Verify (Console):** Artifact Registry → `gateway-docker` → `legacy-dms` should show one `v1` tag.

---

## 6. Deploy the MCP service to Cloud Run (internal LB ingress)

The ingress mode is the key flag — `internal-and-cloud-load-balancing` means only requests from inside the VPC (or via an internal LB) reach the service.

**Console:** Cloud Run → **Deploy container** → Service → Image URL = `us-central1-docker.pkg.dev/{PROJECT}/gateway-docker/legacy-dms:v1` → region `us-central1` → Ingress = **Internal + Cloud Load Balancing** → CPU allocation: only during request processing, min 1 → Variables: `GOOGLE_CLOUD_PROJECT=$PROJECT_ID`, `OTEL_SERVICE_NAME=legacy-dms`.

**gcloud:**

```bash
gcloud run deploy "legacy-dms" \
  --region="$REGION" \
  --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/gateway-docker/legacy-dms:v1" \
  --ingress=internal-and-cloud-load-balancing \
  --port=8080 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},OTEL_SERVICE_NAME=legacy-dms" \
  --min-instances=1 --max-instances=3 \
  --cpu=1 --memory=512Mi --concurrency=80 --timeout=300 \
  --no-allow-unauthenticated
```

**Verify:** Console → Cloud Run → `legacy-dms` → **YAML** tab → `metadata.annotations.run.googleapis.com/ingress: internal-and-cloud-load-balancing` and `spec.template.spec.containerConcurrency: 80`.

> Because you're Owner, you implicitly hold `roles/run.invoker` on every service you create. The upstream demo creates a dedicated `agent-mcp-invoker` SA and grants it `run.invoker`; we'll let the Vertex AI default agent identity invoke directly instead, which works because of the Owner umbrella.

---

## 7. Reserve the LB VIP + private DNS

The agent will call `https://legacy-dms.mcp.internal.example.com/mcp` from inside the VPC. That hostname has to resolve to a private IP we own.

```bash
# 7a. Reserve a static internal IP in the LB subnet
gcloud compute addresses create "${NAME}-lb-vip" \
  --region="$REGION" --subnet="${NAME}-lb" --purpose=GCE_ENDPOINT

export LB_VIP="$(gcloud compute addresses describe "${NAME}-lb-vip" \
  --region="$REGION" --format='value(address)')"
echo "LB_VIP=$LB_VIP"

# 7b. Private DNS zone, visible only to our VPC
gcloud dns managed-zones create "$MCP_ZONE_NAME" \
  --dns-name="${MCP_DOMAIN}." --visibility=private \
  --networks="${NAME}-vpc" --description="MCP private zone"

# 7c. Point legacy-dms.<MCP_DOMAIN> at the LB VIP
gcloud dns record-sets create "legacy-dms.${MCP_DOMAIN}." \
  --zone="$MCP_ZONE_NAME" --type=A --ttl=60 --rrdatas="$LB_VIP"
```

**Console verify:** Network services → Cloud DNS → `mcp-internal` → should show one `A` record `legacy-dms.mcp.internal.example.com.` pointing at `$LB_VIP`.

---

## 8. Certificate for the internal LB

The internal ALB terminates HTTPS. For a hands-on walkthrough we'll use a **self-signed cert** for `*.mcp.internal.example.com` — Cloud Run accepts the upstream connection regardless, and the agent doesn't validate the leaf since it talks to the gateway, not the LB. (In prod you'd use Certificate Manager with Google-managed certs.)

```bash
# 8a. Generate a self-signed wildcard cert (one-liner)
openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
  -keyout /tmp/agw-key.pem -out /tmp/agw-cert.pem \
  -subj "/CN=*.${MCP_DOMAIN}" \
  -addext "subjectAltName=DNS:*.${MCP_DOMAIN}"

# 8b. Upload to Certificate Manager (regional)
gcloud certificate-manager certificates create "${NAME}-mcp-cert" \
  --location="$REGION" \
  --certificate-file=/tmp/agw-cert.pem \
  --private-key-file=/tmp/agw-key.pem
```

**Console verify:** Security → Certificate Manager → Certificates → `agw-mcp-cert` → State = ACTIVE.

---

## 9. Internal ALB — SNEG → backend → URL map → target proxy → forwarding rule

This is the part with the most moving pieces. The trick is the `url_mask`: one Serverless NEG dispatches by Host header to the matching Cloud Run service.

```bash
# 9a. Serverless NEG with url_mask
gcloud compute network-endpoint-groups create "${NAME}-mcp-sneg" \
  --region="$REGION" --network-endpoint-type=SERVERLESS \
  --cloud-run-url-mask="<service>.${MCP_DOMAIN}"

# 9b. Backend service
gcloud compute backend-services create "${NAME}-mcp-bes" \
  --region="$REGION" \
  --load-balancing-scheme=INTERNAL_MANAGED --protocol=HTTPS
gcloud compute backend-services add-backend "${NAME}-mcp-bes" \
  --region="$REGION" \
  --network-endpoint-group="${NAME}-mcp-sneg" \
  --network-endpoint-group-region="$REGION"

# 9c. URL map (default everything to the SNEG)
gcloud compute url-maps create "${NAME}-mcp-url" \
  --region="$REGION" --default-service="${NAME}-mcp-bes"

# 9d. Target HTTPS proxy
gcloud compute target-https-proxies create "${NAME}-mcp-tp" \
  --region="$REGION" --url-map="${NAME}-mcp-url" \
  --certificate-manager-certificates="${NAME}-mcp-cert"

# 9e. Forwarding rule on the reserved VIP
gcloud compute forwarding-rules create "${NAME}-mcp-fr" \
  --region="$REGION" \
  --load-balancing-scheme=INTERNAL_MANAGED \
  --network="${NAME}-vpc" --subnet="${NAME}-lb" \
  --address="$LB_VIP" --ports=443 \
  --target-https-proxy-region="$REGION" \
  --target-https-proxy="${NAME}-mcp-tp"
```

**Console verify:** Network services → Load balancing → `agw-mcp-url` should appear as a regional INTERNAL_MANAGED https LB with one backend service and one frontend on `$LB_VIP:443`.

---

## 10. Firewall — let the PSC interfaces talk to the LB

```bash
gcloud compute firewall-rules create "${NAME}-allow-psc-i" \
  --network="${NAME}-vpc" \
  --direction=INGRESS --priority=1000 \
  --source-ranges="10.10.3.0/24" \
  --action=ALLOW --rules=tcp:443
```

---

## 11. Network attachment (the door the Agent Gateway will egress through)

The gateway is Google-managed; this network attachment is what gives Google permission to place a PSC interface inside *your* VPC, drawing IPs from the PSC-I subnet you made in step 2.

```bash
gcloud compute network-attachments create "${NAME}-na" \
  --region="$REGION" \
  --subnets="${NAME}-psc-i" \
  --connection-preference=ACCEPT_AUTOMATIC

export NA_URI="projects/${PROJECT_ID}/regions/${REGION}/networkAttachments/${NAME}-na"
echo "NA_URI=$NA_URI"
```

**Console verify:** VPC network → **Private Service Connect** → **Network Attachments** → row `agw-na` → Connection preference `Accept automatic`.

---

## 12. Register the MCP server in Agent Registry

The Agent Registry is the catalog the agent uses to discover tool URLs. Each registered `mcpServer` resource is also what IAP binds IAM policies against in step 16. There's no gcloud surface yet, so use `curl`:

```bash
TOKEN="$(gcloud auth print-access-token)"

curl -sS -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://agentregistry.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/${REGION}/mcpServers" \
  -d "{
    \"displayName\": \"MCP - legacy-dms\",
    \"uri\": \"https://legacy-dms.${MCP_DOMAIN}/mcp\",
    \"attributes\": {
      \"agentregistry.googleapis.com/system/RuntimeReference\": {
        \"uri\": \"//run.googleapis.com/projects/${PROJECT_ID}/locations/${REGION}/services/legacy-dms\"
      }
    }
  }"
```

The response includes a `name` like `projects/.../locations/.../mcpServers/agentregistry-00000000-0000-0000-3626-...`. **Capture the trailing ID** — you'll need it in step 16:

```bash
export MCP_SERVER_ID="$(curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://agentregistry.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/${REGION}/mcpServers" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(next(s['name'].split('/')[-1] for s in d['mcpServers'] if s['displayName']=='MCP - legacy-dms'))")"
echo "MCP_SERVER_ID=$MCP_SERVER_ID"
```

> **Why /mcp at the end of the URI?** FastMCP mounts the protocol endpoint at `/mcp` by default. Cloud Run 404s on every other path including `/`, so the URI you register *must* include `/mcp` or the agent's first tool call will fail with a 404 the gateway won't be able to fix.

---

## 13. Model Armor templates (request + response)

Two templates: one screens the request payload (prompt + tool args) before forwarding; the other screens the response coming back.

**Console:** Security → Model Armor → **Create template**. Make two: `ma-req` and `ma-resp`. Enable the filters you want — at minimum RAI categories + PI/jailbreak detection.

**gcloud:**

```bash
gcloud model-armor templates create "ma-req" \
  --location="$REGION" \
  --rai-filters="harassment=high,sexually_explicit=high,dangerous=high,hate_speech=high" \
  --pi-jailbreak-filter-enforcement=ENFORCEMENT \
  --malicious-uri-filter-enforcement=ENFORCEMENT

gcloud model-armor templates create "ma-resp" \
  --location="$REGION" \
  --rai-filters="harassment=high,sexually_explicit=high,dangerous=high,hate_speech=high" \
  --malicious-uri-filter-enforcement=ENFORCEMENT
```

---

## 14. Authz extensions — IAP and Model Armor

These are the two interceptors the Agent Gateway will call on every request. Each is just a pointer to a Google service plus some metadata.

```bash
# 14a. IAP — identity / per-tool authz
gcloud beta network-services authz-extensions create "${NAME}-iap-authz" \
  --location="$REGION" \
  --service="iap.googleapis.com" \
  --timeout=1s \
  --metadata='{"iamEnforcementMode":"ENFORCED"}'

# 14b. Model Armor — content screening
gcloud beta network-services authz-extensions create "${NAME}-ma-authz" \
  --location="$REGION" \
  --service="modelarmor.${REGION}.rep.googleapis.com" \
  --timeout=1s \
  --metadata="{\"model_armor_settings\":\"[{\\\"request_template_id\\\":\\\"projects/${PROJECT_ID}/locations/${REGION}/templates/ma-req\\\",\\\"response_template_id\\\":\\\"projects/${PROJECT_ID}/locations/${REGION}/templates/ma-resp\\\"}]\"}"
```

---

## 15. Create the Agent Gateway

This is the resource everything else is leading up to. Note the four fields that matter:

- `protocols=MCP` — what L7 protocol the gateway speaks (MCP framing over HTTP/2)
- `governed-access-path=AGENT_TO_ANYWHERE` — the gateway can forward to any registered destination, but only registered ones
- `registries` — a *prefix* (project + region), not a list of resources. Membership in this registry is what makes a destination eligible
- `network-attachment` — the door from step 11

```bash
gcloud beta network-services agent-gateways create "$NAME" \
  --location="$REGION" \
  --protocols=MCP \
  --governed-access-path=AGENT_TO_ANYWHERE \
  --registries="projects/${PROJECT_ID}/locations/${REGION}" \
  --network-attachment="$NA_URI"

# Wait ~30s for the resource to settle before binding policies
sleep 30
gcloud beta network-services agent-gateways describe "$NAME" --location="$REGION"
```

**Now bind both authz policies to it:**

```bash
# 15a. IAP — REQUEST_AUTHZ
gcloud beta network-security authz-policies create "${NAME}-iap-policy" \
  --location="$REGION" \
  --policy-profile=REQUEST_AUTHZ --action=CUSTOM \
  --target-resources="projects/${PROJECT_ID}/locations/${REGION}/agentGateways/${NAME}" \
  --custom-provider-authz-extension-resources="projects/${PROJECT_ID}/locations/${REGION}/authzExtensions/${NAME}-iap-authz"

# 15b. Model Armor — CONTENT_AUTHZ
gcloud beta network-security authz-policies create "${NAME}-ma-policy" \
  --location="$REGION" \
  --policy-profile=CONTENT_AUTHZ --action=CUSTOM \
  --target-resources="projects/${PROJECT_ID}/locations/${REGION}/agentGateways/${NAME}" \
  --custom-provider-authz-extension-resources="projects/${PROJECT_ID}/locations/${REGION}/authzExtensions/${NAME}-ma-authz"
```

**Console verify:** Network services → Service Extensions → Authorization policies → both `agw-iap-policy` and `agw-ma-policy` should be ACTIVE and target the `agw` gateway.

---

## 16. Deploy the ADK agent as a Reasoning Engine

This is where you go from infrastructure to behavior. The `agent/` folder in this directory has a minimal ADK agent that:

- discovers MCP tools by calling `AgentRegistry.list_mcp_servers()`
- creates an `MCPToolset` for each, with the URL coming from the registry (which is what makes the call go through the gateway)

```bash
cd agent
uv venv && source .venv/bin/activate
uv pip install "google-cloud-aiplatform[agent_engines]" google-adk httpx

python3 deploy.py
# → prints: resource_name = projects/123.../locations/.../reasoningEngines/9876543210
cd ..
```

**Capture the ID** — the trailing number from `resource_name`:

```bash
export REASONING_ENGINE_NAME="projects/${PROJECT_NUMBER}/locations/${REGION}/reasoningEngines/<paste-id>"
export AGENT_ID="$(basename "$REASONING_ENGINE_NAME")"
echo "AGENT_ID=$AGENT_ID"
```

---

## 17. The one IAM binding everything hinges on — `roles/iap.egressor`

Without this, the agent's first tool call returns 403 at the gateway (and the agent sees it as a tool error). It binds the reasoning engine's principal to `roles/iap.egressor` on the **specific Agent Registry resource** the agent will call.

The catch: `gcloud beta iap web add-iam-policy-binding --mcpServer=…` doesn't exist yet, so the upstream demo wraps the REST call in `scripts/grant_agent_mcp_egress.sh`. Here we do it inline so you see exactly what the script does — three steps: GET policy → merge → SET policy.

```bash
TOKEN="$(gcloud auth print-access-token)"
AGENT_PRINCIPAL="principal://agents.global.org-${ORG_ID}.system.id.goog/resources/aiplatform/projects/${PROJECT_NUMBER}/locations/${REGION}/reasoningEngines/${AGENT_ID}"
IAP_URL="https://iap.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/iap_web/agentRegistry/mcpServers/${MCP_SERVER_ID}"

# 17a. GET current policy (at version 3 so conditional bindings round-trip)
curl -sS -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"options":{"requestedPolicyVersion":3}}' \
  "${IAP_URL}:getIamPolicy" > /tmp/iap-current.json
cat /tmp/iap-current.json

# 17b. SET the merged policy (here we assume the resource is empty — if you've
#      bound things before, merge into the existing bindings array instead)
ETAG="$(jq -r '.etag // ""' /tmp/iap-current.json)"
cat > /tmp/iap-new.json <<EOF
{
  "policy": {
    "version": 3,
    "etag": "${ETAG}",
    "bindings": [
      {
        "role": "roles/iap.egressor",
        "members": ["${AGENT_PRINCIPAL}"]
      }
    ]
  }
}
EOF

curl -sS -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/iap-new.json \
  "${IAP_URL}:setIamPolicy"
```

> **What this does, in plain English.** When the agent calls the gateway with a request targeting `mcpServers/${MCP_SERVER_ID}`, the gateway calls IAP. IAP looks up the IAM policy on that *exact* registry resource. The principal you just bound (the reasoning engine, by numeric ID) holds `roles/iap.egressor`, so IAP returns allow. Without this binding → deny → 403 to the agent.

**Tighten with a condition (optional but instructive).** Re-run 17b but add a CEL condition that only allows the agent to call read-only tools:

```json
{
  "policy": {
    "version": 3,
    "bindings": [{
      "role": "roles/iap.egressor",
      "members": ["${AGENT_PRINCIPAL}"],
      "condition": {
        "title": "read-only tools",
        "expression": "api.getAttribute('iap.googleapis.com/mcp.tool.isReadOnly', false) == true"
      }
    }]
  }
}
```

---

## 18. Smoke test

```bash
# Inspect from the Agent Runtime side
gcloud beta ai reasoning-engines list --region="$REGION"

# Drive the agent (uses the SDK locally; it routes through the same gateway)
cd agent
python3 chat.py "List the documents available"
cd ..
```

If you see:
- a tool-use trace in stdout
- the tool returns a result (the stub `lookup_document` returns mock data)
- **no 403** at the gateway

…the path works end-to-end.

**To verify governance is actually engaged**, do this and re-run:

```bash
# Temporarily remove the binding — agent should start failing
curl -sS -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"policy":{"version":3,"bindings":[]}}' \
  "${IAP_URL}:setIamPolicy"

python3 agent/chat.py "List the documents available"
# → expect: tool call returns 403, agent reports an authorization error
```

Put the binding back when you're done.

---

## 19. Observability

Every hop emits a span:

- **Cloud Trace** — Console → Trace → Trace explorer. Filter by service `legacy-dms`. The span tree shows: agent → gateway → IAP → Model Armor → Cloud Run.
- **Cloud Logging** — `resource.type="agent_gateway" OR resource.type="cloud_run_revision"`. The gateway emits a structured log per request with the IAP and Model Armor verdicts.

---

## 20. Tear down

Reverse order — gateway and policies first, then plumbing.

```bash
# 20a. Authz + gateway
gcloud beta network-security authz-policies delete "${NAME}-iap-policy" --location="$REGION" -q
gcloud beta network-security authz-policies delete "${NAME}-ma-policy"  --location="$REGION" -q
gcloud beta network-services authz-extensions delete "${NAME}-iap-authz" --location="$REGION" -q
gcloud beta network-services authz-extensions delete "${NAME}-ma-authz"  --location="$REGION" -q
gcloud beta network-services agent-gateways delete "$NAME" --location="$REGION" -q

# 20b. Reasoning engine
gcloud beta ai reasoning-engines delete "$AGENT_ID" --region="$REGION" -q

# 20c. Internal LB
gcloud compute forwarding-rules delete "${NAME}-mcp-fr"      --region="$REGION" -q
gcloud compute target-https-proxies delete "${NAME}-mcp-tp"  --region="$REGION" -q
gcloud compute url-maps delete             "${NAME}-mcp-url" --region="$REGION" -q
gcloud compute backend-services delete     "${NAME}-mcp-bes" --region="$REGION" -q
gcloud compute network-endpoint-groups delete "${NAME}-mcp-sneg" --region="$REGION" -q
gcloud compute addresses delete             "${NAME}-lb-vip" --region="$REGION" -q

# 20d. Network attachment, firewall, NAT, subnets, VPC
gcloud compute network-attachments delete   "${NAME}-na"     --region="$REGION" -q
gcloud compute firewall-rules delete        "${NAME}-allow-psc-i" -q
gcloud compute routers nats delete          "${NAME}-nat" --router="${NAME}-router" --region="$REGION" -q
gcloud compute routers delete               "${NAME}-router" --region="$REGION" -q
for sn in "${NAME}-psc-i" "${NAME}-lb" "${NAME}-proxy" "${NAME}-primary"; do
  gcloud compute networks subnets delete "$sn" --region="$REGION" -q
done
gcloud compute networks delete "${NAME}-vpc" -q

# 20e. Cloud Run + Artifact Registry + DNS
gcloud run services delete "legacy-dms" --region="$REGION" -q
gcloud artifacts repositories delete "gateway-docker" --location="$REGION" -q
gcloud dns record-sets delete "legacy-dms.${MCP_DOMAIN}." --zone="$MCP_ZONE_NAME" --type=A -q
gcloud dns managed-zones delete "$MCP_ZONE_NAME" -q

# 20f. Model Armor + cert
gcloud model-armor templates delete "ma-req"  --location="$REGION" -q
gcloud model-armor templates delete "ma-resp" --location="$REGION" -q
gcloud certificate-manager certificates delete "${NAME}-mcp-cert" --location="$REGION" -q

# 20g. Agent Registry resource (must be done after the agent that referenced it is gone)
curl -sS -X DELETE -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://agentregistry.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/${REGION}/mcpServers/${MCP_SERVER_ID}"
```

---

## Troubleshooting cheatsheet

| Symptom | Likely cause | Fix |
|---|---|---|
| Agent reports tool error with 403 | Missing `roles/iap.egressor` binding on the MCP server registry resource | Re-run step 17, double-check `AGENT_ID` matches the current reasoning engine |
| Agent reports tool error with 404 | Agent registry URI doesn't end in `/mcp` | Update the registered URI to include `/mcp` |
| Gateway create fails | Bound registry doesn't exist OR network attachment in wrong region | Both must be in `$REGION` |
| LB health check fails | Cloud Run service has `INGRESS_TRAFFIC_INTERNAL_ONLY` instead of `INTERNAL_LOAD_BALANCING` | Re-deploy with `--ingress=internal-and-cloud-load-balancing` |
| Cross-cutting "USER_PROJECT_DENIED" on agent calls | ADC quota project not set | Pass `--quota-project` to gcloud or set `X-Goog-User-Project` header in raw REST |
| Model Armor blocks everything | Filter thresholds too tight | Re-create the templates with `=low` thresholds and re-bind |

---

## What's intentionally different from the upstream `agent-gateway` demo

- **One MCP server, not three.** The full demo deploys legacy-dms + corporate-email + income-verification-api. Once you've done one, the others are just copy-paste with renamed resources.
- **No `agent-mcp-invoker` SA.** You're Owner, so the default Vertex AI agent identity has the permissions it needs. In a production setup you'd want the dedicated SA so you can blast-radius per-tool, exactly as the upstream demo's Terraform models.
- **No Gemini Enterprise registration.** The upstream demo finishes by registering the reasoning engine as a Gemini Enterprise app for end-user chat. That's a separate Discovery Engine flow — skip it for this hands-on, or follow the "Gemini Enterprise" component card in `agent-gateway-manual.html`.
- **Self-signed cert on the LB.** Production needs a Google-managed cert via Certificate Manager bound to a public DNS zone you own.
- **No bash script for IAM.** Step 17 here is the literal expansion of what `grant_agent_mcp_egress.sh` does on every iteration.

## Related

- `/home/admin_jesusarguelles_altostrat_c/code/agent-gateway-manual.html` — interactive component reference with deep-dive cards and a chat panel. Open it alongside this guide.
- `../agent-gateway-demo/` — sibling project: same gateway, but wired to Microsoft Graph via per-user 3LO OAuth (Door 2 — see its README).
- Upstream public demo: <https://github.com/GoogleCloudPlatform/cloud-networking-solutions/tree/main/demos/agent-gateway>
