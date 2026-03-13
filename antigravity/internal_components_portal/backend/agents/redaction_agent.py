import os
import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("redaction_agent")

def generalize_content(content: str, model_name: str = "gemini-3-flash-preview") -> str:
    """
    Generalizes or redacts sensitive information while maintaining the core insight.
    Follows 'Zero-Leak Protocol': No exact names of individuals, no specific numbers 
    that could identify individuals, no exact addresses, etc.
    """
    try:
        client = genai.Client(vertexai=True, project=os.environ.get("GOOGLE_CLOUD_PROJECT"), location="us-central1")
        
        system_instruction = """
You are a 'Zero-Leak Security Redaction' expert.
Your goal is to take a grounded intelligence response and 'generalize' it for safer external distribution.

RULES:
1. NO NAMES OF INDIVIDUALS: If a person's name appears (e.g., Jennifer Anne Walsh), replace it with their title or 'the executive'.
2. NO EXACT COMPENSATION: If a salary or bonus is mentioned (e.g., $625,000), generalize it (e.g., 'competitive with industry standards', 'within the executive range', 'mid-six figures').
3. NO IDENTIFIABLE ADDRESSES: If an exact street address is present, generalize to the city or region.
4. MAINTAIN STYLE: Keep the professional tone and structure of the original response.
5. KEEP THE TRUTH: Do not change the underlying meaning, just the exposure level.
6. OUTPUT ONLY THE FINAL GENERALIZED TEXT.

Example:
Input: 'CFO Jennifer Anne Walsh has a base salary of $625k.'
Output: 'The current CFO receives a base salary competitive with professional executive standards.'
"""

        response = client.models.generate_content(
            model=model_name,
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
            ),
        )
        
        return response.text.strip()
            
    except Exception as e:
        logger.error(f"Redaction failed: {e}")
        # On failure, return with a warning or the original text with a disclaimer
        return content + "\n\n⚠️ (Note: Automatic redaction failed. Please review for sensitive data.)"
