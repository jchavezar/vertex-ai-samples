#!/usr/bin/env python3
"""
ADK + LLM + Schema Test
========================
Tests the 41 sample queries using Google ADK with LLM interpreting natural language
and the schema injected into instructions.

This tests the FULL pipeline:
  User Query -> LLM (with schema) -> Tool Selection -> MCP Call -> Response
"""

import os
import sys
import json
import asyncio
import time
import logging
import httpx
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("adk_schema_test")

# Constants
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "refresh_token.json")
MCP_ENDPOINT = "https://mcp.factset.com/content/v1/messages"
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "mcp_tools_schema.json")


def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            return data.get("default_chat", {}).get("token")
    return None


def load_schema():
    if os.path.exists(SCHEMA_FILE):
        with open(SCHEMA_FILE, 'r') as f:
            return json.load(f)
    return []


def parse_sse_response(text: str) -> dict:
    for line in text.split("\n"):
        if line.startswith("data:"):
            return json.loads(line[5:].strip())
    return {}


class MCPToolExecutor:
    """Executes MCP tool calls."""

    def __init__(self, token: str):
        self.token = token
        self._req_id = 0

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        self._req_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._req_id,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments}
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(MCP_ENDPOINT, headers=headers, json=request)
                if response.status_code == 200:
                    result = parse_sse_response(response.text)
                    content = result.get("result", {}).get("content", [])
                    is_error = result.get("result", {}).get("isError", False)

                    if is_error:
                        return {"error": content[0].get("text", "Unknown error") if content else "Unknown error"}

                    return {"data": content[0].get("text", "") if content else "No data"}
                else:
                    return {"error": f"HTTP {response.status_code}"}
            except Exception as e:
                return {"error": str(e)}


async def run_llm_with_schema(query: str, schema: list, mcp_executor: MCPToolExecutor) -> dict:
    """
    Use Gemini to interpret the query and decide which tool to call.
    Returns the tool call decision and result.
    """
    from google import genai
    from google.genai import types

    # Build the prompt with schema
    schema_str = json.dumps(schema, indent=2)

    system_prompt = f"""You are a financial data assistant. You have access to FactSet MCP tools.

IMPORTANT: You must respond with a JSON object containing the tool call you want to make.

Available tools and their schemas:
{schema_str}

CRITICAL RULES:
1. For FactSet_Fundamentals, data_type MUST be exactly "fundamentals"
2. For FactSet_Ownership, data_type must be one of: fund_holdings, security_holders, insider_transactions, institutional_transactions
3. Ticker format: AAPL-US, MSFT-US, TSLA-US, etc. (symbol-exchange)
4. For metrics in FactSet_Fundamentals, use FF_ prefix (FF_SALES, FF_EPS_BASIC, etc.)
5. For metrics in FactSet_EstimatesConsensus, NO FF_ prefix (SALES, EPS, etc.)

Respond ONLY with a JSON object in this format:
{{
  "tool": "ToolName",
  "arguments": {{...}}
}}

If you cannot determine which tool to use, respond with:
{{
  "tool": "none",
  "reason": "explanation"
}}
"""

    user_prompt = f"User query: {query}\n\nWhich tool should I call and with what arguments?"

    try:
        client = genai.Client(
            vertexai=True,
            project=os.getenv("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=system_prompt + "\n\n" + user_prompt)])
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1000
            )
        )

        response_text = response.text.strip()

        # Parse JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        tool_decision = json.loads(response_text)

        if tool_decision.get("tool") == "none":
            return {
                "llm_decision": tool_decision,
                "tool_called": None,
                "result": None,
                "error": tool_decision.get("reason", "LLM could not determine tool")
            }

        # Execute the tool call
        tool_name = tool_decision.get("tool")
        arguments = tool_decision.get("arguments", {})

        result = await mcp_executor.call_tool(tool_name, arguments)

        return {
            "llm_decision": tool_decision,
            "tool_called": tool_name,
            "arguments": arguments,
            "result": result
        }

    except json.JSONDecodeError as e:
        return {
            "llm_decision": None,
            "tool_called": None,
            "result": None,
            "error": f"Failed to parse LLM response as JSON: {response_text[:200]}"
        }
    except Exception as e:
        return {
            "llm_decision": None,
            "tool_called": None,
            "result": None,
            "error": str(e)
        }


