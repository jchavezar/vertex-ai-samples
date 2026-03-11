import logging
from typing import AsyncGenerator
from typing_extensions import override

from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.genai import types

# Configuration
GEMINI_FLASH = "gemini-2.5-flash"

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventFlowAgent(BaseAgent):
    """
    Custom orchestrator agent that processes text in steps and yields events.
    """
    summary_agent: LlmAgent
    bullet_point_agent: LlmAgent
    sequential_agent: SequentialAgent

    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str, summary_agent: LlmAgent, bullet_point_agent: LlmAgent):
        sequential_agent = SequentialAgent(
            name="TextProcessingPipeline",
            sub_agents=[summary_agent, bullet_point_agent],
        )

        sub_agents_list = [sequential_agent]

        super().__init__(
            name=name,
            summary_agent=summary_agent,
            bullet_point_agent=bullet_point_agent,
            sequential_agent=sequential_agent,
            sub_agents=sub_agents_list,
        )

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        step = ctx.session.state.get("workflow_step", "start")
        logger.info(f"[{self.name}] Current workflow step: {step}")

        if step == "start":
            logger.info(f"[{self.name}] Running SummaryAgent...")
            async for event in self.summary_agent.run_async(ctx):
                yield event

            current_summary = ctx.session.state.get("current_summary")
            if not current_summary:
                logger.error(f"[{self.name}] Failed to generate summary. Aborting workflow.")
                return

            logger.info(f"[{self.name}] Summary generated. Pausing for user input.")
            ctx.session.state["workflow_step"] = "waiting_for_user"
            
            # Yield a special pause event
            yield Event(
                author="System",
                content=types.Content(parts=[types.Part(text="WAITING_FOR_USER_INPUT")]),
                id="pause_event",
                actions=EventActions(state_delta={"workflow_step": "waiting_for_user"})
            )
            return

        elif step == "waiting_for_user":
            user_decision = ctx.session.state.get("user_decision")
            logger.info(f"[{self.name}] Resuming workflow. User decision: {user_decision}")
            if user_decision == "continue":
                logger.info(f"[{self.name}] Running BulletPointAgent...")
                async for event in self.bullet_point_agent.run_async(ctx):
                    yield event
                
                ctx.session.state["workflow_step"] = "done"
                yield Event(
                    author="System",
                    content=types.Content(parts=[types.Part(text="Workflow sequence complete.")]),
                    id="sequence_complete",
                    actions=EventActions(state_delta={"workflow_step": "done", "user_decision": None})
                )
            else:
                ctx.session.state["workflow_step"] = "done"
                yield Event(
                    author="System",
                    content=types.Content(parts=[types.Part(text="Workflow cancelled by user.")]),
                    id="cancel_event",
                    actions=EventActions(state_delta={"workflow_step": "done", "user_decision": None})
                )

        elif step == "done":
            logger.info(f"[{self.name}] Workflow already completed.")
            yield Event(
                author="System",
                content=types.Content(parts=[types.Part(text="Workflow already completed.")]),
                id="done_event"
            )

# Instances
summary_agent = LlmAgent(
    name="SummaryAgent",
    model=GEMINI_FLASH,
    instruction="""You are an expert summarizer. Read the following text and provide a concise, high-level summary of its main points. Text: {input_text}""",
    input_schema=None,
    output_key="current_summary",
)

bullet_point_agent = LlmAgent(
    name="BulletPointAgent",
    model=GEMINI_FLASH,
    instruction="""You are an analytical assistant. Extract the 3 to 5 most important key takeaways from this summary and format them as bullet points. Summary: {current_summary}""",
    input_schema=None,
    output_key="key_takeaways",
)

root_agent = EventFlowAgent(
    name="EventFlowAgent",
    summary_agent=summary_agent,
    bullet_point_agent=bullet_point_agent,
)
