import pytest
import os
import sys

# Ensure backend app is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from app.services.cloud_logging_service import fetch_gcp_errors
from app.services.cloud_assist_service import _build_fallback_diagnostic

def test_fetch_gcp_errors():
    errors = fetch_gcp_errors("1h")
    assert isinstance(errors, list)
    assert len(errors) > 0
    err = errors[0]
    assert err.id
    assert err.summary
    assert err.serviceName

def test_fallback_diagnostic_oom():
    errors = fetch_gcp_errors("1h")
    oom_err = next(e for e in errors if "oom" in e.id.lower() or "503" in e.summary)
    diag = _build_fallback_diagnostic(oom_err)
    assert diag.title
    assert len(diag.hypotheses) > 0
    hyp = diag.hypotheses[0]
    assert hyp.relevanceScore is not None
    assert len(hyp.remediationCommands) > 0

def test_execute_remediation_real_command():
    from main import execute_remediation, ExecuteCommandRequest
    
    req = ExecuteCommandRequest(command="gcloud version")
    res = execute_remediation(req)
    assert res.exitCode == 0
    assert "Google Cloud SDK" in res.stdout
    assert "--project=" in res.command

@pytest.mark.anyio
async def test_run_subagent_in_sandbox_real_command():
    from app.services.sandbox_parallel_orchestrator import run_subagent_in_sandbox
    from app.models.schemas import HypothesisItem, GcpErrorItem
    
    dummy_err = GcpErrorItem(
        id="test-err",
        timestamp="2026-07-27T18:00:00Z",
        severity="ERROR",
        serviceName="Cloud Run",
        resourceType="cloud_run_revision",
        summary="Test error",
        fullText="Test",
        logPayload={},
        labels={}
    )
    dummy_hyp = HypothesisItem(
        id="test-hyp",
        title="Test Hypothesis",
        relevanceScore=1.0,
        overviewText="Test",
        rootCauseText="Test",
        remediationCommands=["gcloud version"],
        recommendationText="Test",
        relevantResources=[]
    )
    
    res = await run_subagent_in_sandbox("test-agent", dummy_hyp, dummy_err)
    assert res.success is True
    assert len(res.attempts) > 0
    assert "gcloud version" in res.final_command

def test_fallback_diagnostic_scheduler():
    from app.models.schemas import GcpErrorItem
    dummy_err = GcpErrorItem(
        id="test-scheduler-err",
        timestamp="2026-07-27T18:00:00Z",
        severity="ERROR",
        serviceName="Cloud Scheduler",
        resourceType="cloud_scheduler_job",
        summary="Target endpoint returned 404",
        fullText="AttemptFinished event: debugInfo = 404 Not Found",
        logPayload={},
        labels={}
    )
    diag = _build_fallback_diagnostic(dummy_err)
    assert "Cloud Scheduler Job Failure" in diag.title
    assert len(diag.hypotheses) > 0
    hyp = diag.hypotheses[0]
    assert hyp.id == "hyp-scheduler-target-404"
    assert "gcloud scheduler jobs describe" in hyp.remediationCommands[0]
