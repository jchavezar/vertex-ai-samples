#!/usr/bin/env python3
"""
Standalone Deterministic Sandbox & Bespoke Visual Artifact Runner
Square [2.1]: Fannie Mae / Freddie Mac Selling Guide Citation Assistant
UI Archetype: notebooklm_gse_citation_desk (NotebookLM Enterprise & StreamAssist // Fannie B3-3.1 & Freddie 5303 Citation Desk)
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
        "square_code": "2.1",
        "project_title": payload.get("project_title", "Fannie Mae / Freddie Mac Selling Guide Citation Assistant"),
        "ui_archetype": payload.get("ui_archetype", "notebooklm_gse_citation_desk"),
        "sandbox": verified,
        "bespoke_artifact": payload.get("bespoke_visual_artifact", {}),
    }


if __name__ == "__main__":
    print(json.dumps(run_deterministic_sandbox(), indent=2))
