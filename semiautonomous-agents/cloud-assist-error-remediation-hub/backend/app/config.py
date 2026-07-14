import os
import subprocess
from dotenv import load_dotenv

# Enforce override=True per mandatory python backend rules
load_dotenv(override=True)

def get_default_gcp_project() -> str:
    proj = os.getenv("GCP_PROJECT_ID")
    if proj:
        return proj
    try:
        res = subprocess.run(["gcloud", "config", "get-value", "project"], capture_output=True, text=True, check=False)
        if res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "vtxdemos"

GCP_PROJECT_ID = get_default_gcp_project()
GCP_REGION = os.getenv("GCP_REGION", "us-central1")
PORT = int(os.getenv("PORT", "8088"))
