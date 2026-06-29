import os
import asyncio
import json
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
from dotenv import load_dotenv

# Import our agent and auth manager
from agent import root_agent
from auth import MSALAuthManager

# Load environment
load_dotenv(dotenv_path="../.env", override=True)

# Explicit GenAI configuration per rules
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("adk-hosted-mcp.backend")

app = FastAPI(title="SharePoint Hosted Explorer Backend")

# Enable CORS for the local frontend (port 5175)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MSAL Auth Manager
CLIENT_ID = os.environ.get("MS365_CLIENT_ID", "030b6aac-63d1-40e9-8d80-7ce928b839b8")
TENANT_ID = os.environ.get("MS365_TENANT_ID", "de46a3fd-0d68-4b25-8343-6eb5d71afce9")
auth_manager = MSALAuthManager(client_id=CLIENT_ID, tenant_id=TENANT_ID)

# Store pending device code flow in-memory
pending_device_flow = {}

# Initialize ADK Runner
runner = InMemoryRunner(agent=root_agent, app_name="sharepoint-hosted-explorer")

class ChatRequest(BaseModel):
    message: str

@app.get("/api/auth/url")
def start_auth():
    """Starts MSAL Device Code Flow."""
    try:
        flow = auth_manager.start_device_code_flow()
        # Save flow in memory using user_code as key
        user_code = flow.get("user_code")
        pending_device_flow[user_code] = flow
        return {
            "user_code": user_code,
            "verification_uri": flow.get("verification_uri"),
            "message": flow.get("message")
        }
    except Exception as e:
        logger.exception("Failed to start device flow")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start device flow: {str(e)}"
        )

@app.get("/api/auth/complete/{user_code}")
def complete_auth(user_code: str):
    """Completes MSAL Device Code Flow after user authenticates on verification URI."""
    flow = pending_device_flow.get(user_code)
    if not flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active authorization flow not found for this code."
        )
    try:
        account_info = auth_manager.complete_device_code_flow(flow)
        # Clear flow from memory
        del pending_device_flow[user_code]
        return {
            "status": "authenticated",
            "account": account_info
        }
    except Exception as e:
        # If still pending, MSAL raises exception — we return it as pending status or error
        err_msg = str(e)
        if "authorization_pending" in err_msg.lower():
            return {"status": "pending", "message": "Waiting for user authentication..."}
        logger.exception("Failed to complete device flow")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {err_msg}"
        )

@app.get("/api/auth/status")
def auth_status():
    """Checks current auth status and returns account info if authenticated."""
    token = auth_manager.get_access_token()
    if token:
        return {
            "authenticated": True,
            "account": auth_manager.get_account_info()
        }
    return {"authenticated": False}

@app.post("/api/auth/logout")
def logout():
    """Clears user token cache."""
    auth_manager.logout()
    return {"status": "logged_out"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat endpoint returning streaming ADK execution events via SSE."""
    token = auth_manager.get_access_token()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in first."
        )
        
    async def event_generator():
        user_id = "test-user-id"
        session_id = "test-session-id"
        
        # Inject user token into session state under keys agent.py looks for
        session_state = {
            "sharepointauth_hosted": token,
            "temp:sharepointauth_hosted": token,
        }
        
        try:
            # Re-create/update session to ensure fresh state
            try:
                await runner.session_service.create_session(
                    app_name="sharepoint-hosted-explorer",
                    user_id=user_id,
                    session_id=session_id,
                    state=session_state
                )
                logger.info("[Backend] Created ADK session with token injected")
            except Exception as e:
                # If session exists, update its state
                session = await runner.session_service.get_session(
                    app_name="sharepoint-hosted-explorer",
                    user_id=user_id,
                    session_id=session_id
                )
                session.state.update(session_state)
                logger.info("[Backend] Updated existing ADK session state with new token")
                
            content = types.Content(role="user", parts=[types.Part(text=request.message)])
            
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ):
                # Process parts to capture text and tool invocation events
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            yield f"data: {json.dumps({'type': 'text', 'content': part.text})}\n\n"
                        elif part.function_call:
                            fc = part.function_call
                            yield f"data: {json.dumps({'type': 'tool_start', 'name': fc.name, 'arguments': dict(fc.args or {})})}\n\n"
                        elif part.function_response:
                            fr = part.function_response
                            yield f"data: {json.dumps({'type': 'tool_end', 'name': fr.name, 'response': str(fr.response)[:500]})}\n\n"
                
                if event.is_final_response():
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    
        except Exception as e:
            logger.exception("Error during agent execution stream")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    # Use port 8002 to avoid conflict with other apps (8000/8001)
    port = int(os.environ.get("BACKEND_PORT", 8002))
    
    # Port conflict management as per rules
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", port))
        s.close()
    except socket.error:
        logger.warning(f"Port {port} is in use. Attempting to kill listener...")
        import subprocess
        # Terminate active listener on port using rules command
        subprocess.run(f"kill -9 $(lsof -t -i:{port})", shell=True)
        
    logger.info(f"Starting backend server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
