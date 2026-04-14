"""ServiceNow MCP Server — reads credentials from environment variables."""
import os
import json
import logging
import requests
from typing import Optional
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("servicenow_mcp")

mcp = FastMCP("ServiceNow-MCP")

INSTANCE_URL = os.environ.get("SERVICENOW_INSTANCE_URL", "").rstrip("/")
USERNAME = os.environ.get("SERVICENOW_BASIC_AUTH_USER", "")
PASSWORD = os.environ.get("SERVICENOW_BASIC_AUTH_PASS", "")


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
    s.auth = (USERNAME, PASSWORD)
    return s


def _url(table: str) -> str:
    return f"{INSTANCE_URL}/api/now/table/{table}"


@mcp.tool()
def list_incidents(limit: int = 20, state: Optional[str] = None) -> str:
    """List ServiceNow incidents.

    Args:
        limit: Max records to return
        state: Filter by state (1=New, 2=In Progress, 3=On Hold, 6=Resolved, 7=Closed)
    """
    query = "ORDERBYDESCsys_created_on"
    if state:
        query = f"state={state}^{query}"
    resp = _session().get(_url("incident"), params={"sysparm_limit": limit, "sysparm_query": query})
    resp.raise_for_status()
    rows = resp.json().get("result", [])
    if not rows:
        return "No incidents found."
    out = "| Number | Short Description | Priority | State | Created |\n|--------|-------------------|----------|-------|--------|\n"
    for r in rows:
        out += f"| {r.get('number','N/A')} | {(r.get('short_description','') or 'N/A')[:50]} | {r.get('priority','?')} | {r.get('state','?')} | {r.get('sys_created_on','')[:10]} |\n"
    return out


@mcp.tool()
def search_incidents(search_term: str, limit: int = 10) -> str:
    """Search incidents by description.

    Args:
        search_term: Text to search for
        limit: Max results
    """
    query = f"short_descriptionLIKE{search_term}^ORdescriptionLIKE{search_term}^ORDERBYDESCsys_created_on"
    resp = _session().get(_url("incident"), params={"sysparm_limit": limit, "sysparm_query": query})
    resp.raise_for_status()
    rows = resp.json().get("result", [])
    if not rows:
        return f"No incidents matching '{search_term}'."
    return "\n".join(f"- **{r.get('number')}**: {r.get('short_description','N/A')} (P{r.get('priority','?')})" for r in rows)


@mcp.tool()
def get_incident(number: str) -> str:
    """Get a specific incident by number.

    Args:
        number: Incident number (e.g., INC0010001)
    """
    resp = _session().get(_url("incident"), params={"sysparm_limit": 1, "sysparm_query": f"number={number}"})
    resp.raise_for_status()
    rows = resp.json().get("result", [])
    if not rows:
        return f"Incident {number} not found."
    r = rows[0]
    return (
        f"**{r.get('number')}**\n"
        f"- Short Description: {r.get('short_description','N/A')}\n"
        f"- Description: {r.get('description','N/A')}\n"
        f"- Priority: {r.get('priority','?')} | State: {r.get('state','?')}\n"
        f"- Created: {r.get('sys_created_on','N/A')}\n"
    )


@mcp.tool()
def create_incident(short_description: str, description: str = "", priority: int = 3) -> str:
    """Create a new ServiceNow incident.

    Args:
        short_description: Brief summary of the issue
        description: Detailed description
        priority: 1=Critical, 2=High, 3=Medium, 4=Low
    """
    payload = {"short_description": short_description, "description": description, "priority": str(priority)}
    resp = _session().post(_url("incident"), json=payload)
    resp.raise_for_status()
    result = resp.json().get("result", {})
    return f"Created **{result.get('number')}** (Priority {priority})"


@mcp.tool()
def update_incident(number: str, updates_json: str) -> str:
    """Update an existing incident.

    Args:
        number: Incident number (e.g., INC0010001)
        updates_json: JSON fields to update (e.g., '{"state": "2", "priority": "1"}')
    """
    resp = _session().get(_url("incident"), params={"sysparm_limit": 1, "sysparm_query": f"number={number}"})
    resp.raise_for_status()
    rows = resp.json().get("result", [])
    if not rows:
        return f"Incident {number} not found."
    updates = json.loads(updates_json)
    resp = _session().put(f"{_url('incident')}/{rows[0]['sys_id']}", json=updates)
    resp.raise_for_status()
    return f"Incident {number} updated."


@mcp.tool()
def add_work_note(number: str, note: str) -> str:
    """Add a work note to an incident.

    Args:
        number: Incident number
        note: Work note text
    """
    return update_incident(number, json.dumps({"work_notes": note}))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"[MCP] ServiceNow MCP on port {port} | Instance: {INSTANCE_URL}")
    mcp.run(transport="sse", host="0.0.0.0", port=port)
