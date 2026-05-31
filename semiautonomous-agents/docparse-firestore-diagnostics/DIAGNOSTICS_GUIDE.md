# Discovery Engine & Firestore MCP Grounding Diagnostic Guide

This diagnostic directory contains tools, testing scripts, and analysis workflows to verify and troubleshoot the custom Firestore MCP RAG Engine linked to **Gemini Enterprise (GE)**.

---

## 1. Diagnostic Summary: HAR 6 Analysis

During troubleshooting, the user provided a 6th HAR capture (`vertexaisearch.cloud.google.com-streamassist-6.har`) to inspect why queries like *"what is the metaverse?"* were not grounding or returning citations despite our silent execution patch being active.

### Key Finding: 0 Tool Calls Executed
Running the stream analysis script (`print_stream_summary.py`) revealed that the model **did not execute a single action or tool call** throughout the conversation:
* **Total Stream Objects:** 17 chunks.
* **Tool / Action Invocations:** `actions=False`, `invocations=False`.
* **Behavior:** The LLM immediately began streaming general-knowledge response text in the first chunk (`state=IN_PROGRESS`).

```python
[0] state=IN_PROGRESS replies_count=1 actions=False invocations=False err=False
  Reply 0: 'The **metaverse** is a conceptual vision of a highly immersive, shared '...
...
[16] state=SUCCEEDED replies_count=1 actions=False invocations=False err=False
  Reply 0: ''...
```

### Visual Root Cause (GE Chat Bar "Auto" Toggle)
In your Gemini Enterprise screenshot, the selector toggle in the bottom prompt bar was set to **"Auto"**.
* **How "Auto" behaves:** When set to Auto, the router dynamically decides whether to invoke external extensions or answer from the pre-trained model weights. 
* **The Bypass:** Because *"what is the metaverse?"* is a widely known concept, the router completely bypassed the custom MCP connector and responded directly using pre-trained knowledge—bypassing our strict RAG instructions.

---

## 2. Infrastructure Architecture & Silent Execution Patch

The custom Firestore RAG service is deployed to **Cloud Run** and connects directly to Google Discovery Engine:
* **Cloud Run MCP Service URL:** `https://docparse-firestore-mcp-254356041555.us-central1.run.app/mcp`
* **Discovery Engine Connector ID:** `docparse-firestore-mcp-1780165632`
* **Linked Engine ID:** `docparse_1780161524773` (Display Name: `docparse`)

### The OAuth / nested-mask Bypass Pattern
When programmatically patching parameters like `mcp_agent_instructions` or `mcp_server_description` on the federated connector, standard full-resource updates fail with `400` errors regarding write-only fields (e.g. OAuth `client_secret` or scopes).
* **The Solution:** Use explicit, nested update masks to surgically write only the fields you want to update:
  ```python
  patch_url = "https://discoveryengine.googleapis.com/v1alpha/.../dataConnector?updateMask=actionConfig.actionParams.mcp_agent_instructions"
  ```

---

## 3. How to Run Diagnostics

### Step A: Verify Cloud Run MCP Handshake
Ensure the Cloud Run server is alive and listing its available schemas (including `search_docs`):
```bash
python3 test_list_tools.py
```
*(Requires a valid Google cloud platform authentication credential or ID token to bypass Cloud Run invoker permissions).*

### Step B: Inspect Connected Connector
Fetch details of the Discovery Engine connector to verify instructions, active states, and synchronized tools:
```bash
python3 get_connector_details.py
```

### Step C: Trigger Schema Sync
Force Discovery Engine to re-query the Cloud Run MCP endpoint and refresh its dynamic tool definitions:
```bash
python3 patch_active_connector.py
```

---

## 4. Operational Resolution in Gemini Enterprise UI

To force grounding and ensure citation links are generated, follow these steps in your browser:

1. **Check the Active Extension/Agent:**
   * Look at the top-left or extension options in Gemini Enterprise and make sure the specific Custom Agent/App (e.g., **"Metaverse deployment"**) is selected instead of the default generic chat.
2. **Force Tool Invocation via Model Bar:**
   * Do not use the **"Auto"** setting next to the text input. Make sure the Firestore RAG extension is checked/enabled.
3. **Draft Grounding-Biased Prompts:**
   * Explicitly request document lookups: *"Search our database for the metaverse and list citations."*
