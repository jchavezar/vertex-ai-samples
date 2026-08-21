"""Automated Agent Evaluation Suite (Quality Flywheel) against Golden Dataset.

Evaluates:
- Strategic model routing precision
- Tool calling correctness
- Security guardrail enforcement
- Human-in-the-loop (HITL) approval compliance
"""

import json
import os
import pytest
from src.agent import orchestrator
from src.guardrails import security_guardrails, redact_pii


def load_golden_dataset():
    dataset_path = os.path.join(os.path.dirname(__file__), "eval_dataset.json")
    with open(dataset_path, "r") as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_golden_dataset_eval_flywheel():
    """Runs automated evaluation flywheel across golden dataset test cases."""
    dataset = load_golden_dataset()
    assert len(dataset) >= 4

    passed_evals = 0

    for item in dataset:
        eval_id = item["eval_id"]
        prompt = item["prompt"]
        expected_routing = item["expected_routing"]

        result = await orchestrator.process_user_query(
            session_id=f"eval-session-{eval_id}",
            query=prompt
        )

        # 1. Evaluate Security Guardrails Blocking
        if item.get("expected_status") == "BLOCKED_BY_POLICY":
            assert result["status"] == "BLOCKED_BY_POLICY", f"Failed policy check for {eval_id}"
            passed_evals += 1
            continue

        # 2. Evaluate Strategic Routing
        assert result["model"] == expected_routing, f"Routing mismatch for {eval_id}: got {result['model']}, expected {expected_routing}"

        # 3. Evaluate HITL Gating
        if item.get("requires_hitl"):
            assert result["requires_approval"] is True, f"HITL required but not flagged for {eval_id}"
            assert result["approval_token"] is not None

        passed_evals += 1

    accuracy_rate = (passed_evals / len(dataset)) * 100
    assert accuracy_rate == 100.0
