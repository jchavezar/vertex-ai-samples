import logging
import json
import asyncio
import time
from typing import List, Dict, Any
from google.adk.agents import Agent
from google.genai.types import Content, Part
from google.adk import Runner
from google.adk.sessions import InMemorySessionService

logger = logging.getLogger("reasoning_agent")

class ReasoningAgent:
    def __init__(self, session_service=None):
        self.session_service = session_service or InMemorySessionService()

    async def analyze_execution(self, trace_data: List[Dict[str, Any]]) -> str:
        """
        Analyzes the execution trace and generates a performance/reasoning narrative.
        """
        # 1. Filter Trace to relevant events (Tools, Steps, Latency)
        summary_lines = []
        for event in trace_data:
            e_type = event.get("type", "unknown")
            timestamp = event.get("timestamp", 0)
            
            # Basic formatting
            if e_type == "tool_call":
                summary_lines.append(f"[{timestamp}] Tool Call: {event.get('name')} (Args: {str(event.get('args'))[:100]}...)")
            elif e_type == "tool_result":
                res = str(event.get('result', ''))
                summary_lines.append(f"[{timestamp}] Tool Result: {event.get('name')} -> {res[:200]}...")
            elif e_type == "latency":
                summary_lines.append(f"[{timestamp}] Latency: {event.get('tool')} took {event.get('duration', 0):.2f}s")
            elif e_type == "system_status":
                content = event.get("content", "")
                if "Reasoning..." not in content:
                     summary_lines.append(f"[{timestamp}] Status: {content}")
        
        if not summary_lines:
            return "No execution steps recorded."

        trace_text = "\n".join(summary_lines)
        
        prompt = f"""
        You are an expert Observability Agent. 
        Analyze the following execution trace of an AI Agent interacting with financial tools.
        
        Generate a **"Reasoning & Performance Narrative"** in strict Markdown.
        
        **Trace Data**:
        {trace_text}
        
        **Output Requirements**:
        1. **Title**: Start with `### Execution Analysis`
        2. **Timeline Steps**: Break down the flow into 3-5 logical steps using **Bold Headers** (e.g., `#### 1. Initial Query`).
           - Use **bullet points** for details within each step.
           - Explicitly mention tool names in `code blocks`.
        3. **Latency & cognitive Checks**:
           - If a tool took >1s, add a bullet: `* ⚠️ Latency Alert: [Tool] took 1.2s`
           - If self-correction occurred, add a bullet: `* 🔄 Self-Correction: [Logic]`
        4. **Summary**: End with `### Summary` section (1-2 sentences).
        
        **Style Guide**:
        - Use clear paragraph breaks between sections.
        - **Bold** key terms.
        - Keep it cleaner and less dense than a raw log.
        
        **Example Format**:
        ### Execution Analysis
        
        #### 1. Initial Query & Strategy
        * The agent received the query and identified the need for `FactSet_GlobalPrices`.
        * It formulated a plan to fetch data for the last 1 year.
        
        #### 2. Data Retrieval
        * Called `FactSet_GlobalPrices` with frequency `AQ`.
        * ⚠️ **Latency Alert**: The tool took 1.5s to respond.
        
        ### Summary
        The agent successfully retrieved the data despite slight network latency.
        """

        try:
            # Use a fast model
            agent = Agent(
                name="reasoning_worker",
                model="gemini-2.5-flash", 
                instruction="You are a log analysis engine. Output valid Markdown.",
            )
            
            runner = Runner(app_name="reasoning", agent=agent, session_service=self.session_service)
            
            response_text = ""
            msg = Content(role="user", parts=[Part(text=prompt)])
            
            temp_id = f"reasoning_{int(time.time())}"
            # Ensure proper await for session creation
            await self.session_service.create_session(session_id=temp_id, app_name="reasoning", user_id="system")

            async for event in runner.run_async(user_id="system", session_id=temp_id, new_message=msg):
                 if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text
            
            return response_text

        except Exception as e:
            logger.error(f"Reasoning Gen Failed: {e}")
            return f"### Analysis Failed\nCould not generate reasoning narrative: {e}"
