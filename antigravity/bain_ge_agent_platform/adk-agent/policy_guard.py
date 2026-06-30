"""
Real-time Agent Gateway policy guard for the Bain GE demo.

Every tool call routes through this guard, which POSTs to the
`bain-ge-policy-svc` Cloud Run service for an ALLOW/DENY decision before the
underlying tool runs. Decisions are emitted as structured Cloud Logging
entries by the policy service (severity INFO for ALLOW, WARNING for DENY)
and surfaced in the UI's gateway log panel via the `bain-ge-gateway-logs-svc`
sidecar.

This replaces the previous prompt-side "DLP simulation" — where the LLM was
asked to render its own redaction string — with a real backend gate the LLM
cannot bypass.

Note: This is the demo path. In production, the policy service is also
attached as a gRPC `ext_authz v3` extension on the Agent Gateway
`reasoning-engine-gateway`. See ../PRODUCTION_GATEWAY_WIRING.md.
"""
from __future__ import annotations

import logging
import os
import uuid
from functools import wraps
from typing import Any, Awaitable, Callable

import httpx

logger = logging.getLogger("bain-ge-policy-guard")

PROJECT_NUMBER = os.getenv("PROJECT_NUMBER", "254356041555")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION_AE", "us-central1")
AGENT_ENGINE_ID = os.getenv("REASONING_ENGINE_ID", "7757233204599193600")

POLICY_SERVICE_URL = os.getenv(
    "POLICY_SERVICE_URL",
    "https://bain-ge-policy-svc-254356041555.us-central1.run.app",
)
POLICY_TIMEOUT_S = float(os.getenv("POLICY_TIMEOUT_S", "3.0"))
POLICY_FAIL_OPEN = os.getenv("POLICY_FAIL_OPEN", "0") == "1"

# Map tool name → registered target service URN. Each entry is a target that
# the bain agent has been authorized to invoke (modeled as a `bindings`
# relationship in Agent Registry; enforced via R000 in the policy service).
TARGET_FOR_TOOL: dict[str, str] = {
    "search_and_fetch_top": (
        "urn:mcp:projects-254356041555:projects:254356041555:locations:us-central1:"
        "agentregistry:services:sharepoint-mcp"
    ),
    "public_market_multiples": "urn:endpoint:bain:public-market:public_market_multiples",
    "plot_financial_data": "urn:endpoint:bain:public-market:plot_financial_data",
    "check_internet_egress": "urn:endpoint:bain:diagnostics:check_internet_egress",
}


class PolicyDenied(Exception):
    """Raised when the gateway policy service returns DENY."""
    def __init__(self, rule: str, reason: str, correlation_id: str, log_url: str):
        super().__init__(f"[{rule}] {reason}")
        self.rule = rule
        self.reason = reason
        self.correlation_id = correlation_id
        self.log_url = log_url


def _source_urn() -> str:
    return (
        f"urn:agent:projects-{PROJECT_NUMBER}:projects:{PROJECT_NUMBER}:"
        f"locations:{LOCATION}:aiplatform:reasoningEngines:{AGENT_ENGINE_ID}"
    )


def _user_from_ctx(ctx: Any) -> str | None:
    """Best-effort extraction of end-user identity from session state (Pillar A)."""
    try:
        state = dict(getattr(getattr(ctx, "session", None), "state", {}) or {})
        # Common UI-injected key for the consultant identity:
        for k in ("user_email", "consultant_email", "bain_user", "x_user_email"):
            v = state.get(k)
            if isinstance(v, str) and "@" in v:
                return v
        # Fall back to the MS Graph token's `preferred_username` claim if present
        ms_keys = [k for k in state.keys() if "sharepoint" in k.lower() or "graph" in k.lower()]
        for k in ms_keys:
            tok = state.get(k)
            if isinstance(tok, str) and tok.startswith("eyJ"):
                import base64, json as _j
                try:
                    parts = tok.split(".")
                    payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
                    claims = _j.loads(base64.urlsafe_b64decode(payload_b64).decode())
                    for cclaim in ("preferred_username", "upn", "email", "unique_name"):
                        if cclaim in claims:
                            return str(claims[cclaim])
                except Exception:
                    pass
    except Exception:
        pass
    return None


