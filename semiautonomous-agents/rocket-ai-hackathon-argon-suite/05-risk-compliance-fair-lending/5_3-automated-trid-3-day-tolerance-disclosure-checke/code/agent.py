#!/usr/bin/env python3
"""
Rocket Companies AI Hackathon (Oct 2026) — Square [5.3]: Automated TRID 3-Day Tolerance & Disclosure Checker (LE vs. CD)
Bespoke App Archetype: trid_le_cd_tolerance_grid (CFPB TRID 12 CFR § 1026.19(e)(3) // Loan Estimate vs. Closing Disclosure Cure Auditor)
Routed Model: gemini-4-argon (Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox)
"""
import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared.auth_and_vertex import call_vertex_structured_and_executive, run_sandbox_action
from shared.bespoke_apps import get_rich_structured_artifact


def load_mock_data() -> dict:
    mock_path = Path(__file__).resolve().parent.parent / "mock_data" / "sample_payload.json"
    with open(mock_path, "r", encoding="utf-8") as f:
        return json.load(f)


def execute_square_demo(custom_input: str | None = None, model_override: str | None = None) -> dict:
    payload = load_mock_data()
    user_input = custom_input or payload["sample_input"]
    sandbox_result = run_sandbox_action(
        payload.get("sandbox_action", "default"),
        payload.get("sandbox_params", {}),
    )
    bespoke_art = get_rich_structured_artifact("5.3", sandbox_result)
    vertex_res = call_vertex_structured_and_executive(
        code="5.3",
        requested_model=model_override or payload["routed_model"],
        system_prompt=payload["system_prompt"],
        user_input=user_input,
        sandbox_result=sandbox_result,
        output_schema_hint=payload["output_schema_hint"],
    )
    return {
        "ok": vertex_res.get("ok", True),
        "square": "5.3",
        "project": payload["project_title"],
        "ui_archetype": payload["ui_archetype"],
        "model_used": vertex_res.get("model_used"),
        "runtime_badge": payload["runtime_badge"],
        "sandbox": sandbox_result,
        "bespoke_visual_artifact": bespoke_art,
        "structured_data": vertex_res.get("structured_data", {}),
        "output": vertex_res.get("response_markdown", ""),
    }


if __name__ == "__main__":
    result = execute_square_demo()
    print(f"=== Square [5.3] {result['project']} | Archetype: {result['ui_archetype']} | Model: {result['model_used']} ===")
    print(json.dumps(result["structured_data"], indent=2))
