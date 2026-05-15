"""Test grounding metadata flow from Agent Engine to GE."""
import json
import subprocess
import requests

# Firestore Agent
DEPLOY_PROJECT_NUMBER = "984359513632"
DEPLOY_LOCATION = "us-central1"
REASONING_ENGINE_ID = "5229440579179380736"

GE_PROJECT_NUMBER = "984359513632"
AS_APP = "acc_1776970890534"
ASSISTANT = "default_assistant"
AGENT_ID = "3941214075442781492"

TEST_QUESTION = "what is the metaverse?"


def _bearer() -> str:
    return subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()


print("="*80)
print("GROUNDING DIAGNOSTIC - Firestore Agent")
print("="*80)

# Test 1: Agent Engine streamQuery
print("\n=== Test 1: Agent Engine streamQuery ===\n")

headers = {
    "Authorization": f"Bearer {_bearer()}",
    "Content-Type": "application/json",
}

url = f"https://{DEPLOY_LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{DEPLOY_PROJECT_NUMBER}/locations/{DEPLOY_LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}:streamQuery"

payload = {"input": {"query": TEST_QUESTION}}

print(f"URL: {url}")
print(f"Query: {TEST_QUESTION}\n")

r = requests.post(url, headers=headers, json=payload, stream=True, timeout=90)

if r.status_code != 200:
    print(f"ERROR ({r.status_code}): {r.text[:500]}")
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

            print(f"Event {event_count}:")
            print(f"  Type: {type(event)}")

            if isinstance(event, dict):
                print(f"  Keys: {list(event.keys())}")

                # Check for grounding_metadata
                if "grounding_metadata" in event:
                    print(f"  ✓ HAS grounding_metadata")
                    gm = event["grounding_metadata"]
                    print(f"    Structure: {json.dumps(gm, indent=4)[:500]}")
                    found_grounding = True
                else:
                    print(f"  ✗ No grounding_metadata")
            elif isinstance(event, str):
                print(f"  String response: {event[:200]}...")
                if "grounding" in event.lower():
                    print(f"  Contains 'grounding' in text")

            if event_count >= 3:
                break

        except json.JSONDecodeError as e:
            print(f"Parse error: {e}")

    print(f"\nTotal events: {event_count}")

    if not found_grounding:
        print("\n✗ NO grounding_metadata in Agent Engine response")
    else:
        print("\n✓ Agent Engine IS returning grounding_metadata")

print("\n" + "="*80)
print("COMPLETE")
print("="*80)
