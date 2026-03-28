"""
Comprehensive tests for the Dynamic Workflow Router.
Tests routing, stickiness, topic switches, and edge cases.
"""
import os
import sys
import asyncio
import time
from typing import List, Tuple
from dataclasses import dataclass

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.classifier import (
    IntentClassifier,
    Intent,
    is_hard_topic_switch,
    is_exit_signal
)
from workflows.router import RouterWorkflow, RouterConfig


@dataclass
class TestCase:
    """Test case definition."""
    name: str
    messages: List[str]
    expected_routes: List[str]
    description: str


@dataclass
class TestResult:
    """Test result."""
    name: str
    passed: bool
    actual_routes: List[str]
    expected_routes: List[str]
    latencies_ms: List[float]
    error: str = ""


# Test scenarios
TEST_CASES = [
    # === Initial Routing Tests ===
    TestCase(
        name="discovery_initial_documents",
        messages=["Find documents about quarterly earnings"],
        expected_routes=["DISCOVERY"],
        description="Initial query about documents should route to DISCOVERY"
    ),
    TestCase(
        name="discovery_initial_financial",
        messages=["What were our Q3 revenues?"],
        expected_routes=["DISCOVERY"],
        description="Financial query should route to DISCOVERY"
    ),
    TestCase(
        name="discovery_initial_search",
        messages=["Search for the merger proposal"],
        expected_routes=["DISCOVERY"],
        description="Search request should route to DISCOVERY"
    ),
    TestCase(
        name="servicenow_initial_ticket",
        messages=["Create a ticket for the login issue"],
        expected_routes=["SERVICENOW"],
        description="Ticket creation should route to SERVICENOW"
    ),
    TestCase(
        name="servicenow_initial_incident",
        messages=["I need to report an incident with the VPN"],
        expected_routes=["SERVICENOW"],
        description="Incident report should route to SERVICENOW"
    ),
    TestCase(
        name="servicenow_initial_problem",
        messages=["The server is down and needs to be fixed"],
        expected_routes=["SERVICENOW"],
        description="Problem report should route to SERVICENOW"
    ),

    # === Stickiness Tests ===
    TestCase(
        name="stickiness_discovery_followup",
        messages=[
            "Find the budget report",
            "What about last year's version?",
            "Compare them please"
        ],
        expected_routes=["DISCOVERY", "DISCOVERY", "DISCOVERY"],
        description="Follow-up queries should stick to DISCOVERY"
    ),
    TestCase(
        name="stickiness_servicenow_followup",
        messages=[
            "Create a ticket for broken keyboard",
            "Add that it's urgent",
            "Also mention building A room 101"
        ],
        expected_routes=["SERVICENOW", "SERVICENOW", "SERVICENOW"],
        description="Follow-up details should stick to SERVICENOW"
    ),
    TestCase(
        name="stickiness_affirmative_responses",
        messages=[
            "Find the HR policy document",
            "Yes",
            "Sounds good",
            "Perfect, thanks"
        ],
        expected_routes=["DISCOVERY", "DISCOVERY", "DISCOVERY", "DISCOVERY"],
        description="Affirmative responses should stick to current route"
    ),

    # === Topic Switch Tests ===
    TestCase(
        name="switch_discovery_to_servicenow",
        messages=[
            "Search for the IT policy",
            "Actually, I need to create a ticket for my laptop"
        ],
        expected_routes=["DISCOVERY", "SERVICENOW"],
        description="Explicit switch from DISCOVERY to SERVICENOW"
    ),
    TestCase(
        name="switch_servicenow_to_discovery",
        messages=[
            "Create an incident for the outage",
            "Actually, instead search for the outage history"
        ],
        expected_routes=["SERVICENOW", "DISCOVERY"],
        description="Explicit switch from SERVICENOW to DISCOVERY"
    ),

    # === Exit Signal Tests ===
    TestCase(
        name="exit_cancel",
        messages=[
            "Create a ticket",
            "cancel"
        ],
        expected_routes=["SERVICENOW", None],
        description="Cancel should reset route"
    ),
    TestCase(
        name="exit_start_over",
        messages=[
            "Find quarterly reports",
            "start over"
        ],
        expected_routes=["DISCOVERY", None],
        description="Start over should reset route"
    ),

    # === Edge Cases ===
    TestCase(
        name="ambiguous_initial",
        messages=["Help me with something"],
        expected_routes=["DISCOVERY"],  # Default fallback
        description="Ambiguous query should default to DISCOVERY"
    ),
    TestCase(
        name="mixed_keywords",
        messages=["Search for ticket templates"],
        expected_routes=["DISCOVERY"],  # Search takes precedence
        description="Search verb should route to DISCOVERY even with 'ticket' keyword"
    ),
]


