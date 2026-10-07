import json
import os
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from mcp_connectors import execute_servicenow_writeback
from visual_engine import render_svg_chart, run_visual_command_agent

app = FastAPI(
    title="Motorola Visual Command Deck — A2UI Native Chart & War Room Agent"
)

LAST_A2A_HANDSHAKE = {"timestamp": None, "headers": {}, "body": {}}
TASKS_STORE: dict[str, dict] = {}


@app.get("/api/chart/{scenario}/{chart_num}.svg")
async def get_svg_chart(scenario: str, chart_num: int):
  """Serves high-DPI boardroom-grade vector SVG executive charts for A2UI Image cards."""
  svg_xml = render_svg_chart(scenario, chart_num)
  return Response(
      content=svg_xml,
      media_type="image/svg+xml",
      headers={
          "Cache-Control": "public, max-age=300",
          "Access-Control-Allow-Origin": "*",
      },
  )


@app.get("/.well-known/agent-card.json")
async def get_agent_card(request: Request):
  """A2A Protocol Agent Card for Motorola Visual Command Deck."""
  scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
  base_url = f"{scheme}://{request.url.netloc}".rstrip("/")
  return JSONResponse({
      "name": "Motorola Visual Command Deck",
      "description": (
          "Executive Visual Intelligence & War Room Agent for Motorola"
          " Solutions. Delivers an ultra-crisp 5-line Executive Flash Brief"
          " paired with native interactive A2UI v0.9 visual charts, 3-column"
          " KPI cards, live scenario switching, and 1-click ServiceNow OAuth"
          " 2.0 write-back."
      ),
      "url": base_url,
      "version": "1.1.0",
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
                  "uri": "https://a2ui.org/a2a-extension/a2ui/v0.9",
                  "description": "Ability to render A2UI v0.9 Basic Catalog",
                  "required": False,
                  "params": {
                      "supportedCatalogIds": [
                          "https://a2ui.org/specification/v0_9/basic_catalog.json"
                      ],
                      "acceptsInlineCatalogs": True,
                  },
              },
              {
                  "uri": "https://a2ui.org/a2a-extension/a2ui/v0.8",
                  "description": "Ability to render A2UI v0.8 Standard Catalog",
                  "required": False,
                  "params": {
                      "supportedCatalogIds": [
                          "https://a2ui.org/specification/v0_8/standard_catalog_definition.json"
                      ],
                      "acceptsInlineCatalogs": True,
                  },
              },
          ],
      },
      "skills": [
          {
              "id": "deal_restructuring_visual_deck",
              "name": (
                  "Executive Deal & RF Visual Command Deck (Miami-Dade $1.95M)"
              ),
              "description": (
                  "Renders 5-line Executive Flash Brief + live deal comparison"
                  " & RF packet loss charts + 1-click ServiceNow write-back."
              ),
              "tags": ["visual", "charts", "a2ui", "sfdc", "servicenow"],
              "examples": [
                  (
                      "Show the visual executive command deck for Miami-Dade"
                      " Dispatch ($1.95M renewal)"
                  ),
              ],
          },
          {
              "id": "national_portfolio_war_room",
              "name": (
                  "National Public Safety Portfolio War Room ($9.75M Pipeline)"
              ),
              "description": (
                  "Visualizes all public safety renewals ($9.75M across State"
                  " Highway Patrol, City of Metro, Miami-Dade) with grouped bar"
                  " & donut charts."
              ),
              "tags": ["portfolio", "war-room", "charts", "pipeline"],
              "examples": [
                  (
                      "Launch the National Public Safety Portfolio War Room"
                      " across all accounts"
                  ),
              ],
          },
          {
              "id": "tariff_and_redline_simulator",
              "name": (
                  "Global Trade Tariff (INC0010004) & Legal Redline"
                  " (INC0010006) Simulator"
              ),
              "description": (
                  "Simulates Section 301 Customs Tariff savings ($850K) and"
                  " vendor liability cap protection ($1.05M) with interactive"
                  " visual charts."
              ),
              "tags": ["tariff", "hts", "legal", "redline", "charts"],
              "examples": [
                  (
                      "Run the Global Supply Chain Tariff and Legal Redline"
                      " visual simulator"
                  ),
              ],
          },
      ],
  })


@app.get("/api/last-handshake")
async def get_last_handshake():
  return JSONResponse(LAST_A2A_HANDSHAKE)


def _extract_action_context(act: dict) -> dict[str, str]:
  ctx_raw = act.get("context", [])
  out: dict[str, str] = {}
  if isinstance(ctx_raw, dict):
    for k, v in ctx_raw.items():
      out[k] = str(v)
  elif isinstance(ctx_raw, list):
    for item in ctx_raw:
      if isinstance(item, dict) and "key" in item:
        val = item.get("value", {})
        sval = val.get("literalString") if isinstance(val, dict) else str(val)
        if sval is not None:
          out[item["key"]] = sval
  return out


