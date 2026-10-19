#!/usr/bin/env python3
"""
Standalone Deterministic Sandbox & Bespoke Visual Artifact Runner
Square [2.4]: Self-Employed Schedule C / 1040 Cash-Flow Extractor (Form 1084)
UI Archetype: form_1084_tax_worksheet (Fannie Mae Form 1084 // Self-Employed Schedule C & K-1 Cash-Flow Worksheet)
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
        "square_code": "2.4",
        "project_title": payload.get("project_title", "Self-Employed Schedule C / 1040 Cash-Flow Extractor (Form 1084)"),
        "ui_archetype": payload.get("ui_archetype", "form_1084_tax_worksheet"),
        "sandbox": verified,
        "bespoke_artifact": payload.get("bespoke_visual_artifact", {}),
    }


if __name__ == "__main__":
    print(json.dumps(run_deterministic_sandbox(), indent=2))
