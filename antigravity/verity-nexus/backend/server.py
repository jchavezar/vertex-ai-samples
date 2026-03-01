import os
from datetime import datetime
import asyncio
import json
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

from protocol import AIStreamProtocol
from agents.orchestrator.main import orchestrator
from google.adk.sessions import InMemorySessionService
from google.adk import Runner # Using direct import
from google.genai import types

app = FastAPI(title="Verity Nexus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()

@app.get("/api/ledger")
def get_ledger():
    try:
        conn = psycopg2.connect(
            host="localhost", port="5433", user="auditor", password="nexus", dbname="ledger"
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM ledger_transactions ORDER BY date DESC LIMIT 1000")
        rows = cur.fetchall()
        
        for row in rows:
            if 'amount_usd' in row and row['amount_usd'] is not None:
                row['amount_usd'] = float(row['amount_usd'])
            if 'date' in row and row['date'] is not None:
                row['date'] = str(row['date'])
                
        conn.close()
        return {"transactions": rows}
    except Exception as e:
        print(f"Error fetching ledger: {e}")
        return {"error": str(e)}

@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    last_message = messages[-1]["content"]
    user_id = "default_user"
    session_id = body.get("id", str(uuid.uuid4()))
    
    runner = Runner(
        agent=orchestrator, 
        session_service=session_service, 
        app_name="verity_nexus",
        auto_create_session=True
    )

    async def generate():
        try:
            user_msg = types.Content(role="user", parts=[types.Part(text=last_message)])
            
            # Track agent transitions for the Live Graph
            current_agent = "orchestrator"
            
            async for event in runner.run_async(new_message=user_msg, user_id=user_id, session_id=session_id):
                # Check for agent transition via the author or transfer_to_agent action
                if event.author and event.author != current_agent:
                    current_agent = event.author
                    yield AIStreamProtocol.data({
                        "type": "agent_transition",
                        "agent": current_agent,
                        "timestamp": datetime.now().isoformat()
                    })

                # Handle Content
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            yield AIStreamProtocol.text(part.text)
                        
                        if part.function_call:
                            # Stream tool calls for the reasoning stream
                            yield AIStreamProtocol.data({
                                "type": "reasoning_stream",
                                "content": f"Agent {current_agent} invoking tool {part.function_call.name}..."
                            })
                
                # Handle agent transfer actions
                if event.actions and event.actions.transfer_to_agent:
                    yield AIStreamProtocol.data({
                        "type": "agent_transition",
                        "agent": event.actions.transfer_to_agent,
                        "timestamp": datetime.now().isoformat()
                    })

                # Handle Structured Output (Final)
                if hasattr(event, "output") and event.output:
                    output_data = event.output.model_dump() if hasattr(event.output, "model_dump") else event.output
                    print(f"--- [DEBUG] Structured Output from {current_agent}: {json.dumps(output_data)[:200]}...")
                    
                    # Deduplicate or Merge
                    # If this is a WorkflowExecution from orchestrator, and it has empty findings,
                    # but we already had findings from a sub-agent, we might want to be careful.
                    # For now, we yield everything and let the UI handle the merge, but distinguish it.
                    yield AIStreamProtocol.data({
                        "type": "workflow_complete",
                        "agent": current_agent,
                        "data": output_data
                    })

                # Handle Final Output/Workflow Completion
                if event.is_final_response():
                    yield AIStreamProtocol.text("\n\n--- Workflow Complete ---")

        except Exception as e:
            print(f"Error in generate: {e}")
            import traceback
            traceback.print_exc()
            yield AIStreamProtocol.error(str(e))

    return StreamingResponse(generate(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
