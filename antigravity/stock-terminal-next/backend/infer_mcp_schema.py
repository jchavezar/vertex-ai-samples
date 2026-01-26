
import asyncio
import json
import os
import sys
import datetime
from dotenv import load_dotenv

# Ensure we can import src
sys.path.append(os.getcwd())

# Apply Patches
from src import factset_core
from src.smart_agent import create_smart_agent

load_dotenv()

TOKEN_FILE = "factset_tokens.json"

QUERIES = [
    # Introspection
    "List all your available tools and their arguments in a JSON format.",
    
    # Pricing
    "What is the current price of AAPL?",
    "Get the daily closing prices for MSFT from 2024-01-01 to 2024-02-01.",
    "Get the yearly prices for NVDA for the last 5 years.",
    
    # Fundamentals
    "What is the revenue and net income for Google for the last fiscal year?",
    "Get the EPS and P/E ratio for Amazon.",
    
    # Estimates
    "What are the sales estimates for Tesla for the next quarter?",
    "Get the consensus target price for Meta.",
    
    # Search / PDF
    "Search for recent news about OpenAI.",
    "Analyze this PDF: https://example.com/report.pdf" 
]

async def main():
    print("Starting Schema Inference...")
    
    # Load Token
    token = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f).get("default_chat", {})
            token = data.get("token")
            
    if not token:
        print("No token found. Exiting.")
        return

    # Create Agent
    try:
        agent = await create_smart_agent(token, model_name="gemini-2.0-flash-exp")
    except Exception as e:
        print(f"Failed to create agent: {e}")
        return

    print(f"Agent created with {len(agent.tools)} tools.")
    
    inferred_schema = {}
    
    import google.adk as adk
    from google.genai.types import Content, Part
    from google.adk.sessions.sqlite_session_service import SqliteSessionService
    
    # Use ephemeral session service
    session_service = SqliteSessionService("inference_sessions.db")

    for i, query in enumerate(QUERIES):
        print(f"\n--- Query {i+1}: {query} ---")
        
        session_id = f"inference_{i}_{datetime.datetime.now().timestamp()}"
        runner = adk.Runner(app_name="inference", agent=agent, session_service=session_service)
        await session_service.create_session(session_id=session_id, app_name="inference", user_id="user_1")
        
        msg = Content(role="user", parts=[Part(text=query)])
        
        try:
            async for event in runner.run_async(user_id="user_1", session_id=session_id, new_message=msg):
                # Capture Tool Calls
                if hasattr(event, "get_function_calls"):
                    calls = event.get_function_calls()
                    for call in calls:
                        print(f"  [Tool Call] {call.name}")
                        print(f"  [Args] {call.args}")
                        
                        # Merge into schema
                        if call.name not in inferred_schema:
                            inferred_schema[call.name] = {"examples": []}
                        
                        inferred_schema[call.name]["examples"].append({
                            "query": query,
                            "args": call.args if isinstance(call.args, dict) else getattr(call.args, "__dict__", str(call.args))
                        })

        except Exception as e:
            print(f"  Error running query: {e}")
            
    # Save Inferred Schema
    with open("inferred_mcp_schema.json", "w") as f:
        json.dump(inferred_schema, f, indent=2)
        
    print(f"\nInference Complete. Saved to inferred_mcp_schema.json")

if __name__ == "__main__":
    asyncio.run(main())
