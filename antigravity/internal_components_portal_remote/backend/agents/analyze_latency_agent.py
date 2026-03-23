import os
import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("analyze_latency_agent")

def analyze_latency_profiles(history_data: list, model_name: str = "gemini-2.5-flash") -> str:
    """
    Analyzes a history array of latency profiles and outputs a comparative markdown report.
    """
    try:
        client = genai.Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
        
        system_instruction = """
You are a Principal AI Performance Engineer at Deloitte's Global AI Center assigned to analyze execution telemetry for the Zero-Leak Security Proxy.
Your goal is to parse historical latency profiles and generate an ELITE performance report that highlights bottlenecks and architectural advantages.

FORMATTING REQUIREMENTS (CRITICAL):
1. **Bold Highlighting**: Use bold text for all critical numeric values (e.g., **TTFT: 1.2s**, **95th Percentile: 4.5s**).
2. **Color Simulation**: Use standard Markdown callouts (GitHub alerts) to segment the report:
   - Use `> [!NOTE]` for baseline observations.
   - Use `> [!TIP]` for optimization opportunities.
   - Use `> [!IMPORTANT]` for critical performance differences.
3. **Structured Tables**: Use tables to compare different models (e.g., gemini-2.5-flash vs gemini-3-flash) across key metrics (Total Time, Reasoning Steps, Tool Loops).
4. **Architectural Deep-Dive**: Explain the "Why" behind the numbers (e.g., "Flash 2.5 uses an optimized single-pass tool discovery reducing cold-start latency by 40%").
5. **Final Verdict**: End with a "Performance Verdict" summarizing which model/mode is optimal for the current workload.

Be direct, technical, and premium. Output ONLY the markdown report.
"""
        
        # We can safely pass the history directly since we are using Gemini with a 1M context window, 
        # but the JSON dump should be clean.
        content_str = json.dumps(history_data, indent=2)

        response = client.models.generate_content(
            model=model_name,
            contents=content_str,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            ),
        )
        
        return response.text.strip()
            
    except Exception as e:
        logger.error(f"Latency Analysis failed: {e}")
        return f"### Analysis Failed\nAn error occurred while analyzing the latency profiles: {str(e)}"
