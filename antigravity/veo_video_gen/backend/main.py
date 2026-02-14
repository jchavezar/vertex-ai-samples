import os
import logging
import importlib
import sys
import re
import base64
import tempfile
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
from agent_pkg.agent import video_expert_agent as VideoExpertAgent
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

# Persistent local AdkApp instance for session continuity
from vertexai.agent_engines import AdkApp
import vertexai

# Initialize at startup
vertexai.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
)

_local_adk_app = None

def get_local_adk_app():
    """Returns a persistent AdkApp instance for local agent queries."""
    global _local_adk_app
    if _local_adk_app is None:
        from agent_pkg.agent import video_expert_agent
        _local_adk_app = AdkApp(
            agent=video_expert_agent,
            enable_tracing=False  # Disable to avoid telemetry 403 errors
        )
    return _local_adk_app

class ChatRequest(BaseModel):
    message: str
    image_base64: Optional[str] = None
    session_id: str
    agent_resource_name: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    video_base64: Optional[str] = None
    session_id: str

class DeployRequest(BaseModel):
    model_name: str = "gemini-2.5-flash"
    region: str = "us-central1"  # Gemini 3.x models require "global"

@app.get("/")
async def root():
    return {"message": "Veo Video Gen Agent (ADK) is running"}

import vertexai
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp

import threading

# Internal endpoint configuration for Agent Engines
AGENT_ENGINE_DISPLAY_NAME = "Veo Video Agent"
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

def deploy_worker(model_name: str, region: str = "us-central1"):
    """Background worker for deploying the agent."""
    def log_to_ui(msg):
        logger.info(msg)
        deployment_status["logs"].append(msg)

    try:
        # Patch agent.py with the selected model
        log_to_ui(f"Patching agent.py to use model: {model_name}")
        log_to_ui(f"Using region: {region}")
        agent_path = os.path.join(os.path.dirname(__file__), "agent_pkg/agent.py")
        with open(agent_path, "r") as f:
            content = f.read()
        
        # Robust replacement for model="any-string"
        new_content = re.sub(r'model="[^"]+"', f'model="{model_name}"', content)
        
        with open(agent_path, "w") as f:
            f.write(new_content)
            
        # Dynamically import/reload agent to pick up changes
        import agent_pkg.agent as agent
        importlib.reload(agent.agent)
        from agent_pkg.agent import video_expert_agent
        
        log_to_ui(f"Initializing Vertex AI connection for region: {region}...")
        vertexai.init(project=os.environ["GOOGLE_CLOUD_PROJECT"], location=region)
        client = vertexai.Client(project=os.environ["GOOGLE_CLOUD_PROJECT"], location=os.environ["GOOGLE_CLOUD_LOCATION"])
        
        deployment_app = AdkApp(
            agent=video_expert_agent,
            enable_tracing=True
        )
        
        log_to_ui(f"Checking for existing agent: {AGENT_ENGINE_DISPLAY_NAME}")
        all_engines = list(client.agent_engines.list())
        target_engine = next((e for e in all_engines if e.api_resource.display_name == AGENT_ENGINE_DISPLAY_NAME), None)
        
        requirements_list = [
            "google-cloud-aiplatform[adk,agent_engines]",
            "google-adk",
            "google-genai",
            "python-dotenv",
            "requests", 
            "pillow",
            "cloudpickle",
            "pydantic"
        ]
        
        base_dir = os.path.dirname(__file__)
        extra_packages = [
            os.path.join(base_dir, "agent_pkg/agent.py")
        ]
        
        if target_engine:
            log_to_ui(f"Updating existing Reasoning Engine: {target_engine.api_resource.name}")
            remote_app = client.agent_engines.update(
                name=target_engine.api_resource.name,
                agent=deployment_app,
                config={
                    "display_name": AGENT_ENGINE_DISPLAY_NAME,
                    "staging_bucket": STAGING_BUCKET,
                    "requirements": requirements_list,
                    "extra_packages": extra_packages,
                    "env_vars": {"ENABLE_TELEMETRY": "False"}
                }
            )
            deployment_status["resource_name"] = remote_app.api_resource.name
            log_to_ui("Reasoning Engine UPDATE successful!")
        else:
            log_to_ui(f"Creating NEW Reasoning Engine: {AGENT_ENGINE_DISPLAY_NAME}...")
            log_to_ui(f"Staging to bucket: {STAGING_BUCKET}")
            remote_app = client.agent_engines.create(
                agent=deployment_app,
                config={
                    "display_name": AGENT_ENGINE_DISPLAY_NAME,
                    "staging_bucket": STAGING_BUCKET,
                    "requirements": requirements_list,
                    "extra_packages": extra_packages,
                    "env_vars": {"ENABLE_TELEMETRY": "False"}
                }
            )
            deployment_status["resource_name"] = remote_app.api_resource.name
            log_to_ui(f"Reasoning Engine CREATE successful! Resource: {remote_app.api_resource.name}")
        
    except Exception as e:
        err_msg = f"Deployment Error: {str(e)}"
        log_to_ui(err_msg)
        deployment_status["error"] = str(e)
    finally:
        deployment_status["is_deploying"] = False
        log_to_ui("Deployment background worker finished.")

