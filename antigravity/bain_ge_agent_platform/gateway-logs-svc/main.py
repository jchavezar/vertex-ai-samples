"""
Bain GE — Real-time Gateway Logs Proxy

Queries Cloud Logging for actual policy decision entries emitted by
`bain-ge-policy-svc` and serves them as JSON to the UI panel.

Replaces all the hardcoded `addGatewayLog(...)` simulator strings that used
to live in custom-ui/src/components/FlatConsoleChat.tsx.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import logging_v2

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
POLICY_SERVICE = os.getenv("POLICY_SERVICE_NAME", "bain-ge-policy-svc")

client = logging_v2.Client(project=PROJECT)

app = FastAPI(
    title="Bain GE Gateway Logs Proxy",
    description="Streams real Cloud Logging policy-decision entries to the UI.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "project": PROJECT, "policy_service": POLICY_SERVICE}


@app.get("/api/gateway-logs")
def gateway_logs(
    since_seconds: int = Query(default=60, ge=1, le=3600),
    correlation_id: str | None = None,
    decision: str | None = Query(default=None, pattern="^(ALLOW|DENY)$"),
    limit: int = Query(default=100, ge=1, le=500),
) -> dict[str, Any]:
    """
    Query Cloud Logging for real policy decisions from the policy service.

    Returns entries shaped for the UI gateway log panel:
        { entries: [ { ts, severity, decision, rule, reason, tool, source_agent,
                       target_service, user, correlation_id, latency_ms, message } ] }
    """
    since = datetime.now(timezone.utc) - timedelta(seconds=since_seconds)
    filter_parts = [
        'resource.type="cloud_run_revision"',
        f'resource.labels.service_name="{POLICY_SERVICE}"',
        'jsonPayload.component="agent-gateway-policy"',
        f'timestamp >= "{since.isoformat()}"',
    ]
    if correlation_id:
        filter_parts.append(f'jsonPayload.correlation_id="{correlation_id}"')
    if decision:
        filter_parts.append(f'jsonPayload.policy_decision="{decision}"')

    filter_str = "\n".join(filter_parts)

    entries: list[dict[str, Any]] = []
    iter_kwargs = {
        "filter_": filter_str,
        "order_by": logging_v2.DESCENDING,
        "page_size": limit,
    }
    for i, entry in enumerate(client.list_entries(**iter_kwargs)):
        if i >= limit:
            break
        payload = entry.payload if isinstance(entry.payload, dict) else {}
        entries.append(
            {
                "ts": entry.timestamp.isoformat() if entry.timestamp else None,
                "severity": entry.severity or payload.get("severity"),
                "decision": payload.get("policy_decision"),
                "rule": payload.get("rule"),
                "reason": payload.get("reason"),
                "tool": payload.get("tool"),
                "source_agent": payload.get("source_agent"),
                "target_service": payload.get("target_service"),
                "user": payload.get("user"),
                "correlation_id": payload.get("correlation_id"),
                "latency_ms": payload.get("latency_ms"),
                "message": payload.get("message"),
                "policy": payload.get("policy"),
                "policy_version": payload.get("policy_version"),
                "args_preview": payload.get("args_preview"),
            }
        )

    return {
        "project": PROJECT,
        "policy_service": POLICY_SERVICE,
        "filter": filter_str,
        "count": len(entries),
        "entries": list(reversed(entries)),  # oldest -> newest for natural feed order
    }
