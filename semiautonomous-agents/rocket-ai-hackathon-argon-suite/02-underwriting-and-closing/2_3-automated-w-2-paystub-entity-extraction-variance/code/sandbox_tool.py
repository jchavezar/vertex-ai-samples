#!/usr/bin/env python3
"""
Standalone Deterministic Sandbox & Bespoke Visual Artifact Runner
Square [2.3]: Automated W-2 & Paystub Entity Extraction & Variance Pipeline
UI Archetype: docai_paystub_w2_ocr_inspector (Google Cloud Document AI // W-2 & Paystub OCR Bounding-Box & 5% Variance Inspector)
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
        "square_code": "2.3",
        "project_title": payload.get("project_title", "Automated W-2 & Paystub Entity Extraction & Variance Pipeline"),
        "ui_archetype": payload.get("ui_archetype", "docai_paystub_w2_ocr_inspector"),
        "sandbox": verified,
        "bespoke_artifact": payload.get("bespoke_visual_artifact", {}),
    }


if __name__ == "__main__":
    print(json.dumps(run_deterministic_sandbox(), indent=2))