def _build_artifact_parts(
    flash_brief: str,
    v08_begin: dict,
    v08_update: dict,
    v09_messages: list[dict],
    wants_v09: bool,
) -> list[dict]:
  parts: list[dict] = [{"kind": "text", "text": flash_brief}]
  if wants_v09:
    for m in v09_messages:
      parts.append(
          {
              "kind": "data",
              "metadata": {"mimeType": "application/json+a2ui"},
              "data": m,
          }
      )
  else:
    parts.append(
        {
            "kind": "data",
            "metadata": {"mimeType": "application/json+a2ui"},
            "data": v08_begin,
        }
    )
    parts.append(
        {
            "kind": "data",
            "metadata": {"mimeType": "application/json+a2ui"},
            "data": v08_update,
        }
    )
  return parts


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
  LAST_A2A_HANDSHAKE["timestamp"] = time.strftime(
      "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
  )
  LAST_A2A_HANDSHAKE["headers"] = headers_dict
  LAST_A2A_HANDSHAKE["body"] = body
  print(
      f"[VISUAL COMMAND DECK RPC] method={rpc_method} ts={LAST_A2A_HANDSHAKE['timestamp']}",
      flush=True,
  )

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

  # Determine if client negotiated A2UI v0.9 (default True for Gemini Enterprise GA)
  ext_header = (
      headers_dict.get("x-a2a-extensions", "")
      + " "
      + headers_dict.get("a2a-extensions", "")
      + " "
      + json.dumps((body.get("params") or {}).get("metadata", {}))
  )
  wants_v09 = ("v0.9" in ext_header) or ("v0_9" in ext_header)

  msg_in = (
      body.get("params", {}).get("message", {})
      if isinstance(body.get("params"), dict)
      else {}
  )
  context_id = (
      msg_in.get("contextId")
      or (
          body.get("params", {}).get("contextId")
          if isinstance(body.get("params"), dict)
          else None
      )
      or str(uuid.uuid4())
  )
  task_id = (
      msg_in.get("taskId")
      or (
          body.get("params", {}).get("id")
          if isinstance(body.get("params"), dict)
          else None
      )
      or str(uuid.uuid4())
  )
  art_id = str(uuid.uuid4())

  # Check if incoming message is an A2UI userAction / event button click
  parts_in = msg_in.get("parts", [])
  for p in parts_in:
    if isinstance(p, dict) and p.get("kind") == "data":
      data_obj = p.get("data", {})
      if isinstance(data_obj, dict) and (
          "userAction" in data_obj or "action" in data_obj
      ):
        act = data_obj.get("userAction") or data_obj.get("action") or {}
        if isinstance(act.get("event"), dict):
          act = act["event"]
        act_name = act.get("name", "approve_executive_override")
        ctx_map = _extract_action_context(act)

        # Interactive Scenario Switcher button clicked!
        if act_name == "switch_scenario":
          target_scenario = ctx_map.get("scenario", "portfolio_war_room")
          res = await run_visual_command_agent(
              f"Switch to {target_scenario}",
              base_url=base_url,
              explicit_scenario=target_scenario,
          )
          completed_task = {
              "kind": "task",
              "id": task_id,
              "contextId": context_id,
              "status": {
                  "state": "completed",
                  "timestamp": time.strftime(
                      "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                  ),
              },
              "artifacts": [{
                  "artifactId": art_id,
                  "parts": _build_artifact_parts(
                      res["flash_brief"],
                      res["v08_begin"],
                      res["v08_update"],
                      res["v09_messages"],
                      wants_v09,
                  ),
              }],
          }
          TASKS_STORE[task_id] = completed_task
          return JSONResponse(
              {"jsonrpc": "2.0", "id": rpc_id, "result": completed_task}
          )

        # Primary Live ServiceNow Write-Back button clicked!
        inc_num = ctx_map.get("incident_number", "INC0010007")
        sfdc_id = ctx_map.get("sfdc_id", "006jV000001CIWrQAO")
        scen = ctx_map.get("scenario", "deal_restructuring")
        wb_res = await execute_servicenow_writeback(
            inc_num,
            (
                "[Motorola Visual Command Deck — Live A2UI Action] Executive"
                f" Override approved for {sfdc_id} ({scen})."
            ),
            sfdc_id,
        )
        confirm_surface_id = f"motorola-confirm-{inc_num.lower()}"
        confirm_text = (
            f"### ✅ Live ServiceNow Write-Back Executed (`{wb_res['status']}`)\n"
            f"- **ServiceNow Incident Patched:** `{inc_num}` updated live in **`{wb_res['latency_ms']} ms`** via OAuth 2.0 REST API (`dev271596.service-now.com`).\n"
            f"- **Commercial Protection Locked:** Opportunity `{sfdc_id}` protected (`$1.98M` expanded bundle + `0.02%` RF packet loss SLA guaranteed)."
        )
        confirm_v09 = [
            {
                "version": "v0.9",
                "createSurface": {
                    "surfaceId": confirm_surface_id,
                    "catalogId": (
                        "https://a2ui.org/specification/v0_9/basic_catalog.json"
                    ),
                },
            },
            {
                "version": "v0.9",
                "updateComponents": {
                    "surfaceId": confirm_surface_id,
                    "components": [
                        {
                            "id": "root",
                            "component": "Column",
                            "align": "stretch",
                            "children": ["conf_card"],
                        },
                        {
                            "id": "conf_card",
                            "component": "Card",
                            "child": "conf_col",
                        },
                        {
                            "id": "conf_col",
                            "component": "Column",
                            "children": [
                                "conf_h2",
                                "conf_sub",
                                "conf_chart",
                                "conf_btn_row",
                            ],
                        },
                        {
                            "id": "conf_h2",
                            "component": "Text",
                            "variant": "h2",
                            "text": (
                                "✅ Live ServiceNow OAuth 2.0 Write-Back"
                                f" Confirmed ({inc_num} — {wb_res['status']})"
                            ),
                        },
                        {
                            "id": "conf_sub",
                            "component": "Text",
                            "variant": "body",
                            "text": (
                                f"Patched {inc_num} on dev271596.service-now.com"
                                f" in {wb_res['latency_ms']} ms · Opportunity"
                                f" {sfdc_id} secured."
                            ),
                        },
                        {
                            "id": "conf_chart",
                            "component": "Image",
                            "url": (
                                f"{base_url}/api/chart/deal_restructuring/2.svg?v={int(time.time())}"
                            ),
                            "fit": "contain",
                        },
                        {
                            "id": "conf_btn_row",
                            "component": "Row",
                            "justify": "spaceBetween",
                            "children": ["btn_port", "btn_tar"],
                        },
                        {
                            "id": "btn_port_txt",
                            "component": "Text",
                            "text": (
                                "📊 View National Portfolio War Room ($9.75M)"
                            ),
                        },
                        {
                            "id": "btn_port",
                            "component": "Button",
                            "child": "btn_port_txt",
                            "variant": "primary",
                            "action": {
                                "event": {
                                    "name": "switch_scenario",
                                    "context": {
                                        "scenario": "portfolio_war_room"
                                    },
                                }
                            },
                        },
                        {
                            "id": "btn_tar_txt",
                            "component": "Text",
                            "text": "🛡️ View Tariff & Legal Simulator ($1.90M)",
                        },
                        {
                            "id": "btn_tar",
                            "component": "Button",
                            "child": "btn_tar_txt",
                            "action": {
                                "event": {
                                    "name": "switch_scenario",
                                    "context": {
                                        "scenario": "tariff_redline_sim"
                                    },
                                }
                            },
                        },
                    ],
                },
            },
            {
                "version": "v0.9",
                "updateDataModel": {
                    "surfaceId": confirm_surface_id,
                    "path": "/",
                    "value": {"status": wb_res["status"]},
                },
            },
        ]
        confirm_task = {
            "kind": "task",
            "id": task_id,
            "contextId": context_id,
            "status": {
                "state": "completed",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            "artifacts": [{
                "artifactId": art_id,
                "parts": (
                    [{"kind": "text", "text": confirm_text}]
                    + [
                        {
                            "kind": "data",
                            "metadata": {"mimeType": "application/json+a2ui"},
                            "data": m,
                        }
                        for m in confirm_v09
                    ]
                ),
            }],
        }
        TASKS_STORE[task_id] = confirm_task
        return JSONResponse(
            {"jsonrpc": "2.0", "id": rpc_id, "result": confirm_task}
        )

  # Standard prompt execution -> generate 5-line Flash Brief + full A2UI v0.9 visual command deck
  query_text = "Show executive visual command deck for Miami-Dade renewal"
  for p in parts_in:
    if isinstance(p, dict) and p.get("kind") == "text" and p.get("text"):
      query_text = p["text"]
      break

  res = await run_visual_command_agent(query_text, base_url=base_url)
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
          "parts": _build_artifact_parts(
              res["flash_brief"],
              res["v08_begin"],
              res["v08_update"],
              res["v09_messages"],
              wants_v09,
          ),
      }],
  }
  TASKS_STORE[task_id] = completed_task
  return JSONResponse(
      {"jsonrpc": "2.0", "id": rpc_id, "result": completed_task}
  )
