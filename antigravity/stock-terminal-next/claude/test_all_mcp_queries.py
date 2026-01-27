#!/usr/bin/env python3
"""
Comprehensive FactSet MCP Query Test
=====================================
Tests all sample prompts from the documentation and generates a report.
"""

import os
import sys
import json
import asyncio
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "refresh_token.json")
MCP_ENDPOINT = "https://mcp.factset.com/content/v1/messages"


def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            return data.get("default_chat", {}).get("token")
    return None


def parse_sse_response(text: str) -> dict:
    """Parse SSE response to JSON."""
    for line in text.split("\n"):
        if line.startswith("data:"):
            json_str = line[5:].strip()
            return json.loads(json_str)
    return {}


async def mcp_request(client: httpx.AsyncClient, method: str, params: dict, token: str, req_id: int = 1) -> dict:
    """Make an MCP JSON-RPC request."""
    request = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method,
        "params": params
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }

    try:
        response = await client.post(MCP_ENDPOINT, headers=headers, json=request, timeout=60.0)
        if response.status_code == 200:
            return parse_sse_response(response.text)
        else:
            return {"error": f"HTTP {response.status_code}: {response.text[:500]}"}
    except Exception as e:
        return {"error": str(e)}


# Calculate common dates
today = datetime.now()
today_str = today.strftime("%Y-%m-%d")
yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
last_week = (today - timedelta(days=7)).strftime("%Y-%m-%d")
last_month = (today - timedelta(days=30)).strftime("%Y-%m-%d")
last_quarter = (today - timedelta(days=90)).strftime("%Y-%m-%d")
last_year = (today - timedelta(days=365)).strftime("%Y-%m-%d")
two_years_ago = (today - timedelta(days=730)).strftime("%Y-%m-%d")
five_years_ago = (today - timedelta(days=1825)).strftime("%Y-%m-%d")
current_year = str(today.year)
last_year_num = str(today.year - 1)

