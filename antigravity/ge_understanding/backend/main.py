import os
import json
import logging
import google.auth
from typing import Optional, AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import vertexai
from vertexai.preview import reasoning_engines as agent_engines
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.cloud import discoveryengine_v1alpha as discoveryengine
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../.env")

logger = logging.getLogger("uvicorn")

app = FastAPI(title="GE Understanding Interceptor Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Robust Project Discovery
def get_project_id():
    env_project = os.getenv("PROJECT_ID")
    if env_project:
        return env_project
    try:
        credentials, project_id = google.auth.default()
        return project_id
    except Exception:
        return None

PROJECT_ID = get_project_id()
PROJECT_NUMBER = "254356041555" # Default from user request, but can be updated
LOCATION = os.getenv("LOCATION", "us-central1")

logger.info(f"Initialized with PROJECT_ID: {PROJECT_ID}, LOCATION: {LOCATION}")

# IMPORTANT: Must use gRPC for custom payload streaming to avoid REST parsing errors
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    api_transport="grpc"
)

# The default interceptor engine ID (hardcoded for fallback)
DEFAULT_ENGINE_ID = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/9214561650181406720" if PROJECT_ID else ""

# Initialize ADK Session Service
session_service = InMemorySessionService()

class ChatRequest(BaseModel):
    message: str
    session_id: str
    agent_resource_name: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "GE Understanding proxy running (ADK + gRPC + Streaming enabled)"}

