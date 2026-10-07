"""
Salesforce CRM Tools for Enterprise Workspace MCP Server.
Provides full CRUD and SOQL query access to Salesforce Accounts, Opportunities,
Contacts, and Cases, enabling cross-silo workflows across Salesforce + Gong + Workspace.
"""
import json
import logging
import os
import requests
import xml.etree.ElementTree as ET

logger = logging.getLogger("gworkspace-mcp.salesforce")
AUTH_FILE = os.path.expanduser("~/.gemini/sfdc_altostrat_auth.json")


def get_sfdc_session():
    """Load credentials from ~/.gemini/sfdc_altostrat_auth.json and return (session_id, instance_url)."""
    if not os.path.exists(AUTH_FILE):
        raise ValueError("Salesforce credentials not configured at ~/.gemini/sfdc_altostrat_auth.json")

    with open(AUTH_FILE) as f:
        auth = json.load(f)

    if auth.get("session_id"):
        return auth["session_id"], auth["instance_url"]

    username = auth.get("username")
    password = auth.get("password")
    security_token = auth.get("security_token", "")

    url = "https://login.salesforce.com/services/Soap/u/60.0"
    headers = {"Content-Type": "text/xml; charset=UTF-8", "SOAPAction": "login"}
    xml = f"""<?xml version="1.0" encoding="utf-8" ?>
    <env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
      <env:Body>
        <n1:login xmlns:n1="urn:partner.soap.sforce.com">
          <n1:username>{username}</n1:username>
          <n1:password>{password}{security_token}</n1:password>
        </n1:login>
      </env:Body>
    </env:Envelope>"""
    r = requests.post(url, data=xml, headers=headers)
    if r.status_code != 200:
        raise ValueError(f"Salesforce API Login requires Security Token. Click 'Reset My Security Token' in Salesforce Settings.")

    root = ET.fromstring(r.text)
    ns = {"partner": "urn:partner.soap.sforce.com"}
    session_id = root.find(".//partner:sessionId", ns).text
    server_url = root.find(".//partner:serverUrl", ns).text
    instance_url = "/".join(server_url.split("/")[:3])
    return session_id, instance_url


def register_salesforce_tools(mcp):
    """Register Salesforce CRM tools with the MCP server."""

    @mcp.tool()
    def sfdc_query(soql: str) -> str:
        """
        Execute a SOQL query against Salesforce CRM.

        Args:
            soql: SOQL query string (e.g. "SELECT Id, Name, Amount, StageName FROM Opportunity")
        """
        try:
            session_id, instance_url = get_sfdc_session()
            headers = {"Authorization": f"Bearer {session_id}"}
            r = requests.get(
                f"{instance_url}/services/data/v60.0/query",
                headers=headers,
                params={"q": soql}
            )
            r.raise_for_status()
            records = r.json().get("records", [])
            # Clean attributes metadata for readability
            for rec in records:
                rec.pop("attributes", None)
            return f"## Salesforce Query Results ({len(records)} records)\n\n```json\n{json.dumps(records, indent=2)}\n```"
        except Exception as e:
            return f"Salesforce query error: {e}"

    @mcp.tool()
    def sfdc_list_opportunities() -> str:
        """List all Enterprise Opportunities in Salesforce with Stage, Amount, NextStep, and Account Name."""
        soql = "SELECT Id, Name, Account.Name, StageName, Amount, CloseDate, Probability, NextStep, Description FROM Opportunity ORDER BY Amount DESC NULLS LAST LIMIT 25"
        return sfdc_query(soql)

    @mcp.tool()
    def sfdc_update_opportunity(opportunity_id: str, stage_name: str = "", next_step: str = "", amount: float = 0) -> str:
        """
        Update an Opportunity in Salesforce (e.g., advancing StageName or updating NextStep after Deal Desk approval).

        Args:
            opportunity_id: Salesforce Opportunity ID (18 chars)
            stage_name: New StageName (optional, e.g., 'Closed Won', 'Negotiation/Review')
            next_step: Updated NextStep text (optional)
            amount: Updated Amount (optional)
        """
        try:
            session_id, instance_url = get_sfdc_session()
            headers = {"Authorization": f"Bearer {session_id}", "Content-Type": "application/json"}
            payload = {}
            if stage_name:
                payload["StageName"] = stage_name
            if next_step:
                payload["NextStep"] = next_step
            if amount > 0:
                payload["Amount"] = amount
            r = requests.patch(
                f"{instance_url}/services/data/v60.0/sobjects/Opportunity/{opportunity_id}",
                headers=headers,
                json=payload
            )
            r.raise_for_status()
            return f"Successfully updated Salesforce Opportunity `{opportunity_id}` with {json.dumps(payload)}."
        except Exception as e:
            return f"Error updating Opportunity: {e}"

    @mcp.tool()
    def sfdc_create_case(account_id: str, subject: str, description: str, priority: str = "High") -> str:
        """Create a new Support Case in Salesforce linked to an Account."""
        try:
            session_id, instance_url = get_sfdc_session()
            headers = {"Authorization": f"Bearer {session_id}", "Content-Type": "application/json"}
            payload = {
                "AccountId": account_id,
                "Subject": subject,
                "Description": description,
                "Priority": priority,
                "Status": "Working",
                "Origin": "Web"
            }
            r = requests.post(f"{instance_url}/services/data/v60.0/sobjects/Case", headers=headers, json=payload)
            r.raise_for_status()
            return f"Created Salesforce Support Case `{r.json().get('id')}`: **{subject}**"
        except Exception as e:
            return f"Error creating Case: {e}"
