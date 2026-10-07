import json
import os
import time
from google import genai
from mcp_connectors import gather_all_mcp_context

PROJECT_ID = "vtxdemos"
LOCATION = "global"
MODEL_NAME = "gemini-3.8-flash"


def build_a2ui_v09_payload(query_text: str, mcp_data: dict, markdown_summary: str) -> dict:
  """Constructs a standards-compliant A2UI v0.9 JSON payload (application/vnd.a2ui+json)."""
  sfdc_rec = (mcp_data.get("salesforce", {}).get("records") or [{}])[0]
  snow_rec = (mcp_data.get("servicenow", {}).get("records") or [{}])[0]
  drive_doc = mcp_data.get("google_drive", {}).get("document", {})

  inc_num = snow_rec.get("number", "INC0010007")
  inc_prio = snow_rec.get("priority", "1")
  inc_desc = snow_rec.get("short_description", "Active Operational Incident")
  sfdc_id = sfdc_rec.get("Id", "006jV000001CIWrQAO")
  sfdc_name = sfdc_rec.get("Name", "Miami-Dade Dispatch Center ASTRO 25 Renewal")
  sfdc_amount = sfdc_rec.get("Amount", 1950000.0)
  sfdc_stage = sfdc_rec.get("StageName", "Negotiation/Review")
  sfdc_close = sfdc_rec.get("CloseDate", "2026-10-15")
  drive_title = drive_doc.get("title", "Motorola Enterprise Policy & Playbook")
  drive_rules = drive_doc.get("rules", [])

  # Determine scenario-specific A2UI action button & work note
  q_lower = query_text.lower()
  if "precision" in q_lower or "redline" in q_lower or "inc0010006" in q_lower:
    action_label = "Approve Legal Redline Counter-Proposal (Enforce Net-60 & 2.0x Cap)"
    action_note = (
        f"[A2UI Executive Action] Legal & Global Procurement counter-proposal"
        f" approved per {drive_title}. Rejected Net-15 & 0.5x cap; enforced"
        f" Mandatory Net-60 payment terms (or 4.5% early-pay discount) and 2.0x"
        f" TCV Liability Cap on {sfdc_id}."
    )
    badge_text = "LEGAL & PROCUREMENT REDLINE EXCEPTION"
    recommended_action_kpi = "Enforce Mandatory Net-60 & 2.0x Cap"
  elif "tariff" in q_lower or "hts" in q_lower or "inc0010004" in q_lower:
    action_label = "Enforce HTS 8525.60.1050 (7.5% Duty) & Release Customs Hold"
    action_note = (
        f"[A2UI Executive Action] Trade Compliance ruling enforced per"
        f" {drive_title}. Classified Base Station RF Transceivers under HTS"
        f" 8525.60.1050 (7.5% MFN Duty). Customs hold cleared for {sfdc_id}."
    )
    badge_text = "CUSTOMS & TRADE COMPLIANCE HOLD"
    recommended_action_kpi = "Enforce HTS 8525.60.1050 (7.5% Duty)"
  elif "cdmg" in q_lower or "apex" in q_lower or "inc0010003" in q_lower:
    action_label = "Approve CDMG Global Ultimate Hierarchy Link (DUNS 04-882-1904)"
    action_note = (
        f"[A2UI Executive Action] CDMG Data Governance hierarchy override"
        f" approved for Apex Global ({sfdc_id}). Linked to Global Ultimate"
        f" Parent DUNS 04-882-1904 per 2026 CDMG Stewardship Standard."
    )
    badge_text = "CDMG MASTER DATA GOVERNANCE REVIEW"
    recommended_action_kpi = "Approve Global Ultimate DUNS Link"
  elif "apx" in q_lower or "export" in q_lower or "inc0010005" in q_lower:
    action_label = "Authorize FIPS 140-3 AES-256 Hand-Carry Export License (TMP)"
    action_note = (
        f"[A2UI Executive Action] Joint HR/IT & Export Compliance authorization"
        f" granted for 4 AES-256 encrypted APX NEXT smart radios for APCO 2026"
        f" Summit under License Exception TMP."
    )
    badge_text = "EXPORT CONTROL & FIPS 140-3 CLEARANCE"
    recommended_action_kpi = "Grant Temporary Export License (TMP)"
  else:
    action_label = "Authorize 20% Executive Retention Discount & Dispatch APX NEXT Failover Proposal"
    action_note = (
        f"[A2UI Executive Action] Authorized 20% Executive Override Retention"
        f" Discount on {sfdc_id} (${sfdc_amount:,.2f}) per ASTRO 25 Playbook."
        f" Bundled APX NEXT Smart Radios (LTE/Wi-Fi failover) to mitigate"
        f" repeater packet loss ({inc_num})."
    )
    badge_text = f"PRIORITY-{inc_prio} ACTIVE OUTAGE | RENEWAL RISK DETECTED"
    recommended_action_kpi = "20% Retention Override + APX NEXT Bundle"

  return {
      "a2ui_version": "0.9",
      "extension_uri": "https://a2ui.org/a2a-extension/a2ui/v0.9",
      "surface": {
          "id": "motorola_enterprise_command_surface",
          "title": f"Motorola Solutions — Cross-Silo A2UI Action Surface ({inc_num})",
          "status_badge": badge_text,
          "telemetry": {
              "parallel_mcp_latency_ms": mcp_data.get("parallel_execution_ms", 0),
              "connectors_queried": ["Salesforce CRM", "ServiceNow ITSM", "Google Drive Policy Engine"],
              "model": MODEL_NAME,
          },
          "components": [
              {
                  "type": "kpi_grid",
                  "id": "account_360_kpis",
                  "items": [
                      {
                          "label": "SALESFORCE CONTRACT VALUE",
                          "value": f"${sfdc_amount:,.2f}",
                          "subtext": f"ID: {sfdc_id} | Stage: {sfdc_stage}",
                          "source_url": sfdc_rec.get("Url", "#"),
                      },
                      {
                          "label": "SERVICENOW TICKET STATUS",
                          "value": f"{inc_num} (Priority {inc_prio})",
                          "subtext": inc_desc[:62] + ("..." if len(inc_desc) > 62 else ""),
                          "source_url": f"https://dev271596.service-now.com/nav_to.do?uri=incident_list.do?sysparm_query=number={inc_num}",
                      },
                      {
                          "label": "GOVERNANCE / PLAYBOOK RULE",
                          "value": recommended_action_kpi,
                          "subtext": drive_title[:58] + "...",
                          "source_url": drive_doc.get("url", "#"),
                      },
                      {
                          "label": "TARGET CLOSE / SLA DATE",
                          "value": sfdc_close,
                          "subtext": "Cross-Silo Verified via Parallel MCP",
                          "source_url": sfdc_rec.get("Url", "#"),
                      },
                  ],
              },
              {
                  "type": "reconciliation_matrix",
                  "id": "cross_silo_reconciliation",
                  "title": "Cross-Silo Enterprise Reconciliation Matrix",
                  "columns": ["Enterprise Silo", "Record / Document ID", "Live Status / Finding", "Mandatory Policy / Action"],
                  "rows": [
                      [
                          "Salesforce CRM",
                          sfdc_id,
                          f"{sfdc_name} (${sfdc_amount:,.2f} — {sfdc_stage})",
                          f"Protect renewal close on {sfdc_close}",
                      ],
                      [
                          "ServiceNow ITSM",
                          inc_num,
                          inc_desc,
                          f"Priority {inc_prio} Escalation — Immediate Mitigation Required",
                      ],
                      [
                          "Google Drive Policy",
                          drive_doc.get("file_id", "")[:16] + "...",
                          drive_title,
                          drive_rules[0] if drive_rules else "Standard Motorola Compliance Rule",
                      ],
                  ],
              },
              {
                  "type": "interactive_action_card",
                  "id": "servicenow_writeback_action",
                  "title": "1-Click Autonomous Remediation & Write-Back",
                  "description": (
                      f"Execute policy-grounded action directly into ServiceNow"
                      f" Ticket {inc_num} and log CRM commercial override for"
                      f" {sfdc_id}."
                  ),
                  "incident_number": inc_num,
                  "sfdc_id": sfdc_id,
                  "action_button_label": action_label,
                  "work_note_payload": action_note,
              },
          ],
      },
  }


