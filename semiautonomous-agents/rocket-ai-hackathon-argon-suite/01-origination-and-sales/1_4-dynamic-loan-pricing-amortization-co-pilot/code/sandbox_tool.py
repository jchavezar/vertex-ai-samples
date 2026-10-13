#!/usr/bin/env python3
"""
Deterministic gVisor Sandbox & Bespoke Visual Artifact Generator for Square [1.4]: Dynamic Loan Pricing & Amortization Co-Pilot
"""
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shared.auth_and_vertex import run_sandbox_action
from shared.bespoke_apps import get_rich_structured_artifact

if __name__ == "__main__":
    mock_path = Path(__file__).resolve().parent.parent / "mock_data" / "sample_payload.json"
    data = json.loads(mock_path.read_text(encoding="utf-8"))
    sb = run_sandbox_action(data.get("sandbox_action", "default"), data.get("sandbox_params", {}))
    art = get_rich_structured_artifact("1.4", sb)
    print(json.dumps({"sandbox": sb, "bespoke_artifact": art}, indent=2))