@app.post("/api/agents/deploy")
async def deploy_agent(request: DeployRequest):
    """Starts the root agent deployment to Vertex AI Agent Engine."""
    if deployment_status["is_deploying"]:
        raise HTTPException(status_code=400, detail="Deployment already in progress")
        
    deployment_status["is_deploying"] = True
    deployment_status["logs"] = []
    deployment_status["error"] = None
    deployment_status["resource_name"] = None
    
    thread = threading.Thread(target=deploy_worker, args=(request.model_name, request.region))
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
        url = f"https://{api_location}-aiplatform.googleapis.com/v1beta1/{full_resource_name}?force=true"
        headers = {"Authorization": f"Bearer {creds.token}"}
        
        resp = requests.delete(url, headers=headers)
        if not resp.ok:
            logger.warning(f"Deletion warning/error: {resp.text}")
             
        return {"status": "success", "message": f"Delete triggered for {full_resource_name}"}
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

class SessionResetRequest(BaseModel):
    session_id: str

@app.post("/api/session/reset")
async def reset_session(request: SessionResetRequest):
    """Deletes a session from the map, forcing a new ADK session on next chat."""
    session_id = request.session_id
    if session_id in session_map:
        old_adk_session = session_map.pop(session_id)
        logger.info(f"Reset session: frontend={session_id}, adk={old_adk_session}")
        return {"status": "reset", "old_adk_session": old_adk_session}
    return {"status": "not_found", "message": "Session was not in map"}

