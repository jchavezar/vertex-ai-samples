"""
Test InsightComparator Agent via various APIs.

This tests the deployed agent programmatically using:
1. Discovery Engine A2A API (invokes agent registered in Gemini Enterprise)
2. Vertex AI Agent Engine SDK (bypasses GE, calls Agent Engine directly)
3. Discovery Engine API (list agents)

Usage:
    uv run python test_via_api.py                # Test via A2A (recommended)
    uv run python test_via_api.py "custom query" # Custom query
    uv run python test_via_api.py --sdk          # Test via SDK (bypasses GE)
    uv run python test_via_api.py --list         # List Agentspace agents

Version: 1.2.0
Date: 2026-04-04
Last Tested: 2026-04-04 18:24 UTC

A2A Protocol Discovery (2026-04-04):
- Endpoint: .../agents/{agent_id}/a2a/v1/message:stream
- Request format: {"request": {"content": {"text": "query"}}}
- Returns streaming JSON with agent responses
- Requires OAuth authorization for SharePoint (server-side flow)
"""
import os
import sys
import json
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ID = os.environ.get("PROJECT_ID", "sharepoint-wif-agent")
PROJECT_NUMBER = os.environ["PROJECT_NUMBER"]
LOCATION = os.environ.get("LOCATION", "us-central1")
REASONING_ENGINE_RES = os.environ.get("REASONING_ENGINE_RES", "")
ENGINE_ID = os.environ.get("ENGINE_ID", "gemini-enterprise")
AGENT_ID = os.environ.get("AGENT_ID", "7551818683078030090")


def get_access_token():
    """Get GCP access token using gcloud."""
    result = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def print_banner(title: str):
    """Print a formatted banner."""
    width = 70
    print("=" * width)
    print(f" {title}".center(width))
    print("=" * width)


def test_via_a2a(query: str):
    """
    Test the agent via Discovery Engine A2A protocol.
    This invokes the agent registered in Gemini Enterprise directly.

    A2A (Agent-to-Agent) protocol endpoint discovered 2026-04-04:
    - Endpoint: /agents/{agent_id}/a2a/v1/message:stream
    - Request format: {"request": {"content": {"text": "query"}}}
    - Returns streaming JSON with agent responses and diagnostics

    Args:
        query: The test query
    """
    print_banner("A2A TEST - Discovery Engine Agent")

    access_token = get_access_token()

    print(f"Project:  {PROJECT_ID}")
    print(f"Engine:   {ENGINE_ID}")
    print(f"Agent ID: {AGENT_ID}")
    print()

    # A2A endpoint for the registered agent
    url = (
        f"https://discoveryengine.googleapis.com/v1/"
        f"projects/{PROJECT_NUMBER}/locations/global/"
        f"collections/default_collection/engines/{ENGINE_ID}/"
        f"assistants/default_assistant/agents/{AGENT_ID}/"
        f"a2a/v1/message:stream"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER
    }

    # A2A request format (discovered through API exploration)
    payload = {
        "request": {
            "content": {
                "text": query
            }
        }
    }

    print(f"[Query] {query}")
    print("-" * 70)

    try:
        resp = requests.post(url, headers=headers, json=payload)

        if resp.status_code != 200:
            print(f"[ERROR] {resp.status_code}: {resp.text[:500]}")
            return

        # Parse streaming JSON array response
        # Response format: [{...}, {...}, ...]
        full_text = ""
        auth_required = None
        agent_invoked = False
        tool_executed = False

        try:
            # Response is a JSON array with multiple message objects
            raw = resp.text
            # Handle streaming format (array of objects)
            chunks = json.loads(raw)
            if not isinstance(chunks, list):
                chunks = [chunks]

            for chunk in chunks:
                message = chunk.get("message", {})
                metadata = message.get("metadata", {})
                answer = metadata.get("answer", {})

                # Check if our agent was invoked
                for reply in answer.get("replies", []):
                    agent = reply.get("agent", "")
                    if AGENT_ID in agent:
                        agent_invoked = True

                    # Extract text content
                    content = reply.get("groundedContent", {}).get("content", {})
                    text = content.get("text", "")
                    if text and not content.get("thought"):
                        print(text, end="", flush=True)
                        full_text += text

                    # Check for required authorization
                    structured = content.get("structuredData", {}).get("data", {})
                    if "required_authorization" in structured:
                        auth_required = structured["required_authorization"]

                # Check diagnostics for tool calls
                diag = answer.get("diagnosticInfo", {})
                for step in diag.get("plannerSteps", []):
                    if "toolStep" in step:
                        tool_result = step["toolStep"].get("parts", [{}])[0]
                        if "functionResult" in tool_result:
                            tool_executed = True

        except json.JSONDecodeError as e:
            print(f"[WARN] JSON parse error: {e}")
            print(f"Raw response: {resp.text[:500]}")

        print()
        print("-" * 70)

        if agent_invoked:
            print(f"[OK] Agent invoked: InsightComparator ({AGENT_ID})")
            if tool_executed:
                print("[OK] Tool executed: compare_insights")
        else:
            print("[WARN] Agent may not have been invoked")

        if auth_required:
            print()
            print("[AUTH] SharePoint authorization required")
            print(f"       Authorization: {auth_required.get('authorization_name', '').split('/')[-1]}")
            print()
            print("Note: SharePoint access requires user OAuth token.")
            print("      In production, users authorize via Gemini Enterprise UI.")
            print("      The agent IS working - it's requesting the token it needs.")

        if full_text:
            print(f"[OK] Response: {len(full_text)} chars")

    except Exception as e:
        print(f"[ERROR] {e}")


