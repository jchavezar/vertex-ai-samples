# 02 — MCP Apps Protocol (SEP-1865) & Dual-Surface Legal Grid Architecture

## Why MCP Apps (SEP-1865) in Gemini Enterprise?

Standard conversational chat forces lawyers into a 10–15 second LLM round-trip every time they want to sort a table, filter by Indemnity Cap, select specific deal documents, or inspect the surrounding paragraphs of a cited clause.

By implementing the **Model Context Protocol (MCP) Apps Standard (SEP-1865)** over **Streamable HTTP (`POST /mcp`)**, Gemini Enterprise's built-in **Default Assistant** renders an interactive guest application (`ui://lexgraph/legal-grid-workspace.html`) directly inside the `<ucs-mcp-apps>` Picture-in-Picture (PiP) side panel or fullscreen surface.

---

## End-to-End SEP-1865 Handshake & Hydration Sequence

```text
┌──────────────────────────────────────────────────────────────────────────┐
│  1. USER PROMPT IN GEMINI ENTERPRISE DEFAULT ASSISTANT                   │
│     "Compare Indemnity Caps, Baskets, and Skadden Redlines across M-331" │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  2. DISCOVERY ENGINE CALLS POST /mcp (method: "tools/call")              │
│     • Tool: open_legal_analysis_grid(question, selected_doc_ids)         │
│     • Runs Cloud Spanner Hybrid RAG + Gemini dynamic column extraction   │
│     • Caches LATEST_WORKSPACE_STATE in memory                            │
│     • Returns:                                                           │
│       - content: [{type: "text", text: exec_md}]                         │
│       - structuredContent: state (documents, dynamic_columns, citations) │
│       - _meta.ui: {resourceUri: "ui://lexgraph/legal-grid-workspace.html",   │
│                    defaultDisplayMode: "pip"}                            │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  3. <ucs-mcp-apps> CALLS POST /mcp (method: "resources/read")            │
│     • Reads LATEST_WORKSPACE_STATE from memory in ~89ms (zero LLM wait)  │
│     • Returns hydrated HTML string (mimeType: "text/html;profile=mcp-app")│
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  4. GUEST IFRAME <-> HOST APPBRIDGE (window.postMessage JSON-RPC 2.0)    │
│     • Guest -> Host: ui/initialize & ui/notifications/initialized        │
│     • Guest -> Host: ui/request-display-mode ({mode: "pip"})             │
│     • Host -> Guest: ui/notifications/tool-result (structuredContent)    │
│     • Guest -> Host: ui/update-model-context (syncs checked [x] rows)    │
│     • Guest -> Host: ui/message (sends scoped follow-up to GE chat)      │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Critical `<ucs-mcp-apps>` Iframe Engineering Solutions

### 1. Preventing `scrollIntoView()` From Clipping the Iframe Header & Grid
- **Symptom**: Calling `highlightedElement.scrollIntoView({ behavior: "smooth", block: "center" })` inside a sandboxed iframe scrolls **all ancestor containers**, including the iframe's root `<html>` element. When `<body>` has `overflow: hidden`, scrolling `<html>` down by `350px` pushes the top header, filter bar, and Document Grid completely above the top edge of the iframe with no scrollbar to recover.
- **Fix Implemented in [`ui_template.py`](../mcp-app-grid-server/ui_template.py)**:
  1. Lock `html, body` with `position: fixed; inset: 0; width: 100%; height: 100%; overflow: hidden;` plus a passive `window.addEventListener("scroll", lockRootViewport)` guard.
  2. Scroll **only** the internal `#doc-paper-scroll` element using bounding-rect math:
     ```javascript
     const scrollEl = document.getElementById("doc-paper-scroll");
     const containerRect = scrollEl.getBoundingClientRect();
     const elemRect = highlighted.getBoundingClientRect();
     const offsetWithinScroll = (elemRect.top - containerRect.top) + scrollEl.scrollTop;
     const targetScrollTop = offsetWithinScroll - (scrollEl.clientHeight / 2) + (elemRect.height / 2);
     scrollEl.scrollTo({ top: Math.max(0, targetScrollTop), behavior: "smooth" });
     ```

### 2. Eliminating the 24-Second `<md-circular-progress>` Spinner on `resources/read`
- **Symptom**: Gemini Enterprise's `<ucs-mcp-apps>` component displays a blocking circular progress spinner while `fetchAppResource` calls `resources/read`. If `resources/read` triggers a fresh Spanner + LLM call, the user waits 24 seconds staring at a spinner *after* `tools/call` already finished.
- **Fix Implemented in [`app.py`](../mcp-app-grid-server/app.py)**:
  - `build_initial_workspace_state()` caches `LATEST_WORKSPACE_STATE` during `tools/call`. When `resources/read` arrives milliseconds later, it immediately renders `build_workspace_html(LATEST_WORKSPACE_STATE)` in **~89ms**.

### 3. Responsive Layout Across Right-Side PiP (`~680px`) & Fullscreen (`>1000px`)
- Added `[◫ Split | 📊 Grid | 📑 Citation Doc]` view-mode pills in the header bar.
- Replaced the bulky 235px chat dock with a compact 1-line `.scoped-qa-bar` at the bottom of the Grid pane and a `.synthesis-banner` with clickable citation chips at the top of the Original Contract Viewer.


### 4.4 Expanded Full-Screen Split Mode inside Gemini Enterprise
![Gemini Enterprise Fullscreen Split Grid and Citation](./screenshots/09_gemini_enterprise_fullscreen_split_grid_and_citation.png)