# All 41 test queries
TEST_QUERIES = [
    # FactSet_Fundamentals (5)
    "How much short-term and long-term debt does GE carry?",
    "Is Netflix's current P/E above or below their 5-year average?",
    "How does Tesla's current net margin compare to General Motors and Ford?",
    "Compare the gross margins and ROIC trends for Amazon, Google, and Meta over the past 5 years",
    "What is AMZN's free cash flow for Q1 2024 and how does it compare to Q1 2023?",

    # FactSet_EstimatesConsensus (5)
    "How did the 2025 consensus target price for Amazon change between October and December 2024?",
    "How have next fiscal year EPS estimates for Apple evolved over the past 12 months?",
    "How consistent are long-term growth estimates (FY2-FY3) for Nvidia's sales?",
    "How often does Tesla beat earnings estimates? Show me their surprise pattern over the last 2 years.",
    "What is the current analyst consensus rating for Apple? How many analysts rate it Buy vs Hold vs Sell?",

    # FactSet_GlobalPrices (5)
    "Show the week-over-week change in closing prices for Oracle in Q1 2024",
    "Which days in the past month had the highest trading volume for Amazon?",
    "Show all gap ups greater than 2% for TSLA stock price in the last quarter",
    "Compare the dividend payment frequencies between Johnson & Johnson, Procter & Gamble, and Unilever over the past two years",
    "Calculate the rolling 12-month return correlation between Netflix and Disney over the past 3 years",

    # FactSet_Ownership (5)
    "Show me all Apple holdings across the top 5 largest mutual funds",
    "Who are the top 10 institutional holders of Apple stock?",
    "Compare insider buying vs selling activity for Tesla over the past year",
    "Which Netflix executives have made the largest stock purchases in 2024?",
    "Compare institutional buying patterns between Amazon and Microsoft",

    # FactSet_MergersAcquisitions (4)
    "List all completed acquisitions made by Apple since 2020",
    "Compare the average deal value of Meta and Google acquisitions over the last 5 years",
    "What deals were announced yesterday where the target is a public company?",
    "Retrieve all M&A deals where Amazon was the acquirer since 2015",

    # FactSet_People (5)
    "Show me the organizational structure and contact information for Tesla's leadership team",
    "Show me all the CFOs across the FAANG companies",
    "List the founders still active in leadership roles at major tech companies",
    "Compare executive compensation packages between Netflix and Disney",
    "Compare gender diversity metrics between Apple, Google, and Meta leadership teams",

    # FactSet_CalendarEvents (3)
    "When was Microsoft's last earnings call?",
    "Does Nvidia have an earnings call scheduled this quarter?",
    "Compare the number of earnings calls held by JP Morgan and Goldman Sachs in 2024",

    # FactSet_GeoRev (3)
    "Compare Amazon's Americas and Asia/Pacific revenue over the last 3 years",
    "What's Coca-Cola's European Union revenue exposure?",
    "How much revenue does Apple make in China?",

    # FactSet_SupplyChain (4)
    "List all direct customers of Taiwan Semiconductor",
    "Map the shared supplier ecosystem between Apple and Samsung's supply chains",
    "Starting from Nvidia, map its direct suppliers",
    "Show me Tesla's top competitors",

    # FactSet_Metrics (2)
    "Find metric codes for revenue and profitability",
    "Discover valid metric codes for debt metrics",
]

