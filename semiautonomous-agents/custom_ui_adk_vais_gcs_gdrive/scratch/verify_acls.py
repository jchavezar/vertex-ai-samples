import google.auth
import google.auth.transport.requests
import requests
import json

def verify():
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    engine_id = "csearch-gdrive-acl_1780275206896"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    url = (
        f"https://discoveryengine.googleapis.com/v1alpha"
        f"/projects/{proj_num}/locations/global"
        f"/collections/default_collection/engines/{engine_id}"
        f"/servingConfigs/default_search:search"
    )
    
    # We query for Alphabet first
    queries = ["Alphabet", "Amazon", "Microsoft", "Meta", "annual report"]
    
    for query in queries:
        request_body = {
            "query": query,
            "pageSize": 10,
            "spellCorrectionSpec": {"mode": "AUTO"},
            "contentSearchSpec": {
                "snippetSpec": {"returnSnippet": True}
            }
        }
        
        r = requests.post(url, headers=headers, json=request_body)
        print(f"\n==========================================")
        print(f"QUERY: '{query}'")
        print(f"Status: {r.status_code}")
        if r.status_code != 200:
            print("Error:", r.text)
            continue
            
        data = r.json()
        results = data.get("results", [])
        print(f"Total results returned: {len(results)}")
        for i, item in enumerate(results):
            doc = item.get("document", {})
            doc_id = doc.get("id")
            derived = doc.get("derivedStructData", {})
            title = derived.get("title") or doc.get("name", "").split("/")[-1]
            link = derived.get("link", "")
            source = "GCS" if "gs://" in link or "gcs-fin" in doc.get("name", "") else "Drive"
            print(f"  {i+1}. [{source}] Title: {title} (ID: {doc_id})")

if __name__ == "__main__":
    verify()