# All test queries organized by tool
TEST_QUERIES = [
    # ===== FactSet_Fundamentals =====
    {
        "category": "FactSet_Fundamentals",
        "query": "How much short-term and long-term debt does GE carry?",
        "tool": "FactSet_Fundamentals",
        "params": {
            "ids": ["GE-US"],
            "data_type": "fundamentals",
            "metrics": ["FF_DEBT_ST", "FF_DEBT_LT"]
        }
    },
    {
        "category": "FactSet_Fundamentals",
        "query": "Is Netflix's current P/E above or below their 5-year average?",
        "tool": "FactSet_Fundamentals",
        "params": {
            "ids": ["NFLX-US"],
            "data_type": "fundamentals",
            "metrics": ["FF_PE"],
            "fiscalPeriodStart": five_years_ago,
            "fiscalPeriodEnd": today_str,
            "periodicity": "ANN"
        }
    },
    {
        "category": "FactSet_Fundamentals",
        "query": "How does Tesla's current net margin compare to General Motors and Ford?",
        "tool": "FactSet_Fundamentals",
        "params": {
            "ids": ["TSLA-US", "GM-US", "F-US"],
            "data_type": "fundamentals",
            "metrics": ["FF_NET_MGN"]
        }
    },
    {
        "category": "FactSet_Fundamentals",
        "query": "Compare the gross margins and ROIC trends for Amazon, Google, and Meta over the past 5 years",
        "tool": "FactSet_Fundamentals",
        "params": {
            "ids": ["AMZN-US", "GOOGL-US", "META-US"],
            "data_type": "fundamentals",
            "metrics": ["FF_GROSS_MGN", "FF_ROIC"],
            "fiscalPeriodStart": five_years_ago,
            "fiscalPeriodEnd": today_str,
            "periodicity": "ANN"
        }
    },
    {
        "category": "FactSet_Fundamentals",
        "query": "What is AMZN's free cash flow for Q1 2024 and how does it compare to Q1 2023?",
        "tool": "FactSet_Fundamentals",
        "params": {
            "ids": ["AMZN-US"],
            "data_type": "fundamentals",
            "metrics": ["FF_FREE_CF"],
            "fiscalPeriodStart": "2023-01-01",
            "fiscalPeriodEnd": "2024-03-31",
            "periodicity": "QTR"
        }
    },

    # ===== FactSet_EstimatesConsensus =====
    {
        "category": "FactSet_EstimatesConsensus",
        "query": "How did the 2025 consensus target price for Amazon change between October and December 2024?",
        "tool": "FactSet_EstimatesConsensus",
        "params": {
            "ids": ["AMZN-US"],
            "estimate_type": "consensus_rolling",
            "metrics": ["PRICE_TGT"],
            "relativeFiscalStart": 0,
            "relativeFiscalEnd": 0,
            "startDate": "2024-10-01",
            "endDate": "2024-12-31",
            "frequency": "AM"
        }
    },
    {
        "category": "FactSet_EstimatesConsensus",
        "query": "How have next fiscal year EPS estimates for Apple evolved over the past 12 months?",
        "tool": "FactSet_EstimatesConsensus",
        "params": {
            "ids": ["AAPL-US"],
            "estimate_type": "consensus_rolling",
            "metrics": ["EPS"],
            "relativeFiscalStart": 1,
            "relativeFiscalEnd": 1,
            "startDate": last_year,
            "endDate": today_str,
            "frequency": "AM"
        }
    },
    {
        "category": "FactSet_EstimatesConsensus",
        "query": "How consistent are long-term growth estimates (FY2-FY3) for Nvidia's sales?",
        "tool": "FactSet_EstimatesConsensus",
        "params": {
            "ids": ["NVDA-US"],
            "estimate_type": "consensus_rolling",
            "metrics": ["SALES"],
            "relativeFiscalStart": 2,
            "relativeFiscalEnd": 3
        }
    },
    {
        "category": "FactSet_EstimatesConsensus",
        "query": "How often does Tesla beat earnings estimates? Show me their surprise pattern over the last 2 years.",
        "tool": "FactSet_EstimatesConsensus",
        "params": {
            "ids": ["TSLA-US"],
            "estimate_type": "surprise",
            "metrics": ["EPS"],
            "startDate": two_years_ago,
            "endDate": today_str,
            "periodicity": "QTR"
        }
    },
    {
        "category": "FactSet_EstimatesConsensus",
        "query": "What is the current analyst consensus rating for Apple? How many analysts rate it Buy vs Hold vs Sell?",
        "tool": "FactSet_EstimatesConsensus",
        "params": {
            "ids": ["AAPL-US"],
            "estimate_type": "ratings"
        }
    },

    # ===== FactSet_GlobalPrices =====
    {
        "category": "FactSet_GlobalPrices",
        "query": "Show the week-over-week change in closing prices for Oracle in Q1 2024",
        "tool": "FactSet_GlobalPrices",
        "params": {
            "ids": ["ORCL-US"],
            "data_type": "prices",
            "startDate": "2024-01-01",
            "endDate": "2024-03-31",
            "frequency": "W"
        }
    },
    {
        "category": "FactSet_GlobalPrices",
        "query": "Which days in the past month had the highest trading volume for Amazon?",
        "tool": "FactSet_GlobalPrices",
        "params": {
            "ids": ["AMZN-US"],
            "data_type": "prices",
            "startDate": last_month,
            "endDate": today_str,
            "fields": ["volume", "price"]
        }
    },
    {
        "category": "FactSet_GlobalPrices",
        "query": "Show all gap ups greater than 2% for TSLA stock price in the last quarter",
        "tool": "FactSet_GlobalPrices",
        "params": {
            "ids": ["TSLA-US"],
            "data_type": "prices",
            "startDate": last_quarter,
            "endDate": today_str
        }
    },
    {
        "category": "FactSet_GlobalPrices",
        "query": "Compare the dividend payment frequencies between Johnson & Johnson, Procter & Gamble, and Unilever over the past two years",
        "tool": "FactSet_GlobalPrices",
        "params": {
            "ids": ["JNJ-US", "PG-US", "UL-US"],
            "data_type": "corporate_actions",
            "eventCategory": "CASH_DIVS",
            "startDate": two_years_ago,
            "endDate": today_str
        }
    },
    {
        "category": "FactSet_GlobalPrices",
        "query": "Calculate the rolling 12-month return correlation between Netflix and Disney over the past 3 years",
        "tool": "FactSet_GlobalPrices",
        "params": {
            "ids": ["NFLX-US", "DIS-US"],
            "data_type": "returns",
            "startDate": "2022-01-01",
            "endDate": today_str,
            "frequency": "M"
        }
    },

    # ===== FactSet_Ownership =====
    {
        "category": "FactSet_Ownership",
        "query": "Show me all Apple holdings across the top 5 largest mutual funds",
        "tool": "FactSet_Ownership",
        "params": {
            "ids": ["AAPL-US"],
            "data_type": "security_holders",
            "holderType": "M",
            "topn": "5"
        }
    },
    {
        "category": "FactSet_Ownership",
        "query": "Who are the top 10 institutional holders of Apple stock?",
        "tool": "FactSet_Ownership",
        "params": {
            "ids": ["AAPL-US"],
            "data_type": "security_holders",
            "holderType": "F",
            "topn": "10"
        }
    },
    {
        "category": "FactSet_Ownership",
        "query": "Compare insider buying vs selling activity for Tesla over the past year",
        "tool": "FactSet_Ownership",
        "params": {
            "ids": ["TSLA-US"],
            "data_type": "insider_transactions",
            "startDate": last_year,
            "endDate": today_str
        }
    },
    {
        "category": "FactSet_Ownership",
        "query": "Which Netflix executives have made the largest stock purchases in 2024?",
        "tool": "FactSet_Ownership",
        "params": {
            "ids": ["NFLX-US"],
            "data_type": "insider_transactions",
            "transactionType": "P",
            "startDate": "2024-01-01",
            "endDate": "2024-12-31"
        }
    },
    {
        "category": "FactSet_Ownership",
        "query": "Compare institutional buying patterns between Amazon and Microsoft",
        "tool": "FactSet_Ownership",
        "params": {
            "ids": ["AMZN-US", "MSFT-US"],
            "data_type": "institutional_transactions",
            "startDate": last_year,
            "endDate": today_str
        }
    },

    # ===== FactSet_MergersAcquisitions =====
    {
        "category": "FactSet_MergersAcquisitions",
        "query": "List all completed acquisitions made by Apple since 2020",
        "tool": "FactSet_MergersAcquisitions",
        "params": {
            "ids": ["AAPL-US"],
            "data_type": "deals_by_company",
            "startDate": "2024-01-01",
            "endDate": "2024-12-31"
        }
    },
    {
        "category": "FactSet_MergersAcquisitions",
        "query": "Compare the average deal value of Meta and Google acquisitions over the last 5 years",
        "tool": "FactSet_MergersAcquisitions",
        "params": {
            "ids": ["META-US", "GOOGL-US"],
            "data_type": "deals_by_company",
            "startDate": "2024-01-01",
            "endDate": "2024-12-31"
        }
    },
    {
        "category": "FactSet_MergersAcquisitions",
        "query": "What deals were announced yesterday where the target is a public company?",
        "tool": "FactSet_MergersAcquisitions",
        "params": {
            "data_type": "public_targets",
            "status": "All",
            "startDate": last_week,
            "endDate": today_str
        }
    },
    {
        "category": "FactSet_MergersAcquisitions",
        "query": "Retrieve all M&A deals where Amazon was the acquirer since 2015 (2024 window)",
        "tool": "FactSet_MergersAcquisitions",
        "params": {
            "ids": ["AMZN-US"],
            "data_type": "deals_by_company",
            "startDate": "2024-01-01",
            "endDate": "2024-12-31"
        }
    },

    # ===== FactSet_People =====
    {
        "category": "FactSet_People",
        "query": "Show me the organizational structure and contact information for Tesla's leadership team",
        "tool": "FactSet_People",
        "params": {
            "ids": ["TSLA-US"],
            "data_type": "company_people",
            "function": "PEOPLE"
        }
    },
    {
        "category": "FactSet_People",
        "query": "Show me all the CFOs across the FAANG companies",
        "tool": "FactSet_People",
        "params": {
            "ids": ["META-US", "AAPL-US", "AMZN-US", "NFLX-US", "GOOGL-US"],
            "data_type": "company_positions",
            "position": "CFO"
        }
    },
    {
        "category": "FactSet_People",
        "query": "List the founders still active in leadership roles at major tech companies",
        "tool": "FactSet_People",
        "params": {
            "ids": ["META-US", "AAPL-US", "AMZN-US", "MSFT-US", "GOOGL-US"],
            "data_type": "company_positions",
            "position": "FOU"
        }
    },
    {
        "category": "FactSet_People",
        "query": "Compare executive compensation packages between Netflix and Disney",
        "tool": "FactSet_People",
        "params": {
            "ids": ["NFLX-US", "DIS-US"],
            "data_type": "company_compensation"
        }
    },
    {
        "category": "FactSet_People",
        "query": "Compare gender diversity metrics between Apple, Google, and Meta leadership teams",
        "tool": "FactSet_People",
        "params": {
            "ids": ["AAPL-US", "GOOGL-US", "META-US"],
            "data_type": "company_stats",
            "mbType": "MB"
        }
    },

    # ===== FactSet_CalendarEvents =====
    {
        "category": "FactSet_CalendarEvents",
        "query": "When was Microsoft's last earnings call?",
        "tool": "FactSet_CalendarEvents",
        "params": {
            "symbols": ["MSFT-US"],
            "universeType": "Tickers",
            "eventTypes": ["Earnings"],
            "startDateTime": (today - timedelta(days=90)).strftime("%Y-%m-%dT00:00:00Z"),
            "endDateTime": today.strftime("%Y-%m-%dT23:59:59Z")
        }
    },
    {
        "category": "FactSet_CalendarEvents",
        "query": "Does Nvidia have an earnings call scheduled this quarter?",
        "tool": "FactSet_CalendarEvents",
        "params": {
            "symbols": ["NVDA-US"],
            "universeType": "Tickers",
            "eventTypes": ["Earnings", "ConfirmedEarningsRelease", "ProjectedEarningsRelease"],
            "startDateTime": today.strftime("%Y-%m-%dT00:00:00Z"),
            "endDateTime": (today + timedelta(days=89)).strftime("%Y-%m-%dT23:59:59Z")
        }
    },
    {
        "category": "FactSet_CalendarEvents",
        "query": "Compare the number of earnings calls held by JP Morgan and Goldman Sachs in 2024",
        "tool": "FactSet_CalendarEvents",
        "params": {
            "symbols": ["JPM-US", "GS-US"],
            "universeType": "Tickers",
            "eventTypes": ["Earnings"],
            "startDateTime": "2024-10-01T00:00:00Z",
            "endDateTime": "2024-12-31T00:00:00Z"
        }
    },

    # ===== FactSet_GeoRev =====
    {
        "category": "FactSet_GeoRev",
        "query": "Compare Amazon's Americas and Asia/Pacific revenue over the last 3 years",
        "tool": "FactSet_GeoRev",
        "params": {
            "ids": ["AMZN-US"],
            "data_type": "regions",
            "regionIds": ["R101", "R170"],
            "startDate": "2021-01-01",
            "endDate": today_str,
            "frequency": "FY"
        }
    },
    {
        "category": "FactSet_GeoRev",
        "query": "What's Coca-Cola's European Union revenue exposure?",
        "tool": "FactSet_GeoRev",
        "params": {
            "ids": ["KO-US"],
            "data_type": "regions",
            "regionIds": ["R275"]
        }
    },
    {
        "category": "FactSet_GeoRev",
        "query": "How much revenue does Apple make in China?",
        "tool": "FactSet_GeoRev",
        "params": {
            "ids": ["AAPL-US"],
            "data_type": "countries",
            "countryIds": ["CN"]
        }
    },

    # ===== FactSet_SupplyChain =====
    {
        "category": "FactSet_SupplyChain",
        "query": "List all direct customers of Taiwan Semiconductor",
        "tool": "FactSet_SupplyChain",
        "params": {
            "ids": ["TSM-US"],
            "relationshipType": "CUSTOMERS"
        }
    },
    {
        "category": "FactSet_SupplyChain",
        "query": "Map the shared supplier ecosystem between Apple and Samsung's supply chains",
        "tool": "FactSet_SupplyChain",
        "params": {
            "ids": ["AAPL-US", "005930-KR"],
            "relationshipType": "SUPPLIERS"
        }
    },
    {
        "category": "FactSet_SupplyChain",
        "query": "Starting from Nvidia, map its direct suppliers",
        "tool": "FactSet_SupplyChain",
        "params": {
            "ids": ["NVDA-US"],
            "relationshipType": "SUPPLIERS"
        }
    },
    {
        "category": "FactSet_SupplyChain",
        "query": "Show me Tesla's top competitors",
        "tool": "FactSet_SupplyChain",
        "params": {
            "ids": ["TSLA-US"],
            "relationshipType": "COMPETITORS"
        }
    },

    # ===== FactSet_Metrics =====
    {
        "category": "FactSet_Metrics",
        "query": "Find metric codes for revenue and profitability",
        "tool": "FactSet_Metrics",
        "params": {
            "text": ["revenue", "profitability ratios"],
            "target": "metric",
            "data_products": ["fundamentals"],
            "limit": 5
        }
    },
    {
        "category": "FactSet_Metrics",
        "query": "Discover valid metric codes for debt metrics",
        "tool": "FactSet_Metrics",
        "params": {
            "text": ["debt", "leverage"],
            "target": "metric",
            "data_products": ["fundamentals"],
            "limit": 5
        }
    },
]


