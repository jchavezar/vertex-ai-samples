import uvicorn
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from fastapi.responses import StreamingResponse
import requests
import google.auth
from google.auth.transport.requests import Request
from chat_agent import get_chat_stream
import os

app = FastAPI(
    title="Nexus Search Academy API",
    description="Educational API for teaching AuthN/AuthZ and Search flows.",
    version="3050.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, use specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    prompt: str

class ChatRequest(BaseModel):
    query: str
    context: List[dict]

@app.get("/api/status")
def get_status():
    return {
        "status": "online",
        "system": "Nexus Academy Core",
        "epoch": "3050",
        "auth_mode": "Workload Identity Federation (Simulated)"
    }

@app.get("/api/tutorial/steps")
def get_steps():
    """Returns the list of educational steps for the AuthN/AuthZ flow."""
    return [
        {
            "id": 1,
            "title": "The Identity Origin",
            "description": "It all starts with your Enterprise identity. Before touching Google Cloud, we need to verify who you are via Microsoft Entra ID.",
            "icon": "Shield",
            "under_the_hood": {
                "language": "javascript",
                "code": "// Step 1: Login to get Entra ID Token\nconst token = await msalInstance.acquireTokenSilent({ scopes: ['User.Read'] });"
            }
        },
        {
            "id": 2,
            "title": "Workload Identity Federation (STS)",
            "description": "Google Cloud exchanges the Entra ID token for a short-lived Google Token. This is the core of WIF.",
            "icon": "RefreshCw",
            "under_the_hood": {
                "language": "python",
                "code": "# Step 2: STS Token Exchange\nresponse = requests.post('https://sts.googleapis.com/v1/token', json={...})"
            }
        },
        {
            "id": 3,
            "title": "The Google Access Token",
            "description": "We now have a federated Google Access Token scoped strictly to IAM bindings.",
            "icon": "Key",
            "under_the_hood": {
                "language": "json",
                "code": "{\n  \"issuer\": \"sts.googleapis.com\",\n  \"scope\": \"https://www.googleapis.com/auth/cloud-platform\"\n}"
            }
        },
        {
            "id": 4,
            "title": "Backend Metadata Brokerage",
            "description": "The backend elevates credentials exclusively to read Administrative Configurations (`widgetConfigs`) avoids authorization lookup failures securely.",
            "icon": "Shield",
            "under_the_hood": {
                "language": "python",
                "code": "# Step 4: Elevated admin configuration fetch\nadmin_creds, _ = google.auth.default()\nds_resp = requests.get(ds_url, headers={'Authorization': f'Bearer {admin_creds.token}'})"
            }
        },
        {
            "id": 5,
            "title": "The Quantum Search Call",
            "description": "The backend carries ultimate Streams utilizing the USER's token securely back into Vertex AI for optimal security trimming compliance.",
            "icon": "Sparkles",
            "under_the_hood": {
                "language": "python",
                "code": "# Step 5: streamAssist execution\nheaders = { 'Authorization': f'Bearer {user_token}' }\nresponse_stream = requests.post(url, headers=headers, json=payload)"
            }
        }
    ]

@app.post("/api/simulate/query")
def simulate_query(request: QueryRequest):
    """Simulates a Vertex AI Search response with verbose educational payloads."""
    prompt = request.prompt.lower()
    
    # Simulated Response Structure replicating VAIS Grounding
    response_data = {
        "query": request.prompt,
        "timestamp": "3050-03-19T00:00:00Z",
        "call_payload": {
            "url": "https://discoveryengine.googleapis.com/v1alpha/projects/PROJECT_ID/locations/global/dataStores/DATASTORE_ID/servingConfigs/default_serving_config:search",
            "method": "POST",
            "headers": {
                "Authorization": "Bearer ya29_SIMULATED_FLOW_TOKEN",
                "Content-Type": "application/json"
            },
            "body": {
                "query": request.prompt,
                "servingConfig": "default_serving_config",
                "pageSize": 10,
                "contentSearchSpec": {
                    "snippetSpec": {"maxSnippetCount": 1},
                    "extractiveContentSpec": {"maxExtractiveAnswerCount": 1}
                }
            }
        },
        "response_payload": {
            "answer": "Based on current quantum data streams, the role requires significant memory allocation.",
            "grounding": [
                {
                    "id": "doc_001",
                    "title": "Quantum HR Guidelines 3050",
                    "snippet": "...CFO salary ranges from 5,000 to 10,000 Credits per cycle depending on quantum yield...",
                    "source": "SharePoint (Federated)"
                }
            ]
        }
    }
    
    # Custom response for a known query to make it feel interactive
    if "cfo" in prompt or "salary" in prompt:
        response_data["response_payload"]["answer"] = "The typical CFO salary ranges from 5,000 to 10,000 Credits per cycle, based on recent HR metrics."
        response_data["response_payload"]["grounding"][0]["snippet"] = "...CFO salary ranges from 5,000 to 10,000 Credits per cycle depending on quantum yield..."
    elif "sharepoint" in prompt:
        response_data["response_payload"]["answer"] = "SharePoint integration is fully operational via the STS token exchange pipeline."
        
    return response_data

@app.post("/api/chat/stream")
def chat_stream(request: ChatRequest):
    """Streams responses for the academy overlay chat utilizing telemetry logs."""
    return StreamingResponse(
        get_chat_stream(request.query, request.context),
        media_type="text/event-stream"
    )

@app.post("/api/stream/assist")
def stream_assist(request: ChatRequest, authorization: str = Header(None)):
    """Acts as a proxy endpoint with elevated token privileges to look up widget config grounding."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.split(" ")[1] if " " in authorization else authorization

    # lookup high privileges admin_creds to populate widgetConfigs DataStore buckets
    try:
        admin_creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        if not admin_creds.valid:
            admin_creds.refresh(Request())
        admin_token = admin_creds.token
    except Exception:
        admin_token = token

    PROJECT_NUMBER = "REDACTED_PROJECT_NUMBER"
    LOCATION = "global"
    ENGINE_ID = "deloitte-demo"

    # Fetch DataStores dynamically
    ds_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/widgetConfigs/default_search_widget_config"
    ds_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER
    }
    dataStoreSpecs = []
    try:
        ds_resp = requests.get(ds_url, headers=ds_headers, timeout=10)
        if ds_resp.status_code == 200:
            collections = ds_resp.json().get('collectionComponents', [{}])
            dataStoreSpecs = [
                {'dataStore': r['name']}
                for r in collections[0].get('dataStoreComponents', [])
            ]
    except Exception:
        pass

    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER,
        "Accept": "text/event-stream"
    }
    payload = {
        "query": { "text": request.query }
    }
    if dataStoreSpecs:
        payload["toolsSpec"] = {
            "vertexAiSearchSpec": { "dataStoreSpecs": dataStoreSpecs }
        }
    else:
         DATA_STORE_ID = "5817ee80-82a4-49e3-a19c-2cedc73a6300"
         payload["toolsSpec"] = {
             "vertexAiSearchSpec": {
                 "dataStoreSpecs": [{ "dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/{DATA_STORE_ID}" }]
             }
         }

    response_stream = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
    
    def generate():
        for chunk in response_stream.iter_content(chunk_size=1024):
            if chunk:
                yield chunk

    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
