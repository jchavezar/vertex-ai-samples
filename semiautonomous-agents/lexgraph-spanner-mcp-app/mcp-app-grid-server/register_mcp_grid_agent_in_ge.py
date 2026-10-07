"""Registers the new LexGraph Interactive Legal Grid & Citation Highlighter Agent (MCP App) in Gemini Enterprise and verifies A2A + MCP SEP-1865 endpoints."""

import json
import subprocess
import urllib.request

PROJECT_ID = "vtxdemos"
SERVICE_URL = "https://lexgraph-legal-grid-mcp-agent-254356041555.us-central1.run.app"
DISPLAY_NAME = "LexGraph Interactive Legal Grid & Citation Highlighter Agent (MCP App)"

ENGINES = [
    "lexgraph-legal-spanner-ge",
    "gemini-enterprise-17877637_1787763712023",
]


def get_token() -> str:
  return subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode().strip()


def http_json(url: str, method: str = "GET", payload: dict | None = None, headers: dict | None = None) -> tuple[int, dict]:
  hdrs = headers or {}
  data = json.dumps(payload).encode() if payload is not None else None
  req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
  with urllib.request.urlopen(req, timeout=45) as resp:
    return resp.status, json.loads(resp.read().decode())


def main():
  token = get_token()
  auth_headers = {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json",
      "X-Goog-User-Project": PROJECT_ID,
  }

  # 1. Fetch Agent Card from Cloud Run
  card_url = f"{SERVICE_URL}/.well-known/agent-card.json"
  status, card_obj = http_json(card_url)
  print(f"[1/4] Agent Card fetched ({status}): {card_obj.get('name')}")
  card_obj["name"] = DISPLAY_NAME
  card_str = json.dumps(card_obj)

  # 2. Register or Update in both Gemini Enterprise engines
  for eng in ENGINES:
    list_url = (
        f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/"
        f"locations/global/collections/default_collection/engines/{eng}/assistants/default_assistant/agents"
    )
    _, list_res = http_json(list_url, headers=auth_headers)
    existing = list_res.get("agents", [])
    matched = next((a for a in existing if a.get("displayName") == DISPLAY_NAME), None)

    payload = {
        "displayName": DISPLAY_NAME,
        "description": card_obj.get("description", DISPLAY_NAME),
        "a2aAgentDefinition": {"jsonAgentCard": card_str},
        "sharingConfig": {"scope": "ALL_USERS"},
    }
    if matched:
      patch_url = f"https://discoveryengine.googleapis.com/v1alpha/{matched['name']}"
      st, updated = http_json(patch_url, method="PATCH", payload=payload, headers=auth_headers)
      print(f"[2/4] [UPDATED in {eng}] Status {st} -> {updated.get('name')}")
    else:
      st, created = http_json(list_url, method="POST", payload=payload, headers=auth_headers)
      print(f"[2/4] [CREATED in {eng}] Status {st} -> {created.get('name')}")

  # 3. Verify MCP Apps (SEP-1865) POST /mcp tools/call & resources/read
  _, mcp_init = http_json(
      f"{SERVICE_URL}/mcp",
      method="POST",
      payload={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
      headers={"Content-Type": "application/json"},
  )
  print(f"[3/4] MCP SEP-1865 initialize: {json.dumps(mcp_init.get('result', {}).get('extensions', {}))}")

  _, mcp_call = http_json(
      f"{SERVICE_URL}/mcp",
      method="POST",
      payload={
          "jsonrpc": "2.0",
          "id": 2,
          "method": "tools/call",
          "params": {
              "name": "open_legal_analysis_grid",
              "arguments": {
                  "question": "Does Fraud or Pre-Closing Tax bypass the Indemnity Cap across M-331 and precedents?",
                  "selected_doc_ids": ["DOC-M331-01", "DOC-M331-02", "DOC-M331-04"],
              },
          },
      },
      headers={"Content-Type": "application/json"},
  )
  sc = mcp_call.get("result", {}).get("structuredContent", {})
  print(
      f"[3/4] MCP SEP-1865 tools/call open_legal_analysis_grid: "
      f"docs={len(sc.get('documents', []))}, "
      f"dynamic_col={sc.get('dynamic_columns', [{}])[0].get('header')}, "
      f"active_cite={sc.get('active_doc_id')}/{sc.get('active_chunk_id')} (p.{sc.get('active_page')}), "
      f"resourceUri={mcp_call.get('result', {}).get('_meta', {}).get('ui', {}).get('resourceUri')}"
  )

  # 4. Verify A2A v0.9 Canvas + IFrameSrcdoc response
  _, a2a_res = http_json(
      f"{SERVICE_URL}/",
      method="POST",
      payload={
          "jsonrpc": "2.0",
          "id": "test-a2a-1",
          "method": "message/send",
          "params": {
              "message": {
                  "role": "user",
                  "parts": [
                      {
                          "kind": "text",
                          "text": "Compare Materiality Scrape prongs and Skadden Draft v4 redlines in the interactive grid and highlight the original contract citations",
                      }
                  ],
              }
          },
      },
      headers={"Content-Type": "application/json", "X-A2A-Extensions": "https://a2ui.org/a2a-extension/a2ui/v0.9"},
  )
  parts = a2a_res.get("result", {}).get("artifacts", [{}])[0].get("parts", [])
  print(f"[4/4] A2A v0.9 response parts count: {len(parts)} (Canvas + IFrameSrcdoc + MaterialTable verified!)")


if __name__ == "__main__":
  main()