@app.get("/api/session/{session_id}")
async def get_session_info(session_id: str):
    """Returns info about a session."""
    if session_id in session_map:
        return {
            "frontend_session_id": session_id,
            "adk_session_id": session_map[session_id],
            "exists": True
        }
    return {"frontend_session_id": session_id, "exists": False}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        from agent_pkg.agent import video_expert_agent
        from vertexai import agent_engines

        session_id = request.session_id
        logger.info(f"Processing chat for front-end session {session_id}")
        
        prompt_text = request.message
        if request.image_base64:
            # Save to temp file to ensure tool can read it
            try:
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

        agent_response_text = ""
        video_data = None
        
        if request.agent_resource_name:
            # Force the correct project ID in the resource string
            parts = request.agent_resource_name.split("/")
            if len(parts) >= 2 and parts[0] == "projects":
                 parts[1] = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
            fixed_resource_name = "/".join(parts)
            
            logger.info(f"Querying REMOTE agent: {fixed_resource_name}")
            remote_app = agent_engines.get(fixed_resource_name)
            
            if session_id not in session_map:
                session_resp = await remote_app.async_create_session(user_id="user")
                session_map[session_id] = session_resp["id"] if isinstance(session_resp, dict) and "id" in session_resp else getattr(session_resp, "id", None)
            
            adk_session_id = session_map[session_id]
            
            async for event in remote_app.async_stream_query(
                user_id="user",
                session_id=adk_session_id,
                message=prompt_text,
            ):
                logger.info(f"Event: {type(event)}")
                evt_str = str(event)
                
                # Extract video file path from payload if present
                if "VIDEO_FILE_PATH_PAYLOAD:" in evt_str:
                    logger.info("Found VIDEO_FILE_PATH_PAYLOAD marker in remote stream.")
                    match = re.search(r"VIDEO_FILE_PATH_PAYLOAD:([^\s'\"\}\]]+)", evt_str)
                    if match:
                        file_path = match.group(1)
                        logger.info(f"Extracted file path: {file_path}")
                        try:
                            if os.path.exists(file_path):
                                with open(file_path, "rb") as f:
                                    # Use global base64
                                    video_data = base64.b64encode(f.read()).decode("utf-8")
                                logger.info(f"Loaded base64 payload of length: {len(video_data)}")
                                # Cleanup temp file
                                os.remove(file_path)
                            else:
                                logger.error(f"Video file not found: {file_path}")
                        except Exception as e:
                            logger.error(f"Error loading video file: {e}")
                
                # Robust text extraction from ModelResponse or other text-bearing events
                try:
                    # Recursive search for text in dict events
                    def find_text_in_dict(d):
                        txt = ""
                        if isinstance(d, dict):
                            if "text" in d and d["text"]:
                                txt += d["text"]
                            for v in d.values():
                                txt += find_text_in_dict(v)
                        elif isinstance(d, list):
                            for item in d:
                                txt += find_text_in_dict(item)
                        return txt
                    
                    if isinstance(event, dict):
                        extracted = find_text_in_dict(event)
                        if extracted and extracted not in agent_response_text:
                             # Append or replace based on overlap
                             if agent_response_text and extracted.startswith(agent_response_text):
                                 agent_response_text = extracted
                             else:
                                 agent_response_text += extracted
                    elif hasattr(event, 'text') and event.text:
                        agent_response_text += event.text
                    elif hasattr(event, 'message') and hasattr(event.message, 'content'):
                        for part in event.message.content:
                            if hasattr(part, 'text') and part.text:
                                agent_response_text += part.text
                except Exception as e:
                    logger.error(f"Error extracting text from event: {e}")
                    
        else:
            logger.info("Querying LOCAL agent: video_expert_agent")
            local_app = get_local_adk_app()  # Use persistent instance

            if session_id not in session_map:
                try:
                    session = await local_app.async_create_session(user_id="user")
                    # ADK returns different types based on version, handle both
                    if isinstance(session, dict):
                        session_map[session_id] = session.get("id")
                    else:
                        session_map[session_id] = getattr(session, "id", None)
                    logger.info(f"Created new ADK session: {session_map[session_id]} for frontend session {session_id}")
                except Exception as e:
                    logger.error(f"Failed to create ADK session: {e}")
                    # Fallback or error? Let's try to proceed if we have a session or fail gracefully
                    if session_id not in session_map:
                         raise HTTPException(status_code=500, detail="Failed to initialize agent session")

            adk_session_id = session_map[session_id]
            logger.info(f"Using ADK session: {adk_session_id}")

            async for event in local_app.async_stream_query(
                user_id="user",
                session_id=adk_session_id,
                message=prompt_text,
            ):
                logger.info(f"Event: {type(event)}")
                evt_str = str(event)
                
                # Extract video file path from payload if present
                if "VIDEO_FILE_PATH_PAYLOAD:" in evt_str:
                    logger.info("Found VIDEO_FILE_PATH_PAYLOAD marker in local stream.")
                    # Regex improved to exclude trailing quotes or braces if inside a str(dict)
                    match = re.search(r"VIDEO_FILE_PATH_PAYLOAD:([^\s'\"\}\]]+)", evt_str)
                    if match:
                        file_path = match.group(1)
                        logger.info(f"Extracted file path: {file_path}")
                        try:
                            if os.path.exists(file_path):
                                with open(file_path, "rb") as f:
                                    # Use global base64
                                    video_data = base64.b64encode(f.read()).decode("utf-8")
                                logger.info(f"Loaded base64 payload of length: {len(video_data)}")
                                # Cleanup temp file
                                os.remove(file_path)
                            else:
                                logger.error(f"Video file not found: {file_path}")
                        except Exception as e:
                            logger.error(f"Error loading video file: {e}")
                
                # Robust text extraction from ModelResponse or other text-bearing events
                try:
                    # Deep debug log for dict events
                    if isinstance(event, dict):
                        logger.info(f"Local Event Detail: {event.keys()}")
                        if "response" in event:
                             logger.info(f"Response data: {str(event['response'])[:200]}...")

                    # Refined text extraction: only look for text in specific places
                    def extract_clean_text(obj):
                        if isinstance(obj, str): 
                            # Exclude our internal markers from visible text
                            if "VIDEO_FILE_PATH_PAYLOAD:" in obj:
                                return ""
                            return obj
                        
                        if isinstance(obj, dict):
                            # Targeted extraction: only from 'parts' if it exists, or 'text'
                            text_out = ""
                            if "text" in obj and isinstance(obj["text"], str):
                                if "VIDEO_FILE_PATH_PAYLOAD:" not in obj["text"]:
                                    text_out += obj["text"]
                            
                            # If this is a content object with parts
                            parts = obj.get("content", {}).get("parts", []) if isinstance(obj.get("content"), dict) else []
                            if not parts and "parts" in obj: parts = obj["parts"]
                            
                            if isinstance(parts, list):
                                for p in parts:
                                    if isinstance(p, dict) and "text" in p:
                                        text_out += p["text"]
                            
                            # Fallback but avoid internal keys
                            # (Optional: we could recurse only into specific keys)
                            return text_out
                            
                        if isinstance(obj, list):
                            return "".join([extract_clean_text(i) for i in obj])
                        
                        if hasattr(obj, "text") and isinstance(obj.text, str):
                            return obj.text if "VIDEO_FILE_PATH_PAYLOAD:" not in obj.text else ""
                            
                        return ""

                    extracted_text = extract_clean_text(event)
                    if extracted_text:
                        # Heuristic to handle streaming updates (delta vs full)
                        if agent_response_text and extracted_text.startswith(agent_response_text):
                            agent_response_text = extracted_text
                        else:
                            if extracted_text not in agent_response_text:
                                 agent_response_text += extracted_text
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
