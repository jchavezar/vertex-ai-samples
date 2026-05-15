"""Simple grounding test using REST APIs directly."""
import json
import subprocess

import requests

# Config
DEPLOY_PROJECT_NUMBER = "254356041555"
DEPLOY_LOCATION = "us-central1"
REASONING_ENGINE_ID = "3083690861016383488"

GE_PROJECT_NUMBER = "984359513632"
AS_APP = "acc_1776970890534"
ASSISTANT = "default_assistant"
AGENT_ID = "14273082181461981556"

TEST_QUESTION = "What was the total mentions of metaverse-related keywords in 2020 Q1?"


def _bearer() -> str:
    return subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()


print("=" * 80)
print("GROUNDING DIAGNOSTIC TEST - REST APIs")
print("=" * 80)

# Test 1: Call Agent Engine via streamQueryReasoningEngine
print("\n=== Test 1: Agent Engine streamQueryReasoningEngine ===\n")

headers = {
    "Authorization": f"Bearer {_bearer()}",
    "Content-Type": "application/json",
}

url = (
    f"https://{DEPLOY_LOCATION}-aiplatform.googleapis.com/v1/"
    f"projects/{DEPLOY_PROJECT_NUMBER}/locations/{DEPLOY_LOCATION}/"
    f"reasoningEngines/{REASONING_ENGINE_ID}:streamQuery"
)

payload = {
    "input": {
        "message": TEST_QUESTION,
        "user_id": "test_user_grounding_diag",
    }
}

print(f"URL: {url}")
print(f"Querying: {TEST_QUESTION}\n")

r = requests.post(url, headers=headers, json=payload, stream=True)

if r.status_code != 200:
    print(f"ERROR ({r.status_code}): {r.text}")
else:
    print("Streaming response:\n")
    full_text_parts = []
    found_grounding = False
    event_count = 0

    # Read all response content first
    all_lines = list(r.iter_lines())
    print(f"Total response lines: {len(all_lines)}\n")

    for line in all_lines:
        if not line:
            continue

        # The response is newline-delimited JSON
        try:
            event = json.loads(line)
            event_count += 1

            # Print each event
            print(f"Event {event_count}:")
            print(json.dumps(event, indent=2))
            print()

            # Check for grounding metadata
            if isinstance(event, dict):
                # Look for grounding in various places
                if "grounding_metadata" in event or "groundingMetadata" in event:
                    print("  ✓ FOUND GROUNDING METADATA IN EVENT")
                    print(f"    Value: {json.dumps(event.get('grounding_metadata') or event.get('groundingMetadata'), indent=4)[:500]}")
                    found_grounding = True

                # Check nested structures
                for key in event:
                    if isinstance(event[key], dict):
                        if "grounding_metadata" in event[key] or "groundingMetadata" in event[key]:
                            print(f"  ✓ FOUND GROUNDING METADATA IN event['{key}']")
                            found_grounding = True

                # Collect text
                if "text" in event:
                    full_text_parts.append(event["text"])
                if "content" in event and isinstance(event["content"], dict):
                    if "parts" in event["content"]:
                        for part in event["content"]["parts"]:
                            if isinstance(part, dict) and "text" in part:
                                full_text_parts.append(part["text"])

        except json.JSONDecodeError as e:
            print(f"Could not parse line as JSON: {line[:200]}")
            print(f"Error: {e}\n")

    print(f"\nTotal events: {event_count}")
    print(f"Full response text: {' '.join(full_text_parts)[:500]}...")

    if not found_grounding:
        print("\n✗ NO GROUNDING METADATA found in Agent Engine stream")
    else:
        print("\n✓ Grounding metadata FOUND in Agent Engine")


# Test 2: Call via Gemini Enterprise streamAssist
print("\n\n=== Test 2: Gemini Enterprise streamAssist ===\n")

url = (
    f"https://discoveryengine.googleapis.com/v1alpha/"
    f"projects/{GE_PROJECT_NUMBER}/locations/global/collections/default_collection/"
    f"engines/{AS_APP}/assistants/{ASSISTANT}:streamAssist"
)

payload = {
    "query": {
        "parts": [{"text": TEST_QUESTION}]
    },
    "tools_spec": {
        "agent_ids": [AGENT_ID]
    }
}

print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print()

r = requests.post(url, headers=headers, json=payload, stream=True)

if r.status_code != 200:
    # Try to get error body
    error_text = r.text
    print(f"ERROR ({r.status_code}): {error_text[:1000]}")
else:
    print("Streaming response:\n")
    found_grounding = False
    event_count = 0

    for line in r.iter_lines():
        if not line:
            continue

        try:
            event = json.loads(line)
            event_count += 1

            # Print each event
            print(f"Event {event_count}:")
            print(json.dumps(event, indent=2))
            print()

            # Check for grounding in GE response
            if isinstance(event, dict):
                # GE uses reply.groundedContent.textGroundingMetadata.references[]
                if "reply" in event:
                    reply = event["reply"]
                    if "groundedContent" in reply:
                        grounded = reply["groundedContent"]
                        if "textGroundingMetadata" in grounded:
                            metadata = grounded["textGroundingMetadata"]
                            if "references" in metadata and metadata["references"]:
                                print(f"  ✓ FOUND {len(metadata['references'])} GROUNDING REFERENCES")
                                found_grounding = True
                                # Print first reference
                                if metadata["references"]:
                                    print(f"    First reference: {json.dumps(metadata['references'][0], indent=4)}")

        except json.JSONDecodeError as e:
            print(f"Could not parse line as JSON: {line[:200]}")
            print(f"Error: {e}\n")

    print(f"\nTotal events: {event_count}")

    if not found_grounding:
        print("\n✗ NO GROUNDING REFERENCES found in GE streamAssist")
    else:
        print("\n✓ Grounding references FOUND in GE streamAssist")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
