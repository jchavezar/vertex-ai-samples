"""
Step 2: Connecting the Official Google Cloud MCP Toolbox for Databases (BigQuery) to Google ADK Locally
------------------------------------------------------------------------------------------------------
This script demonstrates how an ADK Agent natively connects to Google Cloud BigQuery
via the official Google Cloud MCP Toolbox for Databases (`@toolbox-sdk/server` / `mcp-toolbox`)
using `McpToolset`.

Enterprise Pattern:
Implements Google Cloud's official MCP Toolbox for Databases:
- Blog: https://cloud.google.com/blog/products/ai-machine-learning/mcp-toolbox-for-databases-now-supports-model-context-protocol
- Repo: https://github.com/googleapis/mcp-toolbox
- Binary / Package: `@toolbox-sdk/server --prebuilt bigquery --stdio`

Live GCP BigQuery Target:
- Project: `vtxdemos`
- Dataset: `weil_legal_vault`
- Live Tables:
  1. `vtxdemos.weil_legal_vault.precedent_deals`
  2. `vtxdemos.weil_legal_vault.gold_standard_clauses`
"""

import os
import sys
import asyncio
from pathlib import Path

# Enforce target environment configuration
os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["BIGQUERY_PROJECT"] = "vtxdemos"
os.environ["BIGQUERY_LOCATION"] = "US"
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS_ENDPOINT"] = "never"

from google.adk.agents import Agent
from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# ---------------------------------------------------------------------------
# 1. Connect to the Official Google Cloud MCP Toolbox for Databases Server
# ---------------------------------------------------------------------------
print("=" * 75)
print("🔌 [MCP TOOLBOX] Connecting to Official Google Cloud MCP Toolbox for Databases...")
print("   MCP Server Package   : @toolbox-sdk/server (v1.10.0+)")
print("   Command              : npx -y @toolbox-sdk/server --prebuilt bigquery --stdio")
print("   GCP Project ID       : vtxdemos")
print("   BigQuery Dataset     : vtxdemos.weil_legal_vault")
print("   Live Tables          : precedent_deals | gold_standard_clauses")
print("=" * 75)

mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@toolbox-sdk/server", "--prebuilt", "bigquery", "--stdio"],
            env={
                **os.environ,
                "BIGQUERY_PROJECT": "vtxdemos",
                "BIGQUERY_LOCATION": "US",
                "GOOGLE_CLOUD_PROJECT": "vtxdemos",
                "GOOGLE_CLOUD_LOCATION": "global",
                "GOOGLE_API_USE_CLIENT_CERTIFICATE": "false",
                "GOOGLE_API_USE_MTLS_ENDPOINT": "never",
            }
        )
    )
)

# ---------------------------------------------------------------------------
# 2. Define the ADK Agent Equipped with Official MCP Toolbox Tools
# ---------------------------------------------------------------------------
bigquery_deal_agent = Agent(
    name="weil_deal_intelligence_agent",
    model="gemini-3.8-flash",
    instruction="""
    You are the Weil Senior M&A Precedent & Deal Benchmarking Specialist.
    You interact with live Google Cloud BigQuery data using the official Google Cloud MCP Toolbox for Databases.
    
    Your mandate:
    1. First discover what legal tables exist in dataset `weil_legal_vault` using `list_table_ids` or `get_dataset_info`.
    2. Query `vtxdemos.weil_legal_vault.precedent_deals` using `execute_sql` for comparable deals in the target sector and deal size threshold.
    3. Query `vtxdemos.weil_legal_vault.gold_standard_clauses` using `execute_sql` for market-standard reverse breakup fee language.
    4. State explicitly the full BigQuery table names queried (`vtxdemos.weil_legal_vault.precedent_deals`), row counts, and exact SQL queries executed.
    5. Synthesize the findings into an executive recommendation for the lead partner.
    """,
    tools=[mcp_toolset],
)

# ---------------------------------------------------------------------------
# 3. Local Execution Demonstration
# ---------------------------------------------------------------------------
async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="weil_mcp_showcase",
        user_id="partner_001",
        session_id="session_mcp_02"
    )
    
    runner = Runner(
        agent=bigquery_deal_agent,
        session_service=session_service,
        app_name="weil_mcp_showcase"
    )
    
    prompt = (
        "Client Nexus Capital is structuring a $2.3B acquisition of Zephyr Robotics. "
        "Inspect our Google Cloud BigQuery legal vault tables (`vtxdemos.weil_legal_vault`), "
        "query comparable deals in tech/robotics above $1000M, "
        "and retrieve the gold-standard reverse breakup fee clause language for antitrust risk."
    )
    
    print(f"\n👤 [PROMPT]:\n{prompt}\n")
    print("🤖 [AGENT REASONING & MCP TOOL DISPATCH (LIVE GCP BIGQUERY)]:")
    
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)]
    )
    
    async for event in runner.run_async(
        user_id="partner_001",
        session_id=session.id,
        new_message=content
    ):
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    print(part.text, end="", flush=True)
                    
    print("\n\n✅ MCP BigQuery Integration Pipeline Complete.")

if __name__ == "__main__":
    asyncio.run(main())
