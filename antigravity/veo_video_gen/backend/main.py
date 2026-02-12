import os
import logging
from dotenv import load_dotenv

# Load params from .env file
# Try loading from home directory or project root
dotenv_path = os.path.expanduser("~/.env")
if not os.path.exists(dotenv_path):
    dotenv_path = "../.env" # Fallback
load_dotenv(dotenv_path=dotenv_path)

# Set internal env vars for ADK/GenAI BEFORE importing agent
# This ensures LlmAgent picks up the correct project/location at initialization time
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
# Provide defaults just in case locally not set, similar to test_auth.py
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID", "vtxdemos")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("LOCATION", "us-central1")

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.adk.runners import Runner
from agent import video_expert_agent as VideoExpertAgent
from google.adk.sessions import InMemorySessionService

# Helper logger
logger = logging.getLogger("uvicorn")

app = FastAPI(title="Veo Video Gen Agent (ADK)")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ADK Runner
session_service = InMemorySessionService()
# Fixed: added 'app_name'
runner = Runner(
    agent=VideoExpertAgent,
    app_name="veo_video_gen",
    session_service=session_service
)

class ChatRequest(BaseModel):
    message: str
    image_base64: Optional[str] = None
    session_id: str

class ChatResponse(BaseModel):
    response: str
    video_base64: Optional[str] = None
    session_id: str

@app.get("/")
async def root():
    return {"message": "Veo Video Gen Agent (ADK) is running"}

import vertexai
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp

import threading

# Internal endpoint configuration for Agent Engines
AGENT_ENGINE_DISPLAY_NAME = "veo-video-expert-agent"
# We assume PROJECT and LOCATION env vars are set properly by the startup code
STAGING_BUCKET = os.getenv("STAGING_BUCKET", f"gs://{os.environ['GOOGLE_CLOUD_PROJECT']}-agent-staging")

deployment_status = {
    "is_deploying": False,
    "logs": [],
    "error": None,
    "resource_name": None
}

class DeployLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        deployment_status["logs"].append(msg)

deploy_handler = DeployLogHandler()
deploy_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
# Capture Vertex AI SDK logs
logging.getLogger("google.cloud.aiplatform").addHandler(deploy_handler)
logging.getLogger("google.cloud.aiplatform").setLevel(logging.INFO)
# Also capture our own backend logs
logger.addHandler(deploy_handler)

