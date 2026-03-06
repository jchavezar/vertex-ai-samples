import os
from datetime import datetime
import asyncio
import json
import uuid
from google.cloud import bigquery
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
from pydantic import BaseModel

class SQLQuery(BaseModel):
    query: str

app = FastAPI(title="Verity Nexus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()

# BigQuery Dataset configurations
BQ_DATASET = "verity_nexus_ledger"
BQ_TABLE = "ledger_transactions"

@app.get("/api/ledger")
def get_ledger():
    try:
        client = bigquery.Client()
        # You need the project ID in the query normally, or just assume default project
        table_ref = f"{client.project}.{BQ_DATASET}.{BQ_TABLE}"
        query = f"SELECT * FROM `{table_ref}` ORDER BY date DESC LIMIT 1000"
        query_job = client.query(query)
        results = query_job.result()
        
        rows = []
        for row in results:
            row_dict = dict(row)
            if 'amount_usd' in row_dict and row_dict['amount_usd'] is not None:
                row_dict['amount_usd'] = float(row_dict['amount_usd'])
            if 'date' in row_dict and row_dict['date'] is not None:
                row_dict['date'] = str(row_dict['date'])
            rows.append(row_dict)
                
        return {"transactions": rows}
    except Exception as e:
        print(f"Error fetching ledger: {e}")
        return {"error": str(e)}

@app.post("/api/sql")
def execute_sql(payload: dict):
    query = payload.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="No query provided")
        
    try:
        client = bigquery.Client()
        query_job = client.query(query)
        results = query_job.result()
        
        # It's a SELECT returning rows
        rows = []
        columns = [field.name for field in results.schema]
        for row in results:
            row_dict = dict(row)
            # Convert non-serializable types safely
            for key, value in row_dict.items():
                if 'amount_usd' in key and value is not None:
                    row_dict[key] = float(value)
                elif 'date' in key and value is not None:
                    row_dict[key] = str(value)
            rows.append(row_dict)
            
        result = {"results": rows, "columns": columns}
        return result
    except Exception as e:
        print(f"SQL Error: {e}")
        return {"error": str(e)}

@app.post("/api/mcp_chat")
async def mcp_chat_sync(request: Request):
    """A direct chat endpoint for the MCP Toolbox UI without streaming."""
    try:
        from google.adk.agents import LlmAgent
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
        
        body = await request.json()
        messages = body.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        last_message = messages[-1]["content"]
        session_id = body.get("id", str(uuid.uuid4()))
        
        # Dynamically determine identity and instruction
        is_protocol = last_message.startswith("EXECUTE PROTOCOL:")
        is_agentless = last_message.startswith("AGENTLESS_DIRECT:")
        
        if is_agentless:
            # TRUE AGENTLESS MODE: Bypassing LLM and ADK Runner entirely.
            # This simulates a direct binary pipe to the data source.
            try:
                # Extract the specific command/query
                cmd = last_message.replace("AGENTLESS_DIRECT:", "").strip()
                client = bigquery.Client()
                table_ref = f"{client.project}.{BQ_DATASET}.{BQ_TABLE}"
                
                # Manual routing for demo buttons
                if "Cayman" in cmd:
                    query = f"SELECT * FROM `{table_ref}` WHERE jurisdiction = 'Cayman' LIMIT 10"
                elif "Pending" in cmd:
                    query = f"SELECT * FROM `{table_ref}` WHERE approval_status = 'Pending' LIMIT 10"
                else:
                    query = f"SELECT * FROM `{table_ref}` WHERE vendor_name = 'Vertex Solutions' LIMIT 10"
                
                query_job = client.query(query)
                results = list(query_job.result())
                raw_json = json.dumps([dict(row) for row in results], indent=2, default=str)
                return {"reply": raw_json}
            except Exception as e:
                return {"reply": f"Direct Pipe Error: {str(e)}"}

        if is_protocol:
            # HYPER-SPEED HANDSHAKE MODE: No chat history, just data.
            agent_name = "Direct_Protocol_Engine"
            instruction = "Execute the tool as requested. OUTPUT: Markdown table ONLY. NO WORDS."
            adk_messages = [{"role": m["role"], "content": m["content"]} for m in messages] # Keep context but minimal instruction
        else:
            agent_name = "Forensic_Swarm_Auditor"
            instruction = """
            You are a lead Forensic Auditor for the Verity Nexus Swarm.
            Schema: trans_id, date, vendor_name, amount_usd, department, description, approval_status, jurisdiction.
            RULES: DO NOT use broken tools. ALWAYS use `get_all_transactions` and filter manually.
            Provide a professional forensic report.
            """
            adk_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

        from google.adk.agents import LlmAgent
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

        mcp_agent = LlmAgent(
            name=agent_name,
            model="gemini-2.5-flash", 
            instruction=instruction,
            tools=[
                MCPToolset(
                    connection_params=SseConnectionParams(
                        url="https://mcp-ledger-toolbox-oyntfgdwsq-uc.a.run.app/mcp/sse"
                    )
                )
            ]
        )
        
        runner = Runner(
            agent=mcp_agent,
            session_service=session_service,
            app_name="verity_nexus_mcp",
            auto_create_session=True
        )
        
        response_text = ""
        async for event in runner.run_async(new_message=user_msg, user_id="default_user", session_id=session_id):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        return {"reply": response_text}
    except Exception as e:
        print(f"Error in mcp_chat: {e}")
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
    uvicorn.run(app, host="0.0.0.0", port=8001)
