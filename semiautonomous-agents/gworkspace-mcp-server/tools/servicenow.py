"""
ServiceNow ITSM & HR Service Delivery Tools for Enterprise MCP Server.
Supports Incident Management (INC), Hardware/Software Catalog Requests (REQ/RITM),
CMDB Configuration Items (CI), and Ticket Approval Workflows.
"""
import json
import logging
import os
import requests

logger = logging.getLogger("gworkspace-mcp.servicenow")
AUTH_FILE = os.path.expanduser("~/.gemini/servicenow_altostrat_auth.json")


def get_sn_headers():
    """Load ServiceNow credentials and exchange for an OAuth 2.0 Bearer Token."""
    if not os.path.exists(AUTH_FILE):
        raise ValueError("ServiceNow credentials not found at ~/.gemini/servicenow_altostrat_auth.json")
    with open(AUTH_FILE) as f:
        cfg = json.load(f)
    base_url = cfg["instance_url"].rstrip("/")
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if cfg.get("client_id") and cfg.get("client_secret"):
        r_oauth = requests.post(f"{base_url}/oauth_token.do", data={
            "grant_type": "password",
            "client_id": cfg["client_id"],
            "client_secret": cfg["client_secret"],
            "username": cfg["username"],
            "password": cfg["password"]
        })
        r_oauth.raise_for_status()
        token = r_oauth.json()["access_token"]
        headers["Authorization"] = f"Bearer {token}"
        return base_url, headers, None
    return base_url, headers, (cfg["username"], cfg["password"])


def register_servicenow_tools(mcp):
    """Register ServiceNow ITSM/HR tools with the MCP server."""

    @mcp.tool()
    def servicenow_list_incidents(limit: int = 15, query: str = "") -> str:
        """
        List ServiceNow Incidents (ITSM / HR escalations).

        Args:
            limit: Max incidents to return (default 15)
            query: Optional sysparm_query filter (e.g. "priority=1^ORshort_descriptionLIKEMotorola")
        """
        try:
            base_url, headers, auth = get_sn_headers()
            params = {
                "sysparm_limit": limit,
                "sysparm_fields": "number,short_description,description,priority,state,category,assigned_to,sys_created_on,sys_id"
            }
            if query:
                params["sysparm_query"] = f"{query}^ORDERBYDESCsys_created_on"
            else:
                params["sysparm_query"] = "ORDERBYDESCsys_created_on"
            r = requests.get(f"{base_url}/api/now/table/incident", auth=auth, params=params, headers=headers)
            r.raise_for_status()
            records = r.json().get("result", [])
            return f"## ServiceNow Incidents ({len(records)} found)\n\n```json\n{json.dumps(records, indent=2)}\n```"
        except Exception as e:
            return f"ServiceNow API error: {e}"

    @mcp.tool()
    def servicenow_create_incident(
        short_description: str,
        description: str,
        urgency: str = "1",
        impact: str = "1",
        category: str = "hardware",
        comments: str = ""
    ) -> str:
        """
        Create a new ServiceNow Incident ticket and return the INC number (Apoorva & Priyanka use case).

        Args:
            short_description: Summary title of the ticket
            description: Detailed problem or HR/IT request description
            urgency: 1 (High), 2 (Medium), 3 (Low)
            impact: 1 (High), 2 (Medium), 3 (Low)
            category: software, hardware, network, inquiry, hr_policy
            comments: Additional work notes or requester context
        """
        try:
            base_url, headers, auth = get_sn_headers()
            payload = {
                "short_description": short_description,
                "description": description,
                "urgency": urgency,
                "impact": impact,
                "category": category,
                "comments": comments
            }
            r = requests.post(
                f"{base_url}/api/now/table/incident",
                auth=auth,
                json=payload,
                headers=headers
            )
            r.raise_for_status()
            res = r.json().get("result", {})
            return (
                f"✅ ServiceNow Ticket Created Successfully!\n\n"
                f"- **Incident Number:** `{res.get('number')}`\n"
                f"- **Sys ID:** `{res.get('sys_id')}`\n"
                f"- **Short Description:** {res.get('short_description')}\n"
                f"- **Priority:** {res.get('priority')}\n"
                f"- **Link:** {base_url}/nav_to.do?uri=incident.do?sys_id={res.get('sys_id')}"
            )
        except Exception as e:
            return f"Error creating ServiceNow incident: {e}"

    @mcp.tool()
    def servicenow_update_incident(
        incident_number_or_sys_id: str,
        state: str = "",
        comments: str = "",
        close_notes: str = "",
        close_code: str = "Solved (Work Around)"
    ) -> str:
        """
        Update, add comments to, or resolve/close a ServiceNow ticket (Apoorva interactive workflow).

        Args:
            incident_number_or_sys_id: INC number (e.g. INC0010001) or sys_id
            state: 1 (New), 2 (In Progress), 6 (Resolved), 7 (Closed)
            comments: Customer-visible comment or approval note to add
            close_notes: Resolution notes (required if state is 6 or 7)
            close_code: Resolution code (default 'Solved (Work Around)')
        """
        try:
            base_url, headers, auth = get_sn_headers()
            # Resolve sys_id if INC number was passed
            sys_id = incident_number_or_sys_id
            if incident_number_or_sys_id.upper().startswith("INC"):
                q_res = requests.get(
                    f"{base_url}/api/now/table/incident",
                    auth=auth,
                    params={"sysparm_query": f"number={incident_number_or_sys_id.upper()}", "sysparm_limit": 1},
                    headers=headers
                ).json().get("result", [])
                if not q_res:
                    return f"Incident {incident_number_or_sys_id} not found."
                sys_id = q_res[0]["sys_id"]

            payload = {}
            if state:
                payload["state"] = state
            if comments:
                payload["comments"] = comments
            if close_notes:
                payload["close_notes"] = close_notes
                payload["close_code"] = close_code

            r = requests.patch(
                f"{base_url}/api/now/table/incident/{sys_id}",
                auth=auth,
                json=payload,
                headers=headers
            )
            r.raise_for_status()
            res = r.json().get("result", {})
            return f"✅ Updated ServiceNow Ticket `{res.get('number')}` (State: {res.get('state')})."
        except Exception as e:
            return f"Error updating ServiceNow incident: {e}"
