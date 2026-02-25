import asyncio
import logging
import uuid
import os
from typing import Annotated, AsyncGenerator, Dict, Any

from google.adk.agents import LlmAgent, SequentialAgent, Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Constants
MODEL_NAME = "gemini-2.5-flash"

# --- 1. Define Background Pipeline Components ---

# A tool that simulates long-running work
def heavy_processing_tool(data: str) -> str:
    """Simulates a heavy processing task by sleeping."""
    # Note: In a real tool, this would be async or run in a thread executor
    # For simulation purposes in the tool call, we just return a status
    return f"Processed data: {data}"

async def run_heavy_processing(data: str) -> str:
    """Async wrapper/implementation if needed for the tool."""
    logger.info(f"Starting heavy processing for: {data}")
    await asyncio.sleep(5) # Simulate 5 seconds work
    logger.info(f"Finished heavy processing for: {data}")
    return f"Processed({data})"


# Agent 1: Validator
validator_agent = LlmAgent(
    name="Validator",
    model=MODEL_NAME,
    instruction="You are a validator. Check if the input request is valid 'work' related. If yes, output 'VALID'. If no, output 'INVALID'.",
    output_key="validation_status"
)

# Agent 2: Worker (Simulated via LLM + Tool, or just LLM for this demo)
# We will use an LLM that calls a 'processing' tool.
class ProcessingTool:
    async def process_data(self, data: str) -> str:
        """Processes the data. Takes about 5 seconds."""
        return await run_heavy_processing(data)

worker_agent = LlmAgent(
    name="Worker",
    model=MODEL_NAME,
    instruction="You are a worker. Call the process_data tool with the user's request.",
    tools=[ProcessingTool().process_data],
    output_key="work_result"
)

# Agent 3: Reporter
reporter_agent = LlmAgent(
    name="Reporter",
    model=MODEL_NAME,
    instruction="You are a reporter. Create a final summary report based on the 'work_result'.",
    output_key="final_report"
)

# The Pipe: Sequential Agent
pipeline_agent = SequentialAgent(
    name="BackgroundPipeline",
    sub_agents=[validator_agent, worker_agent, reporter_agent]
)

# --- 2. Define Main Agent & Delegation Logic ---

# We need a reference to the Runner or Service to spawn the new execution.
# However, inside a tool, we might not have direct access to the outer Runner.
# Pattern: The tool can launch a fire-and-forget asyncio Task.
# To make it "clean", the tool receives the intent and spawns the background task.

# We need a global or shared reference for the session service to run the background pipeline
# effectively on the same session or a side-session. 
# For this demo, we'll use a side-session or just a separate runner flow.

class DelegationTools:
    def __init__(self, session_service: InMemorySessionService):
        self.session_service = session_service

    async def start_background_task(self, task_description: str) -> str:
        """
        Starts a background pipeline to handle the task description.
        Returns immediately telling the user the task has started.
        """
        task_id = str(uuid.uuid4())
        logger.info(f"MainAgent delegating task {task_id}: {task_description}")

        # Create the background task
        asyncio.create_task(self._run_background_pipeline(task_id, task_description))

        return f"Task {task_id} started successfully. You can continue chatting."

    async def _run_background_pipeline(self, task_id: str, description: str):
        logger.info(f"Background Pipeline {task_id} STARTED.")
        
        # We create a new runner for the background pipeline
        # we can repurpose the session service if we want to share state, 
        # or create a new session.
        session_id = f"session_{task_id}"
        
        # Initialize session state for the pipeline
        await self.session_service.create_session(
            app_name="background_app",
            session_id=session_id,
            user_id="background_user"
        )
        
        # We need to inject the input into the session or as a message
        # For SequentialAgent, usually it runs based on the last message or state.
        # We'll send a user message to kick it off.
        
        pipeline_runner = Runner(
            agent=pipeline_agent,
            session_service=self.session_service,
            app_name="background_app"
        )
        
        input_content = types.Content(role="user", parts=[types.Part(text=f"Request: {description}")])
        
        try:
            # Execute the pipeline
            async for event in pipeline_runner.run_async(session_id=session_id, new_message=input_content, user_id="background_user"):
                pass # Consume events
            
            # Retrieve result
            session = await self.session_service.get_session(app_name="background_app", session_id=session_id, user_id="background_user")
            final_report = session.state.get("pipeline_output") or session.state.get("final_report")
            
            # NOTIFICATION (Simulation)
            # In a real app, this would send a WebSocket message or Push Notification
            print(f"\n[NOTIFICATION] Background Task {task_id} COMPLETE!\nResult: {final_report}\n")
            logger.info(f"Background Pipeline {task_id} COMPLETED. Result: {final_report}")

        except Exception as e:
            logger.error(f"Background Pipeline {task_id} FAILED: {e}")
            print(f"\n[NOTIFICATION] Background Task {task_id} FAILED: {e}\n")


async def main():
    # Setup
    api_key = os.getenv("GOOGLE_API_KEY")
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if not api_key and not project:
        logger.warning("Neither GOOGLE_API_KEY nor GOOGLE_CLOUD_PROJECT found in environment. Please set one.")
        # Proceeding might fail if the agents actually try to call the model
    
    session_service = InMemorySessionService()
    delegation_tools = DelegationTools(session_service)

    # Main Agent
    main_agent = LlmAgent(
        name="MainAssistant",
        model=MODEL_NAME,
        instruction="""
        You are a helpful assistant. 
        If the user asks to do a long-running task, analysis, or processing, 
        use the 'start_background_task' tool to offload it. 
        Do not wait for the result. Confirm to the user that it started.
        You can continue chatting about other things.
        """,
        tools=[delegation_tools.start_background_task]
    )

    main_runner = Runner(
        agent=main_agent,
        session_service=session_service,
        app_name="main_app"
    )

    session_id = "main_user_session"
    await session_service.create_session(app_name="main_app", session_id=session_id, user_id="main_user")

    print("--- ADK Async Delegation Demo ---")
    print("User: 'Analyze the stock market trends for me' (triggers background)")
    print("User: 'What is 2+2?' (proves main agent is free)")
    print("---------------------------------")

    # Interactive Loop
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        content = types.Content(role="user", parts=[types.Part(text=user_input)])
        
        # Run Main Agent
        async for event in main_runner.run_async(session_id=session_id, new_message=content, user_id="main_user"):
            if event.is_final_response():
                print(f"Agent: {event.content.parts[0].text}")
        
        # We don't block here, loop continues. 
        # Background tasks run in the event loop.

if __name__ == "__main__":
    asyncio.run(main())
