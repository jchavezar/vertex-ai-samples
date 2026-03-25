import os
import json
import logging
from typing import AsyncGenerator
from dotenv import load_dotenv

# Load environment variables robustly
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path=dotenv_path)

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
from google.genai import types

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from agents.router_agent import get_router_agent
from agents.agent import get_servicenow_agent_with_mcp_tools
from google.adk.tools import VertexAiSearchTool

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI()

# Initialize Session Service (Vertex AI if AGENT_ENGINE_ID is set, else In-Memory)
try:
    from google.adk.sessions.vertex_ai_session_service import VertexAiSessionService
    agent_engine_id = os.environ.get("AGENT_ENGINE_ID")
    if agent_engine_id:
        logger.info(f"Using VertexAiSessionService with ID: {agent_engine_id}")
        session_service = VertexAiSessionService(engine_id=agent_engine_id)
    else:
        logger.info("AGENT_ENGINE_ID not set. Using InMemorySessionService fallback.")
        session_service = InMemorySessionService()
except ImportError:
    logger.warning("VertexAiSessionService could not be imported. Using InMemorySessionService fallback.")
    session_service = InMemorySessionService()

async def get_or_create_session(app_name: str, session_id: str):
    try:
        session = await session_service.get_session(app_name=app_name, user_id="default_user", session_id=session_id)
        if session:
            return session
    except Exception:
        pass
    
    try:
        session = await session_service.create_session(app_name=app_name, user_id="default_user", session_id=session_id)
        return session
    except Exception as e:
        logger.error(f"Failed to create session {session_id}: {e}")
        # fallback
        return await session_service.create_session(app_name=app_name, user_id="default_user")


class ChatRequest(BaseModel):
    prompt: str
    session_id: str

