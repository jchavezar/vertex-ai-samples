# Gemini Enterprise Custom MCP App (`SEP-1865`) Integration Guide & Live Testing Playbook

````carousel
![Gemini Enterprise Default Assistant Invoking the Custom MCP App Tool (`06`)](/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/a1a5da3a-d6df-43d9-9320-cc14cf3cb269/06_gemini_enterprise_agent_tool_invocation.png)
<!-- slide -->
![Gemini Enterprise Side-by-Side (`PiP`) Mode — Chat on Left + Interactive MCP App on Right (`07`)](/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/a1a5da3a-d6df-43d9-9320-cc14cf3cb269/07_gemini_enterprise_side_by_side_citation_panel.png)
<!-- slide -->
![Gemini Enterprise Expanded Full-Screen Split Mode (`09`)](/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/a1a5da3a-d6df-43d9-9320-cc14cf3cb269/09_gemini_enterprise_fullscreen_split_grid_and_citation.png)
<!-- slide -->
![Sandboxed `about:srcdoc` Iframe Verification — Studio 2 Redline & Centered Maximize Modal (`v3.3.0`)](/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/a1a5da3a-d6df-43d9-9320-cc14cf3cb269/srcdoc_verified_redline_modal_v33.png)
<!-- slide -->
![Sandboxed `about:srcdoc` Iframe Verification — Studio 1 Live Parallel Gemini 3.8 Flash `+ Add column` (`v3.3.0`)](/usr/local/google/home/jesusarguelles/.gemini/jetski/brain/a1a5da3a-d6df-43d9-9320-cc14cf3cb269/live_title_column_verified.png)
````

---

## 1. Original Videos, Screencasts & Decks from Your Earlier Chat History