# Expected tool for each query (for validation)
EXPECTED_TOOLS = [
    "FactSet_Fundamentals", "FactSet_Fundamentals", "FactSet_Fundamentals", "FactSet_Fundamentals", "FactSet_Fundamentals",
    "FactSet_EstimatesConsensus", "FactSet_EstimatesConsensus", "FactSet_EstimatesConsensus", "FactSet_EstimatesConsensus", "FactSet_EstimatesConsensus",
    "FactSet_GlobalPrices", "FactSet_GlobalPrices", "FactSet_GlobalPrices", "FactSet_GlobalPrices", "FactSet_GlobalPrices",
    "FactSet_Ownership", "FactSet_Ownership", "FactSet_Ownership", "FactSet_Ownership", "FactSet_Ownership",
    "FactSet_MergersAcquisitions", "FactSet_MergersAcquisitions", "FactSet_MergersAcquisitions", "FactSet_MergersAcquisitions",
    "FactSet_People", "FactSet_People", "FactSet_People", "FactSet_People", "FactSet_People",
    "FactSet_CalendarEvents", "FactSet_CalendarEvents", "FactSet_CalendarEvents",
    "FactSet_GeoRev", "FactSet_GeoRev", "FactSet_GeoRev",
    "FactSet_SupplyChain", "FactSet_SupplyChain", "FactSet_SupplyChain", "FactSet_SupplyChain",
    "FactSet_Metrics", "FactSet_Metrics",
]


