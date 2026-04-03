"""
Test deployed agent with simulated Gemini Enterprise payload.
Passes temp:sharepointauth token like Gemini Enterprise would.
"""
import os
import requests
import json
from dotenv import load_dotenv
import subprocess

load_dotenv()

PROJECT_ID = os.environ.get("PROJECT_ID", "deloitte-plantas")
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER", "REDACTED_PROJECT_NUMBER")
LOCATION = os.environ.get("LOCATION", "us-central1")
REASONING_ENGINE_ID = os.environ.get("REASONING_ENGINE_ID", "5479245222963576832")
AUTH_ID = os.environ.get("AUTH_ID", "sharepointauth")

# Use a test JWT - you can replace this with a real one from the test UI
TEST_JWT = os.environ.get("TEST_JWT", "")


def get_access_token():
    """Get GCP access token using gcloud."""
    result = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def test_with_temp_state():
    """
    Test the deployed agent by simulating Gemini Enterprise's token passing.
    Uses the raw API to pass temp:{AUTH_ID} in session state.
    """
    access_token = get_access_token()
    base_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1"
    resource = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    print("=" * 60)
    print("Simulating Gemini Enterprise Token Passing")
    print("=" * 60)
    print(f"Resource: {resource}")
    print(f"AUTH_ID: {AUTH_ID}")
    print(f"Test JWT: {'<set>' if TEST_JWT else '<not set>'}")
    print()

    # Step 1: Create session with temp:{AUTH_ID} in state
    print("[1] Creating session with temp:{AUTH_ID} state...")

    # Build state with temp: prefix like Gemini Enterprise
    initial_state = {}
    if TEST_JWT:
        state_key = f"temp:{AUTH_ID}"
        initial_state[state_key] = TEST_JWT
        print(f"    Setting state['{state_key}'] = JWT (length: {len(TEST_JWT)})")
    else:
        print("    WARNING: No TEST_JWT set - agent will use service account fallback")
        print("    Set TEST_JWT env var with a valid Microsoft ID token to test WIF")

    session_payload = {
        "input": {
            "user_id": "test_user",
        }
    }

    # Note: The session state might need to be passed differently
    # depending on how ADK handles it
    if initial_state:
        session_payload["input"]["state"] = initial_state

    resp = requests.post(
        f"{base_url}/{resource}:createSession",
        headers=headers,
        json=session_payload
    )

    print(f"    Response status: {resp.status_code}")
    session_data = resp.json()
    print(f"    Response: {json.dumps(session_data, indent=2)[:500]}")

    session_id = session_data.get("id")
    if not session_id:
        print("ERROR: No session ID returned")
        return

    # Step 2: Query with the session
    print(f"\n[2] Querying agent (session_id={session_id})...")

    query = "what is the salary of a cfo?"

    # Try streamQuery with state passed in the message
    query_payload = {
        "input": {
            "message": query,
            "user_id": "test_user",
            "session_id": session_id,
        }
    }

    # Also try passing state in the query (some implementations accept this)
    if initial_state:
        query_payload["input"]["state"] = initial_state

    print(f"    Query: {query}")
    print(f"    Payload: {json.dumps(query_payload, indent=2)}")

    resp = requests.post(
        f"{base_url}/{resource}:streamQuery",
        headers=headers,
        json=query_payload,
        stream=True
    )

    print(f"    Response status: {resp.status_code}")
    print("\n[3] Streaming response:")
    print("-" * 40)

    full_response = ""
    for line in resp.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            full_response += decoded + "\n"
            # Try to parse JSON events
            try:
                if decoded.startswith("{"):
                    event = json.loads(decoded)
                    # Extract text from ADK events
                    if "content" in event:
                        content = event.get("content", {})
                        parts = content.get("parts", [])
                        for part in parts:
                            if "text" in part:
                                print(part["text"], end="", flush=True)
                    elif "text" in event:
                        print(event["text"], end="", flush=True)
                else:
                    print(decoded)
            except json.JSONDecodeError:
                print(decoded)

    print("\n" + "-" * 40)
    print("\n[4] Check Cloud Logging for context debug output:")
    print(f"    https://console.cloud.google.com/logs/query?project={PROJECT_ID}")
    print()
    print("    Look for these log lines:")
    print("    - '[CONTEXT DEBUG] Tool Context Details:'")
    print(f"    - 'state keys: ['temp:{AUTH_ID}']'")
    print(f"    - '[TOKEN] Found via temp:{AUTH_ID}'")


def test_via_sdk():
    """Test using the Python SDK with state injection."""
    import vertexai
    from vertexai import agent_engines

    vertexai.init(project=PROJECT_ID, location=LOCATION)

    resource = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}"
    print(f"Getting agent: {resource}")

    deployed_agent = agent_engines.get(resource)

    # Check what methods are available
    print("\nAvailable methods:")
    for method in dir(deployed_agent):
        if not method.startswith('_'):
            print(f"  - {method}")

    # Try to create session with state
    print("\n[SDK] Creating session...")
    try:
        # Some SDK versions support initial_state parameter
        session = deployed_agent.create_session(
            user_id="test_user",
            # Try passing state (may or may not be supported)
        )
        print(f"Session: {session}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "sdk":
        test_via_sdk()
    else:
        test_with_temp_state()