def test_via_sdk(query: str):
    """
    Test the deployed agent via Vertex AI SDK.
    This is the recommended way to test Agent Engine deployments.

    Args:
        query: The test query
    """
    print_banner("SDK TEST - Agent Engine")

    if not REASONING_ENGINE_RES:
        print("[ERROR] REASONING_ENGINE_RES not set in .env")
        print("        Deploy first: uv run python deploy.py")
        return

    import vertexai
    from vertexai import agent_engines

    print(f"Project:  {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Engine:   {REASONING_ENGINE_RES}")
    print()

    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # Load the deployed agent
    print("[1] Loading agent...")
    try:
        remote_agent = agent_engines.get(REASONING_ENGINE_RES)
        print(f"    Name:  {getattr(remote_agent, 'display_name', None) or 'Unnamed'}")
        print(f"    [OK] Agent loaded")
    except Exception as e:
        print(f"[ERROR] Could not load agent: {e}")
        return

    # Create session and query
    print(f"\n[2] Creating session and querying...")
    print(f"    Query: {query}")
    print("-" * 70)

    try:
        session = remote_agent.create_session(user_id="api_test_user")
        session_id = session.get("id") if isinstance(session, dict) else session.id
        print(f"    Session: {session_id}")

        # Stream response
        response_text = ""
        for event in remote_agent.stream_query(
            user_id="api_test_user",
            session_id=session_id,
            message=query
        ):
            if isinstance(event, dict):
                content = event.get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    if isinstance(part, dict) and part.get("text"):
                        print(part["text"], end="", flush=True)
                        response_text += part["text"]
            elif hasattr(event, 'content'):
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            print(part.text, end="", flush=True)
                            response_text += part.text

        print()
        print("-" * 70)
        print(f"[OK] Response: {len(response_text)} chars")

    except Exception as e:
        print(f"\n[ERROR] Query failed: {e}")


def list_agentspace_agents():
    """List agents registered in Agentspace via Discovery Engine API."""
    print_banner("AGENTSPACE AGENTS")

    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Goog-User-Project": PROJECT_NUMBER
    }

    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{PROJECT_NUMBER}/locations/global/"
        f"collections/default_collection/engines/{ENGINE_ID}/"
        f"assistants/default_assistant/agents"
    )

    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        print(f"[ERROR] {resp.status_code}: {resp.text[:200]}")
        return

    agents = resp.json().get("agents", [])
    print(f"Found {len(agents)} agent(s) in Agentspace:\n")

    for agent in agents:
        name = agent.get('displayName', 'Unnamed')
        agent_id = agent['name'].split('/')[-1]
        state = agent.get('state', 'UNKNOWN')
        sharing = agent.get('sharingConfig', {}).get('scope', 'N/A')

        print(f"  {name}")
        print(f"    ID:      {agent_id}")
        print(f"    State:   {state}")
        print(f"    Sharing: {sharing}")

        if "adkAgentDefinition" in agent:
            re = agent["adkAgentDefinition"].get("provisionedReasoningEngine", {})
            engine = re.get('reasoningEngine', 'N/A')
            print(f"    Engine:  {engine.split('/')[-1] if '/' in engine else engine}")

        if "authorizationConfig" in agent:
            auths = agent["authorizationConfig"].get("toolAuthorizations", [])
            for auth in auths:
                auth_id = auth.split('/')[-1]
                print(f"    Auth:    {auth_id}")

        print()


def main():
    """Main entry point."""
    print_banner("InsightComparator API Testing")
    print()
    print("Test the deployed agent via various APIs.")
    print()
    print("Note: SharePoint returns 403 when testing without Microsoft JWT.")
    print("      This is expected - in Gemini Enterprise UI, user tokens are used.")
    print()

    # Parse arguments
    query = "What are cloud security best practices?"
    list_only = False
    use_sdk = False

    for arg in sys.argv[1:]:
        if arg == "--list":
            list_only = True
        elif arg == "--sdk":
            use_sdk = True
        elif arg == "--help":
            print("Usage:")
            print("  uv run python test_via_api.py              # Test agent via A2A (recommended)")
            print("  uv run python test_via_api.py 'query'      # Custom query")
            print("  uv run python test_via_api.py --sdk        # Test via SDK (bypasses GE)")
            print("  uv run python test_via_api.py --list       # List Agentspace agents")
            print()
            print("A2A (Agent-to-Agent) Protocol:")
            print("  The A2A endpoint invokes agents registered in Gemini Enterprise.")
            print("  Endpoint: /agents/{agent_id}/a2a/v1/message:stream")
            print("  Request:  {\"request\": {\"content\": {\"text\": \"query\"}}}")
            return
        elif not arg.startswith("-"):
            query = arg

    if list_only:
        list_agentspace_agents()
    elif use_sdk:
        test_via_sdk(query)
    else:
        test_via_a2a(query)

    print()
    print_banner("COMPLETE")


if __name__ == "__main__":
    main()
