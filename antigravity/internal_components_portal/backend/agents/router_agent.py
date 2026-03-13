import os
import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("router_agent")

def get_intent(prompt: str) -> str:
    """
    Analyzes the user's prompt to determine if they are asking for information (SEARCH)
    or asking to perform an action like creating a report/document (ACTION).
    Returns "SEARCH" or "ACTION".
    """
    try:
        # Use a lightweight fast model for routing
        # The user requested gemini-3-flash-lite-preview but if unavailable gemini-2.5-flash is fine.
        model_name = "gemini-3-flash-preview"
        # We can fallback to gemini-2.5-flash if needed, but let's try the specified one first.
        
        client = genai.Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
        
        system_instruction = """
You are a highly efficient Intent Router for an Enterprise Security Proxy.
Your job is to read the user's prompt and output exactly one word from the following options:
- SEARCH: If the user is asking a question, looking for information, inquiring about data, policies, or general knowledge. Examples: "What is our travel policy?", "Tell me about the CFO", "How many employees do we have?".
- ACTION: If the user is asking to create, update, generate, or modify something. **KEY IDENTIFIER**: Verbs like "Create", "Generate", "Build", "Update", "Write to", "Move", "Delete". Examples: "Generate a PDF summary of X", "Create a report", "Update the SharePoint folder", "Summarize this into a new file".

CRITICAL: "Summarize this information" is SEARCH, but "Summarize this into a new PDF/File" is ACTION.

Respond ONLY with "SEARCH" or "ACTION". Do not include any other text or punctuation.
"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
            ),
        )
        
        intent = response.text.strip().upper()
        # Log evidence of API call for telemetry
        api_evidence = {
            "endpoint": "Vertex AI (Gemini Enterprise)",
            "model": model_name,
            "project": os.environ.get("GOOGLE_CLOUD_PROJECT"),
            "location": "us-central1"
        }
        logger.info(f"Intent detection API call evidence: {api_evidence}")

        # Strict normalization
        if "ACTION" in intent and "SEARCH" not in intent:
            final_intent = "ACTION"
        elif "SEARCH" in intent:
            final_intent = "SEARCH"
        else:
            final_intent = "SEARCH" # Default fallback
            
        return final_intent, api_evidence
            
    except Exception as e:
        logger.error(f"Router intent detection failed: {e}")
        # Default to SEARCH on failure
        return "SEARCH", {"error": str(e)}