@app.post("/api/chat")
async def chat_stream(request: ChatRequest, raw_request: Request):
    """
    Main Chat Stream Endpoint.
    Routes user query to either Discovery Engine or ServiceNow MCP.
    """
    logger.info(f"Received chat request for session {request.session_id}")
    
    auth_header = raw_request.headers.get("Authorization")
    bearer_token = None
    if auth_header and auth_header.startswith("Bearer "):
        bearer_token = auth_header.split(" ")[1]
        
    prompt = request.prompt # Captured by _stream closure
    
    async def _stream() -> AsyncGenerator[str, None]:
        # 1. Evaluate Intent using Router Agent
        router = get_router_agent()
        runner = Runner(app_name="light_portal_router", agent=router, session_service=session_service)
        
        # Ensure session exists
        await get_or_create_session("light_portal_router", request.session_id)
        
        # We run the router and get the classification result
        msg_obj = types.Content(role="user", parts=[types.Part.from_text(text=request.prompt)])
        stream = runner.run_async(user_id="default_user", session_id=request.session_id, new_message=msg_obj)
        async for event in stream:
            pass # Consume stream to let it run and update session
            
        # Extract classification from session state (ADK stores output in state if output_key is set)
        session = await session_service.get_session(app_name="light_portal_router", user_id="default_user", session_id=request.session_id)
        classification = None
        if session and session.state:
            classification = session.state.get("router_classification")
        
        if classification:
            # Check if it is a dict or has an attribute (depending on how ADK stores it)
            if isinstance(classification, dict):
                intent = classification.get("intent", "SEARCH")
            else:
                intent = getattr(classification, "intent", "SEARCH")
            logger.info(f"Router Classification: {intent}")
        else:
            logger.warning("Router failed to classify. Falling back to SEARCH.")
            intent = "SEARCH"

        # 2. Yield Status to UI
        yield f"data: {json.dumps({'type': 'status', 'message': f'Intent Detected: {intent}. Routing...', 'icon': 'zap'})}\n\n"

        # 3. Route to corresponding Agent
        if intent == "SERVICENOW":
            # ServiceNow Route
            agent, exit_stack = await get_servicenow_agent_with_mcp_tools()
            agent_runner = Runner(app_name="servicenow_agent", agent=agent, session_service=session_service)
            
            # Ensure session exists for ServiceNow
            await get_or_create_session("servicenow_agent", request.session_id)
            
            try:
                # Stream content from ServiceNow Agent
                msg_obj = types.Content(role="user", parts=[types.Part.from_text(text=request.prompt)])
                async for event in agent_runner.run_async(user_id="default_user", session_id=request.session_id, new_message=msg_obj):
                    # Convert Event to UI format
                    if hasattr(event, "content") and event.content and event.content.parts:
                        text = event.content.parts[0].text
                        yield f"data: {json.dumps({'type': 'text', 'content': text})}\n\n"
                    elif hasattr(event, "tool_call") and event.tool_call:
                        yield f"data: {json.dumps({'type': 'status', 'message': f'Calling Tool: {event.tool_call.function_name}', 'icon': 'tool'})}\n\n"
            finally:
                await exit_stack.aclose()
                
        else:
            # SEARCH Route - Using Direct streamAssist with User Identity (STS Exchange)
            logger.info("Executing Search Path with Direct streamAssist")
            
            # 1. STS Token Exchange (Workload Identity Federation)
            exchanged_token = bearer_token
            if bearer_token and len(bearer_token) > 50: # Likely a real JWT
                try:
                    sts_url = "https://sts.googleapis.com/v1/token"
                    # Config from nexus_search_academy breakthrough
                    PROJECT_NUMBER = "REDACTED_PROJECT_NUMBER"
                    POOL_ID = "entra-id-oidc-pool-d"
                    PROVIDER_ID = "entra-id-oidc-pool-provider-de"
                    audience = f"//iam.googleapis.com/projects/{PROJECT_NUMBER}/locations/global/workloadIdentityPools/{POOL_ID}/providers/{PROVIDER_ID}"
                    
                    sts_payload = {
                        "audience": audience,
                        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
                        "scope": "https://www.googleapis.com/auth/cloud-platform",
                        "subjectToken": bearer_token,
                        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt"
                    }
                    
                    logger.info("Exchanging user token for Google STS token...")
                    sts_response = requests.post(sts_url, json=sts_payload, timeout=5)
                    if sts_response.status_code == 200:
                        exchanged_token = sts_response.json().get("access_token")
                        logger.info("STS Token Exchange Successful")
                    else:
                        logger.error(f"STS Exchange failed: {sts_response.text}")
                except Exception as e:
                    logger.error(f"Error during STS exchange: {e}")

            # 2. Config from User instructions
            PROJECT_NUMBER = "REDACTED_PROJECT_NUMBER"
            LOCATION = "global"
            ENGINE_ID = "deloitte-demo"
            DATA_STORE_ID = "5817ee80-82a4-49e3-a19c-2cedc73a6300"
            
            # 3. Direct streamAssist Payload
            assist_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"
            
            headers = {
                "Authorization": f"Bearer {exchanged_token or bearer_token}",
                "Content-Type": "application/json",
                "X-Goog-User-Project": PROJECT_NUMBER,
                "Accept": "text/event-stream"
            }
            
            payload = {
                "query": { "text": prompt },
                "toolsSpec": {
                    "vertexAiSearchSpec": {
                        "dataStoreSpecs": [
                            {
                                "dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/{DATA_STORE_ID}",
                                "description": "SharePoint Online Federated Corpus" 
                            }
                        ]
                    }
                }
            }

            logger.info(f"Calling Discovery Engine streamAssist at {assist_url}")
            yield f"data: {json.dumps({'type': 'status', 'message': 'Authenticating and Searching SharePoint...', 'icon': 'lock'})}\n\n"
            
            try:
                # Streaming from discovery engine
                response = requests.post(assist_url, headers=headers, json=payload, stream=True, timeout=60)
                
                if response.status_code != 200:
                    error_msg = response.text
                    logger.error(f"Search API returned error {response.status_code}: {error_msg}")
                    yield f"data: {json.dumps({'type': 'text', 'content': f'Error from Search API: {error_msg}'})}\n\n"
                    return

                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                event_data = json.loads(line_str[6:])
                                if 'answer' in event_data and 'answerText' in event_data['answer']:
                                    new_text = event_data['answer']['answerText']
                                    yield f"data: {json.dumps({'type': 'text', 'content': new_text})}\n\n"
                            except Exception as e:
                                logger.error(f"Error parsing stream event: {e}")
                                
            except Exception as e:
                logger.error(f"Exception during search streaming: {e}")
                yield f"data: {json.dumps({'type': 'text', 'content': f'An error occurred during search: {str(e)}'})}\n\n"
            
        yield "data: [DONE]\n\n"

    return StreamingResponse(_stream(), media_type="text/event-stream")

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Retrieves session history."""
    try:
        session = await session_service.get(session_id)
        history = []
        for turn in session.turns:
            for message in turn.messages:
                # Message is open-source or ADK type. We need to serialize it.
                # Assuming message has role and content or parts.
                role = message.role
                text = ""
                if hasattr(message.content, "parts"):
                    text = message.content.parts[0].text if message.content.parts else ""
                elif hasattr(message, "text"):
                    text = message.text
                
                history.append({"role": role, "text": text})
        return {"session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        return {"session_id": session_id, "history": []}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8010)) # Using Light MCP Portal specific port
    uvicorn.run(app, host="0.0.0.0", port=port)
