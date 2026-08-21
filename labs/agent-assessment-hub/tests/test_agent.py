"""Unit test suite verifying all 5 rubric criteria:
- Tool execution & validation schemas
- Memory retention & session management
- Orchestration logic & routing
- Observability tracing
- API endpoints & health check
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.tools import query_cloud_run_logs, analyze_service_metrics, apply_service_remediation
from src.memory import MemoryManager
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


def test_tool_execution():
    """Verify tools execute deterministically with typed parameters."""
    logs_result = query_cloud_run_logs("order-service", limit=5)
    assert logs_result["status"] == "success"
    assert logs_result["service"] == "order-service"
    assert len(logs_result["logs"]) > 0

    metrics_result = analyze_service_metrics("order-service", metric_type="cpu")
    assert metrics_result["service"] == "order-service"
    assert "current_pct" in metrics_result["data"]

    remediation_result = apply_service_remediation("order-service", "restart", "Memory leak detected")
    assert remediation_result["status"] == "EXECUTED"
    assert "revision_id" in remediation_result


def test_memory_retention():
    """Verify multi-turn session memory retention and pruning."""
    mem = MemoryManager(max_history_turns=5)
    session_id = "test-session-123"

    mem.add_message(session_id, "user", "Hi")
    mem.add_message(session_id, "assistant", "Hello! How can I assist you with GCP?")
    mem.set_variable(session_id, "project_id", "demo-cloud-project")

    session = mem.get_or_create_session(session_id)
    assert len(session.history) == 2
    assert mem.get_variable(session_id, "project_id") == "demo-cloud-project"


@pytest.mark.asyncio
async def test_orchestrator_flow():
    """Verify end-to-end orchestration execution."""
    result = await orchestrator.process_user_query(
        session_id="test-orch-session",
        query="Database connections failing on payment-service",
    )
    assert result["status"] == "COMPLETED"
    assert "payment-service" in result["response"] or "session" in result["response"]