@app.get("/api/agents")
async def list_agents():
    """Lists all Reasoning Engines in the current project/location."""
    try:
        engines = agent_engines.ReasoningEngine.list()
        result = []
        for eng in engines:
            name = eng.resource_name
            # Try to get display_name from attribute or metadata or resource name
            display_name = getattr(eng, "display_name", None)
            if not display_name:
                metadata = eng.to_dict()
                display_name = metadata.get("display_name", name.split("/")[-1])
            
            is_interceptor = ("Interceptor" in display_name or 
                             "interceptor" in display_name.lower() or 
                             "7166831194611384320" in name)
            
            result.append({
                "resource_name": name,
                "display_name": display_name,
                "uid": name.split("/")[-1],
                "isActive": name == DEFAULT_ENGINE_ID,
                "isInterceptor": is_interceptor
            })
        return result
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ge-agents")
async def list_ge_agents(target_engine_id: str = "agentspace-testing_1748446185255"):
    """Lists all agents registered in a specific Gemini Enterprise (Discovery Engine) app."""
    try:
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token
        
        project_number = PROJECT_NUMBER

        # URL to list agents for the specified engine
        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/engines/{target_engine_id}/assistants/default_assistant/agents"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Goog-User-Project": project_number
        }
        
        logger.info(f"Listing GE Agents from: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
             # If the engine doesn't exist or other error, return empty list or specific error
             logger.error(f"Failed to list GE agents: {response.text}")
             if response.status_code == 404:
                 return [] # Return empty if engine not found (or no agents)
             raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        agents = data.get("agents", [])
        
        # Transform for frontend consistency
        result = []
        for agent in agents:
            name = agent.get("name", "")
            display_name = agent.get("displayName", "Unknown GE Agent")
            description = agent.get("description", "")
            
            # Check if this agent is linked to a Reasoning Engine
            reasoning_engine_link = agent.get("adkAgentDefinition", {}).get("provisionedReasoningEngine", {}).get("reasoningEngine", "")

            result.append({
                "resource_name": name,
                "display_name": display_name,
                "description": description,
                "uid": name.split("/")[-1],
                "reasoning_engine_link": reasoning_engine_link,
                "is_ge_agent": True
            })
            
        return result

    except Exception as e:
        logger.error(f"Failed to list GE agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/{resource_id:path}/register-ge")
async def register_ge(resource_id: str, target_engine_id: Optional[str] = None):
    """Registers a Reasoning Engine in Gemini Enterprise (Discovery Engine)."""
    try:
        # 1. Get Access Token
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token

        # Use explicitly provided target engine ID, or fallback to the resource ID (Reasoning Engine UID)
        engine_id = target_engine_id if target_engine_id else resource_id.split("/")[-1]
        
        project_number = PROJECT_NUMBER # Using the one from user request

        # 2. Extract agent info (using agent engines SDK)
        # Note: resource_id (full path) is required here to get the correct agent metadata
        eng = agent_engines.ReasoningEngine(resource_id)
        display_name = getattr(eng, "display_name", f"GE Agent {engine_id}")
        
        # 3. Construct the Discovery Engine API URL for creating an agent
        # We are creating an agent WITHIN the specified engine application
        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/engines/{engine_id}/assistants/default_assistant/agents"
        
        # 4. Construct the agent definition payload
        payload = {
            "displayName": display_name,
            "description": f"Intercepted Agent for {display_name}",
            # Use a verified Google icon
            "icon": {
                "uri": "https://www.gstatic.com/images/branding/product/2x/googleg_48dp.png" 
            },
            "adk_agent_definition": {
                "tool_settings": {
                    "tool_description": "Use this tool to answer user questions."
                },
                "provisioned_reasoning_engine": {
                    "reasoning_engine": resource_id  # This links the GE agent to the actual Reasoning Engine
                }
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",

            "Content-Type": "application/json",
            "X-Goog-User-Project": project_number
        }

        logger.info(f"Registering in GE: {url}")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"GE Registration failed: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        logger.error(f"Failed to register in GE: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/{resource_id:path}/deregister-ge")
async def deregister_ge(resource_id: str):
    """Deregisters an agent from Gemini Enterprise."""
    try:
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token

        engine_id = resource_id.split("/")[-1]
        project_number = PROJECT_NUMBER

        # Note: Discovery Engine Agent ID typically matches the Engine ID or is 'default-agent'
        # We try to delete the agent under this engine.
        agent_id = "default-agent" # This is a guess, usually we'd list agents first
        
        # Guide says format: projects/{number}/locations/global/collections/default_collection/engines/{engine_id}/assistants/default_assistant/agents/{agent_id}
        # But we can also try to delete the library agent if it was created with engine_id as ID.
        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/engines/{engine_id}/assistants/default_assistant/agents/{engine_id}"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Goog-User-Project": project_number
        }

        logger.info(f"Deregistering from GE: {url}")
        response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 204]:
            return {"status": "deregistered"}
        else:
            # Try alternate path with 'default-agent'
            url_alt = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/engines/{engine_id}/assistants/default_assistant/agents/default-agent"
            response_alt = requests.delete(url_alt, headers=headers)
            if response_alt.status_code in [200, 204]:
                return {"status": "deregistered"}
            
            logger.error(f"GE Deregistration failed: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except Exception as e:
        logger.error(f"Failed to deregister from GE: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ge_search")
async def ge_search(request: dict):
    """Proxy for the Gemini Enterprise search API."""
    try:
        query = request.get("query", "hi")
        engine_id = request.get("engine_id")
        # Logic Fix: If engine_id looks like a Reasoning Engine UID (all digits), use the valid Discovery Engine ID
        if not engine_id or engine_id.isdigit() or len(engine_id) > 15:
            engine_id = "agentspace-testing_1748446185255"
            
        project_number = PROJECT_NUMBER

        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token

        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search:search"
        
        payload = {
            "query": query,
            "pageSize": 10,
            "spellCorrectionSpec": {"mode": "AUTO"},
            "languageCode": "en-US",
            "relevanceScoreSpec": {"returnRelevanceScore": True},
            "userInfo": {"timeZone": "America/Mexico_City"},
            "contentSearchSpec": {"snippetSpec": {"returnSnippet": True}},
            "naturalLanguageQueryUnderstandingSpec": {"filterExtractionCondition": "ENABLED"}
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": project_number
        }

        logger.info(f"GE Search: {url} | Header: {headers.get('X-Goog-User-Project')}")
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        logger.error(f"GE Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ge_answer")
async def ge_answer(request: dict):
    """Proxy for the Gemini Enterprise answer API (Conversational Search)."""
    try:
        query = request.get("query", "hi")
        engine_id = request.get("engine_id")
        # Logic Fix: If engine_id looks like a Reasoning Engine UID (all digits), use the valid Discovery Engine ID
        if not engine_id or engine_id.isdigit() or len(engine_id) > 15:
            engine_id = "agentspace-testing_1748446185255"

        project_number = PROJECT_NUMBER

        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token

        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search:answer"
        
        payload = {
            "query": {"text": query},
            "session": request.get("session", ""),
            "relatedQuestionsSpec": {"enable": True},
            "answerGenerationSpec": {
                "ignoreAdversarialQuery": True,
                "ignoreNonAnswerSeekingQuery": False,
                "ignoreLowRelevantContent": True,
                "multimodalSpec": {},
                "includeCitations": True,
                "modelSpec": {"modelVersion": "stable"}
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": project_number
        }

        logger.info(f"GE Answer: {url} | Header: {headers.get('X-Goog-User-Project')}")
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        logger.error(f"GE Answer Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/agents/{resource_id}")
async def delete_agent(resource_id: str):
    """Deletes a Reasoning Engine by its ID or resource name."""
    try:
        # Resource ID can be full path or just the numeric ID
        full_name = resource_id
        if not resource_id.startswith("projects/"):
            full_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{resource_id}"
            
        logger.info(f"Deleting agent: {full_name}")
        eng = agent_engines.ReasoningEngine(full_name)
        eng.delete()
        return {"status": "deleted", "resource_name": full_name}
    except Exception as e:
        logger.error(f"Failed to delete agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Simulates a Gemini Enterprise / ADK client.
    Proxies the request to Vertex AI Agent Engine using gRPC to intercept the payload.
    Returns a Server-Sent Events (SSE) stream.
    """
    logger.info(f"Chat request received: {request.message} for agent: {request.agent_resource_name}")
    engine_id = request.agent_resource_name or DEFAULT_ENGINE_ID
    
    logger.info(f"Targeting Engine ID: {engine_id}")
    
    # Mocking the request_json structure typically sent by Gemini Enterprise
    # to the 'streaming_agent_run_with_events' method.
    simulated_request_json = {
        "contents": [
            {"role": "user", "parts": [{"text": request.message}]}
        ],
        "systemInstruction": {
            "role": "system", 
            "parts": [{"text": "You are a helpful assistant."}]
        },
        "tools": []
    }

    async def event_generator():
        try:
            logger.info(f"Connecting to Agent Engine via ADK Runner: {engine_id}")
            
            # Using the official Reasoning Engine proxy but wrapping it in ADK logic
            # to capture the interceptor payload.
            remote_agent = agent_engines.ReasoningEngine(engine_id)
            
            # ADK Runner integration
            from agent_pkg.agent import interceptor_app
            runner = Runner(
                agent=interceptor_app,
                session_service=session_service,
                app_name="ge_interceptor"
            )

            # We pass the message to the streaming_agent_run_with_events
            # In a real scenario, Gemini Enterprise sends 'request_json' to the Reasoning Engine endpoint.
            # Here we simulate that call using the SDK.
            stream = remote_agent.streaming_agent_run_with_events(
                request_json=json.dumps(simulated_request_json)
            )
            
            logger.info("Stream initialized, starting to yield events...")
            for event in stream:
                logger.info(f"Yielding event: {str(event)[:100]}...")
                # Pretty print the payload if it's the interceptor event
                # The user requested pretty printing because they can't see the full text
                # when it's minified in the HUD.
                if isinstance(event, dict) and "content" in event:
                    text = event["content"].get("parts", [{}])[0].get("text", "")
                    if "Raw `request_json`" in text:
                        try:
                            # Extract the JSON from the markdown code block
                            json_str = text.split("```json\n")[1].split("\n```")[0]
                            parsed_json = json.loads(json_str)
                            pretty_json = json.dumps(parsed_json, indent=2)
                            
                            # Replace the minified JSON with pretty JSON in the event text
                            event["content"]["parts"][0]["text"] = text.replace(json_str, pretty_json)
                            # Add metadata for the UI HUD
                            event["isIntercepted"] = True
                            event["resource_name"] = engine_id
                            event["parsed_payload"] = parsed_json
                            event["method"] = "streaming_agent_run_with_events"
                        except Exception as pe:
                            logger.error(f"Pretty print error: {pe}")

                yield f"data: {json.dumps(event)}\n\n"
                
        except Exception as e:
            logger.error(f"Error in backend stream: {e}")
            yield f"data: {json.dumps({'error': str(e), 'status': 'failed'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/agents/deploy")
async def deploy_agent(request: dict):
    """Deploys a new GEMINIPayloadInterceptor to Vertex AI."""
    try:
        display_name = request.get("display_name", "GEMINIPayloadInterceptor")
        
        from agent_pkg import agent
        import vertexai
        from vertexai.preview import reasoning_engines
        
        # We assume the environment is already initialized in main, but let's be safe
        # STAGING_BUCKET should be defined or we can use a default if needed
        # For this environment, we might need to find the bucket
        
        logger.info(f"Deploying new agent: {display_name}")
        
        agent_obj = agent.GEMINIPayloadInterceptor()
        
        # Initialize Vertex AI with staging bucket
        LOCATION = os.getenv("LOCATION", "us-central1")
        STAGING_BUCKET = os.getenv("STAGING_BUCKET", "gs://deloitte-plantas_cloudbuild")
        vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
        
        # Deploy using reasoning_engines
        new_engine = reasoning_engines.ReasoningEngine.create(
            agent_obj,
            display_name=display_name,
            description=f"GE Interceptor: {display_name}",
            requirements=[
                "google-adk",
                "google-cloud-aiplatform",
                "google-genai",
                "google-cloud-discoveryengine",
                "requests"
            ],
            extra_packages=["agent_pkg"],
        )
        
        return {
            "status": "deployed",
            "resource_name": new_engine.resource_name,
            "display_name": display_name
        }
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
