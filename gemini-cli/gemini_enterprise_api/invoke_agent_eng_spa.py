#!/usr/bin/env python3
"""
Invoke a Gemini Enterprise agent (e.g., "Eng-Spa") using the v1alpha/v1beta streamAssist API.

This script demonstrates how to programmatically invoke agents registered in
Gemini Enterprise (Google Cloud Discovery Engine) using the REST API.

Installation:
    pip install google-auth requests
"""

import os
import json
import requests
from google.auth.transport.requests import Request
import google.auth


# ============================================================================
# CONFIGURATION
# ============================================================================

# The project number for your Discovery Engine
PROJECT_NUMBER = "254356041555"

# Location where your Discovery Engine is deployed
LOCATION = "global"

# Collection name
COLLECTION = "default_collection"

# Your Gemini Enterprise engine ID
ENGINE_ID = "agentspace-testing_1748446185255"

# Assistant ID (typically "default_assistant")
ASSISTANT_ID = "default_assistant"

# Your registered agent's ID
# Placeholder for the specific "Eng-Spa" agent ID
# If not found, use a placeholder
AGENT_ID = "Eng-Spa" 

# Optional: Display name for logging purposes
AGENT_DISPLAY_NAME = "Eng-Spa"

# Sample query to test the agent
SAMPLE_QUERY = "Help me translate this sentence from English to Spanish: 'The sky is clear today.'"

# ============================================================================
# END CONFIGURATION
# ============================================================================


def get_access_token():
    """
    Get OAuth2 access token for Google Cloud API authentication.
    """
    credentials, project = google.auth.default(
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )

    if not credentials.valid:
        credentials.refresh(Request())

    return credentials.token


def invoke_agent_streamassist(query: str, verbose: bool = True) -> str:
    """
    Invoke a Gemini Enterprise agent using the streamAssist REST API.
    """

    # Construct the v1alpha/v1beta streamAssist endpoint URL
    # Using v1alpha for the agent-specific invocation pattern
    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/{COLLECTION}/"
        f"engines/{ENGINE_ID}/assistants/{ASSISTANT_ID}:streamAssist"
    )

    # Get OAuth2 access token for authentication
    token = get_access_token()

    # Prepare HTTP request headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER
    }

    # Prepare request body
    # Including agentsSpec to target the specific agent
    body = {
        "query": {
            "text": query
        },
        "agentsSpec": {
            "agentSpecs": [
                {
                    "agentId": AGENT_ID
                }
            ]
        }
    }

    # Prepare sanitized headers for logging
    log_headers = headers.copy()
    log_headers["Authorization"] = "Bearer <MASKED_TOKEN>"

    print("\n" + "=" * 60)
    print("--- REQUEST ---")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(log_headers, indent=2)}")
    print(f"Query: {query}")
    print(f"Target Agent: {AGENT_DISPLAY_NAME} ({AGENT_ID})")
    print(f"Body: {json.dumps(body, indent=2)}")
    print("=" * 60 + "\n")

    # Make the HTTP POST request with streaming
    print("Querying Gemini Enterprise Agent...\n")
    response = requests.post(url, headers=headers, json=body, stream=True)

    if response.status_code != 200:
        error_msg = f"Error {response.status_code}: {response.text}"
        print(f"ERROR: {error_msg}")
        return ""

    # Process the streaming response
    print("--- ANSWER ---")
    full_response = []
    
    # Process line-by-line for the stream
    for line in response.iter_lines():
        if not line:
            continue
            
        decoded_line = line.decode('utf-8').strip()
        
        # Simple extraction logic for demonstration
        # Look for text chunks in the JSON stream
        if '"text":' in decoded_line:
            # Clean up the line for simple parsing
            clean_line = decoded_line.rstrip(',')
            if not clean_line.endswith('}'):
                clean_line += '}'
            if not clean_line.startswith('{'):
                clean_line = '{' + clean_line
                
            try:
                data = json.loads(clean_line)
                text = data.get("text", "")
                if text:
                    print(text, end="", flush=True)
                    full_response.append(text)
            except json.JSONDecodeError:
                # If simple parsing fails, skip it for this demo
                continue

    print("\n" + "-" * 60)
    print("--- STREAM COMPLETED ---")

    return "".join(full_response)


if __name__ == "__main__":
    try:
        # Invoke the agent with the sample query
        answer = invoke_agent_streamassist(SAMPLE_QUERY, verbose=True)

        if not answer:
            print("\n[NOTE] No response received. Check if AGENT_ID is correct.")
            print("To list agents, you may need to use the discoveryengine API client.")

    except Exception as e:
        print(f"\nError: {e}")
