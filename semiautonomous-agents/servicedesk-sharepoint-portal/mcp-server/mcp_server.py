"""
ServiceNow MCP Server with StreamableHTTP transport.
Receives JWT token in Authorization header from Agent Engine.
"""
import os
import json
import logging
import requests
from typing import Optional
from dotenv import load_dotenv
from fastmcp import FastMCP, Context

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_servicenow")

# Initialize FastMCP
mcp = FastMCP("ServiceNow-MCP")

# Configuration
INSTANCE_URL = os.environ.get("SERVICENOW_INSTANCE_URL", "").rstrip("/")


class FallbackSession(requests.Session):
    """
    Custom session that falls back to Basic Auth if JWT fails.
    This ensures the UI doesn't break during OIDC configuration issues.
    """

    def request(self, method, url, **kwargs):
        resp = super().request(method, url, **kwargs)

        # If 401 with Bearer token, try Basic Auth fallback
        if resp.status_code == 401 and "Bearer" in self.headers.get("Authorization", ""):
            logger.warning("[MCP] JWT auth failed (401). Trying Basic Auth fallback...")
            self.headers.pop("Authorization", None)

            fallback_user = os.environ.get("SERVICENOW_BASIC_AUTH_USER")
            fallback_pass = os.environ.get("SERVICENOW_BASIC_AUTH_PASS")

            if fallback_user and fallback_pass:
                self.auth = (fallback_user, fallback_pass)
                resp = super().request(method, url, **kwargs)
                if resp.ok:
                    logger.info("[MCP] Basic Auth fallback succeeded")

        return resp


def _extract_token_from_context(ctx: Context) -> Optional[str]:
    """
    Extract JWT token from the request context headers.
    The Agent Engine passes the user JWT via X-User-Token header
    (Authorization is used for Cloud Run service-to-service auth).
    """
    headers = None

    # Try to get headers from request context's request object (Starlette Request)
    if ctx and hasattr(ctx, "request_context") and ctx.request_context:
        request = getattr(ctx.request_context, "request", None)
        if request and hasattr(request, "headers"):
            headers = request.headers
            logger.info(f"[MCP] Got headers from request_context.request")

    # Fallback: try get_http_request from FastMCP dependencies
    if headers is None:
        try:
            from fastmcp.server.dependencies import get_http_request
            http_request = get_http_request()
            headers = http_request.headers
            logger.info(f"[MCP] Got headers from get_http_request()")
        except Exception as e:
            logger.warning(f"[MCP] Could not get HTTP request: {e}")

    if headers is None:
        logger.warning("[MCP] No headers available in context")
        return None

    # First try X-User-Token (for Cloud Run deployments)
    user_token = headers.get("x-user-token") or headers.get("X-User-Token")
    if user_token and user_token.startswith("eyJ"):
        logger.info(f"[MCP] Found user JWT in X-User-Token (length: {len(user_token)})")
        return user_token

    # Fallback to Authorization header (for local testing)
    auth_header = headers.get("authorization") or headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
        # Only use if it's a user JWT (starts with eyJ), not a Cloud Run ID token
        if token.startswith("eyJ"):
            logger.info(f"[MCP] Found user JWT in Authorization (length: {len(token)})")
            return token

    logger.warning("[MCP] No user JWT found in headers")
    return None


def _get_session(auth_token: Optional[str] = None) -> requests.Session:
    """
    Create authenticated session for ServiceNow API calls.
    """
    if not INSTANCE_URL:
        raise ValueError("SERVICENOW_INSTANCE_URL is not configured")

    session = FallbackSession()
    session.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json"
    })

    if auth_token:
        # Log JWT claims for debugging (without verification)
        try:
            import base64
            # Decode payload (second part of JWT)
            payload = auth_token.split(".")[1]
            # Add padding if needed
            payload += "=" * (4 - len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            logger.info(f"[MCP] JWT subject: {decoded.get('sub', 'N/A')}")
            logger.info(f"[MCP] JWT upn: {decoded.get('upn', decoded.get('preferred_username', 'N/A'))}")
        except Exception as e:
            logger.debug(f"[MCP] Could not decode JWT for logging: {e}")

        session.headers.update({"Authorization": f"Bearer {auth_token}"})
        logger.info("[MCP] Using JWT Bearer authentication")
        return session

    # Fallback to Basic Auth if no token
    fallback_user = os.environ.get("SERVICENOW_BASIC_AUTH_USER")
    fallback_pass = os.environ.get("SERVICENOW_BASIC_AUTH_PASS")

    if fallback_user and fallback_pass:
        session.auth = (fallback_user, fallback_pass)
        logger.info("[MCP] Using Basic Auth (no JWT provided)")
        return session

    raise ValueError("No authentication credentials available")


def _get_api_url(table_name: str) -> str:
    """Build ServiceNow Table API URL."""
    return f"{INSTANCE_URL}/api/now/table/{table_name}"


# ============================================================
# MCP TOOLS
# ============================================================

@mcp.tool()
def query_table(
    table_name: str,
    query: str = "",
    limit: int = 50,
    offset: int = 0,
    ctx: Context = None
) -> str:
    """
    Query any ServiceNow table with optional filters.

    Args:
        table_name: Table name (e.g., 'incident', 'problem', 'change_request')
        query: Encoded query string (e.g., 'active=true^priority=1')
        limit: Maximum records to return (default 50)
        offset: Starting offset for pagination
    """
    logger.info(f"[MCP] query_table: {table_name}, query='{query}', limit={limit}")

    try:
        token = _extract_token_from_context(ctx)
        session = _get_session(token)

        params = {
            "sysparm_limit": limit,
            "sysparm_offset": offset,
            "sysparm_query": query if query else "ORDERBYDESCsys_created_on"
        }

        response = session.get(_get_api_url(table_name), params=params)
        response.raise_for_status()

        results = response.json().get("result", [])

        if not results:
            return f"No records found in '{table_name}'"

        # Format as Markdown table
        output = f"### {table_name} ({len(results)} records)\n\n"
        output += "| Number | Description | State | Created |\n"
        output += "|--------|-------------|-------|--------|\n"

        for item in results:
            num = item.get("number", item.get("sys_id", "N/A"))[:15]
            desc = (item.get("short_description") or item.get("description") or "N/A")[:40]
            state = item.get("state", "N/A")
            created = item.get("sys_created_on", "N/A")[:10]
            output += f"| {num} | {desc} | {state} | {created} |\n"

        return output

    except Exception as e:
        logger.error(f"[MCP] query_table error: {e}")
        return f"Error querying {table_name}: {str(e)}"


@mcp.tool()
def list_incidents(
    limit: int = 20,
    state: Optional[str] = None,
    ctx: Context = None
) -> str:
    """
    List incidents with optional state filter.

    Args:
        limit: Maximum incidents to return
        state: Filter by state (1=New, 2=In Progress, 3=On Hold, 6=Resolved, 7=Closed)
    """
    query = "ORDERBYDESCsys_created_on"
    if state:
        query = f"state={state}^{query}"
    return query_table("incident", query=query, limit=limit, ctx=ctx)


@mcp.tool()
def search_incidents(
    search_term: str,
    limit: int = 10,
    ctx: Context = None
) -> str:
    """
    Search incidents by description or short description.

    Args:
        search_term: Text to search for
        limit: Maximum results
    """
    query = f"short_descriptionLIKE{search_term}^ORdescriptionLIKE{search_term}^ORDERBYDESCsys_created_on"
    return query_table("incident", query=query, limit=limit, ctx=ctx)


@mcp.tool()
def get_ticket(
    number: str,
    ctx: Context = None
) -> str:
    """
    Get a specific ticket by its number (e.g., INC0010001, PRB0040001).

    Args:
        number: Ticket number (e.g., INC0010001)
    """
    prefix = number[:3].upper()
    table_map = {
        "INC": "incident",
        "PRB": "problem",
        "CHG": "change_request",
        "SCT": "sc_task",
        "RIT": "sc_req_item"
    }
    table = table_map.get(prefix, "task")
    return query_table(table, query=f"number={number}", limit=1, ctx=ctx)


@mcp.tool()
def create_ticket(
    table_name: str,
    short_description: str,
    description: str = "",
    priority: int = 3,
    ctx: Context = None
) -> str:
    """
    Create a new ticket in ServiceNow.

    Args:
        table_name: Table name (e.g., 'incident', 'problem')
        short_description: Brief summary of the issue
        description: Detailed description
        priority: Priority level (1=Critical, 2=High, 3=Medium, 4=Low)
    """
    logger.info(f"[MCP] create_ticket: {table_name}")

    try:
        token = _extract_token_from_context(ctx)
        session = _get_session(token)

        payload = {
            "short_description": short_description,
            "description": description,
            "priority": str(priority)
        }

        response = session.post(_get_api_url(table_name), json=payload)
        response.raise_for_status()

        result = response.json().get("result", {})
        return f"Created {table_name} successfully!\n\n**Number:** {result.get('number')}\n**Sys ID:** `{result.get('sys_id')}`"

    except Exception as e:
        logger.error(f"[MCP] create_ticket error: {e}")
        return f"Error creating ticket: {str(e)}"


@mcp.tool()
def update_ticket(
    table_name: str,
    sys_id: str,
    updates: str,
    ctx: Context = None
) -> str:
    """
    Update an existing ticket.

    Args:
        table_name: Table name (e.g., 'incident')
        sys_id: System ID of the record
        updates: JSON string of fields to update (e.g., '{"state": "2", "priority": "2"}')
    """
    logger.info(f"[MCP] update_ticket: {table_name}/{sys_id}")

    try:
        token = _extract_token_from_context(ctx)
        session = _get_session(token)

        payload = json.loads(updates)
        url = f"{_get_api_url(table_name)}/{sys_id}"

        response = session.put(url, json=payload)
        response.raise_for_status()

        return f"Updated {table_name} `{sys_id}` successfully!"

    except json.JSONDecodeError:
        return "Error: updates must be a valid JSON string"
    except Exception as e:
        logger.error(f"[MCP] update_ticket error: {e}")
        return f"Error updating ticket: {str(e)}"


@mcp.tool()
def add_comment(
    table_name: str,
    sys_id: str,
    comment: str,
    work_note: bool = False,
    ctx: Context = None
) -> str:
    """
    Add a comment or work note to a ticket.

    Args:
        table_name: Table name (e.g., 'incident')
        sys_id: System ID of the record
        comment: Comment text
        work_note: If True, add as internal work note instead of customer-visible comment
    """
    field = "work_notes" if work_note else "comments"
    updates = json.dumps({field: comment})
    return update_ticket(table_name, sys_id, updates, ctx=ctx)


@mcp.tool()
def list_problems(limit: int = 20, ctx: Context = None) -> str:
    """List problem records."""
    return query_table("problem", limit=limit, ctx=ctx)


@mcp.tool()
def list_changes(limit: int = 20, ctx: Context = None) -> str:
    """List change request records."""
    return query_table("change_request", limit=limit, ctx=ctx)


# ============================================================
# SERVER ENTRY POINT
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    transport = os.environ.get("MCP_TRANSPORT", "sse")

    logger.info(f"[MCP] Starting ServiceNow MCP Server")
    logger.info(f"[MCP] Instance URL: {INSTANCE_URL}")
    logger.info(f"[MCP] Transport: {transport}")
    logger.info(f"[MCP] Port: {port}")

    # Run with SSE transport for Agent Engine compatibility
    mcp.run(
        transport=transport,
        host="0.0.0.0",
        port=port
    )