@app.get("/api/agents")
async def list_agents():
    """Returns a list of deployed ADK agents matching the display name using REST API."""
    try:
        import google.auth
        import google.auth.transport.requests
        import requests
        
        project = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        creds, _ = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        
        url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/reasoningEngines"
        headers = {"Authorization": f"Bearer {creds.token}"}
        resp = requests.get(url, headers=headers)
        
        if not resp.ok:
            raise Exception(f"Failed to fetch agents: {resp.text}")
            
        data = resp.json()
        engines = data.get("reasoningEngines", [])
        
        result = []
        for e in engines:
            name = e.get("displayName", "")
            if AGENT_ENGINE_DISPLAY_NAME in name:
                result.append({
                    "resource_name": e.get("name"),
                    "display_name": name,
                    "description": e.get("description", "")
                })
             
        return {"agents": result}
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def deploy_worker():
    """Background worker for deploying the agent."""
    try:
        from agent import video_expert_agent # Ensure we import relative to backend during execution
        
        # We must initialize vertexai with an explicit staging bucket for Reasoning Engine
        vertexai.init(project=os.environ["GOOGLE_CLOUD_PROJECT"], location=os.environ["GOOGLE_CLOUD_LOCATION"])
        client = vertexai.Client(project=os.environ["GOOGLE_CLOUD_PROJECT"], location=os.environ["GOOGLE_CLOUD_LOCATION"])
        
        deployment_app = AdkApp(
            agent=video_expert_agent,
            enable_tracing=True
        )
        
        logger.info(f"Checking for existing agent with display_name='{AGENT_ENGINE_DISPLAY_NAME}'")
        all_engines = list(client.agent_engines.list())
        target_engine = next((e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_DISPLAY_NAME), None)
        
        requirements_list = [
           "google-cloud-aiplatform[adk,agent_engines]",
           "google-genai",
           "python-dotenv",
           "requests", 
           "pillow"
        ]
        
        if target_engine:
            logger.info(f"Existing agent found: {target_engine.api_resource.name}. Triggering UPDATE...")
            remote_app = client.agent_engines.update(
                name=target_engine.api_resource.name,
                agent=deployment_app,
                config={
                    "display_name": AGENT_ENGINE_DISPLAY_NAME,
                    "staging_bucket": STAGING_BUCKET,
                    "requirements": requirements_list,
                    "extra_packages": ["agent.py", "video_tools.py"],
                    "env_vars": {"ENABLE_TELEMETRY": "False"}
                }
            )
            deployment_status["resource_name"] = remote_app.api_resource.name
            logger.info(f"Update successful! Resource: {remote_app.api_resource.name}")
        else:
            logger.info(f"Triggering remote deployment CREATE for {AGENT_ENGINE_DISPLAY_NAME}")
            remote_app = client.agent_engines.create(
                agent=deployment_app,
                config={
                    "display_name": AGENT_ENGINE_DISPLAY_NAME,
                    "staging_bucket": STAGING_BUCKET,
                    "requirements": requirements_list,
                    "extra_packages": ["agent.py", "video_tools.py"],
                    "env_vars": {"ENABLE_TELEMETRY": "False"}
                }
            )
            deployment_status["resource_name"] = remote_app.api_resource.name
            logger.info(f"Deployment successful! Resource: {remote_app.api_resource.name}")
        
    except Exception as e:
        logger.error(f"Error deploying agent: {e}")
        deployment_status["error"] = str(e)
    finally:
        deployment_status["is_deploying"] = False
        logger.info("Deployment background worker finished.")

@app.post("/api/agents/deploy")
async def deploy_agent():
    """Starts the root agent deployment to Vertex AI Agent Engine."""
    if deployment_status["is_deploying"]:
        raise HTTPException(status_code=400, detail="Deployment already in progress")
        
    deployment_status["is_deploying"] = True
    deployment_status["logs"] = []
    deployment_status["error"] = None
    deployment_status["resource_name"] = None
    
    thread = threading.Thread(target=deploy_worker)
    thread.start()
    
    return {
        "status": "started", 
        "message": "Agent deployment started in background"
    }

@app.get("/api/agents/deploy_status")
async def get_deploy_status():
    """Returns the current deployment status and logs."""
    return deployment_status

