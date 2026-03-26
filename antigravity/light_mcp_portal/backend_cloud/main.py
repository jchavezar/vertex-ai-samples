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
from google.adk.tools import VertexAiSearchTool

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI()

# Initialize Session Service (Vertex AI if AGENT_ENGINE_ID is set, else In-Memory)
# Force InMemorySessionService for local router in cloud backend to avoid hangs
logger.info("Using InMemorySessionService for local router in cloud backend.")
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
        router_session = await get_or_create_session("light_portal_router", request.session_id)
        router_session_id = router_session.id
        
        # We run the router and get the classification result
        msg_obj = types.Content(role="user", parts=[types.Part.from_text(text=request.prompt)])
        stream = runner.run_async(user_id="default_user", session_id=router_session_id, new_message=msg_obj)
        async for event in stream:
            pass # Consume stream to let it run and update session
            
        # Extract classification from session state (ADK stores output in state if output_key is set)
        session = await session_service.get_session(app_name="light_portal_router", user_id="default_user", session_id=router_session_id)
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
            accumulatedText = ""
            if os.environ.get("AGENT_ENGINE_ID"):
                logger.info(f"Routing to Remote Agent Engine: {os.environ.get('AGENT_ENGINE_ID')}")
                import vertexai
                from vertexai.agent_engines import AdkApp
                from google.adk.sessions.vertex_ai_session_service import VertexAiSessionService
                
                engine_id = os.environ.get("AGENT_ENGINE_ID")
                if engine_id and "/" in engine_id:
                    engine_id = engine_id.split("/")[-1]
                
                logger.info(f"Routing to Remote Agent Engine ID: {engine_id}")
                
                # Setup cloud session service with the specific engine ID
                from agents.agent import root_agent
                cloud_session_service = VertexAiSessionService(
                    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
                    location="us-central1",
                    agent_engine_id=engine_id
                )
                
                try:
                    # 1. Create a session with the token state
                    session = await cloud_session_service.create_session(
                        app_name="servicenow_mcp_agent_prod",
                        user_id="default_user",
                        state={"USER_TOKEN": bearer_token} if bearer_token else {}
                    )
                    logger.info(f"Created Cloud Session ID: {session.id}")
                    
                    remote_app = AdkApp(agent=root_agent, session_service_builder=lambda: cloud_session_service)
                    
                    # 2. Use the generated session ID
                    async for event in remote_app.async_stream_query(
                        user_id="default_user",
                        session_id=session.id,
                        message=request.prompt
                    ):
                        if hasattr(event, "type"):
                            if event.type == "message":
                                if hasattr(event, "content") and hasattr(event.content, "parts"):
                                    for part in event.content.parts:
                                        if hasattr(part, "text") and part.text:
                                            accumulatedText += part.text
                                            yield f"data: {json.dumps({'type': 'text', 'content': part.text})}\n\n"
                            elif event.type == "tool_call":
                                yield f"data: {json.dumps({'type': 'status', 'message': f'Calling Cloud Tool: {event.tool_call.function_name}', 'icon': 'tool'})}\n\n"
                            elif event.type == "thought":
                                logger.info(f"Cloud AI Thought: {event.text}")
                    
                    if not accumulatedText:
                        error_msg = "The remote ServiceNow agent failed to generate a response."
                        logger.warning(f"Empty ServiceNow result for session {request.session_id}")
                        yield f"data: {json.dumps({'type': 'text', 'content': error_msg})}\n\n"
                
                except Exception as e:
                    logger.error(f"Failed remote Agent Engine call: {e}")
                    yield f"data: {json.dumps({'type': 'text', 'content': f'Remote Agent Error: {e}'})}\n\n"
                    
            else:
                # ServiceNow Local Route
                agent, exit_stack = await get_servicenow_agent_with_mcp_tools(user_token=bearer_token)
                agent_runner = Runner(app_name="servicenow_agent", agent=agent, session_service=session_service)
                
                # Ensure session exists for ServiceNow
                sn_session = await get_or_create_session("servicenow_agent", request.session_id)
                sn_session_id = sn_session.id
                
                try:
                    # Stream content from Local ServiceNow Agent
                    msg_obj = types.Content(role="user", parts=[types.Part.from_text(text=request.prompt)])
                    async for event in agent_runner.run_async(user_id="default_user", session_id=sn_session_id, new_message=msg_obj):
                        # Convert Event to UI format
                        if hasattr(event, "content") and event.content and event.content.parts:
                            for part in event.content.parts:
                                if hasattr(part, "text") and part.text:
                                    accumulatedText += part.text
                                    yield f"data: {json.dumps({'type': 'text', 'content': part.text})}\n\n"
                                elif hasattr(part, "thought") and part.thought:
                                    logger.info(f"AI Thought: {part.thought}")
                        elif hasattr(event, "tool_call") and event.tool_call:
                            yield f"data: {json.dumps({'type': 'status', 'message': f'Calling Tool: {event.tool_call.function_name}', 'icon': 'tool'})}\n\n"
                    
                    if not accumulatedText:
                        error_msg = "The ServiceNow agent failed to generate a response. This often happens if the tool call fails or the response is empty."
                        logger.warning(f"Empty ServiceNow result for session {request.session_id}")
                        yield f"data: {json.dumps({'type': 'text', 'content': error_msg})}\n\n"
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
                    audience = f"//iam.googleapis.com/locations/global/workforcePools/{POOL_ID}/providers/{PROVIDER_ID}"
                    
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
            
            # Dynamically fetch active DataStores for the specific Engine
            try:
                import google.auth
                from google.auth.transport.requests import Request
                admin_creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
                if not admin_creds.valid:
                    admin_creds.refresh(Request())
                admin_token = admin_creds.token
            except Exception as e:
                logger.error(f"Failed to get ADC admin token: {e}")
                admin_token = exchanged_token or bearer_token

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
                    for comp in collections:
                        for ds_comp in comp.get('dataStoreComponents', []):
                            dataStoreSpecs.append({'dataStore': ds_comp['name']})
                            logger.info(f"Dynamically mapped datastore: {ds_comp['name']}")
            except Exception as e:
                logger.error(f"Failed to fetch dynamic widgetConfigs: {e}")

            payload = {
                "query": { "text": prompt }
            }
            if dataStoreSpecs:
                payload["toolsSpec"] = {
                    "vertexAiSearchSpec": { "dataStoreSpecs": dataStoreSpecs }
                }
            else:
                payload["toolsSpec"] = {
                    "vertexAiSearchSpec": {
                        "dataStoreSpecs": [
                            {
                                "dataStore": f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/dataStores/{DATA_STORE_ID}"
                            }
                        ]
                    }
                }

            logger.info(f"Calling Discovery Engine streamAssist at {assist_url}")
            yield f"data: {json.dumps({'type': 'status', 'message': 'Searching SharePoint...', 'icon': 'search'})}\n\n"
            
            try:
                # Synchronous request to get the full JSON array
                response = requests.post(assist_url, headers=headers, json=payload, stream=False, timeout=60)
                
                if response.status_code != 200:
                    error_msg = response.text
                    logger.error(f"Search API returned error {response.status_code}: {error_msg}")
                    yield f"data: {json.dumps({'type': 'text', 'content': f'Error from Search API: {error_msg}'})}\n\n"
                    return

                try:
                    resp_json = response.json()
                    logger.info("### RAW SEARCH RESPONSE ###")
                    logger.info(json.dumps(resp_json, indent=2))
                    full_text = ""
                    for chunk in resp_json:
                        answer = chunk.get("answer", {})
                        for reply in answer.get("replies", []):
                            content = reply.get("groundedContent", {}).get("content", {})
                            if "text" in content:
                                full_text += content["text"]
                    
                    # Recursively extract citations from the entire payload
                    found_results = []
                    def find_grounding(obj):
                        if isinstance(obj, list):
                            for item in obj:
                                find_grounding(item)
                            return
                        if isinstance(obj, dict):
                            # Schema 1: searchResults (common in some configs)
                            if "searchResults" in obj and isinstance(obj.get("searchResults"), list):
                                for res in obj["searchResults"]:
                                    doc = res.get("document", res)
                                    struct = doc.get("structData", res.get("structData", {}))
                                    name = doc.get("name", "")
                                    title = struct.get("title") or (name.split('/')[-1] if name else "Source Material")
                                    found_results.append({
                                        "title": title,
                                        "url": struct.get("url", struct.get("uri", "#")),
                                        "snippet": struct.get("snippet", struct.get("description", ""))
                                    })
                            # Schema 2: textGroundingMetadata (used by streamAssist in this Engine)
                            if "textGroundingMetadata" in obj and isinstance(obj.get("textGroundingMetadata"), dict):
                                metadata = obj["textGroundingMetadata"]
                                if "references" in metadata and isinstance(metadata["references"], list):
                                    for ref in metadata["references"]:
                                        doc_meta = ref.get("documentMetadata", {})
                                        found_results.append({
                                            "title": doc_meta.get("title", "Source Material"),
                                            "url": doc_meta.get("uri", "#"),
                                            "snippet": ref.get("content", "")
                                        })
                            # Schema 3: groundingChunks
                            if "groundingMetadata" in obj and isinstance(obj.get("groundingMetadata"), dict):
                                chunks = obj["groundingMetadata"].get("groundingChunks", [])
                                if isinstance(chunks, list):
                                    for chunk in chunks:
                                        # Grounding chunks often contain a web or retrieved context
                                        ret_ctx = chunk.get("retrievedContext", {})
                                        found_results.append({
                                            "title": ret_ctx.get("title", "Source Material"),
                                            "url": ret_ctx.get("uri", "#"),
                                            "snippet": ret_ctx.get("text", "")
                                        })
                                
                            for k, v in obj.items():
                                if k not in ("answerText", "text") and isinstance(v, (dict, list)):
                                    find_grounding(v)
                                    
                    find_grounding(resp_json)
                    
                    if found_results:
                        full_text += "\n\n---\n**Sources:**\n"
                        seen_titles = set()
                        idx = 1
                        for res in found_results:
                            title = str(res.get("title")).strip()
                            url = str(res.get("url")).strip()
                            snippet_text = str(res.get("snippet")).strip()
                            
                            unique_key = f"{title}-{url}"
                            if unique_key not in seen_titles and snippet_text:
                                seen_titles.add(unique_key)
                                full_text += f"{idx}. **[{title}]({url})**\n   > {snippet_text}\n\n"
                                idx += 1
                                
                    if not full_text:
                        full_text = "Sorry, I could not find relevant information in SharePoint."
                        
                    yield f"data: {json.dumps({'type': 'text', 'content': full_text})}\n\n"
                except Exception as e:
                    logger.error(f"Error parsing Search JSON: {e}")
                    yield f"data: {json.dumps({'type': 'text', 'content': 'Error parsing search results.'})}\n\n"
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Discovery Engine request failed: {e}")
                yield f"data: {json.dumps({'type': 'text', 'content': f'Network Error: {str(e)}'})}\n\n"
            
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
