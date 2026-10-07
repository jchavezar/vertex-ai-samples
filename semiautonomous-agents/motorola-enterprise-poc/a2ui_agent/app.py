import json
import os
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from a2ui_engine import run_unified_adk_a2ui_agent
from mcp_connectors import execute_servicenow_writeback

app = FastAPI(title="Motorola Unified ADK + MCP + A2UI v0.9 Agent")


class QueryRequest(BaseModel):
  query: str


class ActionRequest(BaseModel):
  incident_number: str
  work_note: str


@app.get("/.well-known/agent-card.json")
async def get_agent_card(request: Request):
  """A2A Protocol Agent Card advertising A2UI v0.8 and v0.9 extension support."""
  scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
  base_url = f"{scheme}://{request.url.netloc}".rstrip("/")
  return JSONResponse({
      "name": "Motorola Unified Enterprise AI & A2UI Agent",
      "description": (
          "Unified Google ADK Multi-Connector Agent (Salesforce CRM,"
          " ServiceNow ITSM, Google Drive Policy Engine) with native A2UI"
          " interactive surface rendering and live ServiceNow write-back."
      ),
      "url": base_url,
      "version": "1.0.0",
      "protocolVersion": "0.2.1",
      "defaultInputModes": ["application/json+a2ui", "text/plain"],
      "defaultOutputModes": ["application/json+a2ui", "text/plain"],
      "provider": {
          "organization": "Motorola Solutions Enterprise AI",
          "url": base_url,
      },
      "capabilities": {
          "streaming": False,
          "pushNotifications": False,
          "extensions": [
              {
                  "uri": "https://a2ui.org/a2a-extension/a2ui/v0.8",
                  "description": "Ability to render A2UI v0.8",
                  "required": False,
                  "params": {
                      "supportedCatalogIds": [
                          "https://a2ui.org/specification/v0_8/standard_catalog_definition.json"
                      ],
                      "acceptsInlineCatalogs": True,
                  },
              },
              {
                  "uri": "https://a2ui.org/a2a-extension/a2ui/v0.9",
                  "description": "Ability to render A2UI v0.9",
                  "required": False,
                  "params": {
                      "supportedCatalogIds": [
                          "https://a2ui.org/specification/v0_9/basic_catalog.json"
                      ],
                      "acceptsInlineCatalogs": True,
                  },
              },
          ],
      },
      "skills": [
          {
              "id": "customer_360_renewal_risk",
              "name": "Customer 360 & Renewal Risk (Row 19)",
              "description": (
                  "Cross-references Salesforce renewals, ServiceNow P1 radio"
                  " incidents, and Drive playbooks."
              ),
              "tags": ["enterprise", "motorola", "sfdc", "servicenow"],
              "examples": ["Miami-Dade", "City of Metro"],
          },
          {
              "id": "procurement_legal_redline",
              "name": "Procurement & Legal Redline Escalation (Row 12)",
              "description": (
                  "Audits vendor RFQ redlines (INC0010006) against Motorola"
                  " Net-60 & 2.0x liability cap rules."
              ),
              "tags": ["procurement", "legal", "servicenow"],
              "examples": ["INC0010006", "Precision Antenna Systems redline"],
          },
          {
              "id": "trade_compliance_hts_tariff",
              "name": "Global Trade Compliance & HTS Tariff Hold (Row 14)",
              "description": (
                  "Resolves customs tariff holds (INC0010004) using Motorola"
                  " HTS classification rulings."
              ),
              "tags": ["trade", "customs", "hts"],
              "examples": ["INC0010004", "RFQ #2026-884 HTS tariff hold"],
          },
      ],
  })


LAST_A2A_HANDSHAKE = {"timestamp": None, "headers": {}, "body": {}}
TASKS_STORE: dict[str, dict] = {}


@app.get("/api/last-handshake")
async def get_last_handshake():
  """Returns the exact headers and JSON body sent by Gemini Enterprise on the last A2A call."""
  return JSONResponse(LAST_A2A_HANDSHAKE)


