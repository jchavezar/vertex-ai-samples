import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from fastapi.responses import StreamingResponse
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
                "code": "// Step 1: Implicit Flow or Auth Code flow to get Entra ID Token\nconst token = await msalInstance.acquireTokenSilent({\n  scopes: ['User.Read', 'Sites.Read.All']\n});\nconsole.log('Entra ID JWT:', token.accessToken);"
            }
        },
        {
            "id": 2,
            "title": "Workload Identity Federation (STS)",
            "description": "Google Cloud doesn't trust Entra ID by default. We use Security Token Service (STS) to exchange the Entra ID token for a short-lived Google Token.",
            "icon": "RefreshCw",
            "under_the_hood": {
                "language": "python",
                "code": "# Step 2: STS Token Exchange\nresponse = requests.post(\n    'https://sts.googleapis.com/v1/token',\n    json={\n        'audience': '//iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID',\n        'grantType': 'urn:ietf:params:oauth:grant-type:token-exchange',\n        'requestedTokenType': 'urn:ietf:params:oauth:token-type:access_token',\n        'subjectToken': entra_id_token,\n        'subjectTokenType': 'urn:ietf:params:oauth:token-type:jwt'\n    }\n)\nsa_token = response.json()['access_token']"
            }
        },
        {
            "id": 3,
            "title": "The Google Access Token",
            "description": "We now have a federated Google Access Token. This token is scoped ONLY to what the IAM binding allows for that federated identity.",
            "icon": "Key",
            "under_the_hood": {
                "language": "json",
                "code": "{\n  \"issuer\": \"sts.googleapis.com\",\n  \"audience\": \"//iam.googleapis.com/...\",\n  \"scope\": \"https://www.googleapis.com/auth/cloud-platform\",\n  \"expires_in\": 3600\n}"
            }
        },
        {
            "id": 4,
            "title": "The Quantum Search Call",
            "description": "With the Google Token, we call Vertex AI Search. We pass the query and the token, and Vertex returns grounded answers from SharePoint.",
            "icon": "Sparkles",
            "under_the_hood": {
                "language": "python",
                "code": "# Step 4: Vertex AI Search Call\nclient = discoveryengine.SearchServiceClient(credentials=credentials)\nrequest = discoveryengine.SearchRequest(\n    serving_config='projects/.../servingConfigs/default_search',\n    query='What is the CFO salary?',\n    content_search_spec={\n        'snippet_spec': {'max_snippet_count': 5}\n    }\n)"
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
