import os
import time
import asyncio
from dotenv import load_dotenv

# Load environment variables with override=True
load_dotenv(override=True)

# Set location explicitly to avoid warnings
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.sessions import InMemorySessionService
from google.genai import types
from mcp import StdioServerParameters


def execute_query_t1(query: str) -> tuple[str, float]:
    start_time = time.time()

    # Define Stdio parameters for the payroll MCP server
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "payroll_mcp_server.py"],
        env=os.environ.copy()
    )

    # Initialize the monolithic McpToolset exposing all tools
    payroll_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=server_params,
            timeout=30
        )
    )

    # Initialize the Single Agent
    agent = Agent(
        model="gemini-2.5-flash",
        name="monolithic_payroll_agent",
        instruction="""You are an expert payroll assistant. You have access to all payroll tools.
        Answer the user's questions by selecting the appropriate tools.
        Always identify the employee ID from the query.
        Be professional and concise.""",
        tools=[payroll_toolset]
    )

    # Run the query using Runner
    session_service = InMemorySessionService()
    
    runner = Runner(
        agent=agent,
        app_name="monolithic_app",
        session_service=session_service,
        auto_create_session=True
    )

    # Execute the conversation
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id="user_123", session_id="session_123", new_message=content)
    
    final_answer = ""
    for event in events:
        if event.is_final_response() and event.content:
            final_answer = event.content.parts[0].text.strip()
    
    elapsed = time.time() - start_time
    return final_answer, elapsed

def run_topology_1():
    print("\n--- Running Topology 1: Single Agent with Monolithic MCP Server ---")
    query = "Hi, I am employee EMP101. What is my current accrued PTO balance, and do I have any pending reimbursement claims?"
    print(f"Query: {query}")
    final_answer, elapsed = execute_query_t1(query)
    print("\nAgent Response:")
    print(final_answer)
    print(f"\nTime taken: {elapsed:.2f} seconds")

if __name__ == "__main__":
    run_topology_1()