@app.delete("/api/agents/{resource_name:path}")
async def delete_agent(resource_name: str):
    """Deletes an agent by formatting its full resource name from path params using REST."""
    try:
        import google.auth
        import google.auth.transport.requests
        import requests
        
        full_resource_name = resource_name
        logger.info(f"Deleting agent via REST: {full_resource_name}")
        
        creds, _ = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        
        # We can extract the location from the resource name or just use os.environ
        api_location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        url = f"https://{api_location}-aiplatform.googleapis.com/v1beta1/{full_resource_name}"
        headers = {"Authorization": f"Bearer {creds.token}"}
        
        resp = requests.delete(url, headers=headers)
        if not resp.ok:
            logger.warning(f"Deletion warning/error: {resp.text}")
            
        # For long-running operations, typically returning HTTP 200/202 is enough
        return {"status": "success", "message": f"Delete triggered for {resource_name}"}
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/cat_image")
async def get_debug_cat_image():
    """Returns the base64 of the debug cat image."""
    try:
        # Use a fixed path or relative path to the artifact
        img_path = "/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/470407f1-0bee-4ff7-b95a-849d61d0f7f8/cyberpunk_cat_1770848801294.png"
        if not os.path.exists(img_path):
             # Fallback to creating a dummy image or error if not found? 
             # For now, let's assume it exists as it was in the snippet
             pass
        
        with open(img_path, "rb") as f:
            import base64
            encoded = base64.b64encode(f.read()).decode('utf-8')
            return {"image_base64": encoded}
    except Exception as e:
        logger.error(f"Error serving cat image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

session_map = {}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        from agent import video_expert_agent
        from vertexai.agent_engines import AdkApp
        import vertexai

        # Initialize Vertex AI
        vertexai.init(project=os.environ["GOOGLE_CLOUD_PROJECT"], location=os.environ["GOOGLE_CLOUD_LOCATION"])

        local_app = AdkApp(
            agent=video_expert_agent,
            enable_tracing=True
        )

        session_id = request.session_id
        logger.info(f"Processing chat for front-end session {session_id}")
        
        # Map frontend session to AdkApp session
        if session_id not in session_map:
            session = await local_app.async_create_session(user_id="user")
            # Handle both dict and object returns based on user snippet
            session_map[session_id] = session["id"] if isinstance(session, dict) and "id" in session else session.id
        
        adk_session_id = session_map[session_id]
        
        prompt_text = request.message
        if request.image_base64:
            # Save to temp file to ensure tool can read it
            try:
                import tempfile
                import base64
                fd, temp_path = tempfile.mkstemp(suffix=".png")
                
                # Fix potential padding issues
                b64_image = request.image_base64
                missing_padding = len(b64_image) % 4
                if missing_padding:
                    b64_image += '=' * (4 - missing_padding)
                
                with os.fdopen(fd, "wb") as f:
                    f.write(base64.b64decode(b64_image))
                
                logger.info(f"Saved temp image to {temp_path}")
                prompt_text += f"\n\nHere is the image file you should use for generation: {temp_path}\nDO NOT analyze the image or ask for it. JUST use the 'generate_image_to_video' tool with this path."
            except Exception as e:
                logger.error(f"Failed to save temp image: {e}")
                prompt_text += f"\n[IMAGE_CONTEXT ERROR: {e}]"

        # Use AdkApp session and stream query
        session = await local_app.async_create_session(user_id="user")
        
        agent_response_text = ""
        video_data = None
        
        async for event in local_app.async_stream_query(
            user_id="user",
            session_id=adk_session_id,
            message=prompt_text,
        ):
            logger.info(f"Event: {type(event)}")
            evt_str = str(event)
            
            # Extract video base64 from file if present
            if "VIDEO_BASE64_FILE:" in evt_str:
                import re
                match = re.search(r"VIDEO_BASE64_FILE:([/\w\.-]+)", evt_str)
                if match:
                    temp_path = match.group(1)
                    try:
                        with open(temp_path, "r") as f:
                            video_data = f.read()
                        # Cleanup temp file if desired, or let OS handle /tmp
                    except Exception as fetch_e:
                        logger.error(f"Failed to load video payload: {fetch_e}")
            
            # Robust text extraction from ModelResponse or other text-bearing events
            try:
                if hasattr(event, 'text') and event.text:
                    agent_response_text += event.text
                elif hasattr(event, 'message') and hasattr(event.message, 'content'):
                    for part in event.message.content:
                        if hasattr(part, 'text') and part.text:
                            agent_response_text += part.text
            except Exception as e:
                logger.error(f"Error extracting text from event: {e}")

        # Final check if STILL empty, apply the fallback message
        if not agent_response_text:
            if video_data:
                agent_response_text = "Here is your generated video."
            else:
                agent_response_text = "I'm your Veo Video Expert. I can generate videos from text, animate images, or extend existing videos. How can I help you today?"

        if not agent_response_text and not video_data:
             agent_response_text = "I received your request but didn't know what to say."
        elif not agent_response_text and video_data:
             agent_response_text = "Here is your generated video."

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        response=agent_response_text,
        video_base64=video_data,
        session_id=session_id
    )

if __name__ == "__main__":
    import uvicorn
    # Use port 8001
    uvicorn.run(app, host="0.0.0.0", port=8001)
