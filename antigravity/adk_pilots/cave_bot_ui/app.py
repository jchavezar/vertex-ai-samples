import os

# 1. SET ENVIRONMENT VARIABLES BEFORE ANY ADK/GENAI IMPORTS
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
if "GOOGLE_CLOUD_PROJECT" not in os.environ:
    os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"

import uvicorn
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

app = FastAPI()

# --- STRUCTURED SCHEMA ---
class DesignAdvice(BaseModel):
    pillar: str = Field(description="The core design pillar (e.g. Palette, Typography, Motion)")
    suggestion: str = Field(description="Detailed suggestion based on Modern Cave style")
    implementation_hint: str = Field(description="Brief CSS or JS tip")

# 🧠 ADK Search Agent
def google_search(query: str) -> str:
    """Search the web for architecture info."""
    return f"Search result: The Modern Cave architecture is based on monolithic, organic structures."

# Using gemini-3-flash-preview + STRUCTURED OUTPUT
agent = LlmAgent(
    name="cave_researcher",
    model="gemini-3-flash-preview",
    instruction="""
    You are the 'Echo of the Cave'. 
    You help users understand the architectural philosophy of the Modern Cave.
    Always provide structured design advice.
    Keep your tone mysterious, professional, and slightly neofuturistic.
    """,
    tools=[google_search],
    output_schema=DesignAdvice,
    output_key="advice"
)

runner = Runner(
    app_name="cave_bot_app",
    agent=agent,
    session_service=InMemorySessionService(),
    auto_create_session=True
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

@app.post("/chat")
async def chat(request: ChatRequest):
    print(f"📨 Received: {request.message}")
    try:
        result = runner.run_async(
            user_id="user_123",
            session_id=request.session_id,
            new_message=types.Content(parts=[types.Part(text=request.message)], role="user")
        )
        
        full_text = ""
        async for event in result:
            if hasattr(event, 'text') and event.text:
                full_text += event.text
            elif hasattr(event, 'content') and event.content:
                for part in getattr(event.content, 'parts', []):
                    if hasattr(part, 'text') and part.text:
                        full_text += part.text
        
        # Try to parse the collected text as JSON
        if full_text:
            try:
                # Clean up potential markdown formatting if any
                clean_text = full_text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                
                json_resp = json.loads(clean_text)
                print(f"📡 Sending Structured: {json_resp}")
                return {"response": json_resp, "is_structured": True}
            except:
                print(f"📡 Sending Text: {full_text}")
                return {"response": full_text, "is_structured": False}

        return {"response": "The echo is silent.", "is_structured": False}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"response": f"Error: {str(e)}", "is_structured": False}

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
