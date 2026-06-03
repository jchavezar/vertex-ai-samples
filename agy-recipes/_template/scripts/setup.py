# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-auth",
#     "requests",
# ]
# ///
"""
Setup script template for Antigravity recipes.
Provisions necessary resources and saves details to last_setup_resources.json.
"""
import os
import sys
import json
import google.auth
import google.auth.transport.requests

# 1. Configurations with Env Overrides and Defaults
PROJECT_ID = os.environ.get("GCP_PROJECT", "vtxdemos")
PROJECT_NUMBER = os.environ.get("GCP_PROJECT_NUMBER", "254356041555")
LOCATION = os.environ.get("GCP_LOCATION", "global")
RESOURCE_FILE = "last_setup_resources.json"

# Helper to get authenticated GCP headers
def get_gcp_headers():
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": PROJECT_ID
    }

def main():
    print("====================================================")
    print("  GCP Recipe Setup Execution")
    print("====================================================")
    print(f"  Project ID:     {PROJECT_ID}")
    print(f"  Project Number: {PROJECT_NUMBER}")
    print(f"  Location:       {LOCATION}")
    print("====================================================")

    # Dictionary to keep track of created resources for teardown
    resources = {
        "project_id": PROJECT_ID,
        # Add keys for created resources here (e.g., "bucket_name": bucket_name)
    }

    try:
        # TODO: Implement API enablement check or trigger
        print("[*] Verifying APIs...")

        # TODO: Implement resource creation
        print("[*] Creating resources...")
        
        # Example:
        # bucket_name = f"my-bucket-{PROJECT_ID}"
        # resources["bucket_name"] = bucket_name
        
        print("[+] Setup completed successfully!")
        
        # Save resource details for teardown
        with open(RESOURCE_FILE, "w") as f:
            json.dump(resources, f, indent=2)
        print(f"[*] Resource configurations saved to {RESOURCE_FILE}")

    except Exception as e:
        print(f"[!] Setup failed with error: {e}")
        # Even if setup fails, save what was created so teardown can clean it up
        if resources:
            with open(RESOURCE_FILE, "w") as f:
                json.dump(resources, f, indent=2)
        sys.exit(1)

if __name__ == "__main__":
    main()
