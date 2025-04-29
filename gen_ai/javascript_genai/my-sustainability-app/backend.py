#%%
import logging
import os
import json
from typing import override, AsyncGenerator, Dict, Any, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from google.genai import types
from google.adk.runners import Runner
from google.adk.tools import VertexAiSearchTool, google_search
from google.adk.agents import LlmAgent, BaseAgent, ParallelAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

datastore_id = "projects/vtxdemos/locations/global/collections/default_collection/dataStores/countries-and-their-cultur_1706277976842"
vertex_search_tool = VertexAiSearchTool(data_store_id=datastore_id)
model_id = "gemini-2.0-flash-001"


class WorkFlow(BaseAgent):
    """Orchestrates parallel search followed by analysis."""
    local_search_agent: LlmAgent
    google_search_agent: LlmAgent
    analyzer_agent: LlmAgent
    parallel_agent: ParallelAgent

    model_config = {"arbitrary_types_allowed": True}

    def __init__(
            self,
            name: str,
            local_search_agent: LlmAgent,
            google_search_agent: LlmAgent,
            analyzer_agent: LlmAgent
    ):
        parallel_agent_instance = ParallelAgent(
            name="ParallelSearchAgent",
            sub_agents=[local_search_agent, google_search_agent]
        )
        super().__init__(
            name=name,
            local_search_agent=local_search_agent,
            google_search_agent=google_search_agent,
            parallel_agent=parallel_agent_instance,
            analyzer_agent=analyzer_agent
        )

    @override
    async def _run_async_impl(
            self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Executes the parallel search and analysis workflow."""
        logger.info(f"[{self.name}] Starting parallel search and analysis workflow.")

        logger.info(f"[{self.name}] Running {self.parallel_agent.name}...")
        async for event in self.parallel_agent.run_async(ctx):
            yield event

        logger.info(f"[{self.name}] Retrieving search results from session state...")
        local_search_result = ctx.session.state.get(self.local_search_agent.output_key)
        google_search_result = ctx.session.state.get(self.google_search_agent.output_key)

        logger.info(f"[{self.name}] Retrieved local search result (key='{self.local_search_agent.output_key}'): {local_search_result is not None}")
        logger.info(f"[{self.name}] Retrieved google search result (key='{self.google_search_agent.output_key}'): {google_search_result is not None}")

        if local_search_result and google_search_result:
            logger.info(f"[{self.name}] Running {self.analyzer_agent.name}...")
            async for event in self.analyzer_agent.run_async(ctx):
                yield event
        else:
            logger.warning(f"[{self.name}] Skipping {self.analyzer_agent.name}: One or both search results missing from session state.")

        logger.info(f"[{self.name}] Workflow finished.")

local_search_agent = LlmAgent(
    name="VertexAI_Search",
    model=model_id,
    instruction="""You are a local research analyst. Use your Vertex AI Search tool to gather specific information
from the configured datastore to help answer the user's query: {{user_query}}
Focus on information relevant to the query.
""",
    description="Gather information using a specific Vertex AI Search datastore.",
    tools=[vertex_search_tool],
    output_key="local_search_result"
)

google_search_agent = LlmAgent(
    name="Google_Search",
    model=model_id,
    instruction="""You are an internet researcher. Use the Google Search tool to find relevant, up-to-date
information from the web to help answer the user's query: {{user_query}}
Focus on information relevant to the query.
""",
    description="An Agent to do internet research.",
    tools=[google_search],
    output_key="google_search_result"
)

analyst_agent = LlmAgent(
    name="Analyst_Agent",
    model=model_id,
    instruction=f"""You are a helpful research analyst.
        Your main task is to synthesize the information provided by previous search agents.
        The results are available in the session state under the keys:
        - '{local_search_agent.output_key}' (from Vertex AI Search)
        - '{google_search_agent.output_key}' (from Google Search)

        Review these results and provide a concise, comprehensive summary that directly answers
        the original user query: {{user_query}}
        Present the findings clearly.
        """,
    output_key="final_summary"
)

workflow = WorkFlow(
    name="WorkFlowAgent",
    local_search_agent=local_search_agent,
    google_search_agent=google_search_agent,
    analyzer_agent=analyst_agent
)


APP_NAME = "Analyzer"
session_service = InMemorySessionService()
runner = Runner(
    agent=workflow,
    app_name=APP_NAME,
    session_service=session_service
)


app = FastAPI(
    title="Agent Workflow API",
    description="API to invoke the multi-agent search and analysis workflow."
)

origins = [
    "http://localhost:3000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvokeRequest(BaseModel):
    user_id: str = "default_user"
    session_id: Optional[str] = None
    query: str

class InvokeResponse(BaseModel):
    session_id: str
    final_response: Optional[str] = None
    final_session_state: Dict[str, Any]


@app.post("/invoke", response_model=InvokeResponse)
def invoke_agent_workflow(request: InvokeRequest):
    """
    Invokes the agent workflow with the given query and session details.
    """
    user_id = request.user_id
    session_id = request.session_id or user_id
    user_query = request.query

    logger.info(f"Received request for user '{user_id}', session '{session_id}'")
    logger.info(f"Query: {user_query}")

    current_state = {"user_query": user_query}
    try:
        session = session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        logger.info(f"Creating new session '{session_id}'")
        session = session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state=current_state
        )
        logger.info(f"Initial session state: {session.state}")

    except Exception as e:
        logger.error(f"Error during session management: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Session management error: {e}")

    content = types.Content(role='user', parts=[types.Part(text=user_query)])
    final_response_text = None
    final_session_state = {}

    try:
        logger.info(f"--- Starting Runner for session '{session_id}' ---")
        events = runner.run(user_id=user_id, session_id=session_id, new_message=content)

        logger.info(f"--- Processing Events for session '{session_id}' ---")
        for event in events:
            if event.is_final_response() and event.author == analyst_agent.name:
                if event.content and event.content.parts:
                    logger.info(f"Captured final response from [{event.author}]: {event.content.parts[0].text}")
                    final_response_text = event.content.parts[0].text
                else:
                    logger.warning(f"Final response event from {analyst_agent.name} has no content.")

        logger.info(f"--- Runner Finished for session '{session_id}' ---")

        final_session = session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
        if final_session:
            final_session_state = final_session.state
            logger.info(f"Final session state for '{session_id}': {json.dumps(final_session_state, indent=2)}")
        else:
            logger.error(f"Could not retrieve final session state for '{session_id}'.")

    except Exception as e:
        logger.error(f"Error during agent execution for session '{session_id}': {e}", exc_info=True)
        final_session = session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
        final_session_state = final_session.state if final_session else {}
        raise HTTPException(status_code=500, detail=f"Agent execution error: {e}")

    return InvokeResponse(
        session_id=session_id,
        final_response=final_response_text,
        final_session_state=final_session_state
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
