"""
Bain GE — Agent Gateway Policy Decision Service (gRPC ext_authz v3)

Same `policy.py` evaluator as the HTTP /decide path. This server speaks
Envoy `envoy.service.auth.v3.Authorization.Check`, which is what GCP's
`networkservices.googleapis.com/agentGateways` calls via a
`service-extensions.googleapis.com/authzExtensions` resource.

Wire:
  Agent Gateway → authzPolicy → authzExtension → Internal Application LB
    → Serverless NEG → THIS Cloud Run (HTTP/2) → CheckRequest
  → policy.evaluate(...) → CheckResponse (OK ALLOW | PERMISSION_DENIED 403)
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from concurrent import futures

import grpc

# Generated from envoy/service/auth/v3/external_auth.proto (vendored at build).
from envoy.service.auth.v3 import external_auth_pb2 as ea
from envoy.service.auth.v3 import external_auth_pb2_grpc as eag
from envoy.type.v3 import http_status_pb2
from google.rpc import status_pb2, code_pb2

from policy import POLICY_NAME, POLICY_VERSION, evaluate


# ---- Structured JSON logging (Cloud Run captures stdout as Cloud Logging) ----

class JsonStdoutHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            payload = record.msg if isinstance(record.msg, dict) else {"message": record.getMessage()}
            sys.stdout.write(json.dumps(payload, default=str) + "\n")
            sys.stdout.flush()
        except Exception:
            sys.stdout.write(json.dumps({"message": str(record.msg)}) + "\n")
            sys.stdout.flush()


root = logging.getLogger()
root.handlers = [JsonStdoutHandler()]
root.setLevel(logging.INFO)
logger = logging.getLogger("agent-gateway-policy-grpc")


# ---- The ext_authz handler ----

class AuthzServicer(eag.AuthorizationServicer):
    def Check(self, request: ea.CheckRequest, context: grpc.ServicerContext) -> ea.CheckResponse:
        t0 = time.perf_counter()
        attrs = request.attributes
        http = attrs.request.http

        spiffe = attrs.source.principal or "<no-principal>"
        target_host = http.host or "<no-host>"
        path = http.path or "/"
        method = http.method or "UNKNOWN"
        headers = dict(http.headers) if http.headers else {}

        tool = headers.get("x-bain-tool") or _tool_from_path(path)
        target_service = _target_urn(target_host, path)
        source_agent = _spiffe_to_urn(spiffe)
        user_hdr = headers.get("x-bain-user")
        corr = headers.get("x-bain-correlation-id") or str(uuid.uuid4())

        verdict = evaluate(
            source_agent=source_agent,
            target_service=target_service,
            tool=tool,
            args={"path": path, "method": method, "host": target_host},
            headers=headers,
            user=user_hdr,
        )

        latency_ms = (time.perf_counter() - t0) * 1000.0
        log_entry = {
            "severity": "WARNING" if verdict.decision == "DENY" else "INFO",
            "component": "agent-gateway-policy",
            "transport": "grpc-ext-authz-v3",
            "policy": POLICY_NAME,
            "policy_version": POLICY_VERSION,
            "policy_decision": verdict.decision,
            "rule": verdict.rule,
            "reason": verdict.reason,
            "source_principal_spiffe": spiffe,
            "source_agent": source_agent,
            "target_service": target_service,
            "target_host": target_host,
            "tool": tool,
            "user": user_hdr,
            "request_method": method,
            "request_path": path,
            "latency_ms": round(latency_ms, 3),
            "correlation_id": corr,
            "message": (
                f"[GATEWAY-POLICY] {verdict.decision} {method} {target_host}{path} "
                f"by {_short(source_agent)} — {verdict.reason}"
            ),
        }
        logger.info(log_entry)

        if verdict.decision == "ALLOW":
            return ea.CheckResponse(
                status=status_pb2.Status(code=code_pb2.OK),
                ok_response=ea.OkHttpResponse(
                    headers=[
                        ea.HeaderValueOption(
                            header=ea.HeaderValue(key="x-bain-gateway-rule", value=verdict.rule or "?")
                        ),
                        ea.HeaderValueOption(
                            header=ea.HeaderValue(key="x-bain-gateway-correlation-id", value=corr)
                        ),
                    ]
                ),
            )

        body = json.dumps(
            {
                "blocked_by_agent_gateway": True,
                "decision": verdict.decision,
                "rule": verdict.rule,
                "reason": verdict.reason,
                "correlation_id": corr,
            }
        )
        return ea.CheckResponse(
            status=status_pb2.Status(code=code_pb2.PERMISSION_DENIED, message=verdict.reason),
            denied_response=ea.DeniedHttpResponse(
                status=http_status_pb2.HttpStatus(code=http_status_pb2.Forbidden),
                body=body,
                headers=[
                    ea.HeaderValueOption(
                        header=ea.HeaderValue(key="content-type", value="application/json")
                    ),
                    ea.HeaderValueOption(
                        header=ea.HeaderValue(key="x-bain-gateway-rule", value=verdict.rule or "?")
                    ),
                    ea.HeaderValueOption(
                        header=ea.HeaderValue(key="x-bain-gateway-correlation-id", value=corr)
                    ),
                ],
            ),
        )


def _short(s: str) -> str:
    return s.split(":")[-1] if s else "?"


def _tool_from_path(path: str) -> str:
    seg = [p for p in path.split("/") if p]
    return seg[-1] if seg else "<unknown>"


def _target_urn(host: str, path: str) -> str:
    if "agent-gateway-demo-mcp" in host or "ge-custom-sharepoint-mcp" in host:
        return (
            "urn:mcp:projects-254356041555:projects:254356041555:locations:us-central1:"
            "agentregistry:services:sharepoint-mcp"
        )
    return f"urn:endpoint:gateway-egress:{host}{path}"


def _spiffe_to_urn(spiffe: str) -> str:
    """spiffe://agents.global.org-N.system.id.goog/resources/aiplatform/projects/N/locations/L/reasoningEngines/I
    -> urn:agent:projects-254356041555:...:reasoningEngines:I"""
    if not spiffe.startswith("spiffe://"):
        return spiffe
    try:
        path = spiffe.split("/resources/", 1)[1]
        return (
            "urn:agent:projects-254356041555:projects:254356041555:locations:us-central1:"
            f"aiplatform:reasoningEngines:{path.rsplit('/', 1)[-1]}"
        )
    except Exception:
        return spiffe


def serve() -> None:
    port = int(os.environ.get("PORT", "8080"))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=16))
    eag.add_AuthorizationServicer_to_server(AuthzServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    logger.info({"message": f"ext_authz v3 gRPC server listening on :{port}"})
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
