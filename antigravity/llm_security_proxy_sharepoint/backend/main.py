import json
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from agent import get_agent
from protocol import AIStreamProtocol
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../.env")

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_LOCATION"] = "global"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()

class ChatRequest(BaseModel):
    messages: list

async def _chat_stream(messages: list, model_name: str):
    prompt = messages[-1]['content']
    # Ensure session exists
    session = await session_service.get_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id="default_sess")
    if not session:
        await session_service.create_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id="default_sess")

    runner = Runner(app_name="PWC_Security_Proxy", agent=get_agent(model_name), session_service=session_service)
    
    from google.genai import types
    msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    
    # Run the agent (synchronously handles the tools and LLM)
    async for event in runner.run_async(user_id="default_user", session_id="default_sess", new_message=msg):
        pass
        
    session = await session_service.get_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id="default_sess")
    
    # Get the resulting parts from schema
    result = session.state.get("proxy_output") if session else None
    if not result:
        yield AIStreamProtocol.text("Error: Failed to generate response or no output returned.")
        return

    # Yield parts according to Vercel AI SDK Zero-Parsing stream protocol
    if isinstance(result, dict):
        text_content = result.get('markdown_text', '')
        cards = result.get('project_cards', [])
        
        if text_content:
            yield AIStreamProtocol.text(text_content)
            
        for card in cards:
            widget_payload = {
                "type": "project_card",
                "data": card
            }
            yield AIStreamProtocol.data([widget_payload])
    else:
        text_content = getattr(result, 'markdown_text', '')
        cards = getattr(result, 'project_cards', [])
        
        if text_content:
            yield AIStreamProtocol.text(text_content)
            
        for card in cards:
            widget_payload = {
                "type": "project_card",
                "data": card.model_dump() if hasattr(card, 'model_dump') else card
            }
            yield AIStreamProtocol.data([widget_payload])

from auth_context import set_user_token

async def auth_error_stream(message: str):
    yield AIStreamProtocol.text(message)

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    model_name = data.get("model", "gemini-3-pro-preview")
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        msg = "🔒 **Access Denied: Zero-Leak Protocol active.**\n\nPlease sign in using the button in the top right to securely query the enterprise index."
        return StreamingResponse(auth_error_stream(msg), media_type="text/plain; charset=utf-8")
        
    token = auth_header.split(" ")[1]
    if not token or token in ["null", "undefined"]:
        msg = "🔒 **Access Denied: Invalid token.**\n\nPlease sign in using the button in the top right to securely query the enterprise index."
        return StreamingResponse(auth_error_stream(msg), media_type="text/plain; charset=utf-8")
        
    set_user_token(token)
    return StreamingResponse(_chat_stream(data.get("messages", []), model_name), media_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
