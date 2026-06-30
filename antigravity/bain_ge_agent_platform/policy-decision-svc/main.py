"""
Bain Gemini Enterprise — Agent Gateway Policy Decision Service

Real backend governance for Agent Gateway demos. Each request the agent wants
to make to a downstream MCP/tool is evaluated here before execution.

Wire shape:
- POST /decide  { source_agent, target_service, tool, args, headers }
                -> { decision: "ALLOW"|"DENY", reason, rule, latency_ms }

Every decision is emitted as a structured Cloud Logging entry (JSON to stdout,
captured by Cloud Run's logging adapter) so the UI can tail real entries via
the `gateway-logs-svc` proxy.

This service is also designed to be the source of truth for a gRPC ext_authz
extension attached to the Agent Gateway (see PRODUCTION_GATEWAY_WIRING.md);
the rules below are imported by the gRPC handler so a single policy module
serves both demo HTTP and production mTLS paths.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from policy import (
    Decision,
    POLICY_NAME,
    POLICY_VERSION,
    evaluate,
)

# ---- Structured logging to stdout (Cloud Logging picks this up) ----

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
logger = logging.getLogger("agent-gateway-policy")

# ---- HTTP API ----

app = FastAPI(
    title="Agent Gateway Policy Decision Service",
    description="Bain GE — real backend governance for MCP tool calls.",
    version=POLICY_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class DecideRequest(BaseModel):
    source_agent: str = Field(
        ...,
        description="URN of the calling agent, e.g. urn:agent:projects-254356041555:.../reasoningEngines/<id>",
    )
    target_service: str = Field(
        ...,
        description="URN of the target MCP/endpoint, e.g. urn:mcp:projects-254356041555:.../mcpServers/<id>",
    )
    tool: str = Field(..., description="Tool name being invoked, e.g. search_and_fetch_top")
    args: dict[str, Any] = Field(default_factory=dict, description="Tool call arguments")
    headers: dict[str, str] = Field(default_factory=dict, description="Caller request headers")
    user: str | None = Field(default=None, description="End-user identity (Pillar A), if any")
    correlation_id: str | None = Field(default=None)


class DecideResponse(BaseModel):
    decision: str
    reason: str
    rule: str | None
    policy: str
    policy_version: str
    latency_ms: float
    correlation_id: str
    log_url: str


@app.get("/")
def root_health():
    return {"status": "ok", "policy": POLICY_NAME, "version": POLICY_VERSION}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/decide", response_model=DecideResponse)
async def decide(req: DecideRequest, request: Request):
    t0 = time.perf_counter()
    corr = req.correlation_id or str(uuid.uuid4())

    verdict: Decision = evaluate(
        source_agent=req.source_agent,
        target_service=req.target_service,
        tool=req.tool,
        args=req.args,
        headers=req.headers,
        user=req.user,
    )

    latency_ms = (time.perf_counter() - t0) * 1000.0

    log_entry = {
        "severity": "WARNING" if verdict.decision == "DENY" else "INFO",
        "component": "agent-gateway-policy",
        "policy": POLICY_NAME,
        "policy_version": POLICY_VERSION,
        "policy_decision": verdict.decision,
        "rule": verdict.rule,
        "reason": verdict.reason,
        "source_agent": req.source_agent,
        "target_service": req.target_service,
        "tool": req.tool,
        "user": req.user,
        "args_preview": _preview_args(req.args),
        "latency_ms": round(latency_ms, 2),
        "correlation_id": corr,
        "client_ip": request.client.host if request.client else None,
        "message": (
            f"[POLICY] {verdict.decision} {req.tool} via {_short(req.target_service)} "
            f"by {_short(req.source_agent)} — {verdict.reason}"
        ),
    }
    logger.info(log_entry)

    project = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
    log_url = (
        f"https://console.cloud.google.com/logs/query;query="
        f'jsonPayload.correlation_id%3D%22{corr}%22'
        f"?project={project}"
    )

    return DecideResponse(
        decision=verdict.decision,
        reason=verdict.reason,
        rule=verdict.rule,
        policy=POLICY_NAME,
        policy_version=POLICY_VERSION,
        latency_ms=round(latency_ms, 2),
        correlation_id=corr,
        log_url=log_url,
    )


@app.get("/rules")
def list_rules():
    """Expose the active ruleset so the UI can render a human-readable policy card."""
    from policy import describe_rules
    return {"policy": POLICY_NAME, "version": POLICY_VERSION, "rules": describe_rules()}


def _preview_args(args: dict[str, Any], maxlen: int = 200) -> str:
    try:
        s = json.dumps(args, default=str)
    except Exception:
        s = str(args)
    return s if len(s) <= maxlen else s[:maxlen] + "…"


def _short(urn: str) -> str:
    return urn.split(":")[-1] if urn else "<unknown>"
