# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.27.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""Idempotent setup and verification script for Legacy to AI Modernization Hub."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ID = os.getenv("GCP_PROJECT", "vtxdemos")
BASE_DIR = Path(__file__).resolve().parent.parent
TRACKER_FILE = BASE_DIR / "last_setup_resources.json"
REPO_ROOT = BASE_DIR.parent.parent
APP_DIR = REPO_ROOT / "semiautonomous-agents" / "legacy-to-ai-modernization-hub"

def main():
    print("===============================================================")
    print("⚡ [SETUP] Antigravity Legacy to AI Modernization Hub")
    print("===============================================================")
    print(f"GCP Project Context: {PROJECT_ID}")
    print(f"Application Root:    {APP_DIR}")

    resources = {
        "project_id": PROJECT_ID,
        "backend_port": int(os.getenv("PORT", "8008")),
        "frontend_port": int(os.getenv("FRONTEND_PORT", "5178")),
        "setup_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "components": [
            "FastAPI Backend (app.main)",
            "React 19 Generative Canvas Frontend",
            "50ms Shock Engine",
            "Antigravity 3-Stage Autonomous Refactor Stream",
            "Gemini 2.5/3 Agent Service"
        ]
    }

    # Verify App Directory exists
    if not APP_DIR.exists():
        print(f"❌ Error: App directory {APP_DIR} does not exist!")
        sys.exit(1)

    print("✅ Verified application directory structure.")

    # Save Tracker JSON
    with open(TRACKER_FILE, "w") as f:
        json.dump(resources, f, indent=2)

    print(f"✅ State tracker recorded at: {TRACKER_FILE}")
    print("===============================================================")
    print("🌟 Setup verified! Launch application with ./start.sh")
    print("===============================================================")

if __name__ == "__main__":
    main()