@app.post("/")
async def handle_a2a_or_root_post(request: Request):
  """Handles A2A JSON-RPC 2.0 requests (message/send & tasks/get) from Gemini Enterprise."""
  scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
  base_url = f"{scheme}://{request.url.netloc}".rstrip("/")
  try:
    body = await request.json()
  except Exception:
    body = {}

  headers_dict = dict(request.headers)
  rpc_method = body.get("method", "message/send")
  LAST_A2A_HANDSHAKE["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
  LAST_A2A_HANDSHAKE["headers"] = headers_dict
  LAST_A2A_HANDSHAKE["body"] = body
  print(f"[A2A RPC] method={rpc_method} ts={LAST_A2A_HANDSHAKE['timestamp']} ua={headers_dict.get('user-agent')} x-a2a-ext={headers_dict.get('x-a2a-extensions')}", flush=True)

  rpc_id = body.get("id", str(uuid.uuid4()))

  # Handle tasks/get polling from Gemini Enterprise
  if rpc_method == "tasks/get":
    t_id = (body.get("params") or {}).get("id")
    if t_id and t_id in TASKS_STORE:
      return JSONResponse({
          "jsonrpc": "2.0",
          "id": rpc_id,
          "result": TASKS_STORE[t_id],
      })

  msg_in = body.get("params", {}).get("message", {}) if isinstance(body.get("params"), dict) else {}
  context_id = msg_in.get("contextId") or (body.get("params", {}).get("contextId") if isinstance(body.get("params"), dict) else None) or str(uuid.uuid4())
  task_id = msg_in.get("taskId") or (body.get("params", {}).get("id") if isinstance(body.get("params"), dict) else None) or str(uuid.uuid4())
  msg_id = str(uuid.uuid4())
  art_id = str(uuid.uuid4())

  # Check if incoming message is an A2UI userAction button click event
  parts_in = msg_in.get("parts", [])
  for p in parts_in:
    if isinstance(p, dict) and p.get("kind") == "data":
      data_obj = p.get("data", {})
      if isinstance(data_obj, dict) and ("userAction" in data_obj or "action" in data_obj):
        act = data_obj.get("userAction") or data_obj.get("action") or {}
        ctx_list = act.get("context", [])
        if isinstance(ctx_list, dict):
          inc_num = ctx_list.get("incident_number", "INC0010007")
          sfdc_id = ctx_list.get("sfdc_id", "006jV000001CIWrQAO")
        else:
          inc_num = "INC0010007"
          sfdc_id = "006jV000001CIWrQAO"
          for item in ctx_list if isinstance(ctx_list, list) else []:
            if isinstance(item, dict):
              val = item.get("value", {})
              sval = val.get("literalString") if isinstance(val, dict) else str(val)
              if item.get("key") == "incident_number" and sval:
                inc_num = sval
              elif item.get("key") == "sfdc_id" and sval:
                sfdc_id = sval
        wb_res = await execute_servicenow_writeback(
            inc_num,
            f"[A2UI Inline Gemini Enterprise Action] Executive Override approved via A2UI surface for {sfdc_id}.",
            sfdc_id,
        )
        reply_md = f"### ✅ Live ServiceNow Write-Back Executed (`{wb_res['status']}`)\n- **Incident Updated:** [`{inc_num}`]({wb_res['service_now_url']})\n- **Latency:** `{wb_res['latency_ms']} ms`\n- **Message:** {wb_res['message']}"
        completed_task = {
            "kind": "task",
            "id": task_id,
            "contextId": context_id,
            "status": {
                "state": "completed",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            "artifacts": [{
                "artifactId": art_id,
                "parts": [{"kind": "text", "text": reply_md}],
            }],
        }
        TASKS_STORE[task_id] = completed_task
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": completed_task,
        })

  # Extract user text query
  query_text = "Miami-Dade"
  for p in parts_in:
    if isinstance(p, dict) and "text" in p:
      query_text = p["text"]
      break
  if query_text == "Miami-Dade" and isinstance(body.get("params"), dict) and "query" in body["params"]:
    query_text = body["params"]["query"]
  elif "query" in body:
    query_text = body["query"] if isinstance(body["query"], str) else body["query"].get("text", "Miami-Dade")

  result = await run_unified_adk_a2ui_agent(query_text, base_url=base_url)

  # Build A2UI v0.8 & v0.9 standard catalog components
  sfdc_rec = (result.get("mcp_sources", {}).get("salesforce", {}).get("records") or [{}])[0]
  snow_rec = (result.get("mcp_sources", {}).get("servicenow", {}).get("records") or [{}])[0]
  drive_doc = result.get("mcp_sources", {}).get("google_drive", {}).get("document") or {}
  inc_num = snow_rec.get("number", "INC0010007")
  sfdc_id = sfdc_rec.get("Id", "006jV000001CIWrQAO")
  surface_id = f"motorola-surface-{inc_num.lower()}"
  try:
    sfdc_amt = float(sfdc_rec.get("Amount") or 1950000.0)
  except Exception:
    sfdc_amt = 1950000.0

  # Official A2UI v0.8 Standard Catalog messages (beginRendering MUST come FIRST!)
  a2ui_v08_begin_rendering = {
      "beginRendering": {
          "surfaceId": surface_id,
          "root": "root",
      }
  }
  a2ui_v08_surface_update = {
      "surfaceUpdate": {
          "surfaceId": surface_id,
          "components": [
              {
                  "id": "root",
                  "component": {
                      "Column": {
                          "children": {
                              "explicitList": [
                                  "header_txt",
                                  "main_card",
                              ]
                          }
                      }
                  },
              },
              {
                  "id": "header_txt",
                  "component": {
                      "Text": {
                          "text": {
                              "literalString": f"⚡ Motorola Solutions A2UI Action Surface ({inc_num})"
                          },
                          "usageHint": "h2",
                      }
                  },
              },
              {
                  "id": "main_card",
                  "component": {
                      "Card": {
                          "child": "card_col"
                      }
                  },
              },
              {
                  "id": "card_col",
                  "component": {
                      "Column": {
                          "children": {
                              "explicitList": [
                                  "sfdc_txt",
                                  "snow_txt",
                                  "drive_txt",
                                  "approve_btn",
                              ]
                          }
                      }
                  },
              },
              {
                  "id": "sfdc_txt",
                  "component": {
                      "Text": {
                          "text": {
                              "literalString": f"Salesforce CRM: {sfdc_rec.get('Name', 'Renewal')} (${sfdc_amt:,.2f} — {sfdc_rec.get('StageName', 'Negotiation')})"
                          },
                          "usageHint": "h3",
                      }
                  },
              },
              {
                  "id": "snow_txt",
                  "component": {
                      "Text": {
                          "text": {
                              "literalString": f"ServiceNow ITSM: {inc_num} (Priority {snow_rec.get('priority', '1')}) — {snow_rec.get('short_description', '')}"
                          }
                      }
                  },
              },
              {
                  "id": "drive_txt",
                  "component": {
                      "Text": {
                          "text": {
                              "literalString": f"Governance Policy: {(drive_doc.get('rules') or ['20% Executive Retention Discount Authorized'])[0]}"
                          },
                          "usageHint": "caption",
                      }
                  },
              },
              {
                  "id": "approve_btn",
                  "component": {
                      "Button": {
                          "child": "btn_label",
                          "primary": True,
                          "action": {
                              "name": "approve_executive_override",
                              "context": [
                                  {"key": "incident_number", "value": {"literalString": inc_num}},
                                  {"key": "sfdc_id", "value": {"literalString": sfdc_id}},
                              ],
                          },
                      }
                  },
              },
              {
                  "id": "btn_label",
                  "component": {
                      "Text": {
                          "text": {
                              "literalString": f"Authorize Executive Action & Update ServiceNow ({inc_num})"
                          }
                      }
                  },
              },
          ],
      }
  }

  # Official A2UI v0.9 Basic Catalog messages (createSurface -> updateComponents -> updateDataModel)
  a2ui_v09_messages = [
      {
          "version": "v0.9",
          "createSurface": {
              "surfaceId": surface_id,
              "catalogId": "https://a2ui.org/specification/v0_9/basic_catalog.json",
          },
      },
      {
          "version": "v0.9",
          "updateComponents": {
              "surfaceId": surface_id,
              "components": [
                  {"id": "root", "component": "Column", "children": ["header_txt", "main_card"]},
                  {"id": "header_txt", "component": "Text", "variant": "h2", "text": {"path": "/header"}},
                  {"id": "main_card", "component": "Card", "child": "card_col"},
                  {"id": "card_col", "component": "Column", "children": ["sfdc_txt", "snow_txt", "drive_txt", "approve_btn"]},
                  {"id": "sfdc_txt", "component": "Text", "variant": "h3", "text": {"path": "/sfdc"}},
                  {"id": "snow_txt", "component": "Text", "text": {"path": "/snow"}},
                  {"id": "drive_txt", "component": "Text", "variant": "caption", "text": {"path": "/drive"}},
                  {"id": "btn_label", "component": "Text", "text": {"path": "/btnText"}},
                  {
                      "id": "approve_btn",
                      "component": "Button",
                      "child": "btn_label",
                      "variant": "primary",
                      "action": {
                          "event": {
                              "name": "approve_executive_override",
                              "context": {"incident_number": inc_num, "sfdc_id": sfdc_id},
                          }
                      },
                  },
              ],
          },
      },
      {
          "version": "v0.9",
          "updateDataModel": {
              "surfaceId": surface_id,
              "path": "/",
              "value": {
                  "header": f"⚡ Motorola Solutions A2UI Action Surface ({inc_num})",
                  "sfdc": f"Salesforce CRM: {sfdc_rec.get('Name', 'Renewal')} (${sfdc_amt:,.2f} — {sfdc_rec.get('StageName', 'Negotiation')})",
                  "snow": f"ServiceNow ITSM: {inc_num} (Priority {snow_rec.get('priority', '1')}) — {snow_rec.get('short_description', '')}",
                  "drive": f"Governance Policy: {(drive_doc.get('rules') or ['20% Executive Retention Discount Authorized'])[0]}",
                  "btnText": f"Authorize Executive Action & Update ServiceNow ({inc_num})",
              },
          },
      },
  ]

  ext_hdr = headers_dict.get("x-a2a-extensions") or (body.get("params", {}).get("metadata", {}).get("X-A2A-Extensions") if isinstance(body.get("params"), dict) else None)
  client_caps = msg_in.get("metadata", {}).get("a2uiClientCapabilities") if isinstance(msg_in.get("metadata"), dict) else None
  wants_v09 = (ext_hdr and "v0.9" in str(ext_hdr)) or (client_caps and "v0_9" in json.dumps(client_caps))

  if wants_v09:
    a2ui_data_parts = [
        {"kind": "data", "metadata": {"mimeType": "application/json+a2ui"}, "data": msg}
        for msg in a2ui_v09_messages
    ]
  else:
    # Default to v0.8 (beginRendering FIRST, surfaceUpdate SECOND) — matches wadave/agent-a2ui-demo
    a2ui_data_parts = [
        {"kind": "data", "metadata": {"mimeType": "application/json+a2ui"}, "data": a2ui_v08_begin_rendering},
        {"kind": "data", "metadata": {"mimeType": "application/json+a2ui"}, "data": a2ui_v08_surface_update},
    ]

  artifact_parts = [
      {
          "kind": "text",
          "text": result["markdown_report"],
      },
      *a2ui_data_parts,
  ]

  completed_task = {
      "kind": "task",
      "id": task_id,
      "contextId": context_id,
      "status": {
          "state": "completed",
          "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
      },
      "artifacts": [{
          "artifactId": art_id,
          "parts": artifact_parts,
      }],
  }
  TASKS_STORE[task_id] = completed_task

  return JSONResponse({
      "jsonrpc": "2.0",
      "id": rpc_id,
      "result": completed_task,
  })


