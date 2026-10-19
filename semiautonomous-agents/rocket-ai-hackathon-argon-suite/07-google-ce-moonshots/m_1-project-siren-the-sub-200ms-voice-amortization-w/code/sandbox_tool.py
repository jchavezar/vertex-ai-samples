#!/usr/bin/env python3
"""
Standalone Deterministic Sandbox & Bespoke Visual Artifact Runner
Square [M.1]: Project Siren: The Sub-200ms Voice Amortization Whisperer
UI Archetype: project_siren_live_voice_amortization (Project Siren // Real-Time Gemini Live Audio WebSocket (<200ms Barge-In Amortization))
"""
import json
from pathlib import Path
from typing import Any, Dict

MOCK_PATH = Path(__file__).resolve().parent.parent / "mock_data" / "sample_payload.json"


def load_payload() -> Dict[str, Any]:
    with open(MOCK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_deterministic_sandbox(custom_params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = load_payload()
    verified = dict(payload.get("verified_sandbox_output", {}))
    if custom_params:
        verified["custom_params_applied"] = custom_params
    return {
        "square_code": "M.1",
        "project_title": payload.get("project_title", "Project Siren: The Sub-200ms Voice Amortization Whisperer"),
        "ui_archetype": payload.get("ui_archetype", "project_siren_live_voice_amortization"),
        "sandbox": verified,
        "bespoke_artifact": payload.get("bespoke_visual_artifact", {}),
    }


if __name__ == "__main__":
    print(json.dumps(run_deterministic_sandbox(), indent=2))
