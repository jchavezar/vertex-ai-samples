import os
import json
import logging
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from agent import root_agent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dynamic Workflow Orchestrator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APP_NAME = "dynamic_workflow_app"
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

@app.post("/api/workflow")
async def start_workflow(request: Request):
    data = await request.json()
    action = data.get("action", "start")
    input_text = data.get("text", "")
    session_id = data.get("sessionId", "default-session")
    user_id = data.get("userId", "default-user")
    
    logger.info(f"Workflow requested for session {session_id} with action {action}")
    
    state_delta = {}
    try:
        session = await session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
        if not session:
            raise Exception("Session not found")
        if action == "start":
            state_delta["input_text"] = input_text
            state_delta["workflow_step"] = "start"
            state_delta["user_decision"] = None
        elif action == "continue":
            state_delta["user_decision"] = "continue"
        elif action == "cancel":
            state_delta["user_decision"] = "cancel"
    except Exception:
        state_delta["input_text"] = input_text
        state_delta["workflow_step"] = "start"
        state_delta["user_decision"] = None
        await session_service.create_session(
            app_name=APP_NAME, 
            user_id=user_id, 
            session_id=session_id, 
            state=state_delta
        )

    async def event_generator():
        content_text = f"Action: {action}"
        content = types.Content(role='user', parts=[types.Part(text=content_text)])
        events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content, state_delta=state_delta)
        
        async for event in events:
            # We are interested in partial or final responses from the sub-agents to stream them directly
            event_type = "update"
            part_text = ""
            author = getattr(event, "author", "System")
            
            # Fallback text extraction if possible
            if hasattr(event, "content") and event.content and hasattr(event.content, "parts") and event.content.parts:
                part_text = event.content.parts[0].text
                
            if getattr(event, "is_final_response", lambda: False)():
                event_type = "final"
                
            if part_text:
                if part_text == "WAITING_FOR_USER_INPUT":
                    event_type = "pause"
                    payload = {
                        "author": author,
                        "type": event_type,
                        "text": "Waiting for user approval to extract bullet points...",
                    }
                else:
                    payload = {
                        "author": author,
                        "type": event_type,
                        "text": part_text,
                    }
                yield f"data: {json.dumps(payload)}\n\n"
                
        yield f"data: {json.dumps({'type': 'complete', 'author': 'System', 'text': 'Workflow completed.'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
