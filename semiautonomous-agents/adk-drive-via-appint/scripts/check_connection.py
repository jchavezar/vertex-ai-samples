"""
Connection healthcheck. Run this BEFORE running the agent — it tells you
whether your Application Integration + Drive connector chain is wired up.

Usage:
    uv run python scripts/check_connection.py
"""
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Add repo root to import agent module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.agent import _CONN, _execute_action, drive_about  # noqa: E402


def main() -> None:
    print("Connection metadata:")
    print(json.dumps(_CONN, indent=2))
    print()

    print("=== drive.about.get ===")
    out = drive_about()
    print(json.dumps(out, indent=2)[:1500])
    print()

    if "error" in out:
        print("FAIL: connection runtime is not healthy.")
        print("Likely fixes:")
        print(" 1. Re-create the connection with OAuth user-flow auth (your account)")
        print("    rather than the Compute SA service-account auth, since the SA")
        print("    has no Drive content of its own.")
        print(" 2. Alternatively, grant the SA domain-wide delegation in Workspace")
        print("    admin and impersonate a target user.")
        print(" 3. Check Cloud Logging filtered by:")
        print(f"    resource.type=\"integrations.googleapis.com/Integration\"")
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
