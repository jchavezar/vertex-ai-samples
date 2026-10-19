#!/usr/bin/env python3
"""
Standalone Deterministic Sandbox & Bespoke Visual Artifact Runner
Square [4.2]: Virtual Staging & Localized Hero Ad Creator
UI Archetype: imagen_virtual_staging_comparator (Nano Banana 2 / Gempix-2 // Interactive Corktown Loft Virtual Staging & TILA Ad Studio)
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
        "square_code": "4.2",
        "project_title": payload.get("project_title", "Virtual Staging & Localized Hero Ad Creator"),
        "ui_archetype": payload.get("ui_archetype", "imagen_virtual_staging_comparator"),
        "sandbox": verified,
        "bespoke_artifact": payload.get("bespoke_visual_artifact", {}),
    }


if __name__ == "__main__":
    print(json.dumps(run_deterministic_sandbox(), indent=2))
