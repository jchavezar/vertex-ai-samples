"""Test script to diagnose missing grounding citations.

Calls the docparse agent via:
1. Agent Engine SDK directly (query method)
2. Gemini Enterprise streamAssist (the UI path)

Compares the raw responses to find where grounding metadata is dropped.
"""
import json
import os
import subprocess
from pathlib import Path

import requests
import vertexai
from vertexai.preview import reasoning_engines

# Hardcoded config based on user's message
DEPLOY_PROJECT_ID = "vtxdemos"
DEPLOY_PROJECT_NUMBER = "254356041555"
DEPLOY_LOCATION = "us-central1"
REASONING_ENGINE_RES = "projects/254356041555/locations/us-central1/reasoningEngines/3083690861016383488"

GE_PROJECT_ID = "sharepoint-wif"
GE_PROJECT_NUMBER = "984359513632"
AS_APP = "acc_1776970890534"
ASSISTANT = "default_assistant"
AGENT_ID = "14273082181461981556"

TEST_QUESTION = "What was the total mentions of metaverse-related keywords in 2020 Q1?"


def _bearer() -> str:
    return subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()


def test_agent_engine():
    """Call the agent via Agent Engine SDK (preview.reasoning_engines) and dump response."""
    print("\n=== Test 1: Agent Engine SDK (preview) ===\n")

    vertexai.init(project=DEPLOY_PROJECT_ID, location=DEPLOY_LOCATION)

    # Use preview reasoning_engines (same as the eval script)
    agent = reasoning_engines.ReasoningEngine(REASONING_ENGINE_RES)

    print(f"Querying: {TEST_QUESTION}\n")

    response = agent.query(input=TEST_QUESTION)

    print("Response type:", type(response))
    print("\n--- Raw response ---")
    print(json.dumps(response, indent=2, default=str))

    # Check for grounding in various possible locations
    has_grounding = False
    if isinstance(response, dict):
        if "grounding_metadata" in response:
            print("\n✓ Found grounding_metadata at top level")
            has_grounding = True
        if "output" in response and isinstance(response["output"], dict):
            if "grounding_metadata" in response["output"]:
                print("\n✓ Found grounding_metadata in output")
                has_grounding = True
        # Also check in candidates
        if "candidates" in response:
            for i, cand in enumerate(response["candidates"]):
                if isinstance(cand, dict) and "grounding_metadata" in cand:
                    print(f"\n✓ Found grounding_metadata in candidates[{i}]")
                    has_grounding = True
        # Check in chunks (as used in the eval script)
        if "chunks" in response:
            print(f"\n  Found {len(response['chunks'])} chunks")
            for i, chunk in enumerate(response["chunks"]):
                if isinstance(chunk, dict):
                    print(f"    Chunk {i} keys: {list(chunk.keys())}")

    if not has_grounding:
        print("\n✗ NO grounding_metadata found in Agent Engine response")

    return response


def test_streamassist():
    """Call the agent via Gemini Enterprise streamAssist and dump response."""
    print("\n\n=== Test 2: Gemini Enterprise streamAssist ===\n")

    headers = {
        "Authorization": f"Bearer {_bearer()}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }

    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{GE_PROJECT_NUMBER}/locations/global/collections/"
        f"default_collection/engines/{AS_APP}/assistants/{ASSISTANT}:"
        f"streamAssist"
    )

    # Build the request payload (based on MEMORY.md streamAssist request shape)
    # The memory note says "toolsSpec" not "tools", and "agentIds" - but let's try the actual API
    payload = {
        "query": {
            "parts": [{"text": TEST_QUESTION}]
        },
        "tools_spec": {
            "agent_ids": [AGENT_ID]
        }
    }

    print(f"Querying: {TEST_QUESTION}\n")
    print("Request payload:")
    print(json.dumps(payload, indent=2))
    print()

    r = requests.post(url, headers=headers, data=json.dumps(payload), stream=True)

    if r.status_code != 200:
        print(f"ERROR ({r.status_code}): {r.text}")
        return None

    print("--- Streaming response chunks ---\n")

    full_response = []
    has_grounding = False

    for line in r.iter_lines():
        if not line:
            continue

        # streamAssist returns SSE-like chunks
        line_text = line.decode('utf-8')

        # Skip empty lines and event markers
        if not line_text.strip() or line_text.startswith('data: [DONE]'):
            continue

        # Parse JSON chunk
        if line_text.startswith('data: '):
            line_text = line_text[6:]  # Remove 'data: ' prefix

        try:
            chunk = json.loads(line_text)
            full_response.append(chunk)

            # Print chunk for inspection
            print("Chunk:")
            print(json.dumps(chunk, indent=2))
            print()

            # Check for grounding in this chunk
            if "reply" in chunk:
                reply = chunk["reply"]
                if "groundedContent" in reply:
                    grounded = reply["groundedContent"]
                    if "textGroundingMetadata" in grounded:
                        metadata = grounded["textGroundingMetadata"]
                        if "references" in metadata and metadata["references"]:
                            print("✓ Found textGroundingMetadata.references in this chunk")
                            has_grounding = True

        except json.JSONDecodeError as e:
            print(f"Failed to parse chunk: {line_text[:200]}")
            print(f"Error: {e}\n")

    print("\n--- Full response summary ---")
    print(f"Total chunks: {len(full_response)}")

    if not has_grounding:
        print("\n✗ NO textGroundingMetadata.references found in streamAssist response")

    return full_response


if __name__ == "__main__":
    print("=" * 80)
    print("GROUNDING DIAGNOSTIC TEST")
    print("=" * 80)

    agent_response = test_agent_engine()
    ge_response = test_streamassist()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nCheck the output above to see where grounding metadata is dropped.")
    print("Expected: Agent Engine should emit grounding_metadata,")
    print("          and GE should forward it as textGroundingMetadata.references")
