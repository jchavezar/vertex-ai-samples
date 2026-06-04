# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
#     "google-auth",
# ]
# ///
"""
Test script to call streamAssist and verify GCS search results.
Can run using ADC (Application Default Credentials) or WIF token.
"""
import os
import sys
import json
import requests
import google.auth
import google.auth.transport.requests

# Load .env file dynamically if present
_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ[_k.strip()] = _v.strip().strip('"').strip("'")

# Configurations
PROJECT_ID = os.environ.get("GCP_PROJECT", "vtxdemos")
PROJECT_NUMBER = os.environ.get("GCP_PROJECT_NUMBER", "254356041555")
LOCATION = os.environ.get("GCP_LOCATION", "global")
RESOURCE_FILE = "last_setup_resources.json"

# STS / WIF details (from our active setup)
WIF_POOL_ID = "sp-wif-pool-v2"
WIF_PROVIDER_ID = "entra-provider"

def get_gcp_token_adc():
    """Get standard GCP ADC token."""
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token

def exchange_wif_token(ms_jwt):
    """Exchange Entra JWT for WIF token."""
    print(f"[*] Exchanging Microsoft JWT for WIF token using pool={WIF_POOL_ID}...")
    url = "https://sts.googleapis.com/v1/token"
    payload = {
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{WIF_POOL_ID}/providers/{WIF_PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": ms_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:id_token"
    }
    resp = requests.post(url, json=payload, timeout=15)
    if resp.ok:
        token = resp.json().get("access_token")
        print(f"[+] WIF Token exchanged successfully (len={len(token)})")
        return token
    else:
        print(f"[!] WIF exchange failed ({resp.status_code}): {resp.text}")
        return None

def load_resources():
    if not os.path.exists(RESOURCE_FILE):
        print(f"[!] {RESOURCE_FILE} not found. Ensure setup.py was run.")
        return None
    with open(RESOURCE_FILE, "r") as f:
        return json.load(f)

def run_search(gcp_token, query, engine_id, datastore_id, mode_label):
    print(f"\n[*] Querying streamAssist using [{mode_label}] identity...")
    print(f"    Query: '{query}'")
    
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{engine_id}/assistants/default_assistant:streamAssist"
    
    headers = {
        "Authorization": f"Bearer {gcp_token}",
        "Content-Type": "application/json",
        "x-goog-user-project": PROJECT_ID
    }
    
    # We restrict search specifically to our test datastore
    payload = {
        "query": {"text": query},
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [{
                    "dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/{datastore_id}"
                }]
            }
        }
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if not resp.ok:
        print(f"[!] streamAssist call failed ({resp.status_code}): {resp.text}")
        return False
        
    try:
        chunks = resp.json()
    except Exception:
        print(f"[!] Response is not JSON. Raw body: {resp.text[:500]}")
        return False
        
    print(f"[+] Received {len(chunks)} stream response chunks.")
    
    answer_parts = []
    sources = []
    
    for chunk in chunks:
        # Extract text reply
        for reply in chunk.get("answer", {}).get("replies", []):
            content = reply.get("groundedContent", {}).get("content", {})
            text = content.get("text", "")
            is_thought = content.get("thought", False)
            if text and not is_thought:
                answer_parts.append(text)
                
            # Extract citations
            grounding = reply.get("groundedContent", {}).get("textGroundingMetadata", {})
            for ref in grounding.get("references", []):
                doc = ref.get("documentMetadata", {})
                sources.append({
                    "title": doc.get("title", "Document"),
                    "url": doc.get("uri", "")
                })
                
    answer = "".join(answer_parts)
    print("\n--- streamAssist Answer ---")
    print(answer or "No answer returned.")
    print("---------------------------")
    
    if sources:
        print("\n--- Citations (Grounded Sources) ---")
        seen = set()
        for s in sources:
            key = f"{s['title']}-{s['url']}"
            if key not in seen:
                seen.add(key)
                print(f"  * {s['title']} -> {s['url']}")
        print("------------------------------------")
    else:
        print("\n[!] No grounded sources found in the response. Answer is not grounded on GCS.")
        
    return True

def main():
    resources = load_resources()
    if not resources:
        sys.exit(1)
        
    datastore_id = resources.get("datastore_id")
    engine_id = resources.get("engine_id")
    
    query = "Summarize the key financial highlights from the document."
    if len(sys.argv) > 1:
        # If user passed custom query as arguments
        query = " ".join(sys.argv[1:])
        
    # Check if we should use WIF
    wif_token_path = "/tmp/entra_token.txt"
    gcp_token = None
    mode = "ADC"
    
    if os.path.exists(wif_token_path):
        print(f"[+] Found Entra JWT at {wif_token_path}.")
        try:
            with open(wif_token_path, "r") as f:
                entra_jwt = f.read().strip()
            gcp_token = exchange_wif_token(entra_jwt)
            if gcp_token:
                mode = "WIF"
        except Exception as e:
            print(f"[!] Failed to read/exchange Entra JWT: {e}")
            
    if not gcp_token:
        print("[*] Falling back to standard GCP ADC credentials.")
        gcp_token = get_gcp_token_adc()
        
    if not gcp_token:
        print("[!] No credentials found. Run 'gcloud auth login' or put Microsoft JWT in /tmp/entra_token.txt")
        sys.exit(1)
        
    run_search(gcp_token, query, engine_id, datastore_id, mode)

if __name__ == "__main__":
    main()