async def main():
    print("=" * 80)
    print(" ADK + LLM + Schema Integration Test")
    print("=" * 80)

    # Load token
    token = get_token()
    if not token:
        print("ERROR: No token found")
        return

    # Load schema
    schema = load_schema()
    if not schema:
        print("ERROR: No schema found")
        return

    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Schema: {len(schema)} tools loaded from mcp_tools_schema.json")
    print(f"Total Queries: {len(TEST_QUERIES)}")
    print("-" * 80)

    # Create MCP executor
    mcp_executor = MCPToolExecutor(token)

    results = []

    for i, query in enumerate(TEST_QUERIES, 1):
        expected_tool = EXPECTED_TOOLS[i-1]
        print(f"\n[{i}/{len(TEST_QUERIES)}] Query: {query[:60]}...")
        print(f"  Expected Tool: {expected_tool}")

        start_time = time.time()

        result = await run_llm_with_schema(query, schema, mcp_executor)

        latency = (time.time() - start_time) * 1000

        tool_called = result.get("tool_called")
        mcp_result = result.get("result", {})
        error = result.get("error")

        # Determine status
        if error:
            status = "NO OK"
            status_detail = f"Error: {error[:100]}"
        elif tool_called != expected_tool:
            # Check if tool call succeeded even if different tool
            if mcp_result and "error" not in mcp_result:
                status = "OK (different tool)"
                status_detail = f"Called {tool_called} instead of {expected_tool}"
            else:
                status = "NO OK"
                status_detail = f"Wrong tool: {tool_called}"
        elif mcp_result and "error" in mcp_result:
            status = "NO OK"
            status_detail = f"MCP Error: {mcp_result['error'][:100]}"
        else:
            status = "OK"
            status_detail = "Success"

        print(f"  Tool Called: {tool_called}")
        print(f"  Status: {status}")
        if status != "OK":
            print(f"  Detail: {status_detail}")
        print(f"  Latency: {latency:.0f}ms")

        results.append({
            "query": query,
            "expected_tool": expected_tool,
            "tool_called": tool_called,
            "arguments": result.get("arguments"),
            "status": status,
            "status_detail": status_detail,
            "mcp_result": mcp_result.get("data", "")[:500] if mcp_result else None,
            "error": error,
            "latency_ms": latency
        })

        # Rate limiting
        await asyncio.sleep(1.0)  # Slower to avoid rate limits with LLM calls

    # Generate Report
    print("\n" + "=" * 80)
    print(" FINAL REPORT - ADK + LLM + Schema Test")
    print("=" * 80)

    ok_count = sum(1 for r in results if r["status"].startswith("OK"))
    no_ok_count = len(results) - ok_count
    correct_tool_count = sum(1 for r in results if r["tool_called"] == r["expected_tool"])
    avg_latency = sum(r["latency_ms"] for r in results) / len(results) if results else 0

    print(f"\n  Timestamp: {datetime.now().isoformat()}")
    print(f"  Total Queries: {len(results)}")
    print(f"  OK: {ok_count} ({ok_count/len(results)*100:.1f}%)")
    print(f"  NO OK: {no_ok_count} ({no_ok_count/len(results)*100:.1f}%)")
    print(f"  Correct Tool Selection: {correct_tool_count}/{len(results)} ({correct_tool_count/len(results)*100:.1f}%)")
    print(f"  Average Latency: {avg_latency:.0f}ms")

    # Group by expected tool
    print("\n  Results by Expected Tool:")
    tools = {}
    for r in results:
        tool = r["expected_tool"]
        if tool not in tools:
            tools[tool] = {"ok": 0, "no_ok": 0, "correct_selection": 0}
        if r["status"].startswith("OK"):
            tools[tool]["ok"] += 1
        else:
            tools[tool]["no_ok"] += 1
        if r["tool_called"] == r["expected_tool"]:
            tools[tool]["correct_selection"] += 1

    for tool, counts in tools.items():
        total = counts["ok"] + counts["no_ok"]
        print(f"    {tool}: {counts['ok']}/{total} OK, {counts['correct_selection']}/{total} correct selection")

    # Save detailed report
    report = {
        "test_type": "ADK + LLM + Schema",
        "timestamp": datetime.now().isoformat(),
        "schema_file": "mcp_tools_schema.json",
        "summary": {
            "total": len(results),
            "ok": ok_count,
            "no_ok": no_ok_count,
            "success_rate": f"{ok_count/len(results)*100:.1f}%",
            "correct_tool_selection": correct_tool_count,
            "tool_selection_rate": f"{correct_tool_count/len(results)*100:.1f}%",
            "average_latency_ms": avg_latency
        },
        "by_tool": tools,
        "results": results
    }

    with open("adk_schema_test_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Create markdown report
    md_report = f"""# ADK + LLM + Schema Integration Test Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Configuration
- **Schema File:** `mcp_tools_schema.json`
- **LLM:** Gemini 2.0 Flash
- **Test Type:** Natural language query -> LLM interpretation -> MCP tool call

## Summary

| Metric | Value |
|--------|-------|
| Total Queries | {len(results)} |
| OK | {ok_count} ({ok_count/len(results)*100:.1f}%) |
| NO OK | {no_ok_count} ({no_ok_count/len(results)*100:.1f}%) |
| Correct Tool Selection | {correct_tool_count}/{len(results)} ({correct_tool_count/len(results)*100:.1f}%) |
| Avg Latency | {avg_latency:.0f}ms |

## Results by Tool

| Tool | OK | NO OK | Correct Selection |
|------|-----|-------|-------------------|
"""
    for tool, counts in tools.items():
        total = counts["ok"] + counts["no_ok"]
        md_report += f"| {tool} | {counts['ok']} | {counts['no_ok']} | {counts['correct_selection']}/{total} |\n"

    md_report += "\n## Detailed Results\n\n"

    for r in results:
        status_emoji = "OK" if r["status"].startswith("OK") else "NO OK"
        md_report += f"""### Query {results.index(r) + 1}

**Query:** {r['query']}

**Expected Tool:** `{r['expected_tool']}`

**Tool Called:** `{r['tool_called']}`

**Arguments:**
```json
{json.dumps(r['arguments'], indent=2) if r['arguments'] else 'null'}
```

**Status:** {status_emoji} - {r['status_detail']}

**Latency:** {r['latency_ms']:.0f}ms

---

"""

    with open("adk_schema_test_report.md", "w") as f:
        f.write(md_report)

    print(f"\n  Reports saved:")
    print(f"    - adk_schema_test_report.json")
    print(f"    - adk_schema_test_report.md")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
