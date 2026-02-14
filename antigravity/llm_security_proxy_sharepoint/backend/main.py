import json
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from agent import agent
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

async def _chat_stream(messages: list):
    prompt = messages[-1]['content']
    # Ensure session exists
    session = await session_service.get_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id="default_sess")
    if not session:
        await session_service.create_session(app_name="PWC_Security_Proxy", user_id="default_user", session_id="default_sess")

    runner = Runner(app_name="PWC_Security_Proxy", agent=agent, session_service=session_service)
    
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
    parts = result.get('parts', []) if isinstance(result, dict) else getattr(result, 'parts', [])
    for part in parts:
        if isinstance(part, dict):
            if 'markdown_text' in part:
                yield AIStreamProtocol.text(part['markdown_text'])
            else:
                widget_payload = {
                    "type": "project_card",
                    "data": part
                }
                yield AIStreamProtocol.data([widget_payload])
        else:
            if hasattr(part, 'markdown_text') and getattr(part, 'markdown_text'):
                yield AIStreamProtocol.text(part.markdown_text)
            else:
                widget_payload = {
                    "type": "project_card",
                    "data": part.model_dump()
                }
                yield AIStreamProtocol.data([widget_payload])

from auth_context import set_user_token

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        set_user_token(token)
    return StreamingResponse(_chat_stream(data.get("messages", [])), media_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
