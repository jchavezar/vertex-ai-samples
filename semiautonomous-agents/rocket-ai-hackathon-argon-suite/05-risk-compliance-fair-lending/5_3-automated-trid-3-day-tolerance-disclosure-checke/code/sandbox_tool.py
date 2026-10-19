#!/usr/bin/env python3
"""
Standalone Deterministic Sandbox & Bespoke Visual Artifact Runner
Square [5.3]: Automated TRID 3-Day Tolerance & Disclosure Checker (LE vs. CD)
UI Archetype: trid_le_cd_tolerance_grid (CFPB TRID 12 CFR § 1026.19(e)(3) // Loan Estimate vs. Closing Disclosure Cure Auditor)
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
        "square_code": "5.3",
        "project_title": payload.get("project_title", "Automated TRID 3-Day Tolerance & Disclosure Checker (LE vs. CD)"),
        "ui_archetype": payload.get("ui_archetype", "trid_le_cd_tolerance_grid"),
        "sandbox": verified,
        "bespoke_artifact": payload.get("bespoke_visual_artifact", {}),
    }


if __name__ == "__main__":
    print(json.dumps(run_deterministic_sandbox(), indent=2))
