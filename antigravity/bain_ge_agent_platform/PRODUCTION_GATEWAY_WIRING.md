# Production Agent Gateway Wiring

The demo path (in this repo's default state) has every tool call route through
the **`bain-ge-policy-svc`** HTTPS endpoint for an ALLOW/DENY decision. That
path proves the policy logic end-to-end with real Cloud Logging, but the
network traffic doesn't physically pass through the Agent Gateway resource —
it talks to the policy service directly.

This document is the **production wiring playbook**: it turns the same policy
module (`policy-decision-svc/policy.py`) into a real
`networkservices.googleapis.com / agentGateways` enforcement point, so every
MCP / outbound HTTP call the agent makes is intercepted at the network layer
by the gateway, evaluated by the policy service over Envoy
**`ext_authz v3` gRPC**, and either passed or 403'd.

The customer can flip to this path without rewriting any policy code — the
rule set is identical between the demo and the production wires.

---

## What's already in `vtxdemos`

```bash
gcloud auth print-access-token | xargs -I{} \
  curl -s -H "Authorization: Bearer {}" \
  https://networkservices.googleapis.com/v1/projects/vtxdemos/locations/us-central1/agentGateways
```

Three gateways exist today:

| Name | Mode | Notes |
|---|---|---|
| `reasoning-engine-gateway` | `AGENT_TO_ANYWHERE` | Egress; created 2026-06-24 for the bain agent fleet. **Use this one.** |
| `agent-gateway` | `CLIENT_TO_AGENT` | Ingress; demo only. |
| `my-agent-gateway` | `AGENT_TO_ANYWHERE` | Older / spare. |

```
projects/vtxdemos/locations/us-central1/agentGateways/reasoning-engine-gateway
mtlsEndpoint: projects/f4648b24f2a73ac1ap-tp/regions/us-central1/serviceAttachments/unitkind1-swp-mtls-psc-sa
registries:  //agentregistry.googleapis.com/projects/254356041555/locations/us-central1
protocols:   MCP
```

It has zero `authzPolicies` attached — that's why nothing showed up in Cloud
Logging until now. The steps below attach a real policy.

---

## Step 1 — Build the gRPC `ext_authz v3` service

The `policy-decision-svc/` directory in this repo already ships the
HTTP `/decide` endpoint. Add the gRPC variant alongside it (single image,
shared `policy.py`):

```python
# policy-decision-svc/grpc_server.py
import grpc, json, logging, os
from concurrent import futures
from envoy.service.auth.v3 import external_auth_pb2 as ea
from envoy.service.auth.v3 import external_auth_pb2_grpc as eag
from google.rpc import status_pb2, code_pb2

from policy import evaluate

log = logging.getLogger("authz-grpc")

class Authz(eag.AuthorizationServicer):
    def Check(self, req: ea.CheckRequest, ctx) -> ea.CheckResponse:
        http = req.attributes.request.http
        spiffe = req.attributes.source.principal
        # Translate Envoy's call shape into the policy module's call shape
        v = evaluate(
            source_agent=spiffe,
            target_service=http.host,             # gateway routes by host
            tool=http.headers.get("x-bain-tool", "<unknown>"),
            args={"path": http.path, "method": http.method},
            headers=dict(http.headers),
        )
        log.info(json.dumps({
            "component": "agent-gateway-policy",   # share filter with HTTP path
            "policy_decision": v.decision,
            "rule": v.rule, "reason": v.reason,
            "source_agent": spiffe, "tool": http.headers.get("x-bain-tool"),
            "target_service": http.host, "path": http.path,
        }))
        if v.decision == "ALLOW":
            return ea.CheckResponse(status=status_pb2.Status(code=code_pb2.OK))
        return ea.CheckResponse(
            status=status_pb2.Status(code=code_pb2.PERMISSION_DENIED, message=v.reason),
            denied_response=ea.DeniedHttpResponse(
                status=ea.HttpStatus(code=ea.Forbidden),
                body=json.dumps({"rule": v.rule, "reason": v.reason}),
            ),
        )

def serve():
    s = grpc.server(futures.ThreadPoolExecutor(max_workers=16))
    eag.add_AuthorizationServicer_to_server(Authz(), s)
    s.add_insecure_port(f"[::]:{os.environ.get('PORT','8080')}")  # Cloud Run terminates TLS
    s.start(); s.wait_for_termination()

if __name__ == "__main__":
    serve()
```

`requirements.txt` additions:

```
grpcio==1.66.1
grpcio-tools==1.66.1
envoy-data-plane-api  # vendored / or build envoy protos in the Dockerfile
googleapis-common-protos
```

Deploy as a separate Cloud Run service that exposes gRPC on `$PORT` with HTTP/2:

```bash
gcloud run deploy bain-ge-policy-grpc \
  --source policy-decision-svc/ \
  --region us-central1 \
  --project vtxdemos \
  --use-http2 \
  --no-cpu-throttling \
  --allow-unauthenticated \
  --command "python" --args "grpc_server.py"
```

---

## Step 2 — Front it with an Internal Application LB

Agent Gateway can only call `service-extensions.googleapis.com` extensions
that target a backend service on an Internal Application LB (scheme
`INTERNAL_MANAGED`). Bootstrap:

```bash
# 1. Proxy-only subnet
gcloud compute networks subnets create proxy-only-us-central1 \
  --project=vtxdemos --region=us-central1 \
  --purpose=REGIONAL_MANAGED_PROXY --role=ACTIVE \
  --network=default --range=10.129.0.0/23

# 2. Serverless NEG → Cloud Run
gcloud compute network-endpoint-groups create bain-policy-grpc-neg \
  --project=vtxdemos --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=bain-ge-policy-grpc

# 3. Backend service (HTTP/2)
gcloud compute backend-services create bain-policy-grpc-bs \
  --project=vtxdemos --region=us-central1 \
  --load-balancing-scheme=INTERNAL_MANAGED \
  --protocol=HTTP2

gcloud compute backend-services add-backend bain-policy-grpc-bs \
  --project=vtxdemos --region=us-central1 \
  --network-endpoint-group=bain-policy-grpc-neg \
  --network-endpoint-group-region=us-central1

# 4. URL map + target proxy + forwarding rule (standard ILB plumbing)
gcloud compute url-maps create bain-policy-grpc-um \
  --project=vtxdemos --region=us-central1 \
  --default-service=bain-policy-grpc-bs

gcloud compute target-https-proxies create bain-policy-grpc-tp \
  --project=vtxdemos --region=us-central1 \
  --url-map=bain-policy-grpc-um \
  --ssl-certificates=<your-managed-cert>

gcloud compute forwarding-rules create bain-policy-grpc-fr \
  --project=vtxdemos --region=us-central1 \
  --load-balancing-scheme=INTERNAL_MANAGED \
  --network=default \
  --subnet=default \
  --address=<reserved-internal-ip> \
  --ports=443 \
  --target-https-proxy=bain-policy-grpc-tp \
  --target-https-proxy-region=us-central1
```

---

## Step 3 — Register the `authzExtension`

```yaml
# authz-extension.yaml
name: bain-ge-policy-extension
service: projects/vtxdemos/regions/us-central1/backendServices/bain-policy-grpc-bs
wireFormat: EXT_AUTHZ_GRPC
failOpen: false
timeout: 1s
authority: bain-policy-grpc.internal
forwardHeaders:
  - x-bain-tool
  - x-bain-user
  - x-bain-dlp-acknowledged
```

```bash
gcloud beta service-extensions authz-extensions import bain-ge-policy-extension \
  --project=vtxdemos --location=us-central1 \
  --source=authz-extension.yaml
```

---

## Step 4 — Attach an `authzPolicy` to the Agent Gateway

```yaml
# authz-policy.yaml
name: bain-ge-gateway-policy
target:
  resources:
    - projects/vtxdemos/locations/us-central1/agentGateways/reasoning-engine-gateway
policyProfile: REQUEST_AUTHZ
action: CUSTOM
customProvider:
  authzExtension:
    resources:
      - projects/vtxdemos/locations/us-central1/authzExtensions/bain-ge-policy-extension
```

```bash
gcloud beta network-security authz-policies import bain-ge-gateway-policy \
  --project=vtxdemos --location=us-central1 \
  --source=authz-policy.yaml
```

At this point every MCP call the gateway sees is gRPC-checked against the
policy service. ALLOW = pass-through. DENY = 403 with the rule ID and reason
embedded in the response body. All decisions emit the same structured
`agent-gateway-policy` Cloud Logging entries the UI panel renders.

---

## Step 5 — Route Agent Engine egress through the gateway

The Vertex AI Agent Runtime (Agent Engine) needs network config to send its
outbound HTTP through the gateway's PSC `serviceAttachment`. Two options:

**A) PSC consumer endpoint on the same VPC.** Create a forwarding rule in
your VPC that targets `projects/f4648b24f2a73ac1ap-tp/regions/us-central1/serviceAttachments/unitkind1-swp-mtls-psc-sa`,
then deploy the agent with `vpc_access_connector` (Vertex AI's networking
config) so its outbound MCP calls hit the consumer-side IP, present the agent
identity X.509 client cert via mTLS, and land on the gateway.

