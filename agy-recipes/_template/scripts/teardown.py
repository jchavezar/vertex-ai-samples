# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-auth",
#     "requests",
# ]
# ///
"""
Teardown script template for Antigravity recipes.
Loads resources from last_setup_resources.json and destroys them.
"""
import os
import sys
import json
import google.auth
import google.auth.transport.requests

PROJECT_ID = os.environ.get("GCP_PROJECT", "vtxdemos")
RESOURCE_FILE = "last_setup_resources.json"

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
    print("  GCP Recipe Teardown Execution")
    print("====================================================")

    if not os.path.exists(RESOURCE_FILE):
        print(f"[!] {RESOURCE_FILE} not found. Nothing to tear down.")
        sys.exit(0)

    try:
        with open(RESOURCE_FILE, "r") as f:
            resources = json.load(f)
    except Exception as e:
        print(f"[!] Failed to read {RESOURCE_FILE}: {e}")
        sys.exit(1)

    print(f"[*] Loaded tracking config. Cleaning up resources...")
    errors_encountered = False

    # TODO: Implement resource deletion based on loaded tracker
    # Example:
    # bucket_name = resources.get("bucket_name")
    # if bucket_name:
    #     try:
    #         print(f"[*] Deleting bucket: {bucket_name}")
    #         # Delete logic
    #     except Exception as e:
    #         print(f"[!] Failed to delete bucket: {e}")
    #         errors_encountered = True

    if not errors_encountered:
        print("\n[+] Teardown completed successfully!")
        if os.path.exists(RESOURCE_FILE):
            os.remove(RESOURCE_FILE)
            print(f"[*] Removed {RESOURCE_FILE}")
        sys.exit(0)
    else:
        print("\n[!] Teardown completed with errors. Some resources might still exist.")
        sys.exit(1)

if __name__ == "__main__":
    main()