From sessions [`0bd60a3c-3c3e-4f18-8b6f-f41857734688`](conversation://0bd60a3c-3c3e-4f18-8b6f-f41857734688) and [`325f8f49-6a16-4f5a-9a98-b4ca78d573a5`](conversation://325f8f49-6a16-4f5a-9a98-b4ca78d573a5), here are the internal videos, screencasts, and slide decks that defined this integration:

| Resource Type | Title / Purpose | Link / Local Path |
| :--- | :--- | :--- |
| **Screencast Video 1** | **MCP App in Gemini Enterprise (`SEP-1865` Dual-Surface PiP Demo)** — Shows how a Cloud Run `/mcp` server mounts an interactive UI inside Gemini Enterprise's Default Assistant side panel (`<ucs-mcp-apps>`). | [**Open Screencast 1**](https://screencast.googleplex.com/cast/NjQ5MDg4MTU4MTM4MzY4MHwyNzNlNzgyMS02MQ) |
| **Screencast Video 2** | **Colleague Reference MCP App Walkthrough (`go/fde-mcp-apps`)** — Shows the `New chat` connector toggle, tool call execution, and Picture-in-Picture (`PiP`) / Fullscreen docking inside Gemini Enterprise. | [**Open Screencast 2**](https://screencast.googleplex.com/cast/NTMwODg4MDc1MzAwMDQ0OHxkZDk5NDQyNi1kMA) |
| **Slide Deck** | **`go/build-mcp-app-in-ge` (Slide 11 — Custom MCP Server Connector Setup)** — Official engineering guide for registering `dataSource: "custom_mcp"` connectors and binding `_meta.ui.resourceUri`. | [**Open Slide Deck (Slide 11)**](https://docs.google.com/presentation/d/1SdAGwbGYT7TZe9reXY61dV-GqaSfuAqDjqbsqisxwV8/edit?slide=id.p11) |
| **Video 3 (Local MP4 + Transcript)** | **`legal_governance_v6_demo.mp4` (10:24)** — *Gemini Enterprise for Legal: One request, governed end to end* (`vtxw-legal` Model Armor, VPC-SC, Agent Registry, Agent Gateway, Cloud Trace). | • **Video**: [`media_1790796176555.mp4`](file:///usr/local/google/home/jesusarguelles/.gemini/jetski/brain/0bd60a3c-3c3e-4f18-8b6f-f41857734688/.tempmediaStorage/media_1790796176555.mp4)<br>• **Transcript**: [`2026-09-25_Video_Transcript_Legal_Governance_v6_Demo.txt`](file:///usr/local/google/home/jesusarguelles/lexgraph-grounding-rag/corpus/2026-09-25_Video_Transcript_Legal_Governance_v6_Demo.txt) |
| **Video 4 (Local MP4 + Transcript)** | **`GE_for_Legal_Insights_from_Field_20260928.mp4` (05:50)** — Field readout (Tony Ensinger, Rahul Somanagoudar, Hemal, Ben Carlson) on why law firms need auto-orchestrated Canvas/MCP App UIs instead of manual `/skill` slash commands. | • **Video**: [`media_1790796250274.mp4`](file:///usr/local/google/home/jesusarguelles/.gemini/jetski/brain/0bd60a3c-3c3e-4f18-8b6f-f41857734688/.tempmediaStorage/media_1790796250274.mp4)<br>• **Transcript**: [`2026-09-28_Video_Transcript_GE_for_Legal_Insights_from_Field.txt`](file:///usr/local/google/home/jesusarguelles/lexgraph-grounding-rag/corpus/2026-09-28_Video_Transcript_GE_for_Legal_Insights_from_Field.txt) |

---

## 2. Good News: All 5 Studios Are Already Integrated & `ACTIVE` in Gemini Enterprise!

Via [`register_all_5_mcp_datastores.py`](file:///usr/local/google/home/jesusarguelles/lexgraph/register_all_5_mcp_datastores.py), all **5 Cloud Run services (`:v3.3.0`)** are registered as **5 separate `custom_mcp` DataStores** with `ActionState=ACTIVE` and `dynamicTools[].enabled = True` inside both of your Gemini Enterprise engines:

- **Primary Legal Engine (`lexgraph-legal-spanner-ge`)**:
  [**https://vertexaisearch.cloud.google.com/home/cid/ed20fa6b-3ad3-42e3-8fcf-0c8cc1af065f**](https://vertexaisearch.cloud.google.com/home/cid/ed20fa6b-3ad3-42e3-8fcf-0c8cc1af065f)
- **Secondary Enterprise Engine (`gemini-enterprise-17877637_1787763712023`)**:
  [**https://vertexaisearch.cloud.google.com/home/cid/b9298b3d-d513-4be8-b33a-971d8d3a0965**](https://vertexaisearch.cloud.google.com/home/cid/b9298b3d-d513-4be8-b33a-971d8d3a0965)

### How to Open & Test Each Studio Inside Gemini Enterprise (`✎ New chat`)

> [!IMPORTANT]
> **Always use `✎ New chat` (top-left of the Gemini Enterprise sidebar), NOT the `🚀 Agents` tab!**
> In Gemini Enterprise, **Custom MCP Apps (`SEP-1865`)** run inside the **Default Assistant (`✎ New chat`)** when their connector toggle is switched **ON** in the Sources/Connectors menu at the bottom of the prompt bar.

| Studio # | Connector Name in Gemini Enterprise Menu | MCP Tool & UI Resource URI | Copy-Paste Prompt to Type in Gemini Enterprise (`✎ New chat`) |
| :---: | :--- | :--- | :--- |
| **1** | **`Mike OSS — Tabular Diligence Grid & Pin-Cite Reader (MCP App)`**<br>(`mike-oss-legal-grid-mcp`) | • Tool: `open_legal_analysis_grid`<br>• UI: `ui://mike-gcp/workspace.html` | `Open the Project Kestrel legal analysis grid for Matter M-331 and compare Change of Control provisions across all contracts.` |
| **2** | **`LexGraph Deterministic Redline & Word Legal Legos Studio (MCP App)`**<br>(`lexgraph-redline-legos-mcp`) | • Tool: `run_deterministic_redline`<br>• UI: `ui://mike-gcp/redline-studio.html` | `Run a deterministic redline comparing the LexGraph v3 Playbook against the Skadden v4 counterparty markup for Project Kestrel SPA Section 8.02(b) and open the redline studio.` |
| **3** | **`LexGraph FundGen / FundHQ MFN & Antitrust HSR Lab (MCP App)`**<br>(`lexgraph-funds-antitrust-mcp`) | • Tool: `analyze_fundgen_and_antitrust`<br>• UI: `ui://mike-gcp/funds-antitrust.html` | `Analyze the LexGraph Private Equity Partners XII FundGen LP side-letter MFN tiers and the Antitrust HSR Second Request HHI market concentration.` |
| **4** | **`LexGraph Intapp Ethical Wall, CMN Switcher & Spanner Graph (MCP App)`**<br>(`lexgraph-intapp-wall-graph-mcp`) | • Tool: `traverse_precedent_graph`<br>• UI: `ui://mike-gcp/governance-wall.html` | `Traverse the Cloud Spanner LexGraphLegalGraph for Matter M-331-KESTREL as lawyer L-001 and verify Intapp Ethical Wall Screen-Before-Rank enforcement.` |
| **5** | **`LexGraph Partner Deal Inbox, CMN Auto-Filer & Calendar Triage (MCP App)`**<br>(`lexgraph-inbox-calendar-mcp`) | • Tool: `triage_inbox_and_cmn_wall`<br>• UI: `ui://mike-gcp/inbox-calendar.html` | `Triage Partner Sarah Jenkins's unfiled deal emails EM-9901, EM-9902, EM-9903 and calendar conflict CAL-101.` |

---

## 3. How the Gemini Enterprise `SEP-1865` Integration Works Under the Hood

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  1. USER PROMPT IN GEMINI ENTERPRISE (`✎ New chat` Default Assistant)    │
│     • User enables Connector(s) in the prompt bar menu and sends prompt. │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  2. DISCOVERY ENGINE CALLS CLOUD RUN `POST /mcp` (`method: tools/call`)  │
│     • Executes tool (`open_legal_analysis_grid`, `run_deterministic...`) │
│     • Queries Cloud Spanner (`lexgraph-legal-spanner`) + `gemini-3.8-flash`  │
│     • Returns JSON-RPC 2.0 response with:                                │
│       - `content`: Executive markdown summary for the chat stream        │
│       - `structuredContent`: Hydrated state payload                      │
│       - `_meta.ui.resourceUri`: `"ui://mike-gcp/<studio>.html"`          │
│       - `_meta.ui.defaultDisplayMode`: `"pip"`                           │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  3. `<ucs-mcp-apps>` CALLS `POST /mcp` (`method: resources/read`)        │
│     • Returns self-contained HTML (`mimeType: "text/html;profile=mcp-app"`)│
│     • Pre-renders `<tbody>` + embeds `INITIAL_BOOTSTRAP_DATA` so         │
│       `about:srcdoc` (`window.location.origin === "null"`) loads at 0ms  │
│     • Declares `_meta.ui.csp.connectDomains` pointing to absolute        │
│       Cloud Run `API_BASE` URLs so live button clicks & `+ Add column`   │
│       work inside the sandboxed iframe.                                  │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  4. GUEST IFRAME <-> GEMINI ENTERPRISE HOST (`window.postMessage`)       │
│     • Sends `ui/initialize` & `ui/notifications/initialized`             │
│     • Sends `ui/notifications/size-changed` (`{ height: 760 }`)          │
│     • Sends `ui/request-display-mode` (`{ mode: "pip" }`) to dock into   │
│       the right-hand Gemini Enterprise Side Panel (or `fullscreen`).     │
└──────────────────────────────────────────────────────────────────────────┘
```

### The 5 Engineering Gotchas We Solved (From [`register_all_5_mcp_datastores.py`](file:///usr/local/google/home/jesusarguelles/lexgraph/register_all_5_mcp_datastores.py) & [`app.py`](file:///usr/local/google/home/jesusarguelles/lexgraph/app.py))
1. **Why `setUpDataConnector` Alone Leaves Tools Invisible**:
   - Creating a `custom_mcp` connector via REST leaves `dynamicTools` empty in Discovery Engine's Spanner table until `DataConnectorService.RefreshDataConnectorTools` is called via `stubby` (lines 145–176 of [`register_all_5_mcp_datastores.py`](file:///usr/local/google/home/jesusarguelles/lexgraph/register_all_5_mcp_datastores.py)).
2. **Eliminating the Human-in-the-Loop Confirmation Blocker**:
   - Setting `"readOnlyHint": True` in `annotations` on each primary tool in [`app.py`](file:///usr/local/google/home/jesusarguelles/lexgraph/app.py) allows Gemini Enterprise to immediately execute the tool and pop open the MCP App without blocking on a `"Review: [Send] [Cancel]"` card.
3. **Why Relative `fetch("/api/...")` Fails Inside Gemini Enterprise**:
   - Gemini Enterprise mounts MCP Apps in `<iframe sandbox="allow-scripts" srcdoc="...">` where `window.location.origin === "null"`. Every `fetch()` in [`ui_template.py`](file:///usr/local/google/home/jesusarguelles/lexgraph/ui_template.py) uses the injected absolute Cloud Run `API_BASE` URL, and initial data is server-side pre-rendered into the HTML.
4. **Expanding the Iframe from `180px` to `760px` & Docking to the Side Panel**:
   - Sending `ui/notifications/size-changed` (`{ height: 760 }`) and `ui/request-display-mode` (`{ mode: "pip" }`) via `window.parent.postMessage` on load automatically expands the widget and docks it into Gemini Enterprise's right-hand panel.
5. **1-to-1 Disjoint Tool Routing Across All 5 Studios**:
   - Each of the 5 connectors exposes 1 distinct primary tool (`open_legal_analysis_grid`, `run_deterministic_redline`, `analyze_fundgen_and_antitrust`, `traverse_precedent_graph`, `triage_inbox_and_cmn_wall`) so all 5 can stay toggled **ON** simultaneously in Gemini Enterprise without routing collisions.
