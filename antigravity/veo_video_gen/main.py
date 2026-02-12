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

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        session_id = request.session_id
        logger.info(f"Processing chat for session {session_id}")
        
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

        # Use run_debug for simplicity to get all events at once
        events = await runner.run_debug(
            user_messages=prompt_text,
            session_id=session_id,
            user_id="user"
        )
        
        agent_response_text = ""
        video_data = None
        
        # Iterate events to find model response and video tool output
        for event in events:
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
        
        # If no text found via events, try to get from session history
        if not agent_response_text:
            try:
                if hasattr(session_service, 'sessions'):
                    session = session_service.sessions.get(session_id)
                    if session:
                        # Try different known ADK session history attributes
                        history = getattr(session, 'history', None) or getattr(session, 'messages', None)
                        if history and len(history) > 0:
                            last_msg = history[-1]
                            # Extract text from the last message
                            if hasattr(last_msg, 'content'):
                                agent_response_text = last_msg.content
                            elif hasattr(last_msg, 'text'):
                                agent_response_text = last_msg.text
                            elif hasattr(last_msg, 'parts'):
                                for part in last_msg.parts:
                                    if hasattr(part, 'text') and part.text:
                                        agent_response_text += part.text
            except Exception as e:
                logger.error(f"Failed to extract text from session: {e}")

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
