"""
Policy ruleset for the Bain Gemini Enterprise Agent Gateway demo.

Encodes the "10 non-negotiables" referenced in the architecture doc as
concrete deterministic rules. Each rule:
  - Has a stable `id` so logs/traces can be grepped
  - Has a `description` shown in the UI policy card
  - Returns a Decision when matched

Evaluation order: first matching DENY wins; otherwise ALLOW.

This module is imported by both the FastAPI HTTP server (main.py) and the
production gRPC ext_authz handler so a single source of truth covers both
the demo and the gateway routing path.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

POLICY_NAME = "bain-ge-mnpi-shield"
POLICY_VERSION = "1.0.0"


@dataclass(frozen=True)
class Decision:
    decision: str  # "ALLOW" | "DENY"
    reason: str
    rule: str | None


# ---- Allow-list configuration ----

# Registered MCP/endpoint URNs the demo bain agent is bound to in the Agent Registry.
# Calls to any target NOT in this set are denied by R000 (registry-binding gate).
REGISTERED_TARGETS = {
    # sharepoint-mcp service in vtxdemos us-central1 (Agent Registry mcpServerId)
    "urn:mcp:projects-254356041555:projects:254356041555:locations:us-central1:agentregistry:services:sharepoint-mcp",
    # ge-sharepoint-mcp-service endpoint (Agent Registry endpointId)
    "urn:endpoint:projects-254356041555:projects:254356041555:locations:us-central1:agentregistry:services:ge-sharepoint-mcp-service",
    # public-market mock endpoint (synthetic / local tool)
    "urn:endpoint:bain:public-market:public_market_multiples",
    "urn:endpoint:bain:public-market:plot_financial_data",
    # diagnostic egress
    "urn:endpoint:bain:diagnostics:check_internet_egress",
    # google search
    "urn:endpoint:google:search:google_search",
}

# Approved source agents (URN). Calls from any source NOT in this set are denied
# by R001 (agent identity gate). In production this is enforced via the SPIFFE
# principal extracted from the mTLS client cert by the Agent Gateway and surfaced
# in the ext_authz CheckRequest.attributes.source.principal field.
APPROVED_SOURCE_AGENTS_PREFIX = "urn:agent:projects-254356041555:"

# MNPI / restricted keywords. If a tool call's free-text arg references both a
# restricted-document marker AND a price/compensation keyword, the call is denied.
RESTRICTED_DOC_MARKERS = [
    "02_restricted",
    "restricted_privileged",
    "dlp_audit",
    "holdco",
    "starlight_acquisition",
]
MNPI_KEYWORDS = [
    "strike price",
    "acquisition price",
    "executive compensation",
    "compensation",
    "termination clause",
    "exit multiple",
]

# Prompt-injection canary file. If a tool tries to fetch this file, we audit
# but allow (the demo also has a separate UI flag for observability scenarios).
CANARY_FILE = "05_external_research_addendum_do_not_parse"


def evaluate(
    *,
    source_agent: str,
    target_service: str,
    tool: str,
    args: dict[str, Any],
    headers: dict[str, str] | None = None,
    user: str | None = None,
) -> Decision:
    """Return a Decision based on the active ruleset."""

    # R000 — registry-binding gate
    if target_service not in REGISTERED_TARGETS:
        return Decision(
            decision="DENY",
            reason=(
                f"Target '{_short(target_service)}' is not registered as a bound MCP/endpoint "
                "for this source agent in Agent Registry. Default-deny under Bain non-negotiable #1 "
                "(approved-tools-only)."
            ),
            rule="R000.registry-binding-gate",
        )

    # R001 — agent identity gate
    if not source_agent.startswith(APPROVED_SOURCE_AGENTS_PREFIX):
        return Decision(
            decision="DENY",
            reason=(
                f"Source agent '{_short(source_agent)}' is not under the approved project namespace. "
                "Identity rejected (Bain non-negotiable #2 — verified-identity-only)."
            ),
            rule="R001.identity-gate",
        )

    # R010 — MNPI DLP shield (Bain non-negotiable #5)
    args_blob = _flatten_text(args).lower()
    has_restricted_doc = any(marker in args_blob for marker in RESTRICTED_DOC_MARKERS)
    has_mnpi_keyword = any(kw in args_blob for kw in MNPI_KEYWORDS)
    if has_restricted_doc and has_mnpi_keyword:
        return Decision(
            decision="DENY",
            reason=(
                "MNPI policy match: query references a restricted document marker "
                "AND a price/compensation keyword. Output would expose Material Non-Public "
                "Information. Blocked by Agent Gateway DLP shield."
            ),
            rule="R010.mnpi-dlp-shield",
        )

    # R011 — bare strike-price extraction from any tool, with no restricted-doc context,
    # still flagged because the agent must surface it via the DLP-aware extraction path.
    bare_price_extract = (
        ("strike price" in args_blob or "acquisition price" in args_blob)
        and tool in {"search_and_fetch_top", "doc_reader"}
        and not headers_contains(headers, "x-bain-dlp-acknowledged", "true")
    )
    if bare_price_extract:
        return Decision(
            decision="DENY",
            reason=(
                "Bare price-figure extraction requires DLP acknowledgement header "
                "'X-Bain-DLP-Acknowledged: true'. Add the header to confirm consultant "
                "is on an MNPI-cleared workflow."
            ),
            rule="R011.dlp-handshake-required",
        )

    # R012 — default-deny on restricted-document filename markers, regardless
    # of accompanying keywords. Without this, an LLM can bypass R010 by
    # searching for the filename alone and getting the body back, then
    # extracting MNPI client-side. Bain non-negotiable #3 (no MNPI exfiltration
    # via cleverly-split queries).
    if has_restricted_doc:
        return Decision(
            decision="DENY",
            reason=(
                "Tool call references a restricted document marker (e.g. "
                "'02_Restricted_Privileged_DLP_Audit_Target_HoldCo.docx'). All "
                "access to restricted documents requires an out-of-band MNPI "
                "approval workflow — not a tool call from a consulting agent. "
                "Default-deny under Bain non-negotiable #3."
            ),
            rule="R012.restricted-doc-default-deny",
        )

    # R020 — canary observability marker (allow but flag in audit)
    if CANARY_FILE in args_blob:
        return Decision(
            decision="ALLOW",
            reason=(
                "Canary file accessed for observability test harness. Call permitted; "
                "any prompt-injection content in the file will be neutralized downstream "
                "and reported (Bain non-negotiable #6 — injection-resilience)."
            ),
            rule="R020.canary-observability",
        )

    # Default allow
    return Decision(
        decision="ALLOW",
        reason="No policy match. Call permitted under default-allow for bound targets.",
        rule="R999.default-allow",
    )


def describe_rules() -> list[dict[str, str]]:
    return [
        {
            "id": "R000.registry-binding-gate",
            "summary": "Default-deny for any target MCP/endpoint not bound to this agent in Agent Registry.",
        },
        {
            "id": "R001.identity-gate",
            "summary": "Source agent SPIFFE/URN must be in the approved Bain project namespace.",
        },
        {
            "id": "R010.mnpi-dlp-shield",
            "summary": "Block calls whose args reference both a restricted document marker AND an MNPI keyword (e.g. strike price + HoldCo).",
        },
        {
            "id": "R011.dlp-handshake-required",
            "summary": "Require X-Bain-DLP-Acknowledged: true header for bare price/comp extractions through search/doc tools.",
        },
        {
            "id": "R012.restricted-doc-default-deny",
            "summary": "Default-deny any tool call whose args reference a restricted-document filename marker (02_Restricted_*, HoldCo, dlp_audit, etc).",
        },
        {
            "id": "R020.canary-observability",
            "summary": "Allow access to the prompt-injection canary file but flag for observability.",
        },
        {
            "id": "R999.default-allow",
            "summary": "Default-allow for bound targets under approved identity with no MNPI match.",
        },
    ]


# ---- helpers ----

def _flatten_text(obj: Any) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return " ".join(_flatten_text(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return " ".join(_flatten_text(v) for v in obj)
    return str(obj)


def _short(urn: str) -> str:
    return urn.split(":")[-1] if urn else "<unknown>"


def headers_contains(headers: dict[str, str] | None, key: str, value: str) -> bool:
    if not headers:
        return False
    # case-insensitive
    for k, v in headers.items():
        if k.lower() == key.lower() and str(v).lower() == value.lower():
            return True
    return False