class RouterTester:
    """Test harness for the RouterWorkflow."""

    def __init__(self):
        self.config = RouterConfig(
            classifier_model="gemini-2.5-flash",
            servicenow_model="gemini-2.5-flash",
            reclassify_threshold=0.7,
            max_sticky_turns=10,
        )
        self.workflow = RouterWorkflow(config=self.config)

    async def run_conversation(
        self,
        messages: List[str]
    ) -> Tuple[List[str], List[float]]:
        """
        Run a conversation and return routes and latencies.

        Returns:
            Tuple of (routes, latencies_ms)
        """
        session_state = {}
        routes = []
        latencies = []

        for msg in messages:
            start = time.time()

            # Collect response (we don't need it, just want the routing)
            response_chunks = []
            async for chunk in self.workflow.route(msg, session_state):
                response_chunks.append(chunk)

            latency_ms = (time.time() - start) * 1000
            latencies.append(latency_ms)

            # Get the route that was used
            current_route = session_state.get("current_route")
            routes.append(current_route)

        return routes, latencies

    async def run_test(self, test_case: TestCase) -> TestResult:
        """Run a single test case."""
        try:
            actual_routes, latencies = await self.run_conversation(test_case.messages)

            # Check if routes match expected
            passed = actual_routes == test_case.expected_routes

            return TestResult(
                name=test_case.name,
                passed=passed,
                actual_routes=actual_routes,
                expected_routes=test_case.expected_routes,
                latencies_ms=latencies
            )
        except Exception as e:
            return TestResult(
                name=test_case.name,
                passed=False,
                actual_routes=[],
                expected_routes=test_case.expected_routes,
                latencies_ms=[],
                error=str(e)
            )

    async def run_all_tests(self) -> List[TestResult]:
        """Run all test cases."""
        results = []
        for test_case in TEST_CASES:
            print(f"Running: {test_case.name}...")
            result = await self.run_test(test_case)
            results.append(result)
            status = "PASS" if result.passed else "FAIL"
            print(f"  {status}: {test_case.description}")
            if not result.passed:
                print(f"    Expected: {result.expected_routes}")
                print(f"    Actual:   {result.actual_routes}")
                if result.error:
                    print(f"    Error:    {result.error}")
        return results


def test_heuristics():
    """Test the fast heuristic functions."""
    print("\n=== Testing Heuristics ===\n")

    # Exit signals
    assert is_exit_signal("cancel") == True
    assert is_exit_signal("Cancel this") == True
    assert is_exit_signal("start over") == True
    assert is_exit_signal("nevermind") == True
    assert is_exit_signal("Create a ticket") == False
    assert is_exit_signal("Search for documents") == False
    print("Exit signal tests: PASS")

    # Topic switches
    assert is_hard_topic_switch("Actually, search for documents", "SERVICENOW") == True
    assert is_hard_topic_switch("Instead, find the report", "SERVICENOW") == True
    assert is_hard_topic_switch("Actually, create a ticket", "DISCOVERY") == True
    assert is_hard_topic_switch("Yes please", "SERVICENOW") == False
    assert is_hard_topic_switch("Add more details", "SERVICENOW") == False
    print("Topic switch tests: PASS")


async def run_latency_benchmark():
    """Benchmark routing latency."""
    print("\n=== Latency Benchmark ===\n")

    tester = RouterTester()

    # Warm up
    await tester.run_conversation(["test query"])

    # Benchmark initial classification
    latencies = []
    for _ in range(5):
        _, lats = await tester.run_conversation(["What are the quarterly earnings?"])
        latencies.extend(lats)

    avg_initial = sum(latencies) / len(latencies)
    print(f"Initial classification avg: {avg_initial:.0f}ms")

    # Benchmark sticky follow-up (should be 0ms for classification)
    session_state = {"current_route": "DISCOVERY", "turn_count": 1, "last_intent_confidence": 0.9}
    latencies = []
    for _ in range(5):
        start = time.time()
        async for _ in tester.workflow.route("More details please", session_state):
            pass
        latencies.append((time.time() - start) * 1000)

    avg_sticky = sum(latencies) / len(latencies)
    print(f"Sticky follow-up avg: {avg_sticky:.0f}ms")
    print(f"Stickiness speedup: {avg_initial/avg_sticky:.1f}x")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Light MCP Cloud Portal - Router Test Suite")
    print("=" * 60)

    # Test heuristics first (fast, no API calls)
    test_heuristics()

    # Run full router tests
    print("\n=== Router Integration Tests ===\n")
    tester = RouterTester()
    results = await tester.run_all_tests()

    # Summary
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"\n{'=' * 60}")
    print(f"Results: {passed}/{total} tests passed")

    # Latency summary
    all_latencies = [lat for r in results for lat in r.latencies_ms if r.latencies_ms]
    if all_latencies:
        print(f"Avg latency: {sum(all_latencies)/len(all_latencies):.0f}ms")
        print(f"Max latency: {max(all_latencies):.0f}ms")
        print(f"Min latency: {min(all_latencies):.0f}ms")

    # Run latency benchmark
    await run_latency_benchmark()

    print("=" * 60)

    # Return exit code
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
