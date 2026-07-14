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
