import logging
from typing import AsyncGenerator, Optional
from typing_extensions import override

from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.genai import types

# Configuration - Using Allowed Models (Rule)
# Allowed: gemini-2.5-flash, gemini-2.5-pro, gemini-3-flash-preview, gemini-3-pro-preview
# Switching to gemini-2.5-flash as gemini-3-flash-preview is currently 404 in vtxdemos region.
GEMINI_MODEL = "gemini-2.5-flash"

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
        logger.info(f"[{self.name}] --- NEW INVOCATION ---")
        logger.info(f"[{self.name}] Session ID: {getattr(ctx.session, 'id', 'unknown')}")
        logger.info(f"[{self.name}] Current State Keys: {list(ctx.session.state.keys())}")
        
        # Identify current state
        step = ctx.session.state.get("workflow_step", "start")
        has_summary = "current_summary" in ctx.session.state
        
        # Robustness: Check for resume logic
        if step == "start" and has_summary:
            logger.info(f"[{self.name}] Detected existing summary, auto-resuming to waiting_for_user phase.")
            step = "waiting_for_user"

        logger.info(f"[{self.name}] Resolved Step: {step}")

        if step == "start":
            # 1. Plan Overview
            yield Event(
                author="System",
                content=types.Content(parts=[types.Part(text="### 🚀 Analysis Starting\nI'm beginning the document analysis. First, I'll provide a high-level summary, then await your review before extracting key takeaways.")]),
                id="plan_event"
            )

            # Capture initial input text if not already stored
            if "input_text" not in ctx.session.state:
                user_msg = None
                for event in reversed(ctx.session.events):
                    if getattr(event, 'author', '').lower() == 'user' and event.content and event.content.parts:
                        user_msg = event.content.parts[0].text
                        break
                if user_msg:
                    ctx.session.state["input_text"] = user_msg
                    logger.info(f"[{self.name}] Stored input_text from user message.")

            # Phase 1: Summary Extraction
            logger.info(f"[{self.name}] Executing SummaryAgent...")
            async for event in self.summary_agent.run_async(ctx):
                yield event

            # Prepare for wait
            ctx.session.state["workflow_step"] = "waiting_for_user"
            
            logger.info(f"[{self.name}] Yielding pause event. State set to waiting_for_user.")
            yield Event(
                author="System",
                content=types.Content(parts=[types.Part(text="---\n### ⌛ Summary Ready for Review\nHow would you like to proceed with the key takeaway extraction?\n\n1.  **Type 'Yes'** to proceed with standard bullet points.\n2.  **Provide specific instructions** (e.g., 'focus on financial metrics').\n3.  **Type 'Cancel'** to stop here.")]),
                id="pause_event"
            )
            return

        elif step == "waiting_for_user":
            # Identify the LATEST user message (the response to our pause)
            user_decision = ""
            for event in reversed(ctx.session.events):
                if getattr(event, 'author', '').lower() == 'user' and event.content and event.content.parts:
                    text = event.content.parts[0].text
                    # Check if this message is actually different from the original news text
                    if text != ctx.session.state.get("input_text"):
                        user_decision = text
                        break
            
            user_decision_clean = user_decision.lower().strip()
            logger.info(f"[{self.name}] User decision detected: '{user_decision_clean}'")

            if not user_decision:
                logger.warning(f"[{self.name}] No user decision found in events. Prompting again.")
                yield Event(
                    author="System",
                    content=types.Content(parts=[types.Part(text="Please let me know if you'd like to proceed ('Yes') or if you have specific instructions.")]),
                    id="re_prompt"
                )
                return

            # Handle Cancellation
            if any(keyword in user_decision_clean for keyword in ["cancel", "no", "stop", "exit"]):
                ctx.session.state["workflow_step"] = "done"
                yield Event(
                    author="System",
                    content=types.Content(parts=[types.Part(text="### 🛑 Workflow Stopped\nThe analysis has been cancelled as requested.")]),
                    id="cancel_event",
                    actions=EventActions(state_delta={"workflow_step": "done"})
                )
                return

            # Proceed to Extraction
            yield Event(
                author="System",
                content=types.Content(parts=[types.Part(text="### ✅ Proceeding\nTransitioning to key takeaways extraction...")]),
                id="resume_event"
            )
            
            # Handle custom instructions
            if user_decision_clean not in ["yes", "go", "proceed", "ok"]:
                ctx.session.state["user_instructions"] = user_decision
                logger.info(f"[{self.name}] Applying custom instructions: {user_decision}")
            else:
                ctx.session.state["user_instructions"] = "Standard key takeaways extraction."

            # Phase 2: Bullet Point Extraction
            logger.info(f"[{self.name}] Executing BulletPointAgent...")
            async for event in self.bullet_point_agent.run_async(ctx):
                yield event
            
            # Finalize
            ctx.session.state["workflow_step"] = "done"
            logger.info(f"[{self.name}] Workflow complete. State updated to done.")
            yield Event(
                author="System",
                content=types.Content(parts=[types.Part(text="### ✨ Analysis Complete\nI have extracted the key takeaways based on the summary. Is there anything else you'd like to analyze?")]),
                id="sequence_complete",
                actions=EventActions(state_delta={"workflow_step": "done"})
            )

        elif step == "done":
            logger.info(f"[{self.name}] Session already marked as done.")
            yield Event(
                author="System",
                content=types.Content(parts=[types.Part(text="Analysis complete. Please provide new text if you want to start a new analysis.")]),
                id="done_event"
            )

# Sub-Agent Definitions
summary_agent = LlmAgent(
    name="SummaryAgent",
    model=GEMINI_MODEL,
    instruction="""You are an expert summarizer. 
    Read the provided text and provide a concise, high-level summary.
    Avoid bullet points here, use paragraphs.
    
    Text to summarize:
    {input_text}""",
    output_key="current_summary",
)

bullet_point_agent = LlmAgent(
    name="BulletPointAgent",
    model=GEMINI_MODEL,
    instruction="""You are an analytical assistant. 
    Extract 3-5 critical key takeaways from the provided summary.
    Use bullet points for the output.
    
    User Custom Instructions: {user_instructions}
    
    Summary to analyze:
    {current_summary}""",
    output_key="key_takeaways",
)

root_agent = EventFlowAgent(
    name="EventFlowAgent",
    summary_agent=summary_agent,
    bullet_point_agent=bullet_point_agent,
)