**B) HTTP forward-proxy mode.** When the gateway is configured with an HTTPS
front-door, the agent's HTTP client can be configured with `HTTPS_PROXY=<gateway-host>`.
The agent identity SPIFFE cert (auto-issued by GCP at deploy time) is sent
as the mTLS client identity.

The `policy_guard.py` HTTP check stays in the code as a **belt-and-braces**
fallback: even if the network route is misconfigured, the agent still calls
the policy service and gets a real ALLOW/DENY before executing.

---

## Step 6 — Agent Registry bindings (default-deny gating)

The Agent Registry `bindings` resource gates which MCP/endpoint targets each
source agent is allowed to call (R000 in `policy.py` mirrors this in-policy).
Create binding via:

```bash
curl -X POST -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://agentregistry.googleapis.com/v1alpha/projects/vtxdemos/locations/us-central1/bindings?bindingId=bain-agent-to-sharepoint-mcp" \
  -d '{
    "displayName": "Bain agent → SharePoint MCP (Entra OAuth)",
    "source": {"identifier": "urn:agent:projects-254356041555:projects:254356041555:locations:us-central1:aiplatform:reasoningEngines:<ENGINE_ID>"},
    "target": {"identifier": "urn:mcp:projects-254356041555:projects:254356041555:locations:us-central1:agentregistry:services:sharepoint-mcp"},
    "authProviderBinding": {
      "authProvider": "projects/vtxdemos/locations/us-central1/connectors/<connector_name>"
    }
  }'
```

