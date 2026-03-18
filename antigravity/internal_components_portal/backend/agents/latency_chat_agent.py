import os
import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("latency_chat_agent")

def chat_with_latency_data(messages: list, history_data: list, analysis_result: str = None, model_name: str = "gemini-2.5-flash") -> str:
    """
    Handles chatbot interactions for querying latency and execution data.
    """
    try:
        client = genai.Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
        
        system_instruction = f"""
You are the "Execution Insight" AI, an expert specialized in analyzing AI performance telemetry for the PwC Zero-Leak Security Proxy.
Your purpose is to answer user questions about the specific executions they are viewing in the Telemetry tab.

CONTEXT PROVIDED:
1. **Execution History**: A JSON array of all captured sessions, including metrics (TTFT, Total Time), reasoning steps (tool calls, thoughts), and token usage.
2. **Current Analysis**: {analysis_result if analysis_result else "No cross-session analysis generated yet."}

YOUR GUIDELINES:
- **Accuracy**: Base your answers strictly on the provided JSON data. If the user asks about the "slowest step," find the actual duration in the telemetry.
- **Traceability**: Mention specific session IDs or query titles when referring to data.
- **Conciseness**: Keep answers professional and efficient.
- **Visuals**: Use Markdown tables or lists to compare numbers.
- **Tone**: Professional, analytical, and elite.

EXPERT CAPABILITIES:
- Identify bottlenecks: "The SharePoint file read took 4.5s, representing 60% of the total time."
- Compare models: "Flash 2.5 consistently shows 30% lower TTFT than the alternative."
- Explain reasoning: "The agent spent 3 loops searching before finding the matching compliance document."

If you don't have enough data to answer a specific question, state it clearly and suggest running another query or performing a 'Cross-Session Analysis'.
"""
        
        # Prepare context by appending history to a system-like message or just as a preamble.
        # We'll use a single turn for this implementation, but keeping the conversation history if provided.
        
        # Structure content:
        # [System Message]
        # [Context: History JSON]
        # [Conversation History]
        
        context_preamble = f"### EXECUTION DATA CONTEXT:\n{json.dumps(history_data, indent=2)}"
        
        # Filter and prepare messages for the final call
        final_messages = []
        # Add context as the first user message or part of it
        user_prompt = messages[-1]["content"]
        combined_prompt = f"{context_preamble}\n\nUSER QUESTION: {user_prompt}"
        
        # For simplicity in this specialized chat, we just use the last prompt with the full context.
        # If we wanted full history, we'd need to be careful with context window size (though Gemini is huge).
        
        response = client.models.generate_content(
            model=model_name,
            contents=combined_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
            ),
        )
        
        return response.text.strip()
            
    except Exception as e:
        logger.error(f"Latency Chat failed: {e}")
        return f"### Chat Error\nAn error occurred while processing your request: {str(e)}"
