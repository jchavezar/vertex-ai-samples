"""Test agent using SDK stream_query to see if grounding appears."""
import json
import os

import vertexai
from vertexai import agent_engines

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

PROJECT = "vtxdemos"
LOCATION = "us-central1"
ENGINE_RES = "projects/254356041555/locations/us-central1/reasoningEngines/3083690861016383488"
TEST_QUESTION = "What was the total mentions of metaverse-related keywords in 2020 Q1?"

print("=" * 80)
print("Testing agent with SDK stream_query")
print("=" * 80)

vertexai.init(project=PROJECT, location=LOCATION)

agent = agent_engines.get(ENGINE_RES)

print(f"\nQuestion: {TEST_QUESTION}\n")
print("Streaming events:\n")

event_count = 0
found_grounding = False

try:
    # Create session first
    session = agent.create_session(user_id="test_user_grounding", session_id="test_session_grounding_v2")
    print(f"Created session: {session}\n")

    for event in agent.stream_query(
        user_id="test_user_grounding",
        session_id="test_session_grounding_v2",
        message=TEST_QUESTION
    ):
        event_count += 1
        print(f"Event {event_count}:")

        # Convert to dict for inspection
        if hasattr(event, 'model_dump'):
            event_dict = event.model_dump()
        elif hasattr(event, '__dict__'):
            event_dict = event.__dict__
        else:
            event_dict = event

        print(json.dumps(event_dict, indent=2, default=str))
        print()

        # Check for grounding
        if isinstance(event_dict, dict):
            if "grounding_metadata" in event_dict or "groundingMetadata" in event_dict:
                gm = event_dict.get("grounding_metadata") or event_dict.get("groundingMetadata")
                if gm:
                    print("  ✓ FOUND GROUNDING METADATA!")
                    print(f"    {json.dumps(gm, indent=4, default=str)[:1000]}")
                    found_grounding = True

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\nTotal events: {event_count}")
if found_grounding:
    print("✓ Grounding metadata WAS found")
else:
    print("✗ Grounding metadata NOT found")

print("=" * 80)
