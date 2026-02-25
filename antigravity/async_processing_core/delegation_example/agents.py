import asyncio
import logging
import uuid
import os
from typing import Callable, Optional
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Constants
MODEL_NAME = "gemini-2.5-flash"

# --- 1. Define Background Pipeline Components ---

async def run_heavy_processing(data: str) -> str:
    """Async wrapper/implementation if needed for the tool."""
    logger.info(f"Starting heavy processing for: {data}")
    await asyncio.sleep(5) # Simulate 5 seconds work
    logger.info(f"Finished heavy processing for: {data}")
    return f"Processed({data})"

class ProcessingTool:
    async def process_data(self, data: str) -> str:
        """Processes the data. Takes about 5 seconds."""
        return await run_heavy_processing(data)

# Agent 1: Validator
validator_agent = LlmAgent(
    name="Validator",
    model=MODEL_NAME,
    instruction="You are a validator. Check if the input request is valid 'work' related. If yes, output 'VALID'. If no, output 'INVALID'.",
    output_key="validation_status"
)

# Agent 2: Worker
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

# --- 2. Define Delegation Tools ---

class DelegationTools:
    def __init__(self, session_service: InMemorySessionService, on_complete: Optional[Callable[[str, str], None]] = None):
        self.session_service = session_service
        self.on_complete = on_complete

    async def start_background_task(self, task_description: str) -> str:
        """
        Starts a background pipeline to handle the task description.
        Returns immediately telling the user the task has started.
        """
        task_id = str(uuid.uuid4())
        logger.info(f"MainAgent delegating task {task_id}: {task_description}")

        # Create the background task
        asyncio.create_task(self._run_background_pipeline(task_id, task_description))

        return f"Task {task_id} started successfully."

    async def _run_background_pipeline(self, task_id: str, description: str):
        logger.info(f"Background Pipeline {task_id} STARTED.")
        session_id = f"session_{task_id}"
        
        await self.session_service.create_session(
            app_name="background_app",
            session_id=session_id,
            user_id="background_user"
        )
        
        pipeline_runner = Runner(
            agent=pipeline_agent,
            session_service=self.session_service,
            app_name="background_app"
        )
        
        input_content = types.Content(role="user", parts=[types.Part(text=f"Request: {description}")])
        result_text = "Failed or No Output"

        try:
            async for event in pipeline_runner.run_async(session_id=session_id, new_message=input_content, user_id="background_user"):
                pass
            
            session = await self.session_service.get_session(app_name="background_app", session_id=session_id, user_id="background_user")
            result_text = session.state.get("pipeline_output") or session.state.get("final_report") or "No Report Generated"
            
            logger.info(f"Background Pipeline {task_id} COMPLETED. Result: {result_text}")

        except Exception as e:
            logger.error(f"Background Pipeline {task_id} FAILED: {e}")
            result_text = f"Error: {e}"
        
        # Trigger Callback
        if self.on_complete:
            # We run callback in thread-safe way if needed, but for Streamlit 
            # we might need to be careful. pure python callback is fine for now.
            try:
                if asyncio.iscoroutinefunction(self.on_complete):
                    await self.on_complete(task_id, result_text)
                else:
                    self.on_complete(task_id, result_text)
            except Exception as e:
                logger.error(f"Callback failed: {e}")

def create_main_agent(session_service: InMemorySessionService, on_complete: Optional[Callable] = None, delegation_tools: Optional[DelegationTools] = None):
    if delegation_tools is None:
        delegation_tools = DelegationTools(session_service, on_complete=on_complete)
    
    agent = LlmAgent(
        name="MainAssistant",
        model=MODEL_NAME,
        instruction="""
        You are a helpful assistant. 
        If the user asks to do a long-running task, analysis, or processing, 
        use the 'start_background_task' tool to offload it. 
        Do not wait for the result. Confirm to the user that it started.
        
        CRITICAL: If the user asks how they will know when it's done, tell them:
        "You will see a notification in the app sidebar and a popup when the task completes."
        """,
        tools=[delegation_tools.start_background_task]
    )
    return agent
