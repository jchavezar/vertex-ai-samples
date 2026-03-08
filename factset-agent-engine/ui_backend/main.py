import os
import base64
import time
import json
import httpx
import uvicorn
import urllib.parse
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Vertex AI Agent Engine
import vertexai
from vertexai.agent_engines import AgentEngine
from google.genai import types

load_dotenv()

app = FastAPI(title="FactSet UI Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
FS_CLIENT_ID = os.getenv("FS_CLIENT_ID")
FS_CLIENT_SECRET = os.getenv("FS_CLIENT_SECRET")
FS_REDIRECT_URI = os.getenv("FS_REDIRECT_URI", "http://localhost:8001/auth/callback")
FS_AUTH_URL = "https://auth.factset.com/as/authorization.oauth2"
FS_TOKEN_URL = "https://auth.factset.com/as/token.oauth2"

# In-memory token store
token_store = {}

# Initialize Vertex AI
PROJECT_ID = os.getenv("PROJECT_ID", "vtxdemos")
LOCATION = os.getenv("LOCATION", "us-central1")
AGENT_ENGINE_NAME = os.getenv("AGENT_ENGINE_NAME", "factset_root_agent")

vertexai.init(project=PROJECT_ID, location=LOCATION)

@app.get("/auth/url")
def get_auth_url():
    params = {
        "response_type": "code",
        "client_id": FS_CLIENT_ID,
        "redirect_uri": FS_REDIRECT_URI,
        "scope": "mcp",
        "prompt": "consent"
    }
    return {"url": f"{FS_AUTH_URL}?{urllib.parse.urlencode(params)}"}

@app.get("/auth/callback")
async def auth_callback(code: str):
    auth_str = f"{FS_CLIENT_ID}:{FS_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth}", "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"grant_type": "authorization_code", "code": code, "redirect_uri": FS_REDIRECT_URI}
    async with httpx.AsyncClient() as client:
        resp = await client.post(FS_TOKEN_URL, data=payload, headers=headers)
        if resp.status_code == 200:
            tokens = resp.json()
            token_store["latest"] = tokens.get("access_token")
            return RedirectResponse(os.getenv("FRONTEND_URL", "http://localhost:5173/"))
        return {"error": resp.text}

@app.get("/auth/token")
def get_token():
    return {"token": token_store.get("latest")}

class ChatPayload(BaseModel):
    message: str
    token: str

@app.post("/chat")
async def chat_proxy(payload: ChatPayload):
    """
    Calls the deployed Agent Engine on Vertex AI.
    """
    try:
        # Find the engine
        client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
        engines = list(client.agent_engines.list())
        engine_resource = next((e for e in engines if e.api_resource.display_name == AGENT_ENGINE_NAME), None)
        
        if not engine_resource:
            raise HTTPException(status_code=404, detail="Agent Engine not found.")

        engine = AgentEngine(engine_resource.api_resource.name)
        
        # Prepare the query with state injection
        # We pass the token in the session state 'token'
        query = payload.message
        state = {"token": payload.token}
        
        # Call the engine
        response = engine.query(
            input=query,
            state=state
        )
        
        # Extract the text response
        # Assuming the response is an AdkApp response structure
        return {"message": response.response}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
