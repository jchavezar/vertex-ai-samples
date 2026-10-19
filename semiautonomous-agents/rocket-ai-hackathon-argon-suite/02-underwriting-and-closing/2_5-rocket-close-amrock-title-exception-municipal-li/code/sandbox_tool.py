#!/usr/bin/env python3
"""
Standalone Deterministic Sandbox & Bespoke Visual Artifact Runner
Square [2.5]: Rocket Close (Amrock) Title Exception & Municipal Lien Matcher
UI Archetype: amrock_title_curative_map (Rocket Close (Amrock) // Schedule B-II Title Exception & ALTA Endorsement Clearer)
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
        "square_code": "2.5",
        "project_title": payload.get("project_title", "Rocket Close (Amrock) Title Exception & Municipal Lien Matcher"),
        "ui_archetype": payload.get("ui_archetype", "amrock_title_curative_map"),
        "sandbox": verified,
        "bespoke_artifact": payload.get("bespoke_visual_artifact", {}),
    }


if __name__ == "__main__":
    print(json.dumps(run_deterministic_sandbox(), indent=2))
