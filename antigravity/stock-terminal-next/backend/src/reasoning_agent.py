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
        
        Generate a "Reasoning & Performance Narrative" in Markdown.
        
        Trace:
        {trace_text}
        
        Requirements:
        1. **Title**: "Execution Analysis"
        2. **Timeline**: Break down the flow into 3-5 logical steps (e.g., "Initial Fetch", "Self-Correction", "Final Answer").
           - Infer the "intent" of each step.
           - Mention specific tools used.
           - Note any self-correction (e.g., if a tool failed or returned partial data and the agent tried again).
        3. **Latency Explanation**:
           - If there are specific slow tools (latency > 1s), explain clearly: "The 'FactSet_GlobalPrices' tool took 1.2s to retrieve data."
           - If the agent had to "think" or "correct" itself, mention that as "Cognitive Processing".
        4. **Tone**: Professional, technical but accessible. Like a senior engineer explaining the logs to a user.
        5. **No Hallucinations**: Only describe what happened in the trace.
        
        Example Output Format:
        ### Execution Analysis
        **1. Initial Query**
        The agent identified the need for stock prices and called `FactSet_GlobalPrices`.
        
        **2. Data Retrieval**
        FactSet returned the data successfully in 1.2s.
        
        **Summary**
        Effective execution with no retries.
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
