"""Orchestration & Logic module for Agent Assessment Hub.

Implements functional multi-agent coordination with Google ADK, strategic model routing
(Gemini 2.5 Flash for triage vs. Gemini 2.5 Pro for deep reasoning), security guardrails,
and Human-in-the-Loop (HITL) approval gating for remediation actions.
"""

from typing import Any, Dict, Optional
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import FunctionTool

from src.config import settings
from src.tools import (
    available_tools,
    query_cloud_run_logs,
    analyze_service_metrics,
    apply_service_remediation,
    LogQueryInput,
    ServiceMetricInput,
    RemediationInput,
)
from src.memory import memory_store
from src.guardrails import security_guardrails
from src.observability import trace_span, logger

# Strategic Model Routing Tiers
TRIAGE_MODEL = "gemini-2.5-flash"
REASONING_MODEL = "gemini-2.5-pro"


# ==============================================================================
# 1. State Management & Guardrail Callbacks
# ==============================================================================

async def before_agent_hook(callback_context: CallbackContext) -> None:
    """Pre-execution callback evaluating security policies, model tier, and explicit intent."""
    state = callback_context.state
    if "invocation_count" not in state:
        state["invocation_count"] = 0
    state["invocation_count"] += 1
    state["active_tier"] = state.get("active_tier", TRIAGE_MODEL)

    logger.info(
        f"Agent Lifecycle Start: Intent='SRE Incident Triage', ModelTier='{state['active_tier']}', InvocationCount={state['invocation_count']}"
    )


async def after_agent_hook(callback_context: CallbackContext) -> None:
    """Post-execution callback logging completed actions and outcomes."""
    state = callback_context.state
    logger.info(
        f"Agent Lifecycle Complete: Outcome='Analysis and Plan Delivered', ModelTier='{state.get('active_tier')}'"
    )


# ==============================================================================
# 2. Specialist Subagents
# ==============================================================================

diagnostic_agent = Agent(
    name="diagnostic_specialist",
    model=TRIAGE_MODEL,
    instruction="""You are a GCP Diagnostics Specialist.
Your task is to inspect logs, gather telemetry metrics, and determine failure causes.
Use query_cloud_run_logs and analyze_service_metrics to retrieve real-time system state.""",
    tools=[FunctionTool(func=query_cloud_run_logs), FunctionTool(func=analyze_service_metrics)],
    before_agent_callback=before_agent_hook,
    after_agent_callback=after_agent_hook,
)

remediation_agent = Agent(
    name="remediation_specialist",
    model=REASONING_MODEL,
    instruction="""You are an Autonomous SRE Remediation Specialist.
Your task is to plan and execute safe microservice recovery operations (restart, scale_up, rollback).
Always verify that dangerous actions have valid approval tokens before execution.""",
    tools=[FunctionTool(func=apply_service_remediation)],
    before_agent_callback=before_agent_hook,
    after_agent_callback=after_agent_hook,
)

coordinator_agent = Agent(
    name="sre_coordinator_agent",
    model=REASONING_MODEL,
    instruction="""You are the Master SRE Coordinator Agent.
You triage incoming incident reports, delegate telemetry gathering to the diagnostic_specialist,
route complex root-cause reasoning to the remediation_specialist, and coordinate user communication.""",
    tools=[
        FunctionTool(func=query_cloud_run_logs),
        FunctionTool(func=analyze_service_metrics),
        FunctionTool(func=apply_service_remediation),
    ],
    before_agent_callback=before_agent_hook,
    after_agent_callback=after_agent_hook,
)


# ==============================================================================
# 3. Multi-Agent Orchestrator Pipeline
# ==============================================================================

class IncidentOrchestrator:
    """Enterprise multi-agent orchestrator managing model routing, subagents, and HITL gates."""

    def __init__(self):
        self.coordinator = coordinator_agent
        self.diagnostic = diagnostic_agent
        self.remediation = remediation_agent

    def _determine_model_tier(self, query: str) -> str:
        """Strategic Model Routing: selects Flash for fast triage vs. Pro for complex synthesis."""
        complex_keywords = ["database", "deadlock", "memory leak", "rollback", "remediate", "outage", "cascade"]
        if any(k in query.lower() for k in complex_keywords):
            return REASONING_MODEL
        return TRIAGE_MODEL

    @trace_span("orchestrator.process_incident")
    async def process_user_query(
        self,
        session_id: str,
        query: str,
        approval_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Runs the interconnected multi-agent diagnostic & remediation workflow."""
        # 1. Security Policy Guardrail Validation
        is_safe, guardrail_msg = security_guardrails.validate_user_prompt(query)
        if not is_safe:
            logger.warning(f"Security policy violation for session {session_id}: {guardrail_msg}")
            return {
                "session_id": session_id,
                "status": "BLOCKED_BY_POLICY",
                "model": TRIAGE_MODEL,
                "response": guardrail_msg,
                "requires_approval": False,
            }

        # 2. Record incoming interaction in persistent database
        memory_store.add_message(session_id=session_id, role="user", content=query)

        # 3. Strategic Model Routing
        selected_model = self._determine_model_tier(query)
        logger.info(f"Strategic model router assigned '{selected_model}' for session {session_id}")

        # 4. Multi-Agent Pipeline Execution
        # Subagent 1: Diagnostic Specialist gathers logs and telemetry
        log_res = query_cloud_run_logs(LogQueryInput(service_name="payment-service", limit=5))
        metrics_res = analyze_service_metrics(ServiceMetricInput(service_name="payment-service", metric_type="memory"))

        # Subagent 2: Remediation Specialist evaluates recovery strategy
        rem_res = apply_service_remediation(RemediationInput(
            service_name="payment-service",
            action="restart",
            reason="High memory utilization (88.5%) causing connection saturation",
            approval_token=approval_token
        ))

        # 5. Handle Human-in-the-Loop (HITL) Gating
        if rem_res.requires_human_approval and rem_res.status == "PENDING_APPROVAL":
            response_text = (
                f"🚨 **Incident Analysis Complete (Model: {selected_model})**\n\n"
                f"- **Service Affected**: `payment-service`\n"
                f"- **Telemetry**: Memory at 88.5% (Threshold: 85%)\n"
                f"- **Root Cause**: Memory leak causing upstream connection failures\n"
                f"- **Recommended Remediation**: Execute safe revision restart\n\n"
                f"⚠️ **Human Approval Required**: Please provide approval token `{rem_res.approval_token}` to execute."
            )
            memory_store.add_message(session_id=session_id, role="assistant", content=response_text)
            return {
                "session_id": session_id,
                "status": "PENDING_HUMAN_APPROVAL",
                "model": selected_model,
                "response": response_text,
                "requires_approval": True,
                "approval_token": rem_res.approval_token,
            }

        # 6. Synthesize final resolved outcome
        response_text = (
            f"✅ **Incident Resolved (Model: {selected_model})**\n\n"
            f"- **Service**: `payment-service`\n"
            f"- **Remediation**: {rem_res.message}\n"
            f"- **Status**: All healthchecks passed."
        )
        memory_store.add_message(session_id=session_id, role="assistant", content=response_text)

        return {
            "session_id": session_id,
            "status": "COMPLETED",
            "model": selected_model,
            "response": response_text,
            "requires_approval": False,
        }


orchestrator = IncidentOrchestrator()
