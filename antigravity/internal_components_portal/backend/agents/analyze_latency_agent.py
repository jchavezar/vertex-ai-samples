import os
import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("analyze_latency_agent")

def analyze_latency_profiles(history_data: list, model_name: str = "gemini-3-flash-preview") -> str:
    """
    Analyzes a history array of latency profiles and outputs a comparative markdown report.
    """
    try:
        client = genai.Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
        
        system_instruction = """
You are a Principal AI Performance Engineer analyzing the execution telemetry of multiple LLM queries within the Zero-Leak Security Proxy.
Your goal is to parse the historical latency profiles provided in JSON format, compare the different runs, and explain *why* there are performance differences.

Focus on:
1. Total Turnaround Time.
2. Time to First Token (TTFT).
3. The number of 'Reasoning' or 'Tool' loops executed.
4. Token consumption differences between models (e.g. gemini-2.5-flash vs gemini-3.1-flash-lite-preview).
5. The architectural differences: Multi-pass synthesis vs Single-pass speed optimization.

Format your output in clean, readable Markdown. Use clear headings, bullet points, and highlight the most striking differences. Be direct, authoritative, and deeply analytical. Output ONLY the markdown report.
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
