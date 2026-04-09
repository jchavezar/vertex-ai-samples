"""
Observability Orchestra - Multi-Agent Setup for Agent Engine Testing.

This agent demonstrates multi-model orchestration with:
- Root agent (Gemini 2.5 Flash) for routing
- Claude sub-agent for analytical tasks
- Gemini Flash-Lite sub-agent for creative tasks

Tracing is enabled to test Agent Engine observability features.

REGION HACKS:
1. Agent Engine only supports us-central1
2. Claude models only available in us-east5/europe-west1/global
3. Gemini 3.1 Flash-Lite Preview only available on global endpoint

We create custom model wrappers that override the region/location for each model
while keeping Agent Engine in us-central1.
"""
import os
from functools import cached_property
from dotenv import load_dotenv

# Load environment before ADK imports
load_dotenv(override=True)

# Ensure Vertex AI mode
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "1")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.anthropic_llm import Claude, get_tracking_headers as get_anthropic_headers
from google.adk.models.google_llm import Gemini
from google.adk.utils._google_client_headers import get_tracking_headers as get_gemini_headers
from google.adk.models.registry import LLMRegistry
from anthropic import AsyncAnthropicVertex
from google.genai import Client, types

# Region configuration (separate from Agent Engine region)
CLAUDE_REGION = os.getenv("CLAUDE_REGION", "us-east5")
GEMINI_GLOBAL_REGION = os.getenv("GEMINI_GLOBAL_REGION", "global")


class ClaudeUsEast5(Claude):
    """Claude wrapper that uses us-east5 region instead of GOOGLE_CLOUD_LOCATION.

    This allows Claude to work when Agent Engine is deployed to us-central1,
    which doesn't support Claude models directly.
    """

    @cached_property
    def _anthropic_client(self) -> AsyncAnthropicVertex:
        if "GOOGLE_CLOUD_PROJECT" not in os.environ:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT must be set for using Anthropic on Vertex."
            )

        # Use us-east5 for Claude instead of GOOGLE_CLOUD_LOCATION
        return AsyncAnthropicVertex(
            project_id=os.environ["GOOGLE_CLOUD_PROJECT"],
            region=CLAUDE_REGION,  # Override to us-east5
            default_headers=get_anthropic_headers(),
        )


class GeminiGlobal(Gemini):
    """Gemini wrapper that uses global endpoint instead of regional.

    This allows Gemini 3.1 Flash-Lite Preview to work when Agent Engine
    is deployed to us-central1, as the model is only available on global.
    """

    @cached_property
    def api_client(self) -> Client:
        """Override to use global location for Vertex AI."""
        # Create client with global location explicitly set
        return Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=GEMINI_GLOBAL_REGION,  # Override to global
            http_options=types.HttpOptions(
                headers=get_gemini_headers(),
                retry_options=self.retry_options,
            ),
        )


# Register custom wrappers
LLMRegistry.register(ClaudeUsEast5)
LLMRegistry.register(GeminiGlobal)

# Model configuration
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
FLASHLITE_MODEL = os.getenv("FLASHLITE_MODEL", "gemini-3.1-flash-lite-preview")
ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "gemini-2.5-flash")

print(f"[Agent Init] Claude model: {CLAUDE_MODEL}")
print(f"[Agent Init] Flash-Lite model: {FLASHLITE_MODEL}")
print(f"[Agent Init] Orchestrator model: {ORCHESTRATOR_MODEL}")

# Sub-Agent 1: Claude Analyst (for Product Research - analytical side)
# Use custom ClaudeUsEast5 wrapper to route to us-east5 region
market_analyst = LlmAgent(
    name="market_analyst",
    model=ClaudeUsEast5(model=CLAUDE_MODEL),
    description="Market research analyst for product launch research.",
    instruction="""Analyze the product/market opportunity. Provide:

## Competitive Landscape
- Key competitors and their strengths/weaknesses

## Market Opportunity
- Market size and growth potential

## SWOT Analysis
- Strengths, Weaknesses, Opportunities, Threats

## Risks
- Key challenges to consider

Be concise. Use bullet points.""",
)

# Sub-Agent 2: Gemini Flash-Lite Creator (for Product Research - creative side)
# Use custom GeminiGlobal wrapper to route to global endpoint
creative_strategist = LlmAgent(
    name="creative_strategist",
    model=GeminiGlobal(model=FLASHLITE_MODEL),
    description="Creative strategist for product launch research.",
    instruction="""Generate creative assets for the product. Provide:

## Product Names (5 options)
- Creative, memorable names

## Taglines (3 options)
- Catchy one-liners

## Marketing Angles
- Key positioning strategies

## Target Audience
- Primary buyer personas

Be punchy and creative.""",
)

# Sequential Agent: Runs BOTH analysts for product research
product_research_agent = SequentialAgent(
    name="product_research",
    description=(
        "Product launch research team. ONLY use when user explicitly asks for "
        "'product research', 'launch analysis', or 'market research for [product]'. "
        "Runs market analysis AND creative strategy in sequence."
    ),
    sub_agents=[market_analyst, creative_strategist],
)

# Root Agent: Fast responder + Product Research orchestrator
root_agent = LlmAgent(
    name="assistant",
    model=ORCHESTRATOR_MODEL,
    description="General assistant that answers questions directly. Only delegates for product research.",
    sub_agents=[product_research_agent],
    instruction="""You are a fast, helpful assistant.

## DEFAULT BEHAVIOR (99% of questions)
Answer the user's question DIRECTLY. Be concise and helpful.
Do NOT delegate for general questions.

Examples you answer directly:
- "What is Python?" -> Answer directly
- "How does OAuth work?" -> Answer directly
- "Write a hello world" -> Answer directly
- Greetings, jokes, chat -> Answer directly

## SPECIAL CASE: Product Research
ONLY delegate to **product_research** when user EXPLICITLY asks for:
- "product research for [X]"
- "launch analysis for [X]"
- "market research for [product]"
- "help me research launching [product]"

The product_research agent will automatically run BOTH:
1. Market analysis (Claude) - competitive landscape, SWOT
2. Creative strategy (Flash-Lite) - naming, taglines, positioning

## RULES
- General questions -> ANSWER DIRECTLY (fast)
- Product research requests -> delegate to product_research
- When in doubt, answer directly""",
)

if __name__ == "__main__":
    print(f"""
========================================
Observability Orchestra - Agent Config
========================================
Orchestrator: {ORCHESTRATOR_MODEL}
Claude Agent: {CLAUDE_MODEL}
Flash-Lite Agent: {FLASHLITE_MODEL}
Sub-agents: {[a.name for a in root_agent.sub_agents]}
========================================
""")
