import json
import os
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from geospatial_engine import render_geospatial_svg, run_geospatial_dispatch_agent
from mcp_connectors import execute_servicenow_writeback

app = FastAPI(
    title="Motorola Geospatial RF & Field Dispatch Command — Native A2UI Agent"
)

LAST_A2A_HANDSHAKE = {"timestamp": None, "headers": {}, "body": {}}
TASKS_STORE: dict[str, dict] = {}


@app.get("/api/geo/{scenario}/{asset_num}.svg")
async def get_geospatial_svg(scenario: str, asset_num: int):
  """Serves high-DPI vector GIS/RF coverage maps (1.svg) and telemetry waveforms (2.svg) for A2UI Image cards."""
  svg_xml = render_geospatial_svg(scenario, asset_num)
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
  """A2A Protocol Agent Card for Motorola Geospatial RF & Field Dispatch Command."""
  scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
  base_url = f"{scheme}://{request.url.netloc}".rstrip("/")
  return JSONResponse({
      "name": "Motorola Geospatial RF & Field Dispatch Command",
      "description": (
          "Mission-Critical Geospatial RF Outage, Field Engineering Dispatch &"
          " APCO 2026 VIP Hospitality Command Agent for Motorola Solutions."
          " Renders live vector GIS coverage heatmaps, ASTRO 25 channel"
          " telemetry waveforms, interactive scenario switchers, and 1-click"
          " ServiceNow OAuth 2.0 write-back natively inside Gemini Enterprise."
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
              "id": "miami_geospatial_rf_outage_map",
              "name": (
                  "Live Geospatial RF Outage & Field Dispatch Map (Miami-Dade"
                  " INC0010007)"
              ),
              "description": (
                  "Renders live GIS coverage & dead-zone map for Miami-Dade"
                  " Repeater Site 4 (INC0010007), Field Unit #RF-104 routing,"
                  " and APX NEXT SmartConnect LTE failover."
              ),
              "tags": ["geospatial", "map", "rf", "a2ui", "dispatch"],
              "examples": [
                  (
                      "Show the live geospatial RF outage and field dispatch"
                      " map for Miami-Dade Dispatch"
                  ),
              ],
          },
          {
              "id": "metro_geospatial_lpr_grid",
              "name": (
                  "City of Metro District 4 Congestion & Avigilon LPR Grid"
                  " (INC0010002)"
              ),
              "description": (
                  "Visualizes Cook County District 4 94.2% ASTRO 25 channel"
                  " saturation and Avigilon Alta Cloud Video / LPR camera"
                  " corridors ($3.85M bundle)."
              ),
              "tags": ["geospatial", "lpr", "avigilon", "metro", "map"],
              "examples": [
                  (
                      "Show the geospatial RF congestion and Avigilon LPR"
                      " camera grid for City of Metro Public Safety"
                  ),
              ],
          },
          {
              "id": "apco_vip_summit_command_map",
              "name": (
                  "APCO 2026 Orlando Summit VIP Hospitality & Competitor Map"
                  " (Row 3)"
              ),
              "description": (
                  "Visualizes Orlando Convention Center VIP Suite #A1 ($11.0M"
                  " pipeline across Vance, Rostova, Keller) vs. Axon & L3Harris"
                  " threat zones."
              ),
              "tags": ["apco", "vip", "event", "competitor", "map"],
              "examples": [
                  (
                      "Show the APCO 2026 Orlando VIP hospitality floor map and"
                      " competitor counter-strategy"
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
      f"[GEOSPATIAL DISPATCH RPC] method={rpc_method} ts={LAST_A2A_HANDSHAKE['timestamp']}",
      flush=True,
  )

  rpc_id = body.get("id", str(uuid.uuid4()))

  if rpc_method == "tasks/get":
    t_id = (body.get("params") or {}).get("id")
    if t_id and t_id in TASKS_STORE:
      return JSONResponse({
          "jsonrpc": "2.0",
          "id": rpc_id,
          "result": TASKS_STORE[t_id],
      })

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

  parts_in = msg_in.get("parts", [])
  for p in parts_in:
    if isinstance(p, dict) and p.get("kind") == "data":
      data_obj = p.get("data", {})
      if isinstance(data_obj, dict) and (
          "userAction" in data_obj
          or "action" in data_obj
          or "event" in data_obj
      ):
        act = (
            data_obj.get("userAction")
            or data_obj.get("action")
            or data_obj.get("event")
            or {}
        )
        act_name = act.get("name", "")
        ctx = _extract_action_context(act)

        if act_name == "switch_scenario":
          target_scen = ctx.get("scenario", "miami_rf_outage")
          res = await run_geospatial_dispatch_agent(
              query=target_scen,
              base_url=base_url,
              explicit_scenario=target_scen,
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
          return JSONResponse({
              "jsonrpc": "2.0",
              "id": rpc_id,
              "result": completed_task,
          })

        inc_num = ctx.get("incident_number", "INC0010007")
        sfdc_id = ctx.get("sfdc_id", "006jV000001CIWrQAO")
        scen = ctx.get("scenario", "miami_rf_outage")
        wb_res = await execute_servicenow_writeback(
            inc_num,
            (
                f"[Motorola Geospatial Dispatch Command] Field Unit #RF-104"
                f" dispatched, APX NEXT SmartConnect LTE failover activated, &"
                f" Executive Override logged for {sfdc_id}."
            ),
            sfdc_id,
        )
        reply_md = (
            f"### ✅ Live Field Dispatch & ServiceNow Write-Back Executed (`{wb_res['status']}`)\n"
            f"- **ServiceNow Incident Patched:** [`{inc_num}`]({wb_res['service_now_url']})\n"
            f"- **Salesforce Deal Protected:** `{sfdc_id}`\n"
            f"- **Field Dispatch Status:** Unit `#RF-104` En Route (ETA 11 mins) + APX NEXT SmartConnect LTE Failover Active (`0.02%` loss)\n"
            f"- **Round-Trip OAuth 2.0 Latency:** `{wb_res['latency_ms']} ms`"
        )
        res = await run_geospatial_dispatch_agent(
            query=scen, base_url=base_url, explicit_scenario=scen
        )
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
                    reply_md + "\n\n---\n\n" + res["flash_brief"],
                    res["v08_begin"],
                    res["v08_update"],
                    res["v09_messages"],
                    wants_v09,
                ),
            }],
        }
        TASKS_STORE[task_id] = completed_task
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": completed_task,
        })

  query_text = "Miami-Dade"
  for p in parts_in:
    if isinstance(p, dict) and "text" in p:
      query_text = p["text"]
      break

  res = await run_geospatial_dispatch_agent(query_text, base_url=base_url)

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

  return JSONResponse({
      "jsonrpc": "2.0",
      "id": rpc_id,
      "result": completed_task,
  })
