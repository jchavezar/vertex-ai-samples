#!/usr/bin/env python3
import os
import sys
import urllib.request
import urllib.error
import json
import re

print("=== ANTIGRAVITY ACTIVE BROWSING VERIFIER ===")

# 1. Load Environment from .env
env_vars = {}
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip()

project = env_vars.get("GOOGLE_CLOUD_PROJECT", "")
if not project:
    import subprocess
    try:
        res = subprocess.check_output("gcloud config get-value project", shell=True, stderr=subprocess.DEVNULL)
        project = res.decode("utf-8").strip()
    except Exception:
        pass

location = env_vars.get("GOOGLE_CLOUD_LOCATION", "us-central1")
search_backend = env_vars.get("SEARCH_BACKEND", "vector-search")

# 2. Resolve Deployed URL
url = env_vars.get("APP_URL", "")
if not url:
    print(f"[INFO] No APP_URL found in .env. Attempting to query Cloud Run in project '{project}'...")
    try:
        import subprocess
        cmd = f"gcloud run services describe envato-vibe-app --region={location} --project={project} --format='value(status.url)'"
        res = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        url = res.decode("utf-8").strip()
    except Exception:
        pass

if not url:
    print("[ERROR] Could not resolve Cloud Run service URL. Please make sure the service is deployed and run again.")
    sys.exit(1)

print(f"[INFO] Targeting live URL: {url}")

# 3. Test Root Path Page Rendering
print("\n--- 1. Testing Homepage Response ---")
import ssl
ssl_context = ssl._create_unverified_context()

try:
    req = urllib.request.Request(url, headers={"User-Agent": "Antigravity Active Browser/1.0"})
    with urllib.request.urlopen(req, context=ssl_context) as response:
        html = response.read().decode("utf-8")
        status = response.status
        print(f"[OK] Homepage returned status code {status}")
        
        # Verify premium title or content
        if "index_v2.html" in html or "styles_v2.css" in html or "app_v2.js" in html:
            print("[OK] Homepage served correctly with high-fidelity asset links.")
        else:
            print("[WARNING] Page served successfully but does not contain typical Shutter Vibe assets.")
except urllib.error.HTTPError as e:
    print(f"[ERROR] Homepage returned error code: {e.code}")
    print("This might indicate that the FastAPI templates directory was not packaged or mounted correctly.")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Failed to fetch homepage: {e}")
    sys.exit(1)

# 4. Test API Health Endpoint
print("\n--- 2. Testing API Health ---")
health_url = f"{url}/api/health"
try:
    with urllib.request.urlopen(health_url, context=ssl_context) as response:
        data = json.loads(response.read().decode("utf-8"))
        print(f"[OK] API Health returned status {response.status}")
        print(f"[INFO] Health Status Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"[WARNING] API Health check failed or endpoint not found: {e}")

# 5. Test Live Search Route and Diagnostics
print("\n--- 3. Testing Live Search Modality & Infrastructure Connection ---")
search_test_url = f"{url}/api/search?q=test&modality=all&limit=4"
try:
    with urllib.request.urlopen(search_test_url, context=ssl_context) as response:
        data = json.loads(response.read().decode("utf-8"))
        print(f"[OK] Search API succeeded with status {response.status}")
        print(f"[INFO] Search results returned successfully.")
except urllib.error.HTTPError as e:
    print(f"[DIAGNOSTIC] Search API failed with code: {e.code}")
    try:
        err_body = e.read().decode("utf-8")
        print(f"[DIAGNOSTIC] Server Exception Details: {err_body}")
    except Exception:
        pass
    
    print("\n[IMPORTANT DIAGNOSTIC GUIDANCE]")
    print(f"Current search backend in .env: {search_backend}")
    if search_backend == "vector-search":
        print("-> The 'vector-search' backend uses the high-performance Vertex AI Vector Search endpoint.")
        print("-> If you have not created or deployed an Index Endpoint named 'envato-vibe-endpoint', search queries will FAIL with a 500 error.")
        print("-> SUGGESTION: Switch to the serverless, cost-free BigQuery search backend to get up and running instantly!")
        print("   To do this, edit your `.env` file:")
        print("   SEARCH_BACKEND=bigquery")
        print("   Then run your deployment workflow again to redeploy the app server.")
except Exception as e:
    print(f"[ERROR] Failed to execute search query: {e}")

print("\n=== VERIFICATION COMPLETE ===")
