from google import genai
from google.genai import types
import os
from typing import List, Dict

def get_chat_stream(query: str, logs: List[Dict]):
    """
    Streams a response from Gemini using the provided logs as context.
    """
    # Initialize client.
    client = genai.Client(vertexai=True, location="us-central1")
    
    # Format context from logs
    context_str = "Here is the current telemetry log from the Academy Session:\n\n"
    for log in logs:
        l_type = log.get('type', 'INFO').upper()
        timestamp = log.get('timestamp', '')
        message = log.get('message', '')
        data = log.get('data')
        
        context_str += f"[{l_type}] {timestamp}: {message}\n"
        if data:
            context_str += f"Data: {data}\n"
        context_str += "---\n"

    system_instruction = """You are the Academy Support Subsystem, an advanced AI assistant from the year 3050.
Your role is to help students understand the Authentication (AuthN) and Authorization (AuthZ) flows, specifically Workload Identity Federation (WIF) and Security Token Service (STS).
You have access to the live telemetry logs from their current session.
Use this background context to explain what is happening under the hood.
When they ask about a chunk or packet, refer to the telemetry log provided.
Be concise, highly structured, and futuristic.
If they ask questions unrelated to the Academy session or cloud security, politely guide them back to the current workspace focus.
"""

    contents = [
        f"{context_str}\n\nUser Question: {query}"
    ]

    # Using gemini-2.5-flash for fast streaming and Compliance
    stream = client.models.generate_content_stream(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
    )
    
    for chunk in stream:
        if chunk.text:
            yield f"data: {chunk.text}\n\n"
    yield "data: [DONE]\n\n"
