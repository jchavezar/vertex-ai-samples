"""
Test deployed agent with JWT in session state - simulates Gemini Enterprise.
Passes temp:sharepointauth in session state like Gemini Enterprise would.

Usage:
    # Get JWT from test UI first, then:
    export TEST_JWT="eyJ..."
    uv run python test_with_jwt.py

    # Or pass JWT as argument:
    uv run python test_with_jwt.py "eyJ..."
"""
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ID = os.environ.get("PROJECT_ID", "deloitte-plantas")
LOCATION = os.environ.get("LOCATION", "us-central1")
REASONING_ENGINE_RES = os.environ.get("REASONING_ENGINE_RES")
AUTH_ID = os.environ.get("AUTH_ID", "sharepointauth")


def test_with_jwt(jwt: str, query: str = "what is the salary of a cfo?"):
    """
    Test the deployed agent by passing JWT in session state.
    This simulates how Gemini Enterprise passes the token.
    """
    import vertexai
    from vertexai import agent_engines

    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print("=" * 60)
    print("Simulating Gemini Enterprise Token Passing")
    print("=" * 60)
    print(f"Resource: {REASONING_ENGINE_RES}")
    print(f"AUTH_ID: {AUTH_ID}")
    print(f"JWT length: {len(jwt)}")
    print(f"JWT preview: {jwt[:50]}...")
    print()

    agent = agent_engines.get(REASONING_ENGINE_RES)

    # Create session WITH state containing temp:{AUTH_ID}
    # This is exactly what Gemini Enterprise does
    state_key = f"temp:{AUTH_ID}"
    initial_state = {state_key: jwt}

    print(f"[1] Creating session with state['{state_key}'] = JWT...")

    try:
        session = agent.create_session(
            user_id="test_ge_simulation",
            state=initial_state  # Pass the token in state!
        )
        session_id = session.get("id")
        print(f"    Session ID: {session_id}")
        print(f"    Session state keys: {list(session.get('state', {}).keys())}")
    except Exception as e:
        print(f"    ERROR creating session: {e}")
        return

    # Query
    print(f"\n[2] Querying: {query}")
    print("-" * 40)

    start = time.perf_counter()

    try:
        for event in agent.stream_query(
            user_id="test_ge_simulation",
            session_id=session_id,
            message=query
        ):
            if isinstance(event, dict):
                content = event.get('content', {})
                parts = content.get('parts', [])
                for part in parts:
                    if 'text' in part:
                        print(part['text'], end="", flush=True)
                    elif 'function_call' in part:
                        fc = part['function_call']
                        print(f"\n[Tool Call] {fc.get('name')}: {fc.get('args')}")
                    elif 'function_response' in part:
                        fr = part['function_response']
                        resp = fr.get('response', {})
                        print(f"\n[Tool Response] answer: {resp.get('answer', 'N/A')[:100]}...")
                        print(f"               sources: {resp.get('source_count', 0)}")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    elapsed = time.perf_counter() - start
    print(f"\n\n{'=' * 40}")
    print(f"Latency: {elapsed*1000:.0f}ms ({elapsed:.2f}s)")
    print()
    print("[3] Check Cloud Logging for debug output:")
    print(f"    https://console.cloud.google.com/logs/query?project={PROJECT_ID}")
    print()
    print("    Expected log lines:")
    print(f"    - state keys: ['temp:{AUTH_ID}']")
    print(f"    - [TOKEN] Found via 'temp:{AUTH_ID}' (length: {len(jwt)})")
    print("    - [WIF] STS response status: 200")
    print("    - [WIF] SUCCESS - token length: ...")


if __name__ == "__main__":
    # Get JWT from arg or env
    if len(sys.argv) > 1:
        jwt = sys.argv[1]
    else:
        jwt = os.environ.get("TEST_JWT", "")

    if not jwt:
        print("ERROR: No JWT provided")
        print()
        print("Get a JWT from the test UI first:")
        print("  cd test_ui && uv run python server.py")
        print("  # Open http://localhost:5177, login, copy JWT")
        print()
        print("Then run:")
        print('  export TEST_JWT="eyJ..."')
        print("  uv run python test_with_jwt.py")
        print()
        print("Or pass directly:")
        print('  uv run python test_with_jwt.py "eyJ..."')
        sys.exit(1)

    query = sys.argv[2] if len(sys.argv) > 2 else "what is the salary of a cfo?"
    test_with_jwt(jwt, query)
