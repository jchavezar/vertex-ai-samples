#!/usr/bin/env python3
"""
Standalone Vertex AI Agent Runner for Square [5.5]: Fair Lending Disparate Impact & Bias Audit Engine (ECOA / Reg B)
Bespoke App Archetype: ecoa_fair_lending_twin_certifier (ECOA Regulation B // 500-Counterfactual Twin Fair Lending & Adverse Action Certifier)
Default Model: gemini-4-argon (Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox)
"""
import json
import os
from pathlib import Path
from typing import Any, Dict

from code.sandbox_tool import load_payload, run_deterministic_sandbox


def execute_square_demo(custom_input: str | None = None, model_override: str | None = None) -> Dict[str, Any]:
    payload = load_payload()
    sb_bundle = run_deterministic_sandbox()
    model_id = model_override or os.environ.get("ROCKET_MODEL") or payload.get("routed_model", "gemini-4-argon")
    user_prompt = custom_input or payload.get("sample_input", "")
    sys_instruction = payload.get("system_prompt", "You are a Rocket Companies AI specialist.")
    schema_hint = payload.get("output_schema_hint", "Return structured JSON.")

    structured_out = payload.get("sample_structured_output", {})
    raw_text = ""
    live_called = False

    if os.environ.get("LIVE_VERTEX", "0") == "1":
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(
                vertexai=True,
                project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
                location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
            )
            full_prompt = (
                f"{user_prompt}\n\n"
                f"Verified Deterministic Sandbox Metrics:\n{json.dumps(sb_bundle['sandbox'], indent=2)}\n\n"
                f"Output Schema Requirement: {schema_hint}"
            )
            resp = client.models.generate_content(
                model=model_id,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruction,
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )
            raw_text = resp.text or ""
            structured_out = json.loads(raw_text)
            live_called = True
        except Exception as exc:
            raw_text = f"Fallback to verified precomputed payload ({exc})"

    return {
        "ok": True,
        "square": "5.5",
        "project": payload.get("project_title", "Fair Lending Disparate Impact & Bias Audit Engine (ECOA / Reg B)"),
        "ui_archetype": payload.get("ui_archetype", "ecoa_fair_lending_twin_certifier"),
        "model_used": model_id,
        "live_vertex_called": live_called,
        "runtime_badge": payload.get("runtime_badge", "Vertex AI Global Endpoint (gemini-4-argon) + Antigravity gVisor Sandbox"),
        "sandbox": sb_bundle["sandbox"],
        "bespoke_visual_artifact": sb_bundle["bespoke_artifact"],
        "structured_data": structured_out,
        "raw_response": raw_text,
    }


if __name__ == "__main__":
    res = execute_square_demo()
    print(f"=== Square [5.5] {res['project']} | Archetype: {res['ui_archetype']} | Model: {res['model_used']} ===")
    print(json.dumps(res, indent=2))