async def check(
    *,
    tool: str,
    args: dict[str, Any],
    ctx: Any | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """POST to the policy service. Raise PolicyDenied on DENY."""
    target = TARGET_FOR_TOOL.get(tool, f"urn:endpoint:bain:unknown:{tool}")
    payload = {
        "source_agent": _source_urn(),
        "target_service": target,
        "tool": tool,
        "args": _sanitize(args),
        "headers": headers or {},
        "user": _user_from_ctx(ctx) if ctx is not None else None,
        "correlation_id": str(uuid.uuid4()),
    }
    try:
        async with httpx.AsyncClient(timeout=POLICY_TIMEOUT_S) as client:
            r = await client.post(f"{POLICY_SERVICE_URL}/decide", json=payload)
            r.raise_for_status()
            verdict = r.json()
    except Exception as e:
        if POLICY_FAIL_OPEN:
            logger.warning(f"[policy-guard] Service unreachable — failing open: {e}")
            return {"decision": "ALLOW", "reason": "policy svc unreachable (fail-open)", "rule": "FAIL_OPEN"}
        logger.error(f"[policy-guard] Service unreachable — failing closed: {e}")
        raise PolicyDenied(
            rule="POLICY_SERVICE_UNREACHABLE",
            reason=f"Could not reach Agent Gateway policy service: {e}",
            correlation_id=payload["correlation_id"],
            log_url="",
        )

    if verdict.get("decision") == "DENY":
        raise PolicyDenied(
            rule=verdict.get("rule", "?"),
            reason=verdict.get("reason", "denied"),
            correlation_id=verdict.get("correlation_id", payload["correlation_id"]),
            log_url=verdict.get("log_url", ""),
        )
    return verdict


def guarded(tool_name: str | None = None):
    """
    Decorator that wraps an async ADK tool function with the policy guard.

    Usage:
        @guarded("search_and_fetch_top")
        async def search_and_fetch_top(ctx, query, top_files=3): ...

    If the policy denies, the tool returns a structured dict the LLM can show
    to the user, including the rule ID, reason, and a Cloud Logging deep-link.
    """
    def deco(fn: Callable[..., Awaitable[Any]]):
        name = tool_name or fn.__name__

        @wraps(fn)
        async def wrapper(ctx, *args, **kwargs):
            try:
                verdict = await check(
                    tool=name,
                    args={"args": list(args), "kwargs": kwargs},
                    ctx=ctx,
                )
            except PolicyDenied as denied:
                logger.warning(
                    f"[policy-guard] DENY tool={name} rule={denied.rule} "
                    f"reason={denied.reason}"
                )
                return {
                    "blocked_by_agent_gateway": True,
                    "decision": "DENY",
                    "rule": denied.rule,
                    "reason": denied.reason,
                    "correlation_id": denied.correlation_id,
                    "log_url": denied.log_url,
                    "message": (
                        f"Tool call '{name}' was blocked by the Agent Gateway policy "
                        f"[{denied.rule}]: {denied.reason}"
                    ),
                }
            logger.info(
                f"[policy-guard] ALLOW tool={name} rule={verdict.get('rule')} "
                f"latency_ms={verdict.get('latency_ms')}"
            )
            return await fn(ctx, *args, **kwargs)

        return wrapper

    return deco


def _sanitize(obj: Any) -> Any:
    """Drop bearer tokens / huge blobs from the args echoed to the policy svc."""
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if isinstance(v, str) and v.startswith("eyJ") and len(v) > 200:
                out[k] = f"<jwt:{len(v)}b>"
            else:
                out[k] = _sanitize(v)
        return out
    if isinstance(obj, list):
        return [_sanitize(x) for x in obj]
    if isinstance(obj, str) and len(obj) > 2000:
        return obj[:2000] + "…"
    return obj
