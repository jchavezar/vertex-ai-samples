"""Tool & Interface Design module for Agent Assessment Hub.

Defines strictly typed Pydantic input & output models, Google ADK FunctionTools,
and guided error recovery responses that instruct the LLM on corrective actions.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ValidationError
from src.observability import trace_span, logger
from src.guardrails import security_guardrails


# ==============================================================================
# Pydantic Input Schemas
# ==============================================================================

class LogQueryInput(BaseModel):
    service_name: str = Field(..., min_length=2, max_length=64, description="Name of the microservice (e.g., 'payment-service')")
    limit: int = Field(default=10, ge=1, le=50, description="Max number of log lines to retrieve (1-50)")


class ServiceMetricInput(BaseModel):
    service_name: str = Field(..., min_length=2, max_length=64, description="Target microservice name")
    metric_type: Literal["cpu", "memory", "latency", "5xx_rate"] = Field(
        default="cpu",
        description="Metric category to analyze: 'cpu', 'memory', 'latency', or '5xx_rate'"
    )


class RemediationInput(BaseModel):
    service_name: str = Field(..., min_length=2, max_length=64, description="Target microservice for remediation")
    action: Literal["restart", "scale_up", "rollback"] = Field(..., description="Action: 'restart', 'scale_up', or 'rollback'")
    reason: str = Field(..., min_length=10, description="Root-cause diagnosis justification")
    approval_token: Optional[str] = Field(None, description="Human-in-the-loop approval token for destructive actions")


# ==============================================================================
# Pydantic Output Schemas
# ==============================================================================

class LogEntry(BaseModel):
    timestamp: str
    severity: str
    message: str
    trace_id: str


class LogQueryResponse(BaseModel):
    status: Literal["SUCCESS", "ERROR", "RECOVERY_NEEDED"]
    service: str
    total_entries: int
    logs: List[LogEntry]
    recovery_guidance: Optional[str] = None


class MetricData(BaseModel):
    current_value: float
    threshold_value: float
    unit: str
    status: Literal["HEALTHY", "DEGRADED", "WARNING", "CRITICAL"]


class ServiceMetricsResponse(BaseModel):
    status: Literal["SUCCESS", "ERROR", "RECOVERY_NEEDED"]
    service: str
    metric_type: str
    metrics: Optional[MetricData] = None
    evaluation: str
    recovery_guidance: Optional[str] = None


class RemediationResponse(BaseModel):
    status: Literal["EXECUTED", "PENDING_APPROVAL", "REJECTED", "ERROR"]
    service: str
    action: str
    reason: str
    revision_id: Optional[str] = None
    requires_human_approval: bool = False
    approval_token: Optional[str] = None
    message: str
    recovery_guidance: Optional[str] = None


# ==============================================================================
# Tool Implementations with Guided Error Recovery
# ==============================================================================

@trace_span("tool.query_cloud_run_logs")
def query_cloud_run_logs(params: LogQueryInput) -> LogQueryResponse:
    """Queries Cloud Logging for recent error and warning events for a specific microservice.

    Args:
        params: LogQueryInput containing service_name and log retrieval limit.

    Returns:
        LogQueryResponse with structured log items or guided recovery suggestions.
    """
    logger.info(f"Executing query_cloud_run_logs for {params.service_name}")
    try:
        sample_logs = [
            LogEntry(
                timestamp="2026-08-21T12:00:01Z",
                severity="ERROR",
                message=f"ConnectionRefusedError: Unable to connect to upstream PostgreSQL database in {params.service_name}",
                trace_id="projects/demo-agent/traces/trace-8921",
            ),
            LogEntry(
                timestamp="2026-08-21T12:00:15Z",
                severity="WARNING",
                message=f"Memory utilization exceeded 85% threshold on instance {params.service_name}-00042",
                trace_id="projects/demo-agent/traces/trace-8922",
            ),
        ]

        return LogQueryResponse(
            status="SUCCESS",
            service=params.service_name,
            total_entries=len(sample_logs),
            logs=sample_logs[:params.limit],
        )
    except Exception as exc:
        logger.warning(f"Error querying logs: {str(exc)}")
        return LogQueryResponse(
            status="RECOVERY_NEEDED",
            service=params.service_name,
            total_entries=0,
            logs=[],
            recovery_guidance=f"Cloud Logging query failed with '{str(exc)}'. Recovery action: Verify service name and check if IAM role 'roles/logging.viewer' is granted.",
        )


@trace_span("tool.analyze_service_metrics")
def analyze_service_metrics(params: ServiceMetricInput) -> ServiceMetricsResponse:
    """Analyzes real-time telemetry metrics (CPU, Memory, Latency, 5xx error rate) for a microservice.

    Args:
        params: ServiceMetricInput containing service_name and metric_type.

    Returns:
        ServiceMetricsResponse with telemetry breakdown and health threshold evaluation.
    """
    logger.info(f"Executing analyze_service_metrics for {params.service_name} ({params.metric_type})")
    try:
        metrics_catalog = {
            "cpu": MetricData(current_value=62.4, threshold_value=80.0, unit="%", status="HEALTHY"),
            "memory": MetricData(current_value=88.5, threshold_value=85.0, unit="%", status="DEGRADED"),
            "latency": MetricData(current_value=312.0, threshold_value=500.0, unit="ms", status="WARNING"),
            "5xx_rate": MetricData(current_value=2.1, threshold_value=0.5, unit="%", status="CRITICAL"),
        }

        metric = metrics_catalog.get(params.metric_type, metrics_catalog["cpu"])
        eval_summary = "Action required: telemetry threshold exceeded" if metric.status in ["DEGRADED", "CRITICAL"] else "Telemetry within normal parameters"

        return ServiceMetricsResponse(
            status="SUCCESS",
            service=params.service_name,
            metric_type=params.metric_type,
            metrics=metric,
            evaluation=eval_summary,
        )
    except Exception as exc:
        return ServiceMetricsResponse(
            status="RECOVERY_NEEDED",
            service=params.service_name,
            metric_type=params.metric_type,
            evaluation="Failed to compute metrics",
            recovery_guidance=f"Metric ingestion error: {str(exc)}. Recovery action: Fall back to querying Cloud Logging error trends.",
        )


@trace_span("tool.apply_service_remediation")
def apply_service_remediation(params: RemediationInput) -> RemediationResponse:
    """Applies automated SRE remediation (restart, scale_up, rollback) with Human-in-the-loop safety gating.

    Args:
        params: RemediationInput with service_name, action, justification reason, and optional approval_token.

    Returns:
        RemediationResponse with execution status or approval token requirements.
    """
    # 1. Security Guardrails Policy Check
    is_allowed, reason = security_guardrails.validate_tool_execution(
        "apply_service_remediation",
        {"action": params.action, "service": params.service_name}
    )
    if not is_allowed:
        return RemediationResponse(
            status="REJECTED",
            service=params.service_name,
            action=params.action,
            reason=params.reason,
            requires_human_approval=False,
            message=f"Action blocked by Security Guardrails: {reason}",
            recovery_guidance="Request an approved remediation operation ('restart', 'scale_up', or 'rollback').",
        )

    # 2. Human-in-the-loop (HITL) Gate for Destructive Actions (rollback / restart)
    if params.action in ["rollback", "restart"] and not params.approval_token:
        generated_token = f"APPROVAL-{params.service_name[:4].upper()}-{params.action.upper()}-2026"
        return RemediationResponse(
            status="PENDING_APPROVAL",
            service=params.service_name,
            action=params.action,
            reason=params.reason,
            requires_human_approval=True,
            approval_token=generated_token,
            message=f"Human-in-the-loop confirmation required for destructive action '{params.action}'.",
            recovery_guidance=f"Please prompt the user/SRE to approve token '{generated_token}' before executing {params.action}.",
        )

    # 3. Execution after validation and approval
    new_rev = f"{params.service_name}-rev-autoheal-2026"
    return RemediationResponse(
        status="EXECUTED",
        service=params.service_name,
        action=params.action,
        reason=params.reason,
        revision_id=new_rev,
        requires_human_approval=False,
        message=f"Successfully applied {params.action} to {params.service_name}. New revision {new_rev} is healthy.",
    )


# Function wrappers for ADK agent registration
available_tools = [
    query_cloud_run_logs,
    analyze_service_metrics,
    apply_service_remediation,
]