async def run_unified_adk_a2ui_agent(query_text: str, base_url: str = "") -> dict:
  """Runs parallel MCP connectors + Gemini 3.8 Flash synthesis + A2UI v0.9 builder."""
  t_total = time.time()
  # 1. Gather all 3 MCP connectors in parallel (Salesforce + ServiceNow + Google Drive)
  mcp_data = await gather_all_mcp_context(query_text)

  # 2. Synthesize executive report using Gemini 3.8 Flash
  t_llm = time.time()
  os.environ.pop("GEMINI_API_KEY", None)
  os.environ.pop("GOOGLE_API_KEY", None)
  client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
  prompt = f"""You are the Motorola Solutions Unified Enterprise AI & A2UI Advisor (powered by Gemini 3.8 Flash).
Synthesize the following live cross-silo enterprise data retrieved concurrently via MCP for query: "{query_text}"

1. Salesforce CRM Data:
{json.dumps(mcp_data['salesforce']['records'], indent=2)}

2. ServiceNow ITSM Incidents:
{json.dumps(mcp_data['servicenow']['records'], indent=2)}

3. Google Drive Official Policy / Playbook:
{json.dumps(mcp_data['google_drive']['document'], indent=2)}

Structure your response into a crisp, high-impact Executive Brief with:
- **Executive Summary & Cross-Silo Diagnosis**
- **Cross-Silo Evidence & Citations** (Explicitly cite Salesforce ID, ServiceNow Incident Number, and Google Drive Document Title)
- **Recommended Action & Commercial/Compliance Resolution**
Keep it concise, authoritative, and formatted in clean Markdown."""

  try:
    response = await client.aio.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    markdown_text = response.text
  except Exception as e:
    print("LLM error:", repr(e))
    markdown_text = f"### Executive Cross-Silo Synthesis ({query_text})\n\n* **Salesforce CRM:** `{mcp_data['salesforce']['records'][0]['Id']}` (${mcp_data['salesforce']['records'][0]['Amount']:,.2f})\n* **ServiceNow ITSM:** `{mcp_data['servicenow']['records'][0]['number']}` — {mcp_data['servicenow']['records'][0]['short_description']}\n* **Google Drive Policy:** `{mcp_data['google_drive']['document']['title']}`"

  llm_ms = round((time.time() - t_llm) * 1000, 1)
  total_ms = round((time.time() - t_total) * 1000, 1)

  # 3. Build A2UI v0.9 JSON payload
  a2ui_payload = build_a2ui_v09_payload(query_text, mcp_data, markdown_text)

  # Add clickable A2UI Cockpit link to Markdown if called from Gemini Enterprise chat
  if base_url:
    cockpit_url = f"{base_url.rstrip('/')}/?q={query_text.replace(' ', '+')}"
    markdown_with_link = (
        f"{markdown_text}\n\n---\n### ⚡ Interactive A2UI Surface Available\n"
        f"**[ ⊞ Launch Interactive A2UI Deal Cockpit & 1-Click ServiceNow Write-Back ↗ ]({cockpit_url})**"
    )
  else:
    markdown_with_link = markdown_text

  return {
      "query": query_text,
      "model": MODEL_NAME,
      "timing": {
          "parallel_mcp_ms": mcp_data["parallel_execution_ms"],
          "llm_synthesis_ms": llm_ms,
          "total_ms": total_ms,
      },
      "mcp_sources": mcp_data,
      "markdown_report": markdown_with_link,
      "a2ui_v09_payload": a2ui_payload,
  }