@app.post("/api/query")
async def api_query(req: QueryRequest, request: Request):
  scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
  base_url = f"{scheme}://{request.url.netloc}".rstrip("/")
  result = await run_unified_adk_a2ui_agent(req.query, base_url=base_url)
  return JSONResponse(result)


@app.post("/api/action")
async def api_action(req: ActionRequest):
  res = await execute_servicenow_writeback(req.incident_number, req.work_note)
  return JSONResponse(res)


@app.get("/", response_class=HTMLResponse)
async def serve_a2ui_cockpit():
  html = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Motorola Solutions — Unified ADK + A2UI v0.9 Command Center</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {
      --bg-canvas: #FAFAFA;
      --bg-grid: #EAEAEA;
      --bg-surface: #FFFFFF;
      --bg-elevated: #FAFAFA;
      --border-color: #EAEAEA;
      --border-hover: #111111;
      --text-primary: #09090B;
      --text-secondary: #666666;
      --btn-bg: #000000;
      --btn-text: #FFFFFF;
      --btn-hover: #27272A;
      --badge-bg: #F4F4F5;
      --badge-text: #18181B;
      --ink-gradient: radial-gradient(circle at 30% 30%, #52525b, #18181b, #000000);
    }
    [data-theme="dark"] {
      --bg-canvas: #000000;
      --bg-grid: #111111;
      --bg-surface: #0A0A0A;
      --bg-elevated: #111111;
      --border-color: #222222;
      --border-hover: #EDEDED;
      --text-primary: #EDEDED;
      --text-secondary: #888888;
      --btn-bg: #FFFFFF;
      --btn-text: #000000;
      --btn-hover: #D4D4D8;
      --badge-bg: #18181B;
      --badge-text: #E4E4E7;
      --ink-gradient: radial-gradient(circle at 30% 30%, #ffffff, #a1a1aa, #18181b);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, sans-serif;
      background-color: var(--bg-canvas);
      background-image: 
        linear-gradient(to right, var(--bg-grid) 1px, transparent 1px),
        linear-gradient(to bottom, var(--bg-grid) 1px, transparent 1px);
      background-size: 48px 48px;
      color: var(--text-primary);
      letter-spacing: -0.015em;
      min-height: 100vh;
    }

    /* Top Architectural Header */
    header {
      position: sticky;
      top: 0;
      z-index: 100;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-color);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .brand-row {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .brand-logo {
      width: 32px;
      height: 32px;
      background: var(--btn-bg);
      color: var(--btn-text);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      font-size: 15px;
    }
    .brand-title {
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary);
    }
    .brand-sub {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }
    .header-controls {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .mono-pill {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 6px 10px;
      border: 1px solid var(--border-color);
      background: var(--bg-elevated);
      border-radius: 4px;
      color: var(--text-secondary);
    }
    .theme-btn {
      cursor: pointer;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 500;
      padding: 7px 12px;
      border-radius: 5px;
      border: 1px solid var(--border-color);
      background: var(--bg-surface);
      color: var(--text-primary);
      transition: border-color 0.15s;
    }
    .theme-btn:hover { border-color: var(--border-hover); }

    /* Main Container */
    .container {
      max-width: 1280px;
      margin: 28px auto;
      padding: 0 24px 64px;
    }

    /* Scenario Selector Bar */
    .scenario-bar {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 18px 20px;
      margin-bottom: 20px;
    }
    .scenario-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }
    .scenario-label {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-secondary);
    }
    .scenario-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 14px;
    }
    .scenario-pill {
      cursor: pointer;
      font-size: 12px;
      font-weight: 500;
      padding: 7px 13px;
      border-radius: 5px;
      border: 1px solid var(--border-color);
      background: var(--bg-elevated);
      color: var(--text-primary);
      transition: all 0.15s;
    }
    .scenario-pill:hover, .scenario-pill.active {
      background: var(--btn-bg);
      color: var(--btn-text);
      border-color: var(--btn-bg);
    }

    .search-row {
      display: flex;
      gap: 10px;
    }
    .search-input {
      flex: 1;
      padding: 11px 14px;
      font-size: 14px;
      font-family: 'Inter', sans-serif;
      border: 1px solid var(--border-color);
      border-radius: 6px;
      background: var(--bg-surface);
      color: var(--text-primary);
      outline: none;
    }
    .search-input:focus { border-color: var(--border-hover); }
    .run-btn {
      cursor: pointer;
      padding: 11px 22px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 6px;
      border: none;
      background: var(--btn-bg);
      color: var(--btn-text);
      transition: background 0.15s;
    }
    .run-btn:hover { background: var(--btn-hover); }

    /* Claude-Code Shrinking & Shining Ink Loader */
    .loader-wrapper {
      display: none;
      align-items: center;
      gap: 16px;
      padding: 28px;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      margin-bottom: 20px;
    }
    .shrinking-shining-ink {
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: var(--ink-gradient);
      animation: inkPulse 1.4s infinite ease-in-out;
      flex-shrink: 0;
    }
    @keyframes inkPulse {
      0%, 100% { transform: scale(1); opacity: 0.95; }
      50% { transform: scale(0.55); opacity: 0.4; }
    }
    .sweep-text {
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: var(--text-secondary);
      letter-spacing: 0.04em;
    }

    /* Telemetry Strip */
    .telemetry-strip {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 20px;
    }
    .telemetry-card {
      flex: 1;
      min-width: 180px;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 12px 16px;
    }
    .telemetry-title {
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }
    .telemetry-val {
      font-family: 'JetBrains Mono', monospace;
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }

    /* View Mode Toggle (Rendered A2UI vs Protocol JSON Inspector) */
    .view-tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 16px;
    }
    .tab-btn {
      cursor: pointer;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 8px 14px;
      border-radius: 5px;
      border: 1px solid var(--border-color);
      background: var(--bg-surface);
      color: var(--text-secondary);
    }
    .tab-btn.active {
      background: var(--btn-bg);
      color: var(--btn-text);
      border-color: var(--btn-bg);
    }

    /* A2UI Rendered Surface */
    .a2ui-surface-box {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 24px;
    }
    .surface-top-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 16px;
      margin-bottom: 20px;
    }
    .surface-title {
      font-size: 17px;
      font-weight: 600;
    }
    .status-badge {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 600;
      padding: 5px 10px;
      border-radius: 4px;
      border: 1px solid var(--border-hover);
      background: var(--badge-bg);
      color: var(--badge-text);
    }

    /* KPI Grid */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 14px;
      margin-bottom: 24px;
    }
    .kpi-card {
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 16px;
      background: var(--bg-elevated);
      transition: border-color 0.15s;
    }
    .kpi-card:hover { border-color: var(--border-hover); }
    .kpi-label {
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-secondary);
      margin-bottom: 6px;
    }
    .kpi-value {
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 6px;
    }
    .kpi-sub {
      font-size: 12px;
      color: var(--text-secondary);
    }

    /* Matrix Table */
    .matrix-section {
      margin-bottom: 24px;
    }
    .section-heading {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-secondary);
      margin-bottom: 10px;
    }
    table.matrix-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    table.matrix-table th, table.matrix-table td {
      border: 1px solid var(--border-color);
      padding: 11px 14px;
      text-align: left;
    }
    table.matrix-table th {
      background: var(--bg-elevated);
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-secondary);
    }

    /* Interactive Action Card */
    .action-card {
      border: 1px solid var(--border-hover);
      border-radius: 8px;
      padding: 20px;
      background: var(--bg-elevated);
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .action-card-title {
      font-size: 15px;
      font-weight: 600;
    }
    .action-card-desc {
      font-size: 13px;
      color: var(--text-secondary);
    }
    .action-btn-row {
      display: flex;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
    }
    .execute-action-btn {
      cursor: pointer;
      padding: 11px 20px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 6px;
      border: none;
      background: var(--btn-bg);
      color: var(--btn-text);
    }
    .execute-action-btn:hover { background: var(--btn-hover); }
    .writeback-toast {
      display: none;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      padding: 10px 14px;
      border: 1px solid var(--border-hover);
      background: var(--bg-surface);
      border-radius: 6px;
    }

    /* Markdown Executive Report Box */
    .markdown-box {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 24px;
      line-height: 1.65;
      font-size: 14px;
    }
    .markdown-box h1, .markdown-box h2, .markdown-box h3 {
      margin-top: 16px;
      margin-bottom: 8px;
    }
    .markdown-box ul {
      padding-left: 20px;
      margin-bottom: 12px;
    }
    .markdown-box a {
      color: var(--text-primary);
      font-weight: 600;
      text-decoration: underline;
    }

    /* JSON Inspector Box */
    .json-inspector-box {
      display: none;
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      white-space: pre-wrap;
      overflow-x: auto;
      margin-bottom: 24px;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand-row">
      <div class="brand-logo">M</div>
      <div>
        <div class="brand-title">Motorola Solutions — Unified ADK + A2UI v0.9 Command Center</div>
        <div class="brand-sub">Parallel MCP Orchestration (Salesforce • ServiceNow • Google Drive) • Gemini 3.8 Flash</div>
      </div>
    </div>
    <div class="header-controls">
      <span class="mono-pill">A2A Card: /.well-known/agent-card.json</span>
      <button class="theme-btn" id="themeToggle" onclick="toggleTheme()">🌙 Dark Mode</button>
    </div>
  </header>

  <div class="container">
    <div class="scenario-bar">
      <div class="scenario-header">
        <span class="scenario-label">Select Motorola Enterprise POC Scenario (Pre-Seeded Live MCP Data)</span>
        <span class="scenario-label">A2UI Extension: https://a2ui.org/a2a-extension/a2ui/v0.9</span>
      </div>
      <div class="scenario-pills">
        <button class="scenario-pill active" onclick="runScenario('Miami-Dade', this)">1. Row 19: Customer 360 & Renewal Risk (Miami-Dade)</button>
        <button class="scenario-pill" onclick="runScenario('INC0010006 Precision Antenna Systems Redline', this)">2. Row 12: Legal Redline Escalation (INC0010006)</button>
        <button class="scenario-pill" onclick="runScenario('INC0010004 HTS Tariff Conflict RFQ 2026-884', this)">3. Row 14: Trade Compliance HTS Hold (INC0010004)</button>
        <button class="scenario-pill" onclick="runScenario('INC0010003 CDMG Hierarchy Override Apex Global', this)">4. Row 16: CDMG Hierarchy Governance (INC0010003)</button>
        <button class="scenario-pill" onclick="runScenario('INC0010005 Hand-Carry APX NEXT Export Clearance', this)">5. Row 8: APX NEXT Export Clearance (INC0010005)</button>
      </div>
      <div class="search-row">
        <input type="text" id="queryInput" class="search-input" value="Miami-Dade" placeholder="Enter account name, ServiceNow incident (e.g. INC0010007), or RFQ number..." />
        <button class="run-btn" onclick="executeQuery()">⚡ Run Parallel MCP + Render A2UI</button>
      </div>
    </div>

    <!-- Claude-Code Shrinking & Shining Ink Loader -->
    <div class="loader-wrapper" id="loaderBox">
      <div class="shrinking-shining-ink"></div>
      <div class="sweep-text" id="loaderText">Executing parallel asyncio.gather across Salesforce MCP, ServiceNow ITSM MCP & Google Drive Policy Engine + Gemini 3.8 Flash A2UI v0.9 synthesis...</div>
    </div>

    <!-- Telemetry Strip -->
    <div class="telemetry-strip" id="telemetryStrip">
      <div class="telemetry-card">
        <div class="telemetry-title">PARALLEL MCP I/O TIME</div>
        <div class="telemetry-val" id="telMcp">-- ms</div>
      </div>
      <div class="telemetry-card">
        <div class="telemetry-title">GEMINI 3.8 FLASH SYNTHESIS</div>
        <div class="telemetry-val" id="telLlm">-- ms</div>
      </div>
      <div class="telemetry-card">
        <div class="telemetry-title">TOTAL END-TO-END LATENCY</div>
        <div class="telemetry-val" id="telTotal">-- ms</div>
      </div>
      <div class="telemetry-card">
        <div class="telemetry-title">A2UI PROTOCOL VERSION</div>
        <div class="telemetry-val">a2ui/v0.9 (DataPart)</div>
      </div>
    </div>

    <!-- View Tabs -->
    <div class="view-tabs">
      <button class="tab-btn active" id="tabSurface" onclick="switchView('surface')">[ ⊞ Rendered A2UI v0.9 Interactive Surface ]</button>
      <button class="tab-btn" id="tabJson" onclick="switchView('json')">[ { } Raw A2UI v0.9 Protocol JSON Inspector ]</button>
    </div>

    <!-- Rendered A2UI Surface -->
    <div class="a2ui-surface-box" id="surfaceContainer">
      <div class="surface-top-bar">
        <div class="surface-title" id="surfTitle">Motorola Solutions — Cross-Silo A2UI Action Surface</div>
        <div class="status-badge" id="surfBadge">READY</div>
      </div>

      <!-- KPI Grid -->
      <div class="kpi-grid" id="kpiGrid"></div>

      <!-- Reconciliation Matrix -->
      <div class="matrix-section">
        <div class="section-heading">CROSS-SILO ENTERPRISE RECONCILIATION MATRIX (LIVE MCP PROVENANCE)</div>
        <table class="matrix-table">
          <thead>
            <tr>
              <th>Enterprise Silo</th>
              <th>Record / Document ID</th>
              <th>Live Status / Finding</th>
              <th>Mandatory Policy / Action</th>
            </tr>
          </thead>
          <tbody id="matrixBody"></tbody>
        </table>
      </div>

      <!-- Interactive Action Card -->
      <div class="action-card" id="actionCard">
        <div class="action-card-title" id="actTitle">1-Click Autonomous Remediation & Live ServiceNow Write-Back</div>
        <div class="action-card-desc" id="actDesc">Execute policy-grounded action directly into ServiceNow and log commercial override.</div>
        <div class="action-btn-row">
          <button class="execute-action-btn" id="actBtn" onclick="triggerWriteback()">⚡ Execute Action & Update Live ServiceNow Ticket</button>
          <div class="writeback-toast" id="writebackToast"></div>
        </div>
      </div>
    </div>

    <!-- JSON Inspector -->
    <div class="json-inspector-box" id="jsonInspector"></div>

    <!-- Executive Markdown Report -->
    <div class="section-heading" style="margin-bottom: 10px;">GEMINI 3.8 FLASH EXECUTIVE BRIEFING & CITATIONS (GEMINI ENTERPRISE CANVAS COMPATIBLE)</div>
    <div class="markdown-box" id="markdownBox"></div>
  </div>

  <script>
    let currentActionIncident = "INC0010007";
    let currentActionNote = "";

    function toggleTheme() {
      const root = document.documentElement;
      const current = root.getAttribute("data-theme");
      const next = current === "light" ? "dark" : "light";
      root.setAttribute("data-theme", next);
      document.getElementById("themeToggle").textContent = next === "light" ? "🌙 Dark Mode" : "☀️ Light Mode";
    }

    function switchView(mode) {
      document.getElementById("tabSurface").classList.toggle("active", mode === "surface");
      document.getElementById("tabJson").classList.toggle("active", mode === "json");
      document.getElementById("surfaceContainer").style.display = mode === "surface" ? "block" : "none";
      document.getElementById("jsonInspector").style.display = mode === "json" ? "block" : "none";
    }

    function runScenario(queryText, btnEl) {
      document.querySelectorAll(".scenario-pill").forEach(b => b.classList.remove("active"));
      if (btnEl) btnEl.classList.add("active");
      document.getElementById("queryInput").value = queryText;
      executeQuery();
    }

    async function executeQuery() {
      const query = document.getElementById("queryInput").value.trim() || "Miami-Dade";
      document.getElementById("loaderBox").style.display = "flex";
      document.getElementById("writebackToast").style.display = "none";

      try {
        const resp = await fetch("/api/query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query })
        });
        const data = await resp.json();
        renderA2uiResponse(data);
      } catch (err) {
        console.error(err);
      } finally {
        document.getElementById("loaderBox").style.display = "none";
      }
    }

    function renderA2uiResponse(data) {
      // Update Telemetry
      document.getElementById("telMcp").textContent = data.timing.parallel_mcp_ms + " ms";
      document.getElementById("telLlm").textContent = data.timing.llm_synthesis_ms + " ms";
      document.getElementById("telTotal").textContent = data.timing.total_ms + " ms";

      const surface = data.a2ui_v09_payload.surface;
      document.getElementById("surfTitle").textContent = surface.title;
      document.getElementById("surfBadge").textContent = surface.status_badge;

      // Render KPIs
      const kpiComp = surface.components.find(c => c.type === "kpi_grid");
      const kpiGrid = document.getElementById("kpiGrid");
      kpiGrid.innerHTML = "";
      if (kpiComp) {
        kpiComp.items.forEach(item => {
          kpiGrid.innerHTML += `
            <div class="kpi-card">
              <div class="kpi-label">${item.label}</div>
              <div class="kpi-value">${item.value}</div>
              <div class="kpi-sub">${item.subtext}</div>
            </div>
          `;
        });
      }

      // Render Reconciliation Matrix
      const matrixComp = surface.components.find(c => c.type === "reconciliation_matrix");
      const tbody = document.getElementById("matrixBody");
      tbody.innerHTML = "";
      if (matrixComp) {
        matrixComp.rows.forEach(row => {
          tbody.innerHTML += `
            <tr>
              <td><strong>${row[0]}</strong></td>
              <td style="font-family:'JetBrains Mono',monospace;font-size:12px;">${row[1]}</td>
              <td>${row[2]}</td>
              <td>${row[3]}</td>
            </tr>
          `;
        });
      }

      // Render Action Card
      const actComp = surface.components.find(c => c.type === "interactive_action_card");
      if (actComp) {
        document.getElementById("actTitle").textContent = actComp.title;
        document.getElementById("actDesc").textContent = actComp.description;
        document.getElementById("actBtn").textContent = "⚡ " + actComp.action_button_label;
        currentActionIncident = actComp.incident_number;
        currentActionNote = actComp.work_note_payload;
      }

      // Update JSON Inspector
      document.getElementById("jsonInspector").textContent = JSON.stringify(data.a2ui_v09_payload, null, 2);

      // Update Markdown
      document.getElementById("markdownBox").innerHTML = marked.parse(data.markdown_report);
    }

    async function triggerWriteback() {
      const toast = document.getElementById("writebackToast");
      toast.style.display = "block";
      toast.textContent = "⏳ Updating live ServiceNow ticket " + currentActionIncident + "...";
      try {
        const resp = await fetch("/api/action", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            incident_number: currentActionIncident,
            work_note: currentActionNote
          })
        });
        const res = await resp.json();
        toast.innerHTML = `✅ <strong>${res.status}</strong> (${res.latency_ms} ms): ${res.message} — <a href="${res.service_now_url}" target="_blank" style="color:inherit;text-decoration:underline;">View Live Ticket in ServiceNow ↗</a>`;
      } catch (e) {
        toast.textContent = "❌ Error writing to ServiceNow: " + e;
      }
    }

    // Auto-run query on page load (check URL ?q= parameter first)
    window.addEventListener("DOMContentLoaded", () => {
      const params = new URLSearchParams(window.location.search);
      const qParam = params.get("q");
      if (qParam) {
        document.getElementById("queryInput").value = qParam;
      }
      executeQuery();
    });
  </script>
</body>
</html>
  """
  return HTMLResponse(content=html)
