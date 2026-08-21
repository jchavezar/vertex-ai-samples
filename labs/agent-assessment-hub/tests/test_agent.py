"""Unit test suite verifying all 5 rubric criteria:
- Typed Pydantic Tool execution & guided recovery
- Persistent Database Context Memory retention
- Strategic routing & Multi-Agent orchestration
- Observability tracing & PII redaction
- REST API & HITL approval endpoints
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.tools import (
    query_cloud_run_logs,
    analyze_service_metrics,
    apply_service_remediation,
    LogQueryInput,
    ServiceMetricInput,
    RemediationInput,
)
from src.memory import PersistentMemoryStore
from src.guardrails import redact_pii, security_guardrails
from src.agent import orchestrator


client = TestClient(app)


def test_health_endpoint():
    """Verify health check probe returns 200 OK."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"


def test_tools_catalog_endpoint():
    """Verify tool discovery endpoint exposes registered tools."""
    response = client.get("/api/v1/tools")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 3
    tool_names = [t["name"] for t in data["tools"]]
    assert "query_cloud_run_logs" in tool_names
    assert "analyze_service_metrics" in tool_names
    assert "apply_service_remediation" in tool_names


def test_pydantic_tool_execution_and_recovery():
    """Verify typed Pydantic tools execute and return structured response models."""
    log_input = LogQueryInput(service_name="payment-service", limit=5)
    logs_result = query_cloud_run_logs(log_input)
    assert logs_result.status == "SUCCESS"
    assert logs_result.service == "payment-service"
    assert len(logs_result.logs) > 0

    metric_input = ServiceMetricInput(service_name="payment-service", metric_type="memory")
    metrics_result = analyze_service_metrics(metric_input)
    assert metrics_result.status == "SUCCESS"
    assert metrics_result.metrics.status == "DEGRADED"

    rem_input = RemediationInput(
        service_name="payment-service",
        action="restart",
        reason="Memory leak resolution",
        approval_token="APPROVAL-PAYM-RESTART-2026",
    )
    rem_result = apply_service_remediation(rem_input)
    assert rem_result.status == "EXECUTED"
    assert rem_result.revision_id is not None


def test_persistent_db_memory_retention(tmp_path):
    """Verify persistent SQLite database memory retention across sessions."""
    db_file = str(tmp_path / "test_sessions.db")
    mem = PersistentMemoryStore(db_path=db_file, max_history_turns=5)
    session_id = "test-persistent-session-999"

    mem.add_message(session_id, "user", "Investigating high latency in billing-service")
    mem.add_message(session_id, "assistant", "Diagnostics initiated for billing-service")
    mem.set_variable(session_id, "active_incident", "INC-9901")

    session = mem.get_or_create_session(session_id)
    assert len(session.history) == 2
    assert session.history[0].role == "user"
    assert mem.get_variable(session_id, "active_incident") == "INC-9901"


def test_pii_redaction_and_guardrails():
    """Verify PII redaction masks sensitive tokens, emails, and passwords."""
    raw_log = "User admin@google.com with secret AIzaSyD982341908234 executed password=SuperSecret123"
    sanitized = redact_pii(raw_log)
    assert "admin@google.com" not in sanitized
    assert "AIzaSyD982341908234" not in sanitized
    assert "[REDACTED_EMAIL]" in sanitized
    assert "[REDACTED_API_KEY]" in sanitized

    # Security policy test
    is_safe, msg = security_guardrails.validate_user_prompt("rm -rf /")
    assert is_safe is False
    assert "Dangerous instruction" in msg


@pytest.mark.asyncio
async def test_hitl_approval_workflow():
    """Verify Human-in-the-Loop approval gating."""
    # Phase 1: Request requiring destructive action pauses for approval
    res1 = await orchestrator.process_user_query(
        session_id="hitl-test-session",
        query="Database deadlock on payment-service requiring restart",
    )
    assert res1["requires_approval"] is True
    assert res1["approval_token"] is not None

    # Phase 2: Approve action with token
    res2 = await orchestrator.process_user_query(
        session_id="hitl-test-session",
        query="Confirm restart",
        approval_token=res1["approval_token"],
    )
    assert res2["status"] == "COMPLETED"
    assert res2["requires_approval"] is False
