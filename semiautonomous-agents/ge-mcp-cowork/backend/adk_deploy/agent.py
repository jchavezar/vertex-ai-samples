import os
import httpx
import base64
import logging
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("adk-jira-agent")

# Remote Jira MCP Endpoint (Default)
JIRA_MCP_URL = os.environ.get("JIRA_MCP_URL", "https://jira-mcp-server-254356041555.us-central1.run.app/mcp")

# Atlassian credentials passed via environment
email = os.environ.get("ATLASSIAN_EMAIL", "")
token = os.environ.get("ATLASSIAN_API_TOKEN", "")
site_url = os.environ.get("ATLASSIAN_SITE_URL", "")

jira_headers = {"Content-Type": "application/json"}
if email and token:
    auth_str = f"{email}:{token}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    jira_headers["Authorization"] = f"Basic {b64_auth}"
if site_url:
    jira_headers["X-Atlassian-Site"] = site_url.rstrip("/")

async def _call_mcp(method: str, arguments: dict) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": method,
            "arguments": arguments
        }
    }
    logger.info(f"Calling MCP tool '{method}' on Jira MCP Server...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(JIRA_MCP_URL, headers=jira_headers, json=payload, timeout=60)
            if resp.status_code == 200:
                result = resp.json().get("result", {})
                return result
            else:
                logger.error(f"MCP call failed with status {resp.status_code}: {resp.text}")
                return {"error": f"MCP call failed with status {resp.status_code}"}
        except Exception as e:
            logger.exception(f"Exception calling MCP: {e}")
            return {"error": str(e)}

async def jira_search(ctx: CallbackContext, query: str) -> dict:
    """Search Jira issues using a free-text query.
    
    Args:
        query: The search term or JQL query to execute in Jira.
    """
    return await _call_mcp("search", {"query": query})

async def jira_fetch(ctx: CallbackContext, id: str) -> dict:
    """Fetch a single Jira issue by its issue key (e.g. SMP-123).
    
    Args:
        id: The Jira issue key.
    """
    return await _call_mcp("fetch", {"id": id})

# Define the root agent
root_agent = LlmAgent(
    name="JiraAgentEngine",
    model="gemini-2.5-flash",
    instruction=(
        "You are a helpful assistant with access to Jira issues. "
        "Use the tools jira_search and jira_fetch to find and retrieve issue details. "
        "Cite issue keys in your response.\n\n"
        "**DASHBOARD VISUALIZATION RULES**:\n"
        "When the user asks for summaries, distribution, breakdowns, or comparison metrics of tickets/documents "
        "(e.g., 'distribution of Ducati issues', 'priority breakdown of open tickets'), "
        "you MUST append a beautiful interactive dashboard chart to the end of your text response. "
        "Use the following custom tag syntax:\n"
        "<chart type=\"pie\" title=\"Chart Title\">\n"
        "[\n"
        "  {\"name\": \"Category 1\", \"value\": 10},\n"
        "  {\"name\": \"Category 2\", \"value\": 20}\n"
        "]\n"
        "</chart>\n"
        "Supported types are 'pie' (donut charts, best for status, site breakdowns) and 'bar' (horizontal bar charts, best for lists, scores, comparisons). "
        "Keep category names concise. Do not output raw HTML tags other than <chart>.\n\n"
        "**CRITICAL FOLLOW-UP SUGGESTIONS RULES**:\n"
        "At the very end of your response, after any charts, you MUST suggest 2 to 3 follow-up questions that are directly related to the user's question AND based ONLY on the actual data/context retrieved.\n"
        "Ensure the suggested questions are answerable using the available tools and data in the workspace (for example, if you just retrieved a list of open bugs, suggest asking about the cycle time of those bugs, or who is assigned to them). Do not suggest questions that cannot be answered or are unrelated to the current context.\n"
        "Format these suggestions inside a <suggestions> XML tag block, with each suggestion in a <suggestion> child tag, like this:\n"
        "<suggestions>\n"
        "  <suggestion>What is the average cycle time for the open bugs in PLAT?</suggestion>\n"
        "  <suggestion>Show me who is assigned to the High priority issues.</suggestion>\n"
        "</suggestions>"
    ),
    tools=[jira_search, jira_fetch]
)

__all__ = ["root_agent"]
