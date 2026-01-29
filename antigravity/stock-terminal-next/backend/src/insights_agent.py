from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk import Runner
from google.genai import types
from google.adk.sessions import InMemorySessionService
import sys
import io
import secrets
import logging
import json

logger = logging.getLogger("insights_agent")

# --- SCHEMAS ---

class InsightItem(BaseModel):
    title: str = Field(description="Short title of the insight")
    content: str = Field(description="Main insight text/analysis")
    type: Literal['valuation', 'growth', 'risk', 'technical']
    score: float = Field(description="0-10 score (e.g. 8.5/10 for bullish)")
    evidence: List[str] = Field(description="Data points backing the insight")

class InsightsResponse(BaseModel):
    insights: List[InsightItem]
    summary: str
    follow_up_questions: List[str] = Field(description="3 short strategic follow-up questions")

# --- AGENT ---

INSIGHTS_INSTRUCTIONS = """
You are a Quantitative Financial Analyst.
Your goal is to generate deep, data-driven insights using Python code.

### TOOLS:
- `execute_python_code`: Use this to perform math, stats, or simple logic.
- You do NOT have external data access in code (no internet). Use provided context or make reasonable estimates for demonstration.

### RULES:
1. Generate 3 distinct insights: Valuation, Growth, and Risk.
2. Use Python to calculate potential upside/downside based on typical multiples (e.g. P/E=30 for Tech).
3. Return ONLY a JSON object conforming to `InsightsResponse`.
"""

def execute_python_code(code: str) -> str:
    """
    Executes Python code and returns stdout. 
    Use this for math, stats, or logical calculations.
    """
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    try:
        # Constrained execution
        exec(code, {"__builtins__": __builtins__}, {})
        return new_stdout.getvalue()
    except Exception as e:
        return f"Error: {e}"
    finally:
        sys.stdout = old_stdout

def create_insights_agent(model_name: str = "gemini-2.5-flash") -> LlmAgent:
    return LlmAgent(
        name="insights_agent",
        model=model_name,
        instruction=INSIGHTS_INSTRUCTIONS,
        tools=[execute_python_code],
        output_schema=InsightsResponse,
        output_key="insights_result"
    )

async def fetch_insights_dashboard(ticker: str = "FDS") -> str:
    """
    Orchestrates the Insights Agent.
    Returns a UI Command string.
    """
    session_service = InMemorySessionService()
    sid = f"insights_{ticker}_{secrets.token_hex(4)}"
    await session_service.create_session(session_id=sid, user_id="system", app_name="insights_svc")
    
    agent = create_insights_agent()
    runner = Runner(app_name="insights_svc", agent=agent, session_service=session_service)
    
    msg_text = f"Analyze {ticker}. Calculate fair value scenarios using code. output strictly JSON."
    msg = types.Content(role="user", parts=[types.Part(text=msg_text)])
    
    json_text = ""
    async for event in runner.run_async(user_id="system", session_id=sid, new_message=msg):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text: json_text += part.text
                
    # Clean and Parse
    try:
        clean_json = json_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        # Validate/Re-serialize to ensure safe UI Payload
        validated = InsightsResponse(**data)
        
        payload = {
            "type": "insights_update",
            "data": validated.model_dump()
        }
        
        return f"Generated Insights for {ticker}.\n\n[UI_COMMAND]{json.dumps(payload)}[/UI_COMMAND]"
        
    except Exception as e:
        logger.error(f"Insights failed: {e}")
        return f"Failed to generate insights: {e}"
