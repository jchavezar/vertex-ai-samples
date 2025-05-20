#%%
import logging
from google.genai import types
from typing import override, AsyncGenerator
from google.adk.runners import Runner
from google.adk.tools import VertexAiSearchTool, google_search
from google.adk.agents import LlmAgent, BaseAgent, ParallelAgent
from google.adk.sessions import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

# Temporary to run inline
import os

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
# Temporary to run inline -- end


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

datastore_id = "projects/254356041555/locations/global/collections/default_collection/dataStores/countries-and-their-cultur_1706277976842"
vertex_search_tool = VertexAiSearchTool(data_store_id=datastore_id)

model_id = "gemini-2.0-flash-001"


class WorkFlow(BaseAgent):
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
        parallel_agent = ParallelAgent(
            name="ParallelAgent",
            sub_agents=[local_search_agent, google_search_agent]
        )

        super().__init__(
            name=name,
            local_search_agent=local_search_agent,
            google_search_agent=google_search_agent,
            parallel_agent=parallel_agent,
            analyzer_agent=analyzer_agent
        )

    @override
    async def _run_async_impl(
            self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        logger.info(f"[{self.name}] starting story generation workflow")

        async for event in self.parallel_agent.run_async(ctx):
            logger.info(f"[{self.name}] Event from ParallelAgent: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        local_search_result = ctx.session.state.get("local_search_result")
        google_search_result = ctx.session.state.get("google_search_result")

        if local_search_result and google_search_result:
            async for event in self.analyzer_agent.run_async(ctx):
                logger.info(f"[{self.name}] Event from Analyzer: {event.model_dump_json(indent=2, exclude_none=True)}")
                yield event


local_search_agent = LlmAgent(
    name="VertexAI_Search",
    model=model_id,
    instruction="""You are a local research analyst use your tool to gather as much information as possible
    to accomplish the main task.
    """,
    description="Gather information using a specific Vertex AI Search datastore.",
    tools=[vertex_search_tool],
    output_key="local_search_result"
)

google_search_agent = LlmAgent(
    name="Google_Search",
    model=model_id,
    instruction="""Your are an internet research, by using google search grounding gather as much information as
    possible.
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
        Indicate which parts where fulfilled with local_search_agent and which others with google_search_agent,
        write at the bottom the percentage of participation of each agent.
        """,
    output_key="final_summary" # Add an output key
)


workflow = WorkFlow(
    name="WorkFlowAgent",
    local_search_agent=local_search_agent,
    google_search_agent=google_search_agent,
    analyzer_agent=analyst_agent
)

APP_NAME = "Analyzer"
USER_ID = "jesus"
SESSION_ID = USER_ID

def generate_content(prompt: str):
    initial_state = {"user_query": prompt}

    session_service = InMemorySessionService()
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state
    )
    logger.info(f"Initial session state: {session.state}")

    runner = Runner(
        agent=workflow,
        app_name=APP_NAME,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text
    return final_response