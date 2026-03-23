import os
import json
import logging
import requests
from typing import List, Optional, Any
from fastmcp import FastMCP

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_server_servicenow")

mcp = FastMCP("ServiceNow-MCP")

# Environment Variables
INSTANCE_URL = os.environ.get("SERVICENOW_INSTANCE_URL")
# OAuth JWT Bearer Flow
USER_ID_TOKEN = os.environ.get("USER_ID_TOKEN")
USER_TOKEN = os.environ.get("USER_TOKEN")

def _get_session() -> requests.Session:
    """
    Returns an authenticated requests session using the True JWT Bearer Flow.
    The USER_ID_TOKEN provided by Microsoft Entra ID is passed directly to ServiceNow as a Bearer token.
    ServiceNow validates this JWT using the configured OIDC provider and maps the 'upn' claim to a sys_user record.
    """
    if not INSTANCE_URL:
        raise ValueError("SERVICENOW_INSTANCE_URL is not set.")
        
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
    
    auth_token = USER_ID_TOKEN or USER_TOKEN
    
    # Debug: Print the decoded JWT payload without verification
    if auth_token:
        try:
            import jwt
            decoded = jwt.decode(auth_token, options={"verify_signature": False})
            logger.info(f"[ServiceNow MCP] JWT Payload keys: {list(decoded.keys())}")
            logger.info(f"[ServiceNow MCP] JWT Audience: {decoded.get('aud')}")
            logger.info(f"[ServiceNow MCP] JWT UPN/Email/preferred_username: {decoded.get('upn')} / {decoded.get('email')} / {decoded.get('preferred_username')}")
        except Exception as e:
            logger.error(f"[ServiceNow MCP] Failed to decode JWT: {e}")

    if auth_token:
        logger.info("[ServiceNow MCP] User OIDC JWT Bearer token detected. Bypassing OIDC mapping for developer instance and forcing Basic Auth.")
        # Determine fallback basic auth from environment if mapping fails:
        fallback_user = os.environ.get("SERVICENOW_BASIC_AUTH_USER")
        fallback_pass = os.environ.get("SERVICENOW_BASIC_AUTH_PASS")
        if fallback_user and fallback_pass:
            session.auth = (fallback_user, fallback_pass) 
            return session
        else:
            raise ValueError("SERVICENOW_BASIC_AUTH_USER and SERVICENOW_BASIC_AUTH_PASS must be set for fallback auth.")
        
    logger.error("No valid ServiceNow Authentication credentials mapped. Access Denied.")
    raise ValueError("Access Denied: ServiceNow requires a valid OIDC Token.")

def _get_api_url(table_name: str) -> str:
    """Builds the full Table API URL."""
    base_url = INSTANCE_URL.rstrip("/")
    return f"{base_url}/api/now/table/{table_name}"


# --- GENERIC TABLE API ---

@mcp.tool()
def query_table(table_name: str, query: str = "", limit: int = 10, offset: int = 0) -> str:
    """
    Generic wrapper tool to query any ServiceNow table. Use with standard tables 
    like 'incident', 'problem', 'change_request', 'sc_task', 'sc_req_item'.
    
    Args:
        table_name: Name of the ServiceNow table to query.
        query: Encoded ServiceNow query (e.g., 'active=true^priority=1').
        limit: Max number of records to return (default 10).
        offset: Pagination offset.
    """
    logger.info(f"[ServiceNow MCP] query_table | table={table_name}, query='{query}'")
    try:
        session = _get_session()
        url = _get_api_url(table_name)
        
        params = {
            "sysparm_limit": limit,
            "sysparm_offset": offset,
            "sysparm_query": query if query else "sys_created_on=DESC"
        }
        
        response = session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("result", [])
        
        if not results:
            return f"No records found in table '{table_name}'."
            
        output = f"### ServiceNow Table: {table_name} (Limit: {limit})\n\n"
        
        # Determine standard display fields based on common tables
        for item in results:
            nr = item.get('number', item.get('sys_id'))
            desc = item.get('short_description', item.get('description', 'N/A'))
            output += f"- **{nr}** (SysID: `{item.get('sys_id')}`)\n"
            output += f"  - **Description**: {desc}\n"
            if 'state' in item:
                 output += f"  - **State**: {item.get('state')}\n"
            output += "\n"
            
        return output
        
    except Exception as e:
        logger.error(f"[ServiceNow MCP] query_table FAILED for {table_name}: {str(e)}")
        return f"Error querying table {table_name}: {str(e)}"


# --- SPECIFIC TICKET HELPERS ---

@mcp.tool()
def list_incidents(limit: int = 10, offset: int = 0, state: Optional[str] = None) -> str:
    """Lists incidents matching state rules (Pagination supported)."""
    q = "ORDERBYDESCsys_created_on"
    if state:
        q = f"state={state}^{q}"
    return query_table("incident", query=q, limit=limit, offset=offset)

@mcp.tool()
def search_incidents(search_term: str, limit: int = 10) -> str:
    """
    Searches for incidents containing a specific text string (search_term) in their short_description or description.
    Use this tool when the user asks to find a ticket related to a specific topic, keyword, or name.
    """
    logger.info(f"[ServiceNow MCP] search_incidents | term='{search_term}'")
    query = f"short_descriptionLIKE{search_term}^ORdescriptionLIKE{search_term}^ORDERBYDESCsys_created_on"
    return query_table("incident", query=query, limit=limit)

@mcp.tool()
def list_problems(limit: int = 10, offset: int = 0, state: Optional[str] = None) -> str:
    """Lists Problems board items."""
    q = "ORDERBYDESCsys_created_on"
    if state:
        q = f"state={state}^{q}"
    return query_table("problem", query=q, limit=limit, offset=offset)

@mcp.tool()
def list_changes(limit: int = 10, offset: int = 0, state: Optional[str] = None) -> str:
    """Lists Change Request items."""
    q = "ORDERBYDESCsys_created_on"
    if state:
        q = f"state={state}^{q}"
    return query_table("change_request", query=q, limit=limit, offset=offset)

@mcp.tool()
def list_catalog_tasks(limit: int = 10, offset: int = 0, state: Optional[str] = None) -> str:
    """Lists Catalog Tasks (sc_task)."""
    q = "ORDERBYDESCsys_created_on"
    if state:
        q = f"state={state}^{q}"
    return query_table("sc_task", query=q, limit=limit, offset=offset)


@mcp.tool()
def create_ticket(table_name: str, payload_json: str) -> str:
    """
    Generic tool to create a record in any ServiceNow table (incident, problem, change_request, tasks).
    
    Args:
        table_name: Target table (e.g., 'incident')
        payload_json: Stringified JSON of properties (e.g., '{"short_description": "Issue", "priority": "3"}')
    """
    logger.info(f"[ServiceNow MCP] create_ticket | Table: {table_name}")
    try:
        session = _get_session()
        url = _get_api_url(table_name)
        
        body = json.loads(payload_json)
        response = session.post(url, json=body)
        response.raise_for_status()
        
        result = response.json().get("result", {})
        return f"✅ Record created successfully in '{table_name}'!\n\n**Number**: {result.get('number')}\n**Sys ID**: `{result.get('sys_id')}`"
        
    except Exception as e:
        logger.error(f"[ServiceNow MCP] create_ticket FAILED for {table_name}: {str(e)}")
        return f"Error creating record: {str(e)}"

@mcp.tool()
def update_ticket(table_name: str, sys_id: str, updates_json: str) -> str:
    """
    Generic tool to update a ticket status or metadata inside any ServiceNow table.
    
    Args:
        table_name: Target table (e.g., 'incident')
        sys_id: 32-character sys_id inside table
        updates_json: Stringified JSON of updates (e.g., '{"state": "2"}')
    """
    logger.info(f"[ServiceNow MCP] update_ticket | Table: {table_name} | SysID: {sys_id}")
    try:
        session = _get_session()
        url = f"{_get_api_url(table_name)}/{sys_id}"
        
        body = json.loads(updates_json)
        response = session.put(url, json=body)
        response.raise_for_status()
        
        return f"✅ Record {sys_id} inside '{table_name}' updated successfully."
        
    except Exception as e:
        logger.error(f"[ServiceNow MCP] update_ticket FAILED for {table_name}: {str(e)}")
        return f"Error updating record: {str(e)}"

# --- ADVANCED CAPABILITIES ---

@mcp.tool()
def get_ticket(number: str) -> str:
    """ Retrieves a ticket exactly by its unique number (e.g. INC0000601, PRB0000001). """
    logger.info(f"[ServiceNow MCP] get_ticket | number={number}")
    prefix = number[:3].upper()
    table_map = {"INC": "incident", "PRB": "problem", "CHG": "change_request", "SCT": "sc_task", "RIT": "sc_req_item"}
    table = table_map.get(prefix, "task")
    return query_table(table, query=f"number={number}", limit=1)

@mcp.tool()
def delete_ticket(table_name: str, sys_id: str) -> str:
    """ Deletes a record from a table. Fails if the user lacks ACL permissions. """
    logger.info(f"[ServiceNow MCP] delete_ticket | table={table_name} id={sys_id}")
    try:
        session = _get_session()
        url = f"{_get_api_url(table_name)}/{sys_id}"
        resp = session.delete(url)
        resp.raise_for_status()
        return f"✅ '{table_name}' record {sys_id} deleted successfully."
    except Exception as e:
        return f"Error deleting record (might be an ACL block): {str(e)}"

@mcp.tool()
def add_comment(table_name: str, sys_id: str, text: str, is_internal_work_note: bool = False) -> str:
    """ Appends text to either 'comments' (customer visible) or 'work_notes' (internal IT visible) on a ticket. """
    logger.info(f"[ServiceNow MCP] add_comment | table={table_name} id={sys_id}")
    field = "work_notes" if is_internal_work_note else "comments"
    return update_ticket(table_name, sys_id, json.dumps({field: text}))

@mcp.tool()
def list_attachments(table_name: str, sys_id: str) -> str:
    """ Lists all file attachments associated with a specific record. """
    logger.info(f"[ServiceNow MCP] list_attachments | {table_name} {sys_id}")
    try:
        session = _get_session()
        url = f"{INSTANCE_URL.rstrip('/')}/api/now/attachment"
        params = {"sysparm_query": f"table_name={table_name}^table_sys_id={sys_id}"}
        resp = session.get(url, params=params)
        resp.raise_for_status()
        results = resp.json().get("result", [])
        if not results: return "No attachments found."
        return "\n".join([f"- **{f.get('file_name')}** ({f.get('content_type')}) [ID: {f.get('sys_id')}]" for f in results])
    except Exception as e:
        return f"Error listing attachments: {str(e)}"

@mcp.tool()
def upload_text_attachment(table_name: str, sys_id: str, file_name: str, content: str) -> str:
    """ Uploads raw text content as a .txt or .md file attachment to a ticket. """
    logger.info(f"[ServiceNow MCP] upload_text_attachment | {file_name}")
    try:
        session = _get_session()
        url = f"{INSTANCE_URL.rstrip('/')}/api/now/attachment/file"
        params = {"table_name": table_name, "table_sys_id": sys_id, "file_name": file_name}
        headers = {"Content-Type": "text/plain"}
        # Overlay session headers with the text injection
        full_headers = {**session.headers, **headers}
        resp = session.post(url, params=params, headers=full_headers, data=content.encode("utf-8"))
        resp.raise_for_status()
        return f"✅ Attachment {file_name} uploaded successfully."
    except Exception as e:
        return f"Error uploading attachment: {str(e)}"

@mcp.tool()
def submit_catalog_item(catalog_item_sys_id: str, quantity: int = 1, variables_json: str = "{}") -> str:
    """ Submits a formal Service Catalog request via the 'order_now' Cart API. """
    logger.info(f"[ServiceNow MCP] submit_catalog_item | Item ID: {catalog_item_sys_id}")
    try:
        session = _get_session()
        url = f"{INSTANCE_URL.rstrip('/')}/api/sn_sc/servicecatalog/items/{catalog_item_sys_id}/order_now"
        payload = {"sysparm_quantity": quantity, "variables": json.loads(variables_json)}
        resp = session.post(url, json=payload)
        resp.raise_for_status()
        res = resp.json().get("result", {})
        return f"✅ Catalog Item Ordered!\nRequest Number: {res.get('request_number')}\nRequest SysID: `{res.get('request_id')}`"
    except Exception as e:
        return f"Error submitting catalog item: {str(e)}"

@mcp.tool()
def search_service_requests(search_term: str, limit: int = 10) -> str:
    """
    Searches for Service Requests (Requested Items - RITM) containing text in their short_description or description.
    Use this when the user asks for the status or list of their requests or order items starting with 'RITM'.
    """
    logger.info(f"[ServiceNow MCP] search_service_requests | term='{search_term}'")
    query = f"short_descriptionLIKE{search_term}^ORdescriptionLIKE{search_term}^ORDERBYDESCsys_created_on"
    return query_table("sc_req_item", query=query, limit=limit)

@mcp.tool()
def close_incident(sys_id: str, close_code: str, close_notes: str) -> str:
    """
    Closes an incident correctly by providing mandatory resolution fields in ServiceNow.
    Required args: close_code (e.g., 'Solved (Work Around)', 'Solved (Permanently)') and close_notes.
    State 7 = Closed.
    """
    logger.info(f"[ServiceNow MCP] close_incident | sys_id={sys_id}")
    payload = {
        "state": "7", 
        "close_code": close_code,
        "close_notes": close_notes
    }
    return update_ticket("incident", sys_id, json.dumps(payload))

@mcp.tool()
def search_catalog_items(search_term: str, limit: int = 10) -> str:
    """
    Searches for items in the Service Catalog (sc_cat_item) setup (e.g., 'Laptop', 'iPad', 'Software').
    Use this to find the Catalog Item SysID before ordering via submit_catalog_item.
    """
    logger.info(f"[ServiceNow MCP] search_catalog_items | term='{search_term}'")
    query = f"nameLIKE{search_term}^ORshort_descriptionLIKE{search_term}"
    return query_table("sc_cat_item", query=query, limit=limit)

if __name__ == "__main__":
    mcp.run()
