"""Google ADK Agent Definition: Real-time Intelligence Agent.

This module defines the root ADK Agent instance using Google's Agent Development Kit.
It configures:
  1. The foundation model (Gemini 3 Flash Preview via Vertex AI).
  2. The system instruction guiding the agent's behavior and tool usage.
  3. The registered real-time tools.
"""

import os
from dotenv import load_dotenv
from google.adk.agents import Agent

# Import our custom real-time tools
from .tools import (
    get_stock_quote,
    get_company_profile,
    get_live_weather,
    get_crypto_quote,
)

# Load environment configuration (.env if present, overriding ambient shell defaults)
load_dotenv(override=True)

# Ensure Vertex AI settings for the demo
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

# Active Model: gemini-3.8-flash
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.8-flash")

SYSTEM_INSTRUCTION = """\
You are an executive Real-Time Intelligence Agent built with the Google Agent Development Kit (ADK).
Your goal is to provide accurate, real-time market data, company background, cryptocurrency pricing, and global weather conditions.

Guidelines:
1. ALWAYS use the provided tools for real-time data. Never invent or estimate prices, weather, or market metrics.
2. If a user asks a multifaceted or comparative question (e.g. "Compare Apple and Google stock, and give me the weather in Tokyo"), invoke the required tools systematically.
3. Be concise, professional, and visually structured. Use bullet points, bold highlights, and clean summaries.
4. When reporting financial figures, include the currency and percentage changes where available.
5. When reporting weather, provide both Celsius and Fahrenheit for international clarity.
"""

# The Root Agent: The primary intelligence unit in ADK
root_agent = Agent(
    name="realtime_intelligence_agent",
    model=MODEL_NAME,
    instruction=SYSTEM_INSTRUCTION,
    description="Real-time market, company, crypto, and global weather intelligence assistant.",
    tools=[
        get_stock_quote,
        get_company_profile,
        get_live_weather,
        get_crypto_quote,
    ],
)


def get_agent() -> Agent:
    """Helper function to return the root agent instance."""
    return root_agent
