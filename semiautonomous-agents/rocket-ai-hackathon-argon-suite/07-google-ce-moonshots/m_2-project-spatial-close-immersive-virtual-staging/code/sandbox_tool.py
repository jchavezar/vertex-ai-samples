#!/usr/bin/env python3
"""
Standalone Deterministic Sandbox & Bespoke Visual Artifact Runner
Square [M.2]: Project Spatial Close: Immersive Virtual Staging & 3D Neighborhood Hub
UI Archetype: project_spatial_close_3d_homestyle (Project Spatial Close // 3D Royal Oak Neighborhood Solar & Fannie HomeStyle Renovation Hub)
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
        "square_code": "M.2",
        "project_title": payload.get("project_title", "Project Spatial Close: Immersive Virtual Staging & 3D Neighborhood Hub"),
        "ui_archetype": payload.get("ui_archetype", "project_spatial_close_3d_homestyle"),
        "sandbox": verified,
        "bespoke_artifact": payload.get("bespoke_visual_artifact", {}),
    }


if __name__ == "__main__":
    print(json.dumps(run_deterministic_sandbox(), indent=2))
