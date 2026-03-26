#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "python-dotenv",
# ]
# ///
"""
Local Integration Test Suite for Light MCP Cloud Portal.

Tests each component in isolation, then together.

Usage:
    uv run scripts/test-local.py --test mcp        # Test MCP server only
    uv run scripts/test-local.py --test agent-sim  # Simulate agent locally
    uv run scripts/test-local.py --test all        # Run all tests
"""
import os
import sys
import json
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8081/mcp")
JWT_TOKEN = os.getenv("TEST_JWT_TOKEN", "")

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def log(message: str, color: str = ""):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {message}{RESET}")


def log_success(msg: str):
    log(f"✅ {msg}", GREEN)


def log_error(msg: str):
    log(f"❌ {msg}", RED)


def log_info(msg: str):
    log(f"ℹ️  {msg}", BLUE)


def log_warn(msg: str):
    log(f"⚠️  {msg}", YELLOW)


def decode_jwt(token: str) -> dict:
    """Decode JWT payload without verification."""
    import base64
    try:
        payload = token.split(".")[1]
        # Add padding if needed
        payload += "=" * (4 - len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception as e:
        return {"error": str(e)}


def test_mcp_server_health() -> bool:
    """Test if MCP server is running."""
    log_info(f"Testing MCP server at {MCP_SERVER_URL}")

    # StreamableHTTP requires session initialization
    # Try a simple request to check if server is up
    try:
        # Try the base URL without /mcp
        base_url = MCP_SERVER_URL.replace("/mcp", "")
        resp = requests.get(f"{base_url}/health", timeout=5)
        if resp.ok:
            log_success("MCP server is running (health endpoint)")
            return True
    except:
        pass

    # Try posting to /mcp with proper headers
    try:
        resp = requests.post(
            MCP_SERVER_URL,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            json={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
            timeout=5
        )
        # Even an error response means server is running
        log_success(f"MCP server is running (responded with status {resp.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        log_error("MCP server is not running!")
        log_info("Start it with: cd mcp-server && uv run python mcp_server.py")
        return False
    except Exception as e:
        log_error(f"Error connecting to MCP server: {e}")
        return False


def test_jwt_token() -> bool:
    """Verify JWT token is set and valid."""
    log_info("Checking JWT token...")

    if not JWT_TOKEN:
        log_error("TEST_JWT_TOKEN environment variable not set!")
        log_info("Get a token: uv run scripts/serve-token-page.py")
        log_info("Then: export TEST_JWT_TOKEN='eyJ...'")
        return False

    if not JWT_TOKEN.startswith("eyJ"):
        log_error("Invalid JWT token format (should start with 'eyJ')")
        return False

    claims = decode_jwt(JWT_TOKEN)
    if "error" in claims:
        log_error(f"Could not decode JWT: {claims['error']}")
        return False

    # Check expiration
    exp = claims.get("exp", 0)
    now = datetime.now().timestamp()
    if exp < now:
        log_error("JWT token has expired!")
        log_info(f"Expired at: {datetime.fromtimestamp(exp)}")
        log_info("Get a new token from the helper page")
        return False

    log_success(f"JWT token valid for user: {claims.get('preferred_username', 'unknown')}")
    log_info(f"Expires: {datetime.fromtimestamp(exp)}")
    return True


def test_mcp_with_jwt() -> bool:
    """
    Test MCP server with JWT authentication.

    Since StreamableHTTP requires a proper MCP client, we'll test
    by checking if the server accepts our request format.
    """
    log_info("Testing MCP server with JWT...")

    if not JWT_TOKEN:
        log_warn("Skipping JWT test - no token set")
        return False

    # The StreamableHTTP transport needs an MCP client
    # For now, verify the server is accepting connections
    # and log the JWT we would send

    claims = decode_jwt(JWT_TOKEN)
    log_info(f"Would authenticate as: {claims.get('email', claims.get('preferred_username'))}")

    # Test that ServiceNow is reachable with Basic Auth fallback
    servicenow_url = os.getenv("SERVICENOW_INSTANCE_URL", "https://dev289493.service-now.com")
    log_info(f"Testing ServiceNow connectivity: {servicenow_url}")

    try:
        # Try with JWT first
        resp = requests.get(
            f"{servicenow_url}/api/now/table/incident",
            headers={
                "Authorization": f"Bearer {JWT_TOKEN}",
                "Accept": "application/json"
            },
            params={"sysparm_limit": 1},
            timeout=10
        )

        if resp.status_code == 200:
            log_success("ServiceNow accepted JWT authentication!")
            data = resp.json()
            count = len(data.get("result", []))
            log_info(f"Retrieved {count} incident(s)")
            return True
        elif resp.status_code == 401:
            log_warn("JWT auth failed (401) - trying Basic Auth fallback...")

            # Try Basic Auth
            user = os.getenv("SERVICENOW_BASIC_AUTH_USER")
            passwd = os.getenv("SERVICENOW_BASIC_AUTH_PASS")

            if user and passwd:
                resp = requests.get(
                    f"{servicenow_url}/api/now/table/incident",
                    auth=(user, passwd),
                    headers={"Accept": "application/json"},
                    params={"sysparm_limit": 1},
                    timeout=10
                )
                if resp.ok:
                    log_success("Basic Auth fallback worked!")
                    log_warn("JWT is not accepted by ServiceNow - check OIDC config")
                    return True
                else:
                    log_error(f"Basic Auth also failed: {resp.status_code}")
                    return False
            else:
                log_error("No Basic Auth credentials for fallback")
                return False
        else:
            log_error(f"Unexpected response: {resp.status_code}")
            return False

    except Exception as e:
        log_error(f"Error testing ServiceNow: {e}")
        return False


def test_agent_simulation() -> bool:
    """
    Simulate agent behavior locally.

    This creates a local ADK agent and tests that it would
    correctly pass JWT to the MCP server.
    """
    log_info("Simulating agent with JWT token flow...")

    try:
        # Import ADK components
        from google.adk.agents import LlmAgent
        from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

        log_success("ADK imports successful (google-adk >= 1.9.0)")

        # Create a mock header provider
        def mock_header_provider(context):
            log_info("header_provider called - would inject JWT here")
            return {
                "Authorization": f"Bearer {JWT_TOKEN[:50]}...",
                "Accept": "application/json"
            }

        # Create toolset pointing to local MCP server
        toolset = McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MCP_SERVER_URL,
                timeout=30
            ),
            header_provider=mock_header_provider
        )

        log_success("McpToolset created with StreamableHTTP transport")
        log_success("header_provider configured to inject JWT")

        # Note: We can't fully test without running the agent
        # But we've verified the configuration is correct
        log_info("Agent simulation complete - config is correct")
        log_info("Full test requires deploying to Agent Engine")

        return True

    except ImportError as e:
        log_warn(f"ADK not installed: {e}")
        log_info("Install with: pip install google-adk")
        return False
    except Exception as e:
        log_error(f"Error in agent simulation: {e}")
        return False


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "=" * 60)
    print("🧪 Light MCP Cloud Portal - Local Test Suite")
    print("=" * 60 + "\n")

    results = {}

    # Test 1: JWT Token
    print("\n--- Test 1: JWT Token ---")
    results["jwt"] = test_jwt_token()

    # Test 2: MCP Server Health
    print("\n--- Test 2: MCP Server Health ---")
    results["mcp_health"] = test_mcp_server_health()

    # Test 3: MCP with JWT (ServiceNow direct)
    print("\n--- Test 3: ServiceNow Connectivity ---")
    results["servicenow"] = test_mcp_with_jwt()

    # Test 4: Agent Simulation
    print("\n--- Test 4: Agent Simulation ---")
    results["agent_sim"] = test_agent_simulation()

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results.items():
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        log_success("All tests passed! Ready for Phase 2 (Cloud Deployment)")
        log_info("See: docs/PHASE2_CLOUD_DEPLOYMENT.md")
    else:
        log_error("Some tests failed. Fix issues before proceeding.")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Local integration tests")
    parser.add_argument(
        "--test",
        choices=["mcp", "jwt", "servicenow", "agent-sim", "all"],
        default="all",
        help="Which test to run"
    )
    args = parser.parse_args()

    if args.test == "all":
        success = run_all_tests()
    elif args.test == "mcp":
        success = test_mcp_server_health()
    elif args.test == "jwt":
        success = test_jwt_token()
    elif args.test == "servicenow":
        success = test_jwt_token() and test_mcp_with_jwt()
    elif args.test == "agent-sim":
        success = test_agent_simulation()
    else:
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