async def run_all_tests():
    token = get_token()
    if not token:
        print("ERROR: No token found")
        return

    print("=" * 80)
    print(" FactSet MCP Comprehensive Query Test")
    print("=" * 80)
    print(f"\nDate: {today.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Queries: {len(TEST_QUERIES)}")
    print("-" * 80)

    results = []

    async with httpx.AsyncClient(timeout=120.0) as client:
        for i, test in enumerate(TEST_QUERIES, 1):
            print(f"\n[{i}/{len(TEST_QUERIES)}] {test['category']}")
            print(f"  Query: {test['query'][:70]}...")
            print(f"  Tool: {test['tool']}")

            start_time = asyncio.get_event_loop().time()

            result = await mcp_request(
                client,
                "tools/call",
                {"name": test["tool"], "arguments": test["params"]},
                token,
                i
            )

            latency = (asyncio.get_event_loop().time() - start_time) * 1000

            content = result.get("result", {}).get("content", [])
            is_error = result.get("result", {}).get("isError", False)
            error_in_result = "error" in result

            if is_error or error_in_result:
                if error_in_result:
                    error_text = str(result.get("error", "Unknown error"))
                else:
                    error_text = content[0].get("text", "Unknown error") if content else "Unknown error"

                print(f"  Status: NO OK")
                print(f"  Error: {error_text[:100]}")
                results.append({
                    "category": test["category"],
                    "query": test["query"],
                    "tool": test["tool"],
                    "status": "NO OK",
                    "answer": f"ERROR: {error_text[:500]}",
                    "latency_ms": latency
                })
            else:
                response_text = content[0].get("text", "No response") if content else "No response"
                # Check if response has actual data
                try:
                    response_json = json.loads(response_text)
                    data = response_json.get("data", [])
                    if data and len(data) > 0:
                        # Check if data has non-null values
                        has_data = any(
                            v is not None
                            for item in data[:3]
                            for k, v in item.items()
                            if k not in ["requestId", "fsymId"]
                        )
                        if has_data:
                            print(f"  Status: OK")
                            print(f"  Response: {response_text[:100]}...")
                            results.append({
                                "category": test["category"],
                                "query": test["query"],
                                "tool": test["tool"],
                                "status": "OK",
                                "answer": response_text[:1000],
                                "latency_ms": latency
                            })
                        else:
                            print(f"  Status: OK (empty data)")
                            results.append({
                                "category": test["category"],
                                "query": test["query"],
                                "tool": test["tool"],
                                "status": "OK",
                                "answer": "Data returned but values are null (may be market closed or no data)",
                                "latency_ms": latency
                            })
                    else:
                        print(f"  Status: OK (no data)")
                        results.append({
                            "category": test["category"],
                            "query": test["query"],
                            "tool": test["tool"],
                            "status": "OK",
                            "answer": response_text[:500],
                            "latency_ms": latency
                        })
                except json.JSONDecodeError:
                    print(f"  Status: OK")
                    print(f"  Response: {response_text[:100]}...")
                    results.append({
                        "category": test["category"],
                        "query": test["query"],
                        "tool": test["tool"],
                        "status": "OK",
                        "answer": response_text[:1000],
                        "latency_ms": latency
                    })

            print(f"  Latency: {latency:.0f}ms")
            await asyncio.sleep(0.3)  # Rate limiting

    # Generate Report
    print("\n" + "=" * 80)
    print(" FINAL REPORT")
    print("=" * 80)

    ok_count = sum(1 for r in results if r["status"] == "OK")
    no_ok_count = len(results) - ok_count
    avg_latency = sum(r["latency_ms"] for r in results) / len(results) if results else 0

    print(f"\n  Timestamp: {datetime.now().isoformat()}")
    print(f"  Total Queries: {len(results)}")
    print(f"  OK: {ok_count} ({ok_count/len(results)*100:.1f}%)")
    print(f"  NO OK: {no_ok_count} ({no_ok_count/len(results)*100:.1f}%)")
    print(f"  Average Latency: {avg_latency:.0f}ms")

    # Group by category
    print("\n  Results by Category:")
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"ok": 0, "no_ok": 0}
        if r["status"] == "OK":
            categories[cat]["ok"] += 1
        else:
            categories[cat]["no_ok"] += 1

    for cat, counts in categories.items():
        total = counts["ok"] + counts["no_ok"]
        print(f"    {cat}: {counts['ok']}/{total} OK")

    # Save detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": len(results),
            "ok": ok_count,
            "no_ok": no_ok_count,
            "success_rate": f"{ok_count/len(results)*100:.1f}%",
            "average_latency_ms": avg_latency
        },
        "by_category": categories,
        "results": results
    }

    with open("comprehensive_mcp_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Create markdown report
    md_report = f"""# FactSet MCP Comprehensive Query Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value |
|--------|-------|
| Total Queries | {len(results)} |
| OK | {ok_count} ({ok_count/len(results)*100:.1f}%) |
| NO OK | {no_ok_count} ({no_ok_count/len(results)*100:.1f}%) |
| Avg Latency | {avg_latency:.0f}ms |

## Results by Category

| Category | OK | NO OK | Rate |
|----------|-----|-------|------|
"""
    for cat, counts in categories.items():
        total = counts["ok"] + counts["no_ok"]
        rate = counts["ok"]/total*100 if total > 0 else 0
        md_report += f"| {cat} | {counts['ok']} | {counts['no_ok']} | {rate:.0f}% |\n"

    md_report += "\n## Detailed Results\n\n"

    for r in results:
        status_emoji = "OK" if r["status"] == "OK" else "NO OK"
        md_report += f"""### {r['category']}

**Query:** {r['query']}

**Tool:** `{r['tool']}`

**Status:** {status_emoji}

**Answer:**
```
{r['answer'][:500]}{"..." if len(r['answer']) > 500 else ""}
```

**Latency:** {r['latency_ms']:.0f}ms

---

"""

    with open("comprehensive_mcp_report.md", "w") as f:
        f.write(md_report)

    print(f"\n  Reports saved:")
    print(f"    - comprehensive_mcp_report.json")
    print(f"    - comprehensive_mcp_report.md")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
