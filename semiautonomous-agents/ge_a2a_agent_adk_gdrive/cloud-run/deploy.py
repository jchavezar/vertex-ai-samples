"""Deploy the Cloud Run-hosted A2A agent.

Two-pass deploy:
  1. `gcloud run deploy --source .` — initial build + push.
  2. `gcloud run services update --update-env-vars PUBLIC_A2A_URL=<url>` —
     so the agent card returned at /v1/card reports the canonical run.app URL
     back to GE.

Writes the resolved URL into .env as A2A_URL_CR.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv, set_key

HERE = Path(__file__).resolve().parent
ENV_FILE = HERE / ".env"
load_dotenv(ENV_FILE)

SERVICE = "ge-a2a-auth-cr"


def _gcloud_deploy(*args: str) -> str:
    cmd = ["gcloud", *args, "--format=value(status.url)"]
    print("$", " ".join(cmd))
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(proc.stderr, end="", file=sys.stderr)
    return proc.stdout.strip()


def main() -> None:
    project = os.environ["PROJECT_ID"]
    region = os.environ.get("LOCATION", "us-central1")

    url = _gcloud_deploy(
        "run", "deploy", SERVICE,
        f"--project={project}",
        f"--region={region}",
        f"--source={HERE}",
        "--allow-unauthenticated",
        "--memory=1Gi",
        "--cpu=1",
        "--max-instances=3",
        "--port=8080",
        "--quiet",
    )
    if not url:
        raise SystemExit("gcloud returned no URL")
    print(f"Deployed: {url}")

    print("Updating service with PUBLIC_A2A_URL env var...")
    subprocess.run([
        "gcloud", "run", "services", "update", SERVICE,
        f"--project={project}",
        f"--region={region}",
        f"--update-env-vars=PUBLIC_A2A_URL={url}",
        "--quiet",
    ], check=True)
    print(f"PUBLIC_A2A_URL={url}")

    set_key(str(ENV_FILE), "A2A_URL_CR", url)
    print(f"Wrote A2A_URL_CR to {ENV_FILE.name}")


if __name__ == "__main__":
    try:
        main()
    except KeyError as e:
        raise SystemExit(f"Missing env var: {e}")