> The `authProvider` field requires an Integration Connector resource path
> (`projects/.../locations/.../connectors/<name>`). This resource type is
> currently a preview/private surface — the previously-referenced
> `entra-oauth-sharepoint` and `sharepoint-3lo` names exist as session
> identifiers but are not visible via the `connectors.googleapis.com`
> public API. Coordinate with your Google account team to provision a real
> connector before this binding will succeed.

---

## Verification

After Steps 1-5 are in place, fire a known-DENY query against the agent
("extract strike price from 02_Restricted_Privileged_DLP_Audit_Target_HoldCo.docx")
and inspect:

```bash
# Cloud Logging: real gateway ext_authz decisions
gcloud logging read '
  resource.type="cloud_run_revision" AND
  resource.labels.service_name="bain-ge-policy-grpc" AND
  jsonPayload.component="agent-gateway-policy" AND
  jsonPayload.policy_decision="DENY"
' --project=vtxdemos --limit=5

# Network-level audit: agentGateway request log
gcloud logging read '
  resource.type="networkservices.googleapis.com/AgentGateway" AND
  resource.labels.location="us-central1" AND
  resource.labels.gateway_name="reasoning-engine-gateway"
' --project=vtxdemos --limit=5
```

Both queries should return entries for the same correlation ID.
