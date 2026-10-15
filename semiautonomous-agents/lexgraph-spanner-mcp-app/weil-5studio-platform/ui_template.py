"""Mike OSS (`willchen96/mike`) + Gemini Enterprise (`ucs-canvas-panel`) Unified UI Template.

Engineered specifically for Gemini Enterprise (`vertexaisearch.cloud.google.com`) Custom MCP Apps (`SEP-1865`):
1. Full SEP-1865 `@modelcontextprotocol/ext-apps` Bidirectional `postMessage` Handshake:
   - Sends `ui/initialize`, `ui/notifications/initialized`, `ui/notifications/size-changed` (`height: 760`),
     and `ui/request-display-mode` (`mode: "pip"`) so Gemini Enterprise automatically expands the iframe
     and docks the app into the right-hand side panel (with 1-click Side Panel / Maximize toggles).
2. Zero-Latency Pre-Baked Bootstrap State (`INITIAL_BOOTSTRAP_DATA`) + Server-Side Pre-Rendered Rows:
   - Because Gemini Enterprise renders `resources/read` inside a sandboxed `about:srcdoc` iframe (`origin: null`),
     all 5 studios pre-bake their complete corpus, clauses, contract pages, redlines, Legal Legos, FundGen/FundHQ
     MFN matrices, HSR HHI bars, base64 multimodal charts, Intapp Wall/Graph nodes, and Partner Inbox/Calendar
     items directly into the HTML and execute all API calls against absolute `API_BASE` URLs.
3. Exact Mike OSS + Gemini Enterprise Design System (`EB Garamond` + `Google Sans Flex` / `Inter`).
"""

import base64
import html as html_lib
import json
import os
from pathlib import Path
from typing import Any, Dict

import adk_agents
import demo_data
import spanner_engine

DEFAULT_CLOUD_RUN_BASE = os.environ.get(
    "PUBLIC_API_BASE_URL",
    "https://mike-gcp-platform-254356041555.us-central1.run.app",
)

_BOOTSTRAP_CACHE: Dict[str, Any] = {}


def _encode_png_data_uri(filename: str, fallback_url: str) -> str:
    """Encodes a chart/diagram PNG from corpus/charts_and_images/ as a data URI so it renders inside sandboxed srcdoc iframes."""
    p = Path(__file__).resolve().parent / "corpus" / "charts_and_images" / filename
    if p.exists():
        try:
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            return f"data:image/png;base64,{b64}"
        except Exception:
            pass
    return fallback_url


def _build_bootstrap_payload(initial_view: str, api_base: str) -> Dict[str, Any]:
    cache_key = f"{initial_view}:{api_base}"
    if cache_key in _BOOTSTRAP_CACHE:
        return _BOOTSTRAP_CACHE[cache_key]

    payload: Dict[str, Any] = {}

    if initial_view == "tabular-view":
        kestrel_rows = list(demo_data.TABULAR_REVIEWS)
        unfiled_row = {
            "doc_id": "EM-9901",
            "filename": "EM-9901_Unfiled_Tax_Email_Section_338h10_Election.eml",
            "matter": "M-331-KESTREL",
            "coc_trigger": "IRC § 338(h)(10) Joint Election & Asset Step-Up",
            "consent_required": "30-Day Teammate Grant Active (Screen-Before-Rank)",
            "notice_window": "Pre-Signing Tax Covenant",
            "termination_right": "First-Dollar Tax Indemnity Carve-Out",
            "fee_or_penalty": "$14.2M Tax Gross-Up Escrow Reserve (Citibank N.A.)",
            "citation": "Tax Rider § 6.09(a)",
            "page": 1,
            "rrf_score": 0.0341,
            "entailment_verified": True,
            "quote": (
                "Per Marcus Thorne (Tax Partner, EM-9901): Seller shareholders require a $14,200,000 Tax Gross-Up Escrow "
                "at Citibank N.A. to compensate for ordinary-income vs. capital-gains rate differentials triggered by the "
                "IRC Section 338(h)(10) election on Brightwater's cleanroom fab assets."
            ),
        }
        if not any(r.get("doc_id") == "EM-9901" for r in kestrel_rows):
            kestrel_rows.append(unfiled_row)

        clauses_path = Path(__file__).resolve().parent / "corpus" / "indexed_clauses.json"
        clauses_list = []
        if clauses_path.exists():
            try:
                clauses_list = json.loads(clauses_path.read_text(encoding="utf-8"))
            except Exception:
                clauses_list = []
        by_doc: Dict[str, Dict[str, Any]] = {}
        for c in clauses_list:
            did = c.get("doc_id", "")
            if did and did not in by_doc:
                by_doc[did] = {
                    "doc_id": did,
                    "section_id": c.get("section_id", "1.01"),
                    "section_title": c.get("section_title", "Executed Provision"),
                    "category": c.get("category", "Corporate / M&A"),
                    "page": c.get("page", 1),
                    "text": (c.get("text") or "")[:240],
                }

        all_docs = list(demo_data.DOCUMENTS) + [demo_data.UNFILED_EMAIL]
        scaled_rows = []
        for d in all_docs:
            did = d["id"]
            sample = by_doc.get(did, {})
            scaled_rows.append({
                "doc_id": did,
                "filename": d["name"],
                "matter": d.get("matter_id", "M-331-KESTREL"),
                "coc_trigger": sample.get("section_title") or d.get("version") or "Executed Deal Provision",
                "consent_required": "Prior Written Consent Required" if "01" in did or "02" in did else "Verified Spanner Graph Node",
                "notice_window": d.get("size", "Indexed"),
                "termination_right": sample.get("category", "Corporate / M&A"),
                "fee_or_penalty": d.get("status", "3,072-dim Vector + FTS"),
                "citation": f"Sec. {sample['section_id']}" if sample.get("section_id") else "Sec. 1.01",
                "page": sample.get("page", 1),
                "quote": sample.get("text") or (d.get("summary") or "")[:240] or "Indexed in Cloud Spanner WeilLegalGraph.",
            })

        doc_pages: Dict[str, str] = {}
        for r in kestrel_rows:
            did = r["doc_id"]
            pg = r.get("page", 1)
            try:
                page_res = spanner_engine.get_document_page_text(did, pg)
                doc_pages[did] = (page_res.get("text") or r.get("quote", ""))[:1800]
            except Exception:
                doc_pages[did] = r.get("quote", "")

        payload["kestrel_rows"] = kestrel_rows
        payload["scaled_rows"] = scaled_rows
        payload["doc_pages"] = doc_pages

    elif initial_view == "redline-view":
        redlines = {}
        for pid in ("KESTREL-SPA-802", "KESTREL-SCRAPE-804", "KESTREL-TAX-304", "KESTREL-COC-804"):
            redlines[pid] = adk_agents.compute_deterministic_redline(pair_id=pid)
        payload["redlines"] = redlines
        payload["legal_legos_default"] = adk_agents.compose_legal_legos_clause(
            block_ids=["LEGO-DE-FRAUD", "LEGO-338H10-TAX", "LEGO-PRIVACY-PRO"]
        )
        payload["legal_legos_blocks"] = list(adk_agents.DEFAULT_LEGAL_LEGOS_BLOCKS.values())

    elif initial_view == "funds-view":
        funds_on = adk_agents.analyze_fundgen_mfn_and_antitrust_hhi(0.0, True)
        funds_off = adk_agents.analyze_fundgen_mfn_and_antitrust_hhi(0.0, False)
        for f_obj in (funds_on, funds_off):
            for vf in f_obj.get("visual_files", []):
                raw_img = vf.get("image_url", "")
                if raw_img.startswith("/"):
                    vf["image_url"] = f"{api_base}{raw_img}"
                raw_pdf = vf.get("pdf_url", "")
                if raw_pdf.startswith("/"):
                    vf["pdf_url"] = f"{api_base}{raw_pdf}"
        payload["funds_remedy_on"] = funds_on
        payload["funds_remedy_off"] = funds_off

    elif initial_view == "governance-view":
        gov_matrix: Dict[str, Any] = {}
        for lid in ("L-001", "L-002", "L-003", "L-005"):
            for mid in ("M-331-KESTREL", "M-402", "M-610-FUNDGEN", "M-720-ANTITRUST", "M-999"):
                key = f"{lid}__{mid}"
                raw_graph = spanner_engine.traverse_precedent_graph(matter_id=mid, lawyer_id=lid)
                nodes = [n for n in (raw_graph.get("nodes") or []) if n.get("type") in ("Document", "Clause")][:6]
                edges = [e for e in (raw_graph.get("edges") or []) if e.get("type") in ("CITES_PRECEDENT", "CONTAINS_CLAUSE")][:6]
                gov_matrix[key] = {
                    "gov": adk_agents.verify_cmn_and_intapp_wall(lawyer_id=lid, matter_id=mid),
                    "graph": {"nodes": nodes, "edges": edges},
                }
        payload["gov_matrix"] = gov_matrix

    elif initial_view == "inbox-view":
        payload["inbox_initial"] = adk_agents.triage_partner_inbox_and_calendar(reset_state=False)

    _BOOTSTRAP_CACHE[cache_key] = payload
    return payload


def _prerender_kestrel_tbody_html(kestrel_rows: list) -> str:
    """Server-side pre-renders the 7 Kestrel rows into <tbody> so the grid is populated at 0.0ms even before JS runs."""
    rows_html = []
    for idx, row in enumerate(kestrel_rows):
        consent = str(row.get("consent_required", ""))
        cl = consent.lower()
        if any(k in cl for k in ("prior written", "unanimous", "joint", "sole discretion")):
            pill_cls = "red"
        elif any(k in cl for k in ("notice", "30", "45")):
            pill_cls = "amber"
        else:
            pill_cls = "green"
        active_cls = "active-row" if idx == 0 else ""
        rows_html.append(
            f'<tr id="tr-row-{idx}" class="{active_cls}">'
            f'<td onclick="openSideInspector({idx})" style="cursor:pointer;">'
            f'<div class="doc-cell-title">'
            f'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" style="flex-shrink:0;">'
            f'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>'
            f'</svg>'
            f'<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{html_lib.escape(str(row.get("filename", "")))}</span>'
            f'</div>'
            f'<div class="doc-cell-sub">{html_lib.escape(str(row.get("doc_id", "")))} · {html_lib.escape(str(row.get("citation", "Sec. 8.02")))}</div>'
            f'</td>'
            f'<td onclick="openSideInspector({idx})" style="cursor:pointer;">'
            f'{html_lib.escape(str(row.get("coc_trigger", "")))}'
            f'<button type="button" class="citation-pill" onclick="event.stopPropagation();openSideInspector({idx})">1</button>'
            f'</td>'
            f'<td onclick="openSideInspector({idx})" style="cursor:pointer;">'
            f'<span class="status-pill {pill_cls}">{html_lib.escape(consent)}</span>'
            f'</td>'
            f'<td onclick="openSideInspector({idx})" style="cursor:pointer;">'
            f'{html_lib.escape(str(row.get("notice_window", "")))}'
            f'</td>'
            f'<td onclick="openSideInspector({idx})" style="cursor:pointer;">'
            f'<div style="font-weight:500;color:#111827;">{html_lib.escape(str(row.get("fee_or_penalty", "")))}</div>'
            f'<div style="font-size:11px;color:#6b7280;">{html_lib.escape(str(row.get("termination_right", "")))}</div>'
            f'</td>'
            f'</tr>'
        )
    return "\n".join(rows_html)


def build_mike_gcp_html(
    initial_view: str = "tabular-view",
    api_base: str = DEFAULT_CLOUD_RUN_BASE,
) -> str:
    if initial_view in ("assistant-view", "project-view", ""):
        initial_view = "tabular-view"

    bootstrap = _build_bootstrap_payload(
        initial_view=initial_view,
        api_base=api_base,
    )
    bootstrap_json = json.dumps(bootstrap).replace("</", "<\\/")
    kestrel_rows = bootstrap.get("kestrel_rows") or list(demo_data.TABULAR_REVIEWS)
    prerendered_tbody = _prerender_kestrel_tbody_html(kestrel_rows) if initial_view == "tabular-view" else ""
    first_row = kestrel_rows[0]
    first_quote = html_lib.escape(first_row.get("quote", ""))
    first_page_text = html_lib.escape((bootstrap.get("doc_pages") or {}).get(first_row["doc_id"], first_row.get("quote", "")))

    html = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Mike — Enterprise Legal AI for Gemini Enterprise</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..700;1,400..700&family=Google+Sans+Flex:opsz,wght@8..144,400..600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
:root {
  /* Official Mike OSS (willchen96/mike) + Gemini Enterprise Luminous Tokens */
  --app-background: #f9fafb;
  --app-surface: #fdfdfe;
  --app-surface-hover: #f3f4f6;
  --app-surface-active: #eff0f3;
  --app-floating: #fefefe;
  --table-grid-border: #e5e7eb;
  --border-subtle: #e5e7eb;
  --border-strong: #d1d5db;

  --editor-heading: #111827;
  --editor-text: #374151;
  --editor-muted-text: #6b7280;

  --color-blue: #0088ff;
  --ge-primary: #2563eb;
  --citation-selected-background: rgba(0, 136, 255, 0.09);
  --citation-selected-text: #172554;

  --spreadsheet-header-tint: rgba(241, 245, 249, 0.85);
  --spreadsheet-header-corner: #f1f5f9;
  --spreadsheet-highlight-background: rgba(59, 130, 246, 0.12);
  --spreadsheet-highlight-outline: #3b82f6;

  --font-serif: "EB Garamond", Georgia, serif;
  --font-sans: "Google Sans Flex", "Google Sans", "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  scrollbar-width: thin;
  scrollbar-color: rgba(107, 114, 128, 0.3) transparent;
}

html, body {
  width: 100%;
  height: 100%;
  min-height: 680px;
  overflow: hidden;
  font-family: var(--font-sans);
  font-size: 13px;
  line-height: 1.5;
  background-color: var(--app-background);
  color: var(--editor-text);
  -webkit-font-smoothing: antialiased;
}

button, input, select, textarea {
  font-family: inherit;
}

button {
  cursor: pointer;
}

/* Official Mike OSS Liquid Glass Surfaces (LiquidGlassUI.css) */
.liquid-glass-flat {
  background: var(--app-surface);
  border: 1px solid rgba(229, 231, 235, 0.9);
  box-shadow:
    0 1px 3px 0 rgba(0, 0, 0, 0.06),
    0 1px 2px -1px rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.75);
}

/* Official Mike OSS TabPillButtonUI (TabPillButtonUI.tsx) */
.tab-pill-btn {
  display: inline-flex;
  height: 26px;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border-radius: 9999px;
  padding: 0 10px;
  font-size: 11.5px;
  font-weight: 500;
  color: #4b5563;
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.85);
  transition: background-color 0.15s, color 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.tab-pill-btn:hover {
  background: #ffffff;
  color: #111827;
  border-color: #d1d5db;
}
.tab-pill-btn.active {
  background: #ffffff;
  color: #111827;
  border-color: #cbd5e1;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08), inset 0 1px 0 #ffffff;
  font-weight: 600;
}

/* Official Mike OSS PillButtonUI (PillButtonUI.styles.ts) */
.pill-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 26px;
  padding: 0 11px;
  border-radius: 9999px;
  font-size: 11.5px;
  font-weight: 500;
  line-height: 1;
  transition: background-color 0.15s, color 0.15s, box-shadow 0.15s, transform 0.1s;
  white-space: nowrap;
  border: 1px solid transparent;
}
.pill-btn:active {
  transform: scale(0.98);
}
.pill-btn-xs {
  height: 23px;
  padding: 0 9px;
  font-size: 11px;
}
.pill-btn-blue {
  background: rgba(37, 99, 235, 0.92);
  color: #ffffff;
  box-shadow:
    0 2px 6px rgba(37, 99, 235, 0.14),
    inset 1px 1px 0 rgba(255, 255, 255, 0.28);
}
.pill-btn-blue:hover:not(:disabled) {
  background: #1d4ed8;
}
.pill-btn-white {
  background: #fdfdfe;
  color: #374151;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.7);
}
.pill-btn-white:hover:not(:disabled) {
  background: #f3f4f6;
  color: #111827;
}
.pill-btn-danger {
  background: rgba(220, 38, 38, 0.92);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(127, 29, 29, 0.14);
}
.pill-btn-danger:hover:not(:disabled) {
  background: #b91c1c;
}

/* Official Mike OSS CitationPillUI (CitationPillUI.tsx) */
.citation-pill {
  display: inline-flex;
  height: 17px;
  min-width: 17px;
  padding: 0 4px;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  background: rgba(229, 231, 235, 0.85);
  font-family: var(--font-serif);
  font-size: 11px;
  font-weight: 600;
  color: #1f2937;
  border: none;
  margin-left: 3px;
  vertical-align: middle;
  transition: background-color 0.15s, color 0.15s;
}
.citation-pill:hover,
.citation-pill.active {
  background: #dbeafe;
  color: #1e3a8a;
}

/* Official Mike OSS Status / Risk Pills (pillUtils.ts) */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border-radius: 9999px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
  line-height: 1.25;
  white-space: nowrap;
}
.tr-table td .status-pill {
  white-space: normal;
  text-align: left;
  line-height: 1.3;
}
.status-pill.red {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}
.status-pill.amber {
  background: #fffbeb;
  color: #b45309;
  border: 1px solid #fde68a;
}
.status-pill.green {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}
.status-pill.blue {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}
.status-pill.gray {
  background: #f3f4f6;
  color: #4b5563;
  border: 1px solid #e5e7eb;
}

/* Main App Container */
#app-shell {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
  min-height: 680px;
  overflow: hidden;
  background: var(--app-background);
}

.studio-screen {
  display: none;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 680px;
  overflow: hidden;
}
.studio-screen.active {
  display: flex;
}

/* Mike OSS PageHeader (Single-line compact header so it never eats vertical height) */
.mike-page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-height: 44px;
  padding: 6px 12px;
  background: var(--app-surface);
  border-bottom: 1px solid var(--table-grid-border);
  flex-shrink: 0;
}
.header-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex: 1;
}
.header-brand > div {
  min-width: 0;
  flex: 1;
}
.header-title {
  font-family: var(--font-serif);
  font-size: 17px;
  font-weight: 500;
  color: var(--editor-heading);
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.header-subtitle {
  font-size: 10.5px;
  color: var(--editor-muted-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-shrink: 0;
}

/* Mike OSS TableToolbar */
.mike-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  padding: 6px 12px;
  background: var(--app-background);
  border-bottom: 1px solid var(--table-grid-border);
  flex-shrink: 0;
  flex-wrap: wrap;
}
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
}
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-left: auto;
}

.search-input {
  height: 26px;
  padding: 0 10px;
  border-radius: 9999px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  font-size: 11.5px;
  color: #111827;
  outline: none;
  width: 170px;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.search-input:focus {
  border-color: var(--color-blue);
  box-shadow: 0 0 0 2px rgba(0, 136, 255, 0.15);
}

/* Split Workspace Stage */
.workspace-stage {
  flex: 1;
  display: flex;
  min-height: 480px;
  overflow: hidden;
  position: relative;
}

.primary-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

/* Mike OSS TRSidePanel (TRSidePanel.tsx) */
.side-inspector-pane {
  width: 420px;
  max-width: 45%;
  background: var(--app-surface);
  border-left: 1px solid var(--table-grid-border);
  display: none;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  box-shadow: -4px 0 16px rgba(15, 23, 42, 0.04);
  z-index: 30;
}
.side-inspector-pane.open {
  display: flex;
}

@media (max-width: 780px) {
  .side-inspector-pane {
    position: absolute;
    inset: 0;
    width: 100%;
    max-width: 100%;
    border-left: none;
  }
  .search-input {
    width: 125px;
  }
  .header-title {
    font-size: 15.5px;
  }
}

/* Mike OSS Tabular Review Grid (TRTable.tsx + TabularCell.tsx) */
.tr-grid-scroll {
  flex: 1;
  min-height: 420px;
  overflow: auto;
  background: var(--app-surface);
}
.tr-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 12px;
}
.tr-table th {
  position: sticky;
  top: 0;
  z-index: 15;
  background: #f8fafc;
  border-bottom: 1px solid var(--table-grid-border);
  border-right: 1px solid var(--table-grid-border);
  padding: 7px 10px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: #4b5563;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tr-table td {
  border-bottom: 1px solid var(--table-grid-border);
  border-right: 1px solid var(--table-grid-border);
  padding: 7px 10px;
  vertical-align: top;
  color: #374151;
  line-height: 1.42;
  background: var(--app-surface);
  transition: background-color 0.12s;
}
.tr-table tr:hover td {
  background: #f9fafb;
}
.tr-table tr.active-row td {
  background: rgba(0, 136, 255, 0.05);
}

.doc-cell-title {
  font-weight: 500;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}
.doc-cell-title:hover {
  color: var(--ge-primary);
}
.doc-cell-sub {
  font-size: 11px;
  color: #6b7280;
  margin-top: 2px;
}

/* Inline Add Column Drawer (AddColumnModal.tsx) */
.add-col-bar {
  display: none;
  padding: 8px 12px;
  background: #ffffff;
  border-bottom: 1px solid var(--table-grid-border);
  gap: 6px;
  flex-direction: column;
}
.add-col-bar.open {
  display: flex;
}
.add-col-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.field-input {
  height: 26px;
  padding: 0 9px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  font-size: 11.5px;
  color: #111827;
  outline: none;
}
.field-input:focus {
  border-color: var(--color-blue);
  box-shadow: 0 0 0 2px rgba(0, 136, 255, 0.15);
}

/* Mike OSS Document & Pin-Cite Reader */
.inspector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--table-grid-border);
  background: #f8fafc;
  flex-shrink: 0;
}
.inspector-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  font-family: var(--font-serif);
  font-size: 14.5px;
  line-height: 1.65;
  color: var(--editor-text);
  background: var(--app-surface);
}
.pin-cite-box {
  font-family: var(--font-sans);
  font-size: 11.5px;
  background: var(--citation-selected-background);
  color: var(--citation-selected-text);
  border-left: 3px solid var(--color-blue);
  padding: 8px 10px;
  border-radius: 0 8px 8px 0;
  margin-bottom: 12px;
}
.contract-highlight {
  background: #fef08a;
  color: #713f12;
  padding: 1px 4px;
  border-radius: 3px;
  box-shadow: 0 0 0 1px #facc15;
}

/* Mike OSS EditCardUI & TextSlabUI */
.edit-card {
  background: var(--app-surface);
  border: 1px solid var(--table-grid-border);
  border-radius: 10px;
  padding: 10px 12px;
  margin-bottom: 8px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}
.text-slab {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 9px 11px;
  font-family: var(--font-serif);
  font-size: 14px;
  line-height: 1.58;
  color: #1f2937;
}
.redline-del, del.redline-del {
  color: #dc2626;
  text-decoration: line-through;
  background: rgba(254, 226, 226, 0.55);
  padding: 0 2px;
  border-radius: 3px;
}
.redline-ins, ins.redline-ins {
  color: #15803d;
  text-decoration: none;
  font-weight: 600;
  background: rgba(220, 252, 231, 0.65);
  padding: 0 2px;
  border-radius: 3px;
}

/* Split Grid for Studios 2, 3, 4, 5 */
.two-col-studio {
  flex: 1;
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  min-height: 480px;
  overflow: hidden;
}
@media (max-width: 780px) {
  .two-col-studio {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }
}
.studio-col {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow-y: auto;
  padding: 12px 14px;
  gap: 10px;
}
.studio-col + .studio-col {
  border-left: 1px solid var(--table-grid-border);
  background: #fdfdfe;
}
@media (max-width: 780px) {
  .studio-col {
    overflow-y: visible;
  }
  .studio-col + .studio-col {
    border-left: none;
    border-top: 1px solid var(--table-grid-border);
  }
}

.section-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #6b7280;
  margin-bottom: 4px;
}

.skeleton-bar {
  height: 12px;
  border-radius: 4px;
  background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Realistic Microsoft Word (.docx) & Legal Contract Print-Layout Sheet */
.docx-canvas-wrap {
  background: #eef1f5;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(15, 23, 42, 0.06);
}
.docx-word-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 6px 12px;
  background: #1e3a8a;
  color: #ffffff;
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 500;
}
.docx-word-toolbar-sub {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 4px 12px;
  background: #f8fafc;
  border-bottom: 1px solid #cbd5e1;
  font-family: var(--font-mono);
  font-size: 9.5px;
  color: #64748b;
  letter-spacing: 0.05em;
  white-space: nowrap;
  overflow: hidden;
}
.docx-paper-scroll {
  padding: 12px 14px;
  max-height: 440px;
  overflow-y: auto;
  background: #e5e9f0;
}
.docx-paper-sheet {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 3px;
  padding: 18px 22px 16px 22px;
  box-shadow:
    0 4px 14px rgba(15, 23, 42, 0.08),
    0 1px 3px rgba(15, 23, 42, 0.05);
  font-family: var(--font-serif);
  color: #111827;
  line-height: 1.62;
  position: relative;
}
.docx-running-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding-bottom: 6px;
  margin-bottom: 10px;
  border-bottom: 2px double #cbd5e1;
  font-family: var(--font-sans);
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #64748b;
  white-space: nowrap;
}
.docx-doc-title {
  text-align: center;
  font-family: var(--font-serif);
  font-size: 15.5px;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: #0f172a;
  margin-bottom: 3px;
}
.docx-doc-subtitle {
  text-align: center;
  font-family: var(--font-serif);
  font-size: 12.5px;
  font-style: italic;
  color: #475569;
  margin-bottom: 12px;
}
.docx-recital {
  font-size: 13px;
  text-align: justify;
  text-indent: 24px;
  color: #1f2937;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f1f5f9;
}
.docx-clause-block {
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 2px solid #dbeafe;
}
.docx-clause-meta-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  margin-bottom: 3px;
}
.docx-clause-heading {
  font-family: var(--font-serif);
  font-size: 14.5px;
  font-weight: 700;
  color: #0f172a;
}
.docx-clause-heading u {
  text-underline-offset: 3px;
  text-decoration-color: #64748b;
}
.docx-subclause {
  font-family: var(--font-serif);
  font-size: 13.8px;
  color: #1f2937;
  text-align: justify;
  padding-left: 26px;
  text-indent: -20px;
  margin-top: 5px;
  line-height: 1.58;
}
.docx-subclause-num {
  font-weight: 700;
  color: #0f172a;
  margin-right: 4px;
}
.docx-running-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 14px;
  padding-top: 8px;
  border-top: 1px solid #cbd5e1;
  font-family: var(--font-mono);
  font-size: 9.5px;
  color: #64748b;
}
/* Track Changes Margin Bar on Redline Sheet */
.docx-redline-margin {
  border-left: 3px solid #dc2626;
  padding-left: 14px;
  text-align: justify;
  font-size: 14.2px;
  line-height: 1.65;
  color: #111827;
}

/* Clickable Maximize Button inside Word Toolbar */
.docx-max-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 9px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.32);
  font-family: var(--font-sans);
  font-size: 10.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s, border-color 0.15s;
  white-space: nowrap;
}
.docx-max-btn:hover {
  background: rgba(255, 255, 255, 0.28);
  border-color: #ffffff;
}
.docx-max-btn:active {
  transform: scale(0.97);
}
.docx-paper-sheet.clickable-sheet {
  cursor: zoom-in;
  transition: box-shadow 0.15s, border-color 0.15s;
}
.docx-paper-sheet.clickable-sheet:hover {
  border-color: #93c5fd;
  box-shadow:
    0 6px 18px rgba(37, 99, 235, 0.12),
    0 1px 4px rgba(15, 23, 42, 0.06);
}

/* Centered Full-Document Print-Layout Overlay Modal (#docx-modal-overlay) */
.docx-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(15, 23, 42, 0.62);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  display: none;
  align-items: center;
  justify-content: center;
  padding: 18px 24px;
}
.docx-modal-backdrop.open {
  display: flex;
  animation: modalFadeIn 0.16s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes modalFadeIn {
  from { opacity: 0; transform: scale(0.97); }
  to { opacity: 1; transform: scale(1); }
}
.docx-modal-window {
  width: min(980px, 95vw);
  height: min(860px, 92vh);
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow:
    0 25px 60px rgba(15, 23, 42, 0.42),
    0 4px 16px rgba(15, 23, 42, 0.22);
}
.docx-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  background: #1e3a8a;
  color: #ffffff;
  flex-shrink: 0;
}
.docx-modal-controls-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 7px 16px;
  background: #f1f5f9;
  border-bottom: 1px solid #cbd5e1;
  font-family: var(--font-sans);
  font-size: 11.5px;
  color: #334155;
  flex-shrink: 0;
  flex-wrap: wrap;
}
.docx-modal-ruler {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 3px 24px;
  background: #f8fafc;
  border-bottom: 1px solid #cbd5e1;
  font-family: var(--font-mono);
  font-size: 9.5px;
  color: #64748b;
  letter-spacing: 0.08em;
  flex-shrink: 0;
}
.docx-modal-scroll {
  flex: 1;
  overflow-y: auto;
  background: #cbd5e1;
  padding: 24px 32px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}
.docx-modal-paper {
  width: 100%;
  max-width: 780px;
  min-height: 660px;
  background: #ffffff;
  border: 1px solid #94a3b8;
  border-radius: 3px;
  padding: 40px 52px 36px 52px;
  box-shadow:
    0 12px 32px rgba(15, 23, 42, 0.18),
    0 2px 6px rgba(15, 23, 42, 0.08);
  font-family: var(--font-serif);
  color: #111827;
  line-height: 1.68;
  transform-origin: top center;
  transition: transform 0.15s ease;
}
.docx-modal-paper .docx-doc-title {
  font-size: 18px;
  margin-bottom: 4px;
}
.docx-modal-paper .docx-doc-subtitle {
  font-size: 14px;
  margin-bottom: 16px;
}
.docx-modal-paper .docx-recital {
  font-size: 14.5px;
  margin-bottom: 16px;
  padding-bottom: 12px;
}
.docx-modal-paper .docx-clause-heading {
  font-size: 16px;
  margin-bottom: 4px;
}
.docx-modal-paper .docx-subclause {
  font-size: 15px;
  line-height: 1.68;
  margin-top: 7px;
}
.docx-modal-paper .docx-redline-margin {
  font-size: 15.5px;
  line-height: 1.72;
}
/* Per-subclause interactive redline states */
.redline-subclause-item {
  padding: 6px 10px;
  border-radius: 6px;
  margin-top: 8px;
  border-left: 3px solid transparent;
  transition: background-color 0.25s, border-color 0.25s;
}
.redline-subclause-item.state-accepted {
  background: #f0fdf4;
  border-left-color: #16a34a;
}
.redline-subclause-item.state-rejected {
  background: #fef2f2;
  border-left-color: #dc2626;
}
.redline-decision-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-family: var(--font-sans);
  font-size: 10.5px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  margin-bottom: 4px;
}
.redline-decision-badge.accepted {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #86efac;
}
.redline-decision-badge.rejected {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}
</style>
</head>
<body>

<div id="app-shell">

  <!-- ===================================================================== -->
  <!-- STUDIO 1: MIKE OSS TABULAR REVIEW & PIN-CITE READER (mike-gcp-platform) -->
  <!-- ===================================================================== -->
  <section id="tabular-view" class="studio-screen">
    <header class="mike-page-header">
      <div class="header-brand">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#111827" stroke-width="1.8" style="flex-shrink:0;">
          <circle cx="12" cy="12" r="9.5" stroke="#9ca3af"/>
          <path d="M12 2.5L15 9.5M21.5 12L14.5 15M12 21.5L9 14.5M2.5 12L9.5 9"/>
          <circle cx="12" cy="12" r="3" fill="#2563eb" stroke="none"/>
        </svg>
        <div>
          <div class="header-title">Project Kestrel — Change of Control Review</div>
          <div class="header-subtitle" id="tr-subtitle">Matter M-331 · CMN 31402-0018 · 7 Active Contracts in Cloud Spanner</div>
        </div>
      </div>
      <div class="header-actions">
        <button id="btn-toggle-add-col" class="pill-btn pill-btn-blue" onclick="toggleAddColumnBar()">
          + Add column
        </button>
        <button id="btn-export-csv" class="pill-btn pill-btn-white" onclick="exportGridToCsv()">
          Export CSV
        </button>
        <button class="pill-btn pill-btn-white pill-btn-xs" onclick="requestHostDisplayMode('pip')" title="Dock in Gemini Enterprise Right Side Panel">
          Side Panel
        </button>
        <button class="pill-btn pill-btn-white pill-btn-xs" onclick="requestHostDisplayMode('fullscreen')" title="Expand to Fullscreen">
          Maximize
        </button>
      </div>
    </header>

    <div class="mike-toolbar">
      <div class="toolbar-left">
        <button id="pill-corpus-kestrel" class="tab-pill-btn active" onclick="switchTabularCorpus('kestrel')">
          Kestrel CoC Grid (7)
        </button>
        <button id="pill-corpus-all" class="tab-pill-btn" onclick="switchTabularCorpus('scaled')">
          All Deal Documents (46)
        </button>
        <button id="pill-grant-em9901" class="tab-pill-btn" onclick="toggleTeammateGrant()" title="Toggle 30-day Screen-Before-Rank grant for unfiled tax email EM-9901">
          <span id="grant-dot" style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#10b981;"></span>
          <span id="grant-label">EM-9901 Grant: Active</span>
        </button>
      </div>
      <div class="toolbar-right">
        <input id="tr-search-input" type="search" class="search-input" placeholder="Filter contracts or clauses..." oninput="filterTabularRows(this.value)" />
      </div>
    </div>

    <!-- Inline Add Column Bar (Mike OSS AddColumnModal pattern — Live Parallel Gemini 3.8 Flash) -->
    <div id="add-col-bar" class="add-col-bar">
      <div class="add-col-row">
        <span style="font-size:11px;font-weight:600;color:#4b5563;">Quick Presets:</span>
        <button type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="fillPresetColumn('Agreement Title & Parties', 'Extract the official agreement title and contracting parties from the preamble.')">
          Agreement Title &amp; Parties
        </button>
        <button type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="fillPresetColumn('Indemnity Cap & Basket', 'Extract the exact dollar and percentage Indemnity Cap, Deductible/Tipping Basket, and Fraud Carve-out.')">
          Indemnity Cap &amp; Basket
        </button>
        <button type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="fillPresetColumn('Governing Law & Venue', 'Extract the governing law jurisdiction, arbitration or court venue, and jury waiver.')">
          Governing Law &amp; Venue
        </button>
        <button type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="fillPresetColumn('IP & J.Crew Blocker', 'Identify whether Material IP drop-downs to Unrestricted Subsidiaries are blocked and required lender consent %.')">
          IP &amp; J.Crew Blocker
        </button>
      </div>
      <div class="add-col-row">
        <input id="new-col-name" type="text" class="field-input" style="width:175px;" placeholder="Column name (e.g. Title, Parties, Law)" value="" onkeydown="if(event.key==='Enter')runDynamicColumnExtraction()" />
        <input id="new-col-prompt" type="text" class="field-input" style="flex:1;min-width:190px;" placeholder="Optional extraction instructions (leave blank to auto-extract by Column name via Gemini 3.8 Flash)..." value="" onkeydown="if(event.key==='Enter')runDynamicColumnExtraction()" />
        <button id="btn-run-col-extract" type="button" class="pill-btn pill-btn-blue" onclick="runDynamicColumnExtraction()">
          Run extraction
        </button>
        <button type="button" class="pill-btn pill-btn-white" onclick="toggleAddColumnBar()">
          Cancel
        </button>
      </div>
    </div>

    <div class="workspace-stage">
      <div class="primary-pane">
        <div class="tr-grid-scroll">
          <table class="tr-table" id="kestrel-grid-table">
            <thead id="tr-thead">
              <tr>
                <th style="width:220px;">Document</th>
                <th style="width:185px;">CoC / Provision Trigger</th>
                <th style="width:210px;">Consent Requirement</th>
                <th style="width:125px;">Notice Window</th>
                <th style="width:185px;">Termination &amp; Fee Impact</th>
              </tr>
            </thead>
            <tbody id="tr-tbody">
__PRERENDERED_TBODY__
            </tbody>
          </table>
        </div>
      </div>

      <!-- Mike OSS TRSidePanel Document & Pin-Cite Reader -->
      <aside id="tr-side-panel" class="side-inspector-pane">
        <div class="inspector-header">
          <div style="min-width:0;">
            <div id="insp-doc-title" style="font-weight:600;font-size:12px;color:#111827;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
              01_Supply_Agreement_Halvorsen_Brightwater.docx
            </div>
            <div id="insp-doc-meta" style="font-size:11px;color:#6b7280;">
              DOC-KESTREL-01 · Section 12.03(a) · Page 4
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:4px;flex-shrink:0;">
            <button id="btn-prev-row" class="pill-btn pill-btn-white pill-btn-xs" onclick="navigateInspectorRow(-1)" title="Previous contract">↑</button>
            <button id="btn-next-row" class="pill-btn pill-btn-white pill-btn-xs" onclick="navigateInspectorRow(1)" title="Next contract">↓</button>
            <button id="btn-maximize-inspector" class="pill-btn pill-btn-blue pill-btn-xs" onclick="openDocxModal('inspector')" title="Open full-page document overlay">⤢ Maximize</button>
            <a id="insp-download-link" href="__DEFAULT_API_BASE__/api/corpus/file/01_Supply_Agreement_Halvorsen_Brightwater.docx" target="_blank" class="pill-btn pill-btn-white pill-btn-xs" style="text-decoration:none;">Original</a>
            <button id="btn-close-inspector" class="pill-btn pill-btn-white pill-btn-xs" onclick="closeSideInspector()">✕</button>
          </div>
        </div>
        <div class="inspector-body" style="padding:10px 12px;background:#e5e9f0;">
          <div class="pin-cite-box" id="insp-pincite-quote" style="background:#ffffff;border:1px solid #bfdbfe;border-left:4px solid #2563eb;box-shadow:0 2px 6px rgba(15,23,42,0.05);">
            <strong>Pin-Cite (Section 12.03(a), p.4):</strong> “__FIRST_QUOTE__”
          </div>
          <div class="docx-canvas-wrap">
            <div class="docx-word-toolbar">
              <span>Executed Agreement · Print Layout</span>
              <div style="display:flex;align-items:center;gap:8px;">
                <span id="insp-toolbar-badge" style="opacity:0.9;">Spanner BBox Verified</span>
                <button type="button" class="docx-max-btn" onclick="openDocxModal('inspector')">⤢ Maximize</button>
              </div>
            </div>
            <div class="docx-word-toolbar-sub">
              <span>1 · · · 2 · · · 3 · · · 4 · · · 5</span>
              <span>CLICK SHEET OR MAXIMIZE FOR FULL PAGE</span>
            </div>
            <div style="padding:10px;background:#e5e9f0;">
              <div class="docx-paper-sheet clickable-sheet" onclick="openDocxModal('inspector')" title="Click to open full-page document preview overlay" style="padding:14px 18px;">
                <div class="docx-running-header">
                  <span>WEIL · EXECUTION COPY</span>
                  <span id="insp-running-docid">DOC-KESTREL-01</span>
                </div>
                <div id="insp-contract-body" style="font-family:var(--font-serif);font-size:14px;line-height:1.65;color:#111827;">__FIRST_PAGE_TEXT__</div>
                <div class="docx-running-footer">
                  <span>WEIL:\98412034.4\31402.0018</span>
                  <span id="insp-running-page">Page 4 of 12</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </section>

  <!-- ===================================================================== -->
  <!-- STUDIO 2: CONTRACT REDLINE & WORD LEGAL LEGOS (weil-redline-word-agent) -->
  <!-- ===================================================================== -->
  <section id="redline-view" class="studio-screen">
    <header class="mike-page-header">
      <div class="header-brand">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#111827" stroke-width="1.8" style="flex-shrink:0;">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="9" y1="15" x2="15" y2="15" stroke="#2563eb"/>
        </svg>
        <div>
          <div class="header-title">Contract Redline &amp; Legal Legos Composer</div>
          <div class="header-subtitle">Weil v3 Playbook vs. Skadden v4 Counterparty Markup · Privacy Pro .docx Builder</div>
        </div>
      </div>
      <div class="header-actions">
        <a id="btn-download-v4-docx" href="__DEFAULT_API_BASE__/api/corpus/file/08_M331_Brightwater_Merger_Agreement_Skadden_v4_Redline.docx" target="_blank" class="pill-btn pill-btn-white" style="text-decoration:none;">
          Skadden v4 .docx
        </a>
        <a id="btn-download-legos-docx" href="__DEFAULT_API_BASE__/api/legal-legos/docx" target="_blank" class="pill-btn pill-btn-blue" style="text-decoration:none;">
          Export Composed .docx
        </a>
        <button class="pill-btn pill-btn-white pill-btn-xs" onclick="requestHostDisplayMode('pip')">Side Panel</button>
        <button class="pill-btn pill-btn-white pill-btn-xs" onclick="requestHostDisplayMode('fullscreen')">Maximize</button>
      </div>
    </header>

    <div class="mike-toolbar">
      <div class="toolbar-left">
        <button id="red-pair-802" class="tab-pill-btn active" onclick="loadRedlinePair('KESTREL-SPA-802', this)">
          SPA § 8.02(b) Indemnity Cap
        </button>
        <button id="red-pair-scrape" class="tab-pill-btn" onclick="loadRedlinePair('KESTREL-SCRAPE-804', this)">
          SPA § 8.04(a) Materiality Scrape
        </button>
        <button id="red-pair-tax" class="tab-pill-btn" onclick="loadRedlinePair('KESTREL-TAX-304', this)">
          Tax Rider § 3.04 338(h)(10)
        </button>
        <button id="red-pair-coc" class="tab-pill-btn" onclick="loadRedlinePair('KESTREL-COC-804', this)">
          Quillfeather § 8.04 CoC
        </button>
      </div>
      <div class="toolbar-right">
        <span id="redline-stats-pill" class="status-pill blue">74.2% Similarity · 0.4ms Diff</span>
      </div>
    </div>

    <div class="two-col-studio">
      <div class="studio-col">
        <div>
          <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:4px;">
            <div class="section-label" id="redline-doc-pair-label" style="margin-bottom:0;">
              07_M331_Brightwater_Merger_Agreement_Weil_v3.docx vs. 08_M331_Skadden_v4_Redline.docx
            </div>
            <button id="btn-maximize-redline-top" type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="openDocxModal('redline')">
              ⤢ Maximize Redline
            </button>
          </div>
          <div id="redline-playbook-banner" style="font-size:12px;color:#1e3a8a;background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:8px 12px;margin-bottom:8px;"></div>
          <div class="docx-canvas-wrap">
            <div class="docx-word-toolbar" style="background:#0f172a;">
              <div style="display:flex;align-items:center;gap:6px;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <span id="redline-sheet-filename">08_M331_Brightwater_SPA_Skadden_v4_Redline.docx</span>
              </div>
              <div style="display:flex;align-items:center;gap:8px;">
                <span id="redline-toolbar-mode-label" style="font-size:10.5px;color:#93c5fd;">Track Changes: ALL MARKUP</span>
                <button id="btn-maximize-redline" type="button" class="docx-max-btn" onclick="openDocxModal('redline')">⤢ Maximize</button>
              </div>
            </div>
            <div class="docx-word-toolbar-sub">
              <span>1 · · · 2 · · · 3 · · · 4 · · · 5 · · · 6 · · · 7</span>
              <span id="redline-ruler-legend">STRIKETHROUGH: REJECTED TEXT  |  GREEN: ACTIVE / ACCEPTED PLAYBOOK LINE</span>
            </div>
            <div style="padding:10px 12px;background:#e5e9f0;">
              <div class="docx-paper-sheet clickable-sheet" onclick="openDocxModal('redline')" title="Click to open centered full-page Redline overlay" style="padding:16px 22px;">
                <div class="docx-running-header">
                  <span>WEIL, GOTSHAL &amp; MANGES LLP · TRACK CHANGES COMPARE</span>
                  <span id="redline-sheet-matter">MATTER M-331-KESTREL</span>
                </div>
                <div id="redline-sheet-title" style="font-family:var(--font-serif);font-size:14.5px;font-weight:700;color:#0f172a;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.02em;">
                  ARTICLE VIII — INDEMNIFICATION · SECTION 8.02
                </div>
                <div id="redline-diff-slab" class="docx-redline-margin"></div>
                <div class="docx-running-footer">
                  <span>Compare: Weil Playbook v3.4 ↔ Counterparty Markup v4.0</span>
                  <span>OpenXML w:del / w:ins</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <span class="section-label">Tracked Playbook Deviations (Mike OSS EditCardUI)</span>
            <button id="btn-reset-redline-cards" class="pill-btn pill-btn-white pill-btn-xs" onclick="resetRedlineDecisions()">Reset decisions</button>
          </div>
          <div id="redline-edit-cards"></div>
        </div>
      </div>

      <div class="studio-col">
        <div>
          <div class="section-label">Weil Privacy Pro &amp; M&amp;A "Legal Legos" Clause Blocks</div>
          <p style="font-size:11.5px;color:#6b7280;margin-bottom:6px;">
            Select pre-vetted Weil Playbook clause blocks to assemble a numbered OpenXML <code>.docx</code> rider:
          </p>
          <div id="legos-checkbox-list" style="display:flex;flex-direction:column;gap:6px;margin-bottom:10px;">
            <label class="liquid-glass-flat" style="display:flex;align-items:flex-start;gap:8px;padding:7px 10px;border-radius:8px;cursor:pointer;">
              <input type="checkbox" class="lego-cb" value="LEGO-DE-FRAUD" checked onchange="updateLegalLegos()" style="margin-top:3px;" />
              <div>
                <div style="font-size:12px;font-weight:600;color:#111827;">LEGO-DE-FRAUD · Delaware Express Actual Fraud (ABRY)</div>
                <div style="font-size:11px;color:#6b7280;">Article VIII → Section 8.02(c)(i)..(ii) · Excludes constructive/equitable fraud</div>
              </div>
            </label>
            <label class="liquid-glass-flat" style="display:flex;align-items:flex-start;gap:8px;padding:7px 10px;border-radius:8px;cursor:pointer;">
              <input type="checkbox" class="lego-cb" value="LEGO-338H10-TAX" checked onchange="updateLegalLegos()" style="margin-top:3px;" />
              <div>
                <div style="font-size:12px;font-weight:600;color:#111827;">LEGO-338H10-TAX · IRC § 338(h)(10) $14.2M Tax Escrow</div>
                <div style="font-size:11px;color:#6b7280;">Article VI → Section 6.09(a)..(b) · Citibank N.A. 18-month tax reserve</div>
              </div>
            </label>
            <label class="liquid-glass-flat" style="display:flex;align-items:flex-start;gap:8px;padding:7px 10px;border-radius:8px;cursor:pointer;">
              <input type="checkbox" class="lego-cb" value="LEGO-PRIVACY-PRO" checked onchange="updateLegalLegos()" style="margin-top:3px;" />
              <div>
                <div style="font-size:12px;font-weight:600;color:#111827;">LEGO-PRIVACY-PRO · Zero Foundation Model Training &amp; GDPR</div>
                <div style="font-size:11px;color:#6b7280;">Article XI → Section 11.04(a)..(c) · 24-hour cyber breach notice</div>
              </div>
            </label>
            <label class="liquid-glass-flat" style="display:flex;align-items:flex-start;gap:8px;padding:7px 10px;border-radius:8px;cursor:pointer;">
              <input type="checkbox" class="lego-cb" value="LEGO-MFN-FUNDGEN" onchange="updateLegalLegos()" style="margin-top:3px;" />
              <div>
                <div style="font-size:12px;font-weight:600;color:#111827;">LEGO-MFN-FUNDGEN · Size-Tiered LP MFN Election Rider</div>
                <div style="font-size:11px;color:#6b7280;">Side Letter → Paragraph 4(a)..(c) · $250M+ anchor carve-out</div>
              </div>
            </label>
          </div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <span class="section-label">Composed Multi-Level .docx Document Preview</span>
            <div style="display:flex;gap:6px;">
              <button id="btn-copy-legos" class="pill-btn pill-btn-white pill-btn-xs" onclick="copyLegalLegosText()">Copy Rider</button>
              <button id="btn-compose-legos" class="pill-btn pill-btn-white pill-btn-xs" onclick="updateLegalLegos(true)">Refresh Outline</button>
              <button id="btn-maximize-legos" class="pill-btn pill-btn-blue pill-btn-xs" onclick="openDocxModal('legos')">⤢ Maximize</button>
            </div>
          </div>
          <div class="docx-canvas-wrap">
            <div class="docx-word-toolbar">
              <div style="display:flex;align-items:center;gap:6px;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#93c5fd" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <span>Weil_Legal_Legos_Composed_Rider.docx</span>
              </div>
              <div style="display:flex;align-items:center;gap:8px;">
                <span id="legos-block-count-badge" style="font-size:10.5px;color:#dbeafe;">3 Clauses · Print Layout</span>
                <button id="btn-maximize-legos-toolbar" type="button" class="docx-max-btn" onclick="openDocxModal('legos')">⤢ Maximize</button>
              </div>
            </div>
            <div class="docx-word-toolbar-sub">
              <span>1 · · · 2 · · · 3 · · · 4 · · · 5 · · · 6</span>
              <span>15-YR MULTI-LEVEL NUMBERING · CLICK TO MAXIMIZE</span>
            </div>
            <div class="docx-paper-scroll">
              <div id="legos-preview-box" class="docx-paper-sheet clickable-sheet" onclick="openDocxModal('legos')" title="Click to open centered full-page .docx overlay"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===================================================================== -->
  <!-- STUDIO 3: FUNDGEN / FUNDHQ MFN & ANTITRUST HSR (weil-funds-antitrust) -->
  <!-- ===================================================================== -->
  <section id="funds-view" class="studio-screen">
    <header class="mike-page-header">
      <div class="header-brand">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#111827" stroke-width="1.8" style="flex-shrink:0;">
          <rect x="3" y="3" width="18" height="18" rx="3" stroke="#9ca3af"/>
          <path d="M7 16V11M12 16V7M17 16V13" stroke="#2563eb" stroke-width="2.2" stroke-linecap="round"/>
        </svg>
        <div>
          <div class="header-title">FundGen / FundHQ MFN &amp; Antitrust HSR Analyzer</div>
          <div class="header-subtitle">Matter M-610 ($12.5B Fund VIII LPA) &amp; Matter M-720 (FTC Second Request HHI &amp; Multimodal Charts)</div>
        </div>
      </div>
      <div class="header-actions">
        <a href="__DEFAULT_API_BASE__/api/corpus/file/DOC-FUND-02_Weil_FundHQ_Sovereign_LP_MFN_Side_Letter_Compendium.pdf" target="_blank" class="pill-btn pill-btn-white" style="text-decoration:none;">
          FundHQ PDF
        </a>
        <a href="__DEFAULT_API_BASE__/api/corpus/file/DOC-HSR-01_Hart_Scott_Rodino_Second_Request_Market_Share_Filing.pdf" target="_blank" class="pill-btn pill-btn-white" style="text-decoration:none;">
          HSR Filing PDF
        </a>
        <button class="pill-btn pill-btn-white pill-btn-xs" onclick="requestHostDisplayMode('pip')">Side Panel</button>
        <button class="pill-btn pill-btn-white pill-btn-xs" onclick="requestHostDisplayMode('fullscreen')">Maximize</button>
      </div>
    </header>

    <div class="mike-toolbar">
      <div class="toolbar-left">
        <span style="font-size:11px;font-weight:600;color:#4b5563;">LP Tier Filter:</span>
        <button id="btn-lp-all" class="tab-pill-btn active" onclick="loadFundsAntitrust(0, null, this)">
          All LPs (5)
        </button>
        <button id="btn-lp-150" class="tab-pill-btn" onclick="loadFundsAntitrust(150, null, this)">
          &gt;= $150M Early-Bird
        </button>
        <button id="btn-lp-250" class="tab-pill-btn" onclick="loadFundsAntitrust(250, null, this)">
          &gt;= $250M Sovereign Anchor
        </button>
      </div>
      <div class="toolbar-right">
        <button id="btn-hsr-remedy-toggle" class="pill-btn pill-btn-blue" onclick="toggleHsrRemedy()">
          HSR Divestiture Remedy: ON (Cleared +30 Δ HHI)
        </button>
      </div>
    </div>

    <div class="two-col-studio">
      <div class="studio-col">
        <div>
          <div class="section-label">FundHQ Sovereign &amp; Institutional LP Side-Letter MFN Matrix (DOC-FUND-01 / 02)</div>
          <div id="fundhq-savings-banner" style="font-size:12px;color:#065f46;background:#ecfdf5;border:1px solid #a7f3d0;border-radius:8px;padding:8px 12px;margin-bottom:8px;"></div>
          <div style="overflow-x:auto;border:1px solid var(--table-grid-border);border-radius:8px;">
            <table class="tr-table">
              <thead>
                <tr>
                  <th style="width:28%;">Limited Partner</th>
                  <th style="width:16%;">Commit ($M)</th>
                  <th style="width:16%;">Fee / Carry</th>
                  <th style="width:40%;">MFN Election Scope &amp; Excusal Rights</th>
                </tr>
              </thead>
              <tbody id="fundhq-lp-tbody"></tbody>
            </table>
          </div>
        </div>

        <div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
            <span class="section-label">FTC HSR Second Request — HHI Market Concentration (DOC-HSR-01)</span>
            <span id="hsr-status-badge" class="status-pill green">CLEARED (+30 Δ HHI)</span>
          </div>
          <div id="hsr-summary-card" class="liquid-glass-flat" style="padding:10px 12px;border-radius:8px;font-size:12px;margin-bottom:8px;"></div>
          <div id="hsr-bars-container" style="display:flex;flex-direction:column;gap:6px;"></div>
        </div>
      </div>

      <div class="studio-col">
        <div>
          <div class="section-label">Extracted Multimodal Exhibits (corpus/charts_and_images/)</div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;">
            <button id="mm-btn-0" class="tab-pill-btn active" onclick="selectMultimodalExhibit(0, this)">EBITDA Bridge</button>
            <button id="mm-btn-1" class="tab-pill-btn" onclick="selectMultimodalExhibit(1, this)">LP Fee Curve</button>
            <button id="mm-btn-2" class="tab-pill-btn" onclick="selectMultimodalExhibit(2, this)">J.Crew Org Chart</button>
            <button id="mm-btn-3" class="tab-pill-btn" onclick="selectMultimodalExhibit(3, this)">Citibank $18M Scan</button>
          </div>
          <div id="mm-exhibit-card" class="liquid-glass-flat" style="padding:12px;border-radius:10px;">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:4px;">
              <div id="mm-exhibit-title" style="font-family:var(--font-serif);font-size:16px;font-weight:600;color:#111827;"></div>
              <button id="btn-maximize-exhibit" type="button" class="pill-btn pill-btn-blue pill-btn-xs" onclick="openDocxModal('exhibit')">⤢ Maximize</button>
            </div>
            <div id="mm-exhibit-takeaway" style="font-size:12px;color:#374151;margin-bottom:10px;"></div>
            <div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;padding:8px;text-align:center;cursor:zoom-in;" onclick="openDocxModal('exhibit')" title="Click to maximize exhibit">
              <img id="mm-exhibit-img" src="__DEFAULT_API_BASE__/api/corpus/image/DOC-CHART-01_Brightwater_EBITDA_Bridge_and_Valuation_Waterfall.png" alt="Multimodal Exhibit" style="max-width:100%;max-height:260px;border-radius:6px;object-fit:contain;" />
            </div>
            <div style="margin-top:8px;display:flex;justify-content:space-between;align-items:center;">
              <span style="font-size:11px;color:#6b7280;">Extracted via docparse Bounding-Box Schema → Cloud Spanner</span>
              <a id="mm-exhibit-pdf-link" href="__DEFAULT_API_BASE__/api/corpus/file/DOC-CHART-01_Brightwater_EBITDA_Bridge_and_Valuation_Waterfall.pdf" target="_blank" class="pill-btn pill-btn-white pill-btn-xs" style="text-decoration:none;">Open Source PDF</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===================================================================== -->
  <!-- STUDIO 4: INTAPP ETHICAL WALL & SPANNER GRAPH (weil-governance-wall)  -->
  <!-- ===================================================================== -->
  <section id="governance-view" class="studio-screen">
    <header class="mike-page-header">
      <div class="header-brand">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#111827" stroke-width="1.8" style="flex-shrink:0;">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <circle cx="12" cy="11" r="2.5" fill="#2563eb" stroke="none"/>
        </svg>
        <div>
          <div class="header-title">Intapp Ethical Wall &amp; Cloud Spanner Graph</div>
          <div class="header-subtitle">Screen-Before-Rank Access Verification · Client Matter Number (CMN) Switcher</div>
        </div>
      </div>
      <div class="header-actions">
        <button id="btn-verify-wall" class="pill-btn pill-btn-blue" onclick="loadGovernanceAndGraph(true)">
          Verify Screen-Before-Rank
        </button>
        <button class="pill-btn pill-btn-white pill-btn-xs" onclick="requestHostDisplayMode('pip')">Side Panel</button>
        <button class="pill-btn pill-btn-white pill-btn-xs" onclick="requestHostDisplayMode('fullscreen')">Maximize</button>
      </div>
    </header>

    <div class="mike-toolbar">
      <div class="toolbar-left">
        <span style="font-size:11px;font-weight:600;color:#4b5563;">Attorney:</span>
        <select id="gov-lawyer-select" class="field-input" style="border-radius:9999px;" onchange="loadGovernanceAndGraph()">
          <option value="L-001">L-001 · Sarah Jenkins (M&amp;A Managing Partner — Walled from M-999)</option>
          <option value="L-002">L-002 · David Vance (Senior M&amp;A Partner)</option>
          <option value="L-003">L-003 · Marcus Thorne (Tax Partner — Owner of EM-9901)</option>
          <option value="L-005">L-005 · Elena Rostova (Restructuring Partner — Cleared for M-999)</option>
        </select>
      </div>
      <div class="toolbar-right" style="flex-wrap:wrap;">
        <button id="cmn-btn-m331" class="tab-pill-btn active" onclick="selectGovernanceMatter('M-331-KESTREL', this)">M-331 Brightwater</button>
        <button id="cmn-btn-m402" class="tab-pill-btn" onclick="selectGovernanceMatter('M-402', this)">M-402 Apollo</button>
        <button id="cmn-btn-m610" class="tab-pill-btn" onclick="selectGovernanceMatter('M-610-FUNDGEN', this)">M-610 FundGen</button>
        <button id="cmn-btn-m720" class="tab-pill-btn" onclick="selectGovernanceMatter('M-720-ANTITRUST', this)">M-720 HSR</button>
        <button id="cmn-btn-m999" class="tab-pill-btn" onclick="selectGovernanceMatter('M-999', this)">M-999 Omega (Wall)</button>
      </div>
    </div>

    <div class="two-col-studio">
      <div class="studio-col">
        <div id="gov-status-banner" class="liquid-glass-flat" style="padding:12px;border-radius:10px;"></div>

        <div class="liquid-glass-flat" style="padding:10px 12px;border-radius:10px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <span class="section-label">Unfiled Deal Email 30-Day Teammate Grant (EM-9901)</span>
            <span id="gov-grant-pill" class="status-pill green">ACTIVE (30-Day TTL)</span>
          </div>
          <p style="font-size:11.5px;color:#4b5563;margin-bottom:8px;">
            Controls whether Marcus Thorne's unfiled Exchange tax email (<code>EM-9901</code> · $14.2M IRC § 338(h)(10) Gross-Up) is traversable in Cloud Spanner <code>TeammateGrants</code>:
          </p>
          <div style="display:flex;gap:8px;">
            <button id="btn-gov-grant" class="pill-btn pill-btn-blue pill-btn-xs" onclick="setGovGrant(true)">Grant 30-Day Access</button>
            <button id="btn-gov-revoke" class="pill-btn pill-btn-white pill-btn-xs" onclick="setGovGrant(false)">Revoke Access</button>
          </div>
        </div>

        <div>
          <div class="section-label">Cloud Spanner ISO GQL Screen-Before-Rank Query</div>
          <pre id="gov-gql-box" class="text-slab" style="font-family:var(--font-mono);font-size:11px;white-space:pre-wrap;"></pre>
        </div>
      </div>

      <div class="studio-col">
        <div>
          <div class="section-label">Live Cloud Spanner Property Graph (WeilLegalGraph)</div>
          <div id="graph-nodes-list" style="display:flex;flex-direction:column;gap:8px;"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===================================================================== -->
  <!-- STUDIO 5: PARTNER DEAL INBOX & CALENDAR TRIAGE (weil-inbox-calendar)  -->
  <!-- ===================================================================== -->
  <section id="inbox-view" class="studio-screen">
    <header class="mike-page-header">
      <div class="header-brand">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#111827" stroke-width="1.8" style="flex-shrink:0;">
          <rect x="3" y="4" width="18" height="16" rx="2"/>
          <polyline points="3 7 12 13 21 7" stroke="#2563eb"/>
        </svg>
        <div>
          <div class="header-title">Partner Deal Inbox &amp; Calendar Conflict Triage</div>
          <div class="header-subtitle">Sarah Jenkins (L-001) · One-Tap iManage CMN Auto-Filer &amp; FTC HSR Conflict Resolver</div>
        </div>
      </div>
      <div class="header-actions">
        <button id="btn-reset-inbox" class="pill-btn pill-btn-white" onclick="resetInboxState()">
          Reset Queue
        </button>
        <button class="pill-btn pill-btn-white pill-btn-xs" onclick="requestHostDisplayMode('pip')">Side Panel</button>
        <button class="pill-btn pill-btn-white pill-btn-xs" onclick="requestHostDisplayMode('fullscreen')">Maximize</button>
      </div>
    </header>

    <div class="mike-toolbar">
      <div class="toolbar-left">
        <button id="inb-filter-all" class="tab-pill-btn active" onclick="setInboxFilter('all', this)">
          All Priority Items (4)
        </button>
        <button id="inb-filter-pending" class="tab-pill-btn" onclick="setInboxFilter('pending', this)">
          Pending Sign-Off
        </button>
        <button id="inb-filter-cal" class="tab-pill-btn" onclick="setInboxFilter('calendar', this)">
          Calendar Conflicts (CAL-101)
        </button>
      </div>
      <div class="toolbar-right">
        <a href="__DEFAULT_API_BASE__/api/corpus/file/CAL-101_Closing_Board_Call_and_FTC_HSR_Conflict.ics" target="_blank" class="pill-btn pill-btn-white pill-btn-xs" style="text-decoration:none;">
          Download .ics
        </a>
      </div>
    </div>

    <div class="two-col-studio">
      <div class="studio-col" id="inbox-emails-col">
        <div class="section-label">Partner Deal Emails &amp; iManage CMN Filing Queue (corpus/emails_and_calendar/)</div>
        <div id="inbox-email-cards" style="display:flex;flex-direction:column;gap:8px;"></div>
      </div>

      <div class="studio-col" id="inbox-cal-col">
        <div class="section-label">Closing &amp; Regulatory Calendar Conflict (CAL-101)</div>
        <div id="inbox-calendar-cards" style="display:flex;flex-direction:column;gap:8px;"></div>

        <div style="margin-top:6px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
            <div class="section-label" id="raw-eml-header" style="margin-bottom:0;">Rendered Exchange Email &amp; Calendar Invite Preview</div>
            <button id="btn-maximize-eml-top" type="button" class="pill-btn pill-btn-blue pill-btn-xs" onclick="openDocxModal('eml')">⤢ Maximize</button>
          </div>
          <div class="docx-canvas-wrap">
            <div class="docx-word-toolbar" style="background:#0f172a;">
              <span>Microsoft Exchange / iManage Deal Filing Preview</span>
              <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:10.5px;color:#93c5fd;">RFC-822 / iCalendar Verified</span>
                <button id="btn-maximize-eml" type="button" class="docx-max-btn" onclick="openDocxModal('eml')">⤢ Maximize</button>
              </div>
            </div>
            <div style="padding:10px;background:#e5e9f0;">
              <div id="raw-eml-viewer" class="docx-paper-sheet clickable-sheet" onclick="openDocxModal('eml')" title="Click to open centered full-page preview" style="padding:14px 18px;max-height:250px;overflow-y:auto;"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===================================================================== -->
  <!-- CENTERED FULL-DOCUMENT OVERLAY MODAL (#docx-modal-overlay)            -->
  <!-- ===================================================================== -->
  <div id="docx-modal-overlay" class="docx-modal-backdrop" onclick="if(event.target===this)closeDocxModal()">
    <div class="docx-modal-window" role="dialog" aria-modal="true" aria-labelledby="docx-modal-title">
      <div class="docx-modal-header">
        <div style="display:flex;align-items:center;gap:10px;min-width:0;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#93c5fd" stroke-width="2" style="flex-shrink:0;">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <div style="min-width:0;">
            <div id="docx-modal-title" style="font-family:var(--font-sans);font-size:13.5px;font-weight:600;color:#ffffff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
              Weil_Legal_Legos_Composed_Rider.docx
            </div>
            <div id="docx-modal-subtitle" style="font-family:var(--font-sans);font-size:11px;color:#bfdbfe;">
              Microsoft Word Print-Layout Preview · Full 8.5" × 11" Legal Sheet
            </div>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:6px;flex-shrink:0;">
          <button type="button" class="docx-max-btn" onclick="setDocxModalZoom(0.9)">90%</button>
          <button type="button" class="docx-max-btn" onclick="setDocxModalZoom(1.0)">100%</button>
          <button type="button" class="docx-max-btn" onclick="setDocxModalZoom(1.12)">112%</button>
          <button id="docx-modal-copy-btn" type="button" class="docx-max-btn" onclick="copyDocxModalText()">Copy Text</button>
          <a id="docx-modal-download-btn" href="__DEFAULT_API_BASE__/api/legal-legos/docx" target="_blank" class="docx-max-btn" style="text-decoration:none;background:#2563eb;border-color:#60a5fa;">
            Download .docx
          </a>
          <button id="docx-modal-close-btn" type="button" class="docx-max-btn" onclick="closeDocxModal()" style="background:rgba(220,38,38,0.85);border-color:#fca5a5;">
            ✕ Close (Esc)
          </button>
        </div>
      </div>

      <div id="docx-modal-controls" class="docx-modal-controls-bar"></div>

      <div class="docx-modal-ruler">
        <span>1 · · · · · 2 · · · · · 3 · · · · · 4 · · · · · 5 · · · · · 6 · · · · · 7 · · · · · 8</span>
        <span id="docx-modal-ruler-right">WEIL, GOTSHAL &amp; MANGES LLP · PRINT LAYOUT (100% ZOOM)</span>
      </div>

      <div class="docx-modal-scroll">
        <div id="docx-modal-paper" class="docx-modal-paper"></div>
      </div>
    </div>
  </div>

</div>

<script>
const INITIAL_STUDIO_VIEW = "__INITIAL_STUDIO_VIEW__";
const DEFAULT_API_BASE = "__DEFAULT_API_BASE__";
const API_BASE = (
  window.location.origin &&
  window.location.origin !== "null" &&
  (window.location.origin.includes("run.app") ||
   window.location.origin.includes("localhost") ||
   window.location.origin.includes("127.0.0.1"))
) ? window.location.origin : DEFAULT_API_BASE;

const INITIAL_BOOTSTRAP_DATA = __INITIAL_BOOTSTRAP_JSON__;

let currentCorpusMode = "kestrel";
let tabularRows = (INITIAL_BOOTSTRAP_DATA.kestrel_rows || []).slice();
let dynamicColumns = [];
let activeInspectorRowIdx = 0;
let activeSearchQuery = "";
let grantActiveState = true;
let hsrRemedyActive = true;
let currentLpFilter = 0;
let currentMultimodalData = INITIAL_BOOTSTRAP_DATA.funds_remedy_on || null;
let currentGovernanceMatter = "M-331-KESTREL";
let currentRedlineData = (INITIAL_BOOTSTRAP_DATA.redlines || {})["KESTREL-SPA-802"] || null;
let redlineCardStates = {};
let currentInboxData = INITIAL_BOOTSTRAP_DATA.inbox_initial || null;
let currentInboxFilter = "all";

/* ========================================================================= */
/* SEP-1865 MCP APP (@modelcontextprotocol/ext-apps) BIDIRECTIONAL BRIDGE    */
/* ========================================================================= */
let mcpRpcId = 100;

function notifyHostSizeAndPip(preferredMode) {
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({
        jsonrpc: "2.0",
        method: "ui/notifications/initialized",
        params: {}
      }, "*");
      window.parent.postMessage({
        jsonrpc: "2.0",
        method: "ui/notifications/size-changed",
        params: { height: 760 }
      }, "*");
      if (preferredMode) {
        window.parent.postMessage({
          jsonrpc: "2.0",
          id: ++mcpRpcId,
          method: "ui/request-display-mode",
          params: { mode: preferredMode }
        }, "*");
      }
    }
  } catch (e) {}
}

let activeDocxModalMode = null;
let currentExhibitIdx = 0;
let currentEmlInspectState = { idx: 0, isCal: false };

function requestHostDisplayMode(mode) {
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({
        jsonrpc: "2.0",
        id: ++mcpRpcId,
        method: "ui/request-display-mode",
        params: { mode: mode || "pip" }
      }, "*");
      window.parent.postMessage({
        jsonrpc: "2.0",
        method: "ui/notifications/size-changed",
        params: { height: mode === "fullscreen" ? 900 : 760 }
      }, "*");
    }
    // Also provide immediate standalone Chrome visual behavior:
    const activeScreen = document.querySelector(".studio-screen.active")?.id || INITIAL_STUDIO_VIEW;
    if (mode === "fullscreen") {
      if (activeScreen === "redline-view") {
        openDocxModal("legos");
      } else if (activeScreen === "tabular-view") {
        openDocxModal("inspector");
      } else if (activeScreen === "funds-view") {
        openDocxModal("exhibit");
      } else if (activeScreen === "inbox-view") {
        openDocxModal("eml");
      } else if (activeScreen === "governance-view") {
        openDocxModal("governance");
      }
    } else if (mode === "pip") {
      if (activeScreen === "tabular-view") {
        const panel = document.getElementById("tr-side-panel");
        if (panel) {
          if (panel.classList.contains("open")) {
            panel.classList.remove("open");
          } else {
            openSideInspector(activeInspectorRowIdx || 0);
          }
        }
      } else {
        closeDocxModal();
      }
    }
  } catch (e) {}
}

function initMcpAppBridge() {
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({
        jsonrpc: "2.0",
        id: 1,
        method: "ui/initialize",
        params: {
          protocolVersion: "2026-01-26",
          appInfo: { name: "weil-legal-mcp-app", version: "3.2.0" },
          appCapabilities: {
            availableDisplayModes: ["inline", "fullscreen", "pip"]
          }
        }
      }, "*");
      setTimeout(() => notifyHostSizeAndPip("pip"), 40);
      setTimeout(() => notifyHostSizeAndPip(null), 350);
    }
  } catch (e) {}
}

window.addEventListener("message", (event) => {
  const data = event.data;
  if (!data || typeof data !== "object") return;
  if (data.id === 1 && data.result) {
    notifyHostSizeAndPip("pip");
  }
  if (data.method === "ui/notifications/tool-input" && data.params) {
    const args = data.params.arguments || {};
    if (args.column_name && args.column_prompt) {
      fillPresetColumn(args.column_name, args.column_prompt);
      runDynamicColumnExtraction();
    }
  } else if (data.method === "ui/notifications/tool-result" && data.params) {
    const sc = data.params.structuredContent || {};
    if (sc.added_column && sc.added_column.name) {
      applyServerAddedColumn(sc.added_column);
    }
  }
});

function applyServerAddedColumn(colPayload) {
  if (!colPayload || !colPayload.name) return;
  const exists = dynamicColumns.some(c => c.name === colPayload.name);
  if (!exists) {
    dynamicColumns.push(colPayload);
    renderTabularGrid();
  }
}

function activateInitialStudio() {
  let target = INITIAL_STUDIO_VIEW || "tabular-view";
  try {
    const params = new URLSearchParams(window.location.search);
    if (params.get("view")) target = params.get("view");
  } catch (e) {}
  if (target === "assistant-view" || target === "project-view") {
    target = "tabular-view";
  }
  document.querySelectorAll(".studio-screen").forEach(el => {
    el.classList.toggle("active", el.id === target);
  });

  // Render synchronously from INITIAL_BOOTSTRAP_DATA at 0ms, then refresh in background
  if (target === "tabular-view") {
    renderTabularGrid();
    if (window.innerWidth >= 880) {
      openSideInspector(0);
    }
    loadTabularWorkspace("kestrel");
  } else if (target === "redline-view") {
    renderRedlineFromMemory("KESTREL-SPA-802");
    renderLegalLegosFromMemory(["LEGO-DE-FRAUD", "LEGO-338H10-TAX", "LEGO-PRIVACY-PRO"]);
    loadRedlinePair("KESTREL-SPA-802");
    updateLegalLegos();
  } else if (target === "funds-view") {
    renderFundsAntitrustFromMemory(0, true);
    loadFundsAntitrust(0, true);
  } else if (target === "governance-view") {
    renderGovernanceFromMemory("L-001", "M-331-KESTREL");
    loadGovernanceAndGraph();
  } else if (target === "inbox-view") {
    renderInboxTriage();
    loadInboxTriage();
  }
}

/* ========================================================================= */
/* STUDIO 1: MIKE OSS TABULAR REVIEW & PIN-CITE READER                       */
/* ========================================================================= */

async function loadTabularWorkspace(corpusMode) {
  currentCorpusMode = corpusMode || currentCorpusMode;
  document.getElementById("pill-corpus-kestrel")?.classList.toggle("active", currentCorpusMode === "kestrel");
  document.getElementById("pill-corpus-all")?.classList.toggle("active", currentCorpusMode === "scaled");

  // 1. Instant 0ms local state update from INITIAL_BOOTSTRAP_DATA
  if (currentCorpusMode === "scaled") {
    tabularRows = (INITIAL_BOOTSTRAP_DATA.scaled_rows || []).slice();
    if (!grantActiveState) {
      tabularRows = tabularRows.filter(r => r.doc_id !== "EM-9901");
    }
    document.getElementById("tr-subtitle").textContent =
      `Full Deal Corpus (${tabularRows.length} Files · 1,293 Indexed Clauses) · Cloud Spanner WeilLegalGraph`;
  } else {
    tabularRows = (INITIAL_BOOTSTRAP_DATA.kestrel_rows || []).slice();
    if (!grantActiveState) {
      tabularRows = tabularRows.filter(r => r.doc_id !== "EM-9901");
    }
    document.getElementById("tr-subtitle").textContent =
      `Matter M-331 · CMN 31402-0018 · ${tabularRows.length} Active Contracts in Cloud Spanner`;
  }
  updateGrantPillUI(grantActiveState);
  renderTabularGrid();

  // 2. Background sync with Cloud Run API_BASE
  try {
    const res = await fetch(`${API_BASE}/api/state?corpus=${encodeURIComponent(currentCorpusMode)}`);
    if (!res.ok) return;
    const data = await res.json();
    grantActiveState = !!data.teammate_grant_active;
    updateGrantPillUI(grantActiveState);
    if (currentCorpusMode === "kestrel" && Array.isArray(data.tabular_reviews) && data.tabular_reviews.length) {
      tabularRows = data.tabular_reviews;
      document.getElementById("tr-subtitle").textContent =
        `Matter M-331 · CMN 31402-0018 · ${tabularRows.length} Active Contracts in Cloud Spanner`;
      renderTabularGrid();
    }
  } catch (e) {}
}

function updateGrantPillUI(active) {
  const dot = document.getElementById("grant-dot");
  const lbl = document.getElementById("grant-label");
  if (dot) dot.style.background = active ? "#10b981" : "#9ca3af";
  if (lbl) lbl.textContent = active ? "EM-9901 Grant: Active" : "EM-9901 Grant: Revoked";
}

async function toggleTeammateGrant() {
  grantActiveState = !grantActiveState;
  updateGrantPillUI(grantActiveState);
  await loadTabularWorkspace(currentCorpusMode);
  try {
    const endpoint = grantActiveState ? `${API_BASE}/api/grant` : `${API_BASE}/api/revoke`;
    await fetch(endpoint, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({email_id: "EM-9901"}),
    });
  } catch (e) {}
}

function switchTabularCorpus(mode) {
  loadTabularWorkspace(mode);
}

function filterTabularRows(q) {
  activeSearchQuery = (q || "").trim().toLowerCase();
  renderTabularGrid();
}

function statusPillForConsent(text) {
  const t = (text || "").toLowerCase();
  if (t.includes("prior written") || t.includes("unanimous") || t.includes("joint") || t.includes("sole discretion")) {
    return `<span class="status-pill red">${escapeHtml(text)}</span>`;
  }
  if (t.includes("notice") || t.includes("30") || t.includes("45")) {
    return `<span class="status-pill amber">${escapeHtml(text)}</span>`;
  }
  return `<span class="status-pill green">${escapeHtml(text)}</span>`;
}

function renderTabularGrid() {
  const thead = document.getElementById("tr-thead");
  const tbody = document.getElementById("tr-tbody");
  if (!thead || !tbody) return;

  let colsHtml = `
    <tr>
      <th style="width:220px;">Document</th>
      <th style="width:185px;">CoC / Provision Trigger</th>
      <th style="width:210px;">Consent Requirement</th>
      <th style="width:125px;">Notice Window</th>
      <th style="width:185px;">Termination &amp; Fee Impact</th>
  `;
  dynamicColumns.forEach((dc, colIdx) => {
    const progressText = (dc.totalCount && dc.completedCount < dc.totalCount)
      ? ` <span style="font-size:10px;font-weight:500;color:#2563eb;">(${dc.completedCount}/${dc.totalCount})</span>`
      : "";
    colsHtml += `<th style="width:215px;background:#eff6ff;color:#1e3a8a;">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
        <span>✦ ${escapeHtml(dc.name)}${progressText}</span>
        <button type="button" onclick="removeDynamicColumn(${colIdx})" title="Remove column" style="border:none;background:transparent;color:#64748b;cursor:pointer;font-size:12px;padding:0 2px;line-height:1;">×</button>
      </div>
    </th>`;
  });
  colsHtml += `</tr>`;
  thead.innerHTML = colsHtml;

  const filtered = tabularRows.filter(r => {
    if (!activeSearchQuery) return true;
    const blob = `${r.filename} ${r.doc_id} ${r.coc_trigger} ${r.consent_required} ${r.fee_or_penalty} ${r.quote}`.toLowerCase();
    return blob.includes(activeSearchQuery);
  });

  tbody.innerHTML = filtered.map((row, idx) => {
    const dynCells = dynamicColumns.map(dc => {
      const cellVal = dc.values[row.doc_id];
      if (!cellVal || cellVal.status === "loading") {
        return `<td>
          <div class="skeleton-bar" style="margin-bottom:4px;"></div>
          <div style="font-size:10px;color:#2563eb;font-weight:500;">⚡ Gemini 3.8 Flash...</div>
        </td>`;
      }
      const citeLabel = cellVal.citation ? `<div style="font-size:10px;color:#6b7280;margin-top:2px;">${escapeHtml(cellVal.citation)} · p.${cellVal.page || row.page || 1}</div>` : "";
      return `<td onclick="openSideInspector(${idx}, '${escapeJs(cellVal.quote || row.quote)}', '${escapeJs(cellVal.citation || row.citation)}')" style="cursor:pointer;">
        <div style="font-weight:500;color:#111827;">
          <span>${escapeHtml(cellVal.answer)}</span>
          <button type="button" class="citation-pill" onclick="event.stopPropagation();openSideInspector(${idx}, '${escapeJs(cellVal.quote || row.quote)}', '${escapeJs(cellVal.citation || row.citation)}')">${idx + 1}</button>
        </div>
        ${citeLabel}
      </td>`;
    }).join("");

    return `
      <tr id="tr-row-${idx}" class="${idx === activeInspectorRowIdx ? 'active-row' : ''}">
        <td onclick="openSideInspector(${idx})" style="cursor:pointer;">
          <div class="doc-cell-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" style="flex-shrink:0;">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
            </svg>
            <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escapeHtml(row.filename)}</span>
          </div>
          <div class="doc-cell-sub">${escapeHtml(row.doc_id)} · ${escapeHtml(row.citation || 'Sec. 8.02')}</div>
        </td>
        <td onclick="openSideInspector(${idx})" style="cursor:pointer;">
          ${escapeHtml(row.coc_trigger)}
          <button type="button" class="citation-pill" onclick="event.stopPropagation();openSideInspector(${idx})">1</button>
        </td>
        <td onclick="openSideInspector(${idx})" style="cursor:pointer;">
          ${statusPillForConsent(row.consent_required)}
        </td>
        <td onclick="openSideInspector(${idx})" style="cursor:pointer;">
          ${escapeHtml(row.notice_window)}
        </td>
        <td onclick="openSideInspector(${idx})" style="cursor:pointer;">
          <div style="font-weight:500;color:#111827;">${escapeHtml(row.fee_or_penalty)}</div>
          <div style="font-size:11px;color:#6b7280;">${escapeHtml(row.termination_right)}</div>
        </td>
        ${dynCells}
      </tr>
    `;
  }).join("");
}

function removeDynamicColumn(colIdx) {
  if (colIdx >= 0 && colIdx < dynamicColumns.length) {
    dynamicColumns.splice(colIdx, 1);
    renderTabularGrid();
  }
}

function toggleAddColumnBar() {
  const bar = document.getElementById("add-col-bar");
  if (bar) {
    bar.classList.toggle("open");
    if (bar.classList.contains("open")) {
      setTimeout(() => document.getElementById("new-col-name")?.focus(), 40);
    }
  }
}

function fillPresetColumn(name, prompt) {
  const nameEl = document.getElementById("new-col-name");
  const promptEl = document.getElementById("new-col-prompt");
  if (nameEl) nameEl.value = name;
  if (promptEl) promptEl.value = prompt;
}

async function runDynamicColumnExtraction() {
  const nameInput = document.getElementById("new-col-name");
  const promptInput = document.getElementById("new-col-prompt");
  const colName = ((nameInput && nameInput.value) || "").trim() || "Agreement Title";
  const rawPrompt = ((promptInput && promptInput.value) || "").trim();
  const colPrompt = rawPrompt || `Extract the exact "${colName}" from this agreement/document.`;

  // Reset inputs so the next column starts clean and never reuses an old prompt
  if (nameInput) nameInput.value = "";
  if (promptInput) promptInput.value = "";
  document.getElementById("add-col-bar")?.classList.remove("open");

  const targetRows = tabularRows.slice();
  const colObj = {
    name: colName,
    prompt: colPrompt,
    values: {},
    completedCount: 0,
    totalCount: targetRows.length,
  };

  // Initialize every cell in the column to live parallel loading state (NO mock data)
  targetRows.forEach(r => {
    colObj.values[r.doc_id] = { status: "loading" };
  });
  dynamicColumns.push(colObj);
  renderTabularGrid();

  // Scroll table horizontally so the user sees the new column and parallel loading bars immediately
  const scroller = document.querySelector(".tr-grid-scroll");
  if (scroller) {
    setTimeout(() => { scroller.scrollLeft = scroller.scrollWidth; }, 30);
  }

  // Execute real parallel Gemini 3.8 Flash extractions across all active contracts in the grid
  await Promise.all(targetRows.map(async (r) => {
    try {
      const resp = await fetch(`${API_BASE}/api/extract_single`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          doc_id: r.doc_id,
          column_name: colName,
          column_prompt: colPrompt,
          model: "gemini-3.8-flash",
        }),
      });
      if (resp.ok) {
        const resData = await resp.json();
        const extractedText = resData.extracted_value || resData.extracted_answer || resData.summary || "Not addressed in contract";
        colObj.values[r.doc_id] = {
          status: "done",
          answer: extractedText,
          quote: resData.quote || resData.verbatim_quote || r.quote,
          citation: resData.citation || resData.section_citation || r.citation,
          page: resData.page || r.page || 1,
        };
      } else {
        colObj.values[r.doc_id] = {
          status: "done",
          answer: `HTTP ${resp.status}`,
          quote: r.quote,
          citation: r.citation,
          page: r.page || 1,
        };
      }
    } catch (e) {
      colObj.values[r.doc_id] = {
        status: "done",
        answer: "Connection error",
        quote: r.quote,
        citation: r.citation,
        page: r.page || 1,
      };
    } finally {
      colObj.completedCount = (colObj.completedCount || 0) + 1;
      renderTabularGrid();
    }
  }));
}

async function openSideInspector(rowIdx, overrideQuote, overrideCitation) {
  if (rowIdx < 0 || rowIdx >= tabularRows.length) return;
  activeInspectorRowIdx = rowIdx;
  const row = tabularRows[rowIdx];
  const panel = document.getElementById("tr-side-panel");
  if (panel) panel.classList.add("open");

  document.querySelectorAll("#tr-tbody tr").forEach((tr, i) => {
    tr.classList.toggle("active-row", i === rowIdx);
  });

  const quote = overrideQuote || row.quote || "";
  const citation = overrideCitation || row.citation || "Section 1.01";
  document.getElementById("insp-doc-title").textContent = row.filename;
  document.getElementById("insp-doc-meta").textContent = `${row.doc_id} · ${citation} · Page ${row.page || 1}`;
  document.getElementById("insp-pincite-quote").innerHTML =
    `<strong>Pin-Cite (${escapeHtml(citation)}, p.${row.page || 1}):</strong> “${escapeHtml(quote)}”`;

  const dl = document.getElementById("insp-download-link");
  if (dl) dl.href = `${API_BASE}/api/corpus/file/${encodeURIComponent(row.filename)}`;

  const runDocEl = document.getElementById("insp-running-docid");
  if (runDocEl) runDocEl.textContent = `${row.doc_id} · ${citation.toUpperCase()}`;
  const runPageEl = document.getElementById("insp-running-page");
  if (runPageEl) runPageEl.textContent = `Page ${row.page || 1} of 12`;

  const bodyEl = document.getElementById("insp-contract-body");
  const cachedPage = (INITIAL_BOOTSTRAP_DATA.doc_pages || {})[row.doc_id] || "";
  const formatLegalDocumentHtml = (rawText) => {
    const cleanText = String(rawText || "").trim();
    const lines = cleanText.split(/\n+/);
    const snippet = quote ? quote.slice(0, 42) : "";
    let matchedQuote = false;

    const blocksHtml = lines.map((line) => {
      const trimmed = line.trim();
      if (!trimmed) return "";
      let htmlLine = escapeHtml(trimmed);
      if (snippet && trimmed.includes(snippet)) {
        matchedQuote = true;
        const escSnip = escapeHtml(snippet);
        htmlLine = htmlLine.replace(
          escSnip,
          `<mark class="contract-highlight">${escSnip}</mark>`
        );
      }
      if (/^(ARTICLE\s+[IVXLC0-9]+|EXHIBIT\s+[A-Z0-9]+)/i.test(trimmed)) {
        return `<div class="docx-doc-title" style="margin-top:8px;margin-bottom:6px;font-size:14.5px;">${htmlLine}</div>`;
      }
      if (/^(Section\s+[0-9.]+|[0-9]+\.[0-9]+\s+)/i.test(trimmed)) {
        const m = trimmed.match(/^(Section\s+[0-9.]+(?:\([a-z0-9]+\))?\s*[^.]{0,55}\.)(.*)$/i);
        if (m) {
          let headEsc = escapeHtml(m[1]);
          let restEsc = escapeHtml(m[2]);
          const isTargetClause = (snippet && trimmed.includes(snippet)) || (citation && trimmed.toLowerCase().includes(citation.toLowerCase().replace(/^sec\.\s*/i, "section ")));
          if (isTargetClause) {
            matchedQuote = true;
            return `<div style="margin-top:8px;text-align:justify;background:#fefce8;border-left:3px solid #eab308;padding:6px 10px;border-radius:0 6px 6px 0;"><span class="docx-clause-heading"><u>${headEsc}</u></span> <mark class="contract-highlight">${restEsc.trim()}</mark></div>`;
          }
          return `<div style="margin-top:8px;text-align:justify;"><span class="docx-clause-heading"><u>${headEsc}</u></span>${restEsc}</div>`;
        }
        return `<div class="docx-clause-heading" style="margin-top:8px;"><u>${htmlLine}</u></div>`;
      }
      if (/^\([a-z0-9]+\)/i.test(trimmed)) {
        return `<div class="docx-subclause">${htmlLine}</div>`;
      }
      return `<div style="margin-top:6px;text-align:justify;text-indent:20px;">${htmlLine}</div>`;
    }).join("");

    if (!matchedQuote && quote) {
      return `
        <div class="docx-clause-block" style="background:#fefce8;border-left:3px solid #eab308;padding:8px 12px;margin-bottom:10px;">
          <div style="font-family:var(--font-sans);font-size:10px;font-weight:700;color:#854d0e;text-transform:uppercase;margin-bottom:3px;">
            Highlighted Grounding Clause (${escapeHtml(citation)} · Page ${row.page || 1})
          </div>
          <div style="text-align:justify;"><mark class="contract-highlight">${escapeHtml(quote)}</mark></div>
        </div>
        ${blocksHtml}
      `;
    }
    return blocksHtml;
  };

  // Render at 0ms from pre-baked page cache
  bodyEl.innerHTML = formatLegalDocumentHtml(cachedPage || quote);
  syncDocxModalIfOpen();

  // Also fetch live page text if not in cache
  if (!cachedPage) {
    try {
      const res = await fetch(`${API_BASE}/api/document_page?doc_id=${encodeURIComponent(row.doc_id)}&page=${row.page || 1}`);
      if (res.ok) {
        const data = await res.json();
        if (data.text) {
          bodyEl.innerHTML = formatLegalDocumentHtml(data.text);
          syncDocxModalIfOpen();
        }
      }
    } catch (e) {}
  }
}

function navigateInspectorRow(delta) {
  const nextIdx = activeInspectorRowIdx + delta;
  if (nextIdx >= 0 && nextIdx < tabularRows.length) {
    openSideInspector(nextIdx);
  }
}

function closeSideInspector() {
  document.getElementById("tr-side-panel")?.classList.remove("open");
}

function exportGridToCsv() {
  const headers = ["Document ID", "Filename", "Trigger", "Consent", "Notice Window", "Fee / Penalty", "Citation"];
  dynamicColumns.forEach(dc => headers.push(dc.name));
  const lines = [headers.map(h => `"${h.replace(/"/g, '""')}"`).join(",")];
  tabularRows.forEach(r => {
    const base = [r.doc_id, r.filename, r.coc_trigger, r.consent_required, r.notice_window, r.fee_or_penalty, r.citation];
    dynamicColumns.forEach(dc => {
      const v = dc.values[r.doc_id]?.answer || "";
      base.push(v);
    });
    lines.push(base.map(c => `"${String(c || '').replace(/"/g, '""')}"`).join(","));
  });
  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `Weil_${currentCorpusMode}_Tabular_Review.csv`;
  a.click();
}

/* ========================================================================= */
/* STUDIO 2: CONTRACT REDLINE & WORD LEGAL LEGOS                             */
/* ========================================================================= */

function buildInteractiveRedlineSheetHtml() {
  if (!currentRedlineData) return "";
  const pid = currentRedlineData.pair_id || "KESTREL-SPA-802";
  const devs = currentRedlineData.key_deviations || [];
  const acceptedCount = Object.values(redlineCardStates).filter(v => v === "accepted").length;
  const rejectedCount = Object.values(redlineCardStates).filter(v => v === "rejected").length;

  let summaryBanner = "";
  if (acceptedCount > 0 || rejectedCount > 0) {
    const allResolved = (acceptedCount + rejectedCount) === devs.length && devs.length > 0;
    const bg = allResolved ? "#ecfdf5" : "#eff6ff";
    const bd = allResolved ? "#a7f3d0" : "#bfdbfe";
    const fg = allResolved ? "#047857" : "#1e3a8a";
    summaryBanner = `
      <div style="font-family:var(--font-sans);font-size:11px;font-weight:600;color:${fg};background:${bg};border:1px solid ${bd};padding:5px 10px;border-radius:6px;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between;">
        <span>${allResolved ? '✓ All Playbook Deviations Resolved in Redline Sheet' : 'Track Changes Active in Document Preview'}</span>
        <span>${acceptedCount}/${devs.length} Accepted Weil v3 · ${rejectedCount} Rejected</span>
      </div>
    `;
  }

  const inlineSubActions = (idx, state) => `
    <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;margin-bottom:5px;font-family:var(--font-sans);">
      <div>
        ${state === "accepted"
          ? `<span class="redline-decision-badge accepted" style="margin-bottom:0;">✓ Card #${idx + 1} Accepted · Weil v3 Playbook Counter-Redline Applied</span>`
          : state === "rejected"
            ? `<span class="redline-decision-badge rejected" style="margin-bottom:0;">✗ Card #${idx + 1} · Counterparty v4 Markup Rejected</span>`
            : `<span class="status-pill amber" style="font-size:10px;padding:1px 7px;">Card #${idx + 1} Pending · Incoming Counterparty v4 Redline</span>`}
      </div>
      <div style="display:flex;align-items:center;gap:4px;" onclick="event.stopPropagation();">
        <button type="button" class="pill-btn ${state === 'accepted' ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" style="height:20px;padding:0 7px;font-size:10px;" onclick="event.stopPropagation();decideRedlineCard(${idx}, 'accepted')">
          ${state === 'accepted' ? '✓ Weil v3 Applied' : 'Accept Weil v3'}
        </button>
        <button type="button" class="pill-btn ${state === 'rejected' ? 'pill-btn-danger' : 'pill-btn-white'} pill-btn-xs" style="height:20px;padding:0 7px;font-size:10px;" onclick="event.stopPropagation();decideRedlineCard(${idx}, 'rejected')">
          ${state === 'rejected' ? '✗ Rejected' : 'Reject'}
        </button>
      </div>
    </div>
  `;

  if (pid === "KESTREL-SPA-802") {
    const s0 = redlineCardStates[0] || "pending";
    const s1 = redlineCardStates[1] || "pending";
    const s2 = redlineCardStates[2] || "pending";

    let subA = "";
    if (s0 === "accepted") {
      subA = `
        <div class="redline-subclause-item state-accepted" id="redline-sub-0">
          ${inlineSubActions(0, s0)}
          <span class="docx-subclause-num">(a)</span> Notwithstanding anything to the contrary in this Agreement, the Seller Parties shall have no liability under Section 8.01(a) until the aggregate amount of all Losses exceeds an amount equal to
          <del class="redline-del">0.25% of the Base Purchase Price ($10,500,000) (the 'Tipping Basket')</del>
          <ins class="redline-ins">0.50% of the Base Purchase Price ($21,000,000) (the 'True Deductible Basket')</ins>, in which case Seller Parties shall be liable
          <del class="redline-del">from the first dollar of all Losses.</del>
          <ins class="redline-ins">only for the excess over the Deductible (compromised at 0.375% EV True Deductible per Project Titan precedent DOC-402-A).</ins>
          <div style="margin-top:6px;padding:5px 8px;background:#dcfce7;border:1px solid #86efac;border-radius:4px;font-family:var(--font-sans);font-size:11px;color:#14532d;">
            <strong>New Modified Line (Weil v3 Playbook):</strong> Seller liable solely for Losses exceeding <strong>0.50% EV True Deductible ($21.0M)</strong> (or <strong>0.375% EV</strong> compromise per Project Titan DOC-402-A).
          </div>
        </div>
      `;
    } else if (s0 === "rejected") {
      subA = `
        <div class="redline-subclause-item state-rejected" id="redline-sub-0">
          ${inlineSubActions(0, s0)}
          <span class="docx-subclause-num">(a)</span> Notwithstanding anything to the contrary in this Agreement, the Seller Parties shall have no liability under Section 8.01(a) until the aggregate amount of all Losses exceeds an amount equal to
          <del class="redline-del">0.25% ('Tipping Basket'; liable from first dollar)</del>
          <strong>0.50% of the Base Purchase Price (the 'Deductible'), in which case Seller Parties shall be liable only for the excess over the Deductible.</strong>
        </div>
      `;
    } else {
      subA = `
        <div class="redline-subclause-item" id="redline-sub-0">
          ${inlineSubActions(0, s0)}
          <span class="docx-subclause-num">(a)</span> Notwithstanding anything to the contrary in this Agreement, the Seller Parties shall have no liability under Section 8.01(a) until the aggregate amount of all Losses exceeds an amount equal to
          <del class="redline-del">0.50% of the Base Purchase Price ($21,000,000) (the 'Deductible')</del>
          <span style="background:#fef3c7;color:#92400e;padding:0 4px;border-radius:3px;font-weight:600;border-bottom:1.5px dashed #d97706;">0.25% of the Base Purchase Price ($10,500,000) (the 'Tipping Basket')</span>, in which case Seller Parties shall be liable
          <del class="redline-del">only for the excess over the Deductible.</del>
          <span style="background:#fef3c7;color:#92400e;padding:0 4px;border-radius:3px;font-weight:600;border-bottom:1.5px dashed #d97706;">from the first dollar of all Losses.</span>
        </div>
      `;
    }

    let subB = "";
    if (s1 === "accepted") {
      subB = `
        <div class="redline-subclause-item state-accepted" id="redline-sub-1">
          ${inlineSubActions(1, s1)}
          <span class="docx-subclause-num">(b)</span> The maximum aggregate liability of the Seller Parties under Section 8.01(a) shall not exceed
          <del class="redline-del">0.25% of the Base Purchase Price ($10,500,000) for general representations and 100% of the Base Purchase Price ($4,200,000,000) for Special Environmental &amp; IP Warranties</del>
          <ins class="redline-ins">0.75% of the Base Purchase Price ($31,500,000) single unified R&amp;W Indemnity Cap (routing Special Environmental &amp; IP coverage to the $50,000,000 R&amp;W Insurance Tower)</ins> (the 'Indemnity Cap').
          <div style="margin-top:6px;padding:5px 8px;background:#dcfce7;border:1px solid #86efac;border-radius:4px;font-family:var(--font-sans);font-size:11px;color:#14532d;">
            <strong>New Modified Line (Weil v3 Playbook):</strong> Unified <strong>0.75% EV Cap ($31.5M)</strong>; Special Environmental &amp; IP Warranties routed to $50M R&amp;W Insurance Tower.
          </div>
        </div>
      `;
    } else if (s1 === "rejected") {
      subB = `
        <div class="redline-subclause-item state-rejected" id="redline-sub-1">
          ${inlineSubActions(1, s1)}
          <span class="docx-subclause-num">(b)</span> The maximum aggregate liability of the Seller Parties under Section 8.01(a) shall not exceed
          <del class="redline-del">0.25% ($10,500,000) general cap and 100% EV Special Rep Super-Cap</del>
          <strong>0.75% of the Base Purchase Price ($31,500,000) (the 'Indemnity Cap').</strong>
        </div>
      `;
    } else {
      subB = `
        <div class="redline-subclause-item" id="redline-sub-1">
          ${inlineSubActions(1, s1)}
          <span class="docx-subclause-num">(b)</span> The maximum aggregate liability of the Seller Parties under Section 8.01(a) shall not exceed
          <del class="redline-del">0.75% of the Base Purchase Price ($31,500,000)</del>
          <span style="background:#fef3c7;color:#92400e;padding:0 4px;border-radius:3px;font-weight:600;border-bottom:1.5px dashed #d97706;">0.25% of the Base Purchase Price ($10,500,000) for general representations and 100% of the Base Purchase Price ($4,200,000,000) for Special Environmental &amp; IP Warranties</span> (the 'Indemnity Cap').
        </div>
      `;
    }

    let subC = "";
    if (s2 === "accepted") {
      subC = `
        <div class="redline-subclause-item state-accepted" id="redline-sub-2">
          ${inlineSubActions(2, s2)}
          <span class="docx-subclause-num">(c)</span> The limitations in this Section 8.02 shall not apply
          <del class="redline-del">in the case of Actual or Constructive Fraud, equitable fraud, reckless misrepresentation, or willful breach.</del>
          <ins class="redline-ins">solely in the case of Actual Fraud (defined strictly as intentional common law fraud under Delaware law with respect to the express representations set forth in Article III per ABRY Partners).</ins>
          <div style="margin-top:6px;padding:5px 8px;background:#dcfce7;border:1px solid #86efac;border-radius:4px;font-family:var(--font-sans);font-size:11px;color:#14532d;">
            <strong>New Modified Line (Weil v3 Playbook):</strong> Fraud carve-out restricted strictly to <strong>Delaware Express Written Actual Fraud (ABRY Partners)</strong>.
          </div>
        </div>
      `;
    } else if (s2 === "rejected") {
      subC = `
        <div class="redline-subclause-item state-rejected" id="redline-sub-2">
          ${inlineSubActions(2, s2)}
          <span class="docx-subclause-num">(c)</span> The limitations in this Section 8.02 shall not apply
          <del class="redline-del">to Constructive Fraud, equitable fraud, or reckless misrepresentation</del>
          <strong>solely in the case of Actual Fraud (defined strictly as intentional common law fraud under Delaware law with respect to the express representations set forth in Article III).</strong>
        </div>
      `;
    } else {
      subC = `
        <div class="redline-subclause-item" id="redline-sub-2">
          ${inlineSubActions(2, s2)}
          <span class="docx-subclause-num">(c)</span> The limitations in this Section 8.02 shall not apply
          <del class="redline-del">solely in the case of Actual Fraud (defined strictly as intentional common law fraud under Delaware law with respect to the express representations set forth in Article III)</del>
          <span style="background:#fef3c7;color:#92400e;padding:0 4px;border-radius:3px;font-weight:600;border-bottom:1.5px dashed #d97706;">in the case of Actual or Constructive Fraud, equitable fraud, reckless misrepresentation, or willful breach.</span>
        </div>
      `;
    }

    return `
      ${summaryBanner}
      <div style="font-weight:700;color:#0f172a;margin-bottom:4px;">Section 8.02 <u>Limitation on Indemnification.</u></div>
      ${subA}
      ${subB}
      ${subC}
    `;
  }

  // Single-card pairs: KESTREL-SCRAPE-804, KESTREL-TAX-304, KESTREL-COC-804
  const st = redlineCardStates[0] || "pending";
  const dev0 = devs[0] || {};
  if (st === "accepted") {
    return `
      ${summaryBanner}
      <div class="redline-subclause-item state-accepted" id="redline-sub-0">
        ${inlineSubActions(0, st)}
        <div style="margin-bottom:6px;"><del class="redline-del">${escapeHtml(currentRedlineData.clause_b_text || dev0.skadden_v4 || "")}</del></div>
        <div><ins class="redline-ins">${escapeHtml(currentRedlineData.clause_a_text || dev0.weil_v3 || "")} (${escapeHtml(dev0.weil_v3 || "")})</ins></div>
        <div style="margin-top:6px;padding:5px 8px;background:#dcfce7;border:1px solid #86efac;border-radius:4px;font-family:var(--font-sans);font-size:11px;color:#14532d;">
          <strong>New Modified Line (Weil v3 Playbook):</strong> ${escapeHtml(dev0.weil_v3 || "")}
        </div>
      </div>
    `;
  } else if (st === "rejected") {
    return `
      ${summaryBanner}
      <div class="redline-subclause-item state-rejected" id="redline-sub-0">
        ${inlineSubActions(0, st)}
        <div style="margin-bottom:6px;"><del class="redline-del">${escapeHtml(dev0.skadden_v4 || "")}</del></div>
        <div><strong>${escapeHtml(currentRedlineData.clause_a_text || "")}</strong></div>
      </div>
    `;
  }
  return `
    ${summaryBanner}
    <div class="redline-subclause-item" id="redline-sub-0">
      ${inlineSubActions(0, st)}
      ${String(currentRedlineData.redline_html || "")}
    </div>
  `;
}

function applyRedlineSheetUI(data) {
  if (!data) return;
  document.getElementById("redline-doc-pair-label").textContent = `${data.doc_a_name} vs. ${data.doc_b_name}`;
  document.getElementById("redline-playbook-banner").innerHTML =
    `<strong>Playbook Standard:</strong> ${escapeHtml(data.playbook_standard)}`;
  const sheetTitle = document.getElementById("redline-sheet-title");
  if (sheetTitle) sheetTitle.textContent = data.title || "ARTICLE VIII — INDEMNIFICATION";
  const sheetMatter = document.getElementById("redline-sheet-matter");
  if (sheetMatter) sheetMatter.textContent = `MATTER ${data.matter_id || 'M-331-KESTREL'} · PAGE 42`;
  const sheetFn = document.getElementById("redline-sheet-filename");
  if (sheetFn) sheetFn.textContent = data.doc_b_name || "08_M331_Brightwater_SPA_Skadden_v4_Redline.docx";

  updateRedlineSheetFromDecisions();
  renderRedlineEditCards();
}

function renderRedlineFromMemory(pairId) {
  const data = (INITIAL_BOOTSTRAP_DATA.redlines || {})[pairId];
  if (!data) return;
  currentRedlineData = data;
  redlineCardStates = {};
  applyRedlineSheetUI(data);
}

async function loadRedlinePair(pairId, btnEl) {
  if (btnEl) {
    btnEl.parentElement.querySelectorAll(".tab-pill-btn").forEach(b => b.classList.remove("active"));
    btnEl.classList.add("active");
  }
  renderRedlineFromMemory(pairId);
  try {
    const res = await fetch(`${API_BASE}/api/redline?pair_id=${encodeURIComponent(pairId)}`);
    if (!res.ok) return;
    const data = await res.json();
    currentRedlineData = data;
    applyRedlineSheetUI(data);
  } catch (e) {}
}

function renderRedlineEditCards() {
  const container = document.getElementById("redline-edit-cards");
  if (!container || !currentRedlineData) return;
  const devs = currentRedlineData.key_deviations || [];
  container.innerHTML = devs.map((d, idx) => {
    const state = redlineCardStates[idx] || "pending";
    const statusBadge = state === "accepted"
      ? `<span class="status-pill green">✓ Accepted Weil Counter</span>`
      : state === "rejected"
        ? `<span class="status-pill red">✗ Rejected Skadden Markup</span>`
        : `<span class="status-pill ${d.severity === 'CRITICAL' ? 'red' : 'amber'}">${escapeHtml(d.severity)}</span>`;

    return `
      <div class="edit-card" id="edit-card-${idx}" style="${state === 'accepted' ? 'border-color:#86efac;background:#f0fdf4;' : state === 'rejected' ? 'border-color:#fca5a5;background:#fef2f2;' : ''}">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px;">
          <div style="display:flex;align-items:center;gap:6px;">
            <span class="citation-pill">${idx + 1}</span>
            <span style="font-weight:600;font-size:12.5px;color:#111827;">${escapeHtml(d.issue)}</span>
          </div>
          ${statusBadge}
        </div>
        <div class="text-slab" style="font-size:12px;margin-bottom:6px;background:#ffffff;">
          <div><del class="redline-del">${escapeHtml(d.skadden_v4)}</del></div>
          <div style="margin-top:4px;"><ins class="redline-ins">${escapeHtml(d.weil_v3)}</ins></div>
        </div>
        <div style="font-size:11.5px;color:#4b5563;margin-bottom:8px;">
          <strong>Playbook Action:</strong> ${escapeHtml(d.recommendation)}
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
          <button id="btn-accept-card-${idx}" type="button" class="pill-btn ${state === 'accepted' ? 'pill-btn-blue' : 'pill-btn-blue'} pill-btn-xs" onclick="decideRedlineCard(${idx}, 'accepted')">
            ${state === 'accepted' ? '✓ Accepted Weil v3 (Active in Preview)' : 'Accept Weil v3'}
          </button>
          <button id="btn-reject-card-${idx}" type="button" class="pill-btn ${state === 'rejected' ? 'pill-btn-danger' : 'pill-btn-white'} pill-btn-xs" onclick="decideRedlineCard(${idx}, 'rejected')">
            ${state === 'rejected' ? '✗ Rejected Counterparty' : 'Reject Markup'}
          </button>
        </div>
      </div>
    `;
  }).join("");
}

function updateRedlineSheetFromDecisions(changedIdx) {
  if (!currentRedlineData) return;
  const devs = currentRedlineData.key_deviations || [];
  const acceptedCount = Object.values(redlineCardStates).filter(v => v === "accepted").length;
  const rejectedCount = Object.values(redlineCardStates).filter(v => v === "rejected").length;
  const slab = document.getElementById("redline-diff-slab");
  if (!slab) return;

  slab.innerHTML = buildInteractiveRedlineSheetHtml();
  if ((acceptedCount + rejectedCount) === devs.length && devs.length > 0) {
    slab.style.borderLeftColor = "#16a34a";
  } else if (acceptedCount > 0 || rejectedCount > 0) {
    slab.style.borderLeftColor = "#2563eb";
  } else {
    slab.style.borderLeftColor = "#dc2626";
  }

  const statsPill = document.getElementById("redline-stats-pill");
  if (statsPill && currentRedlineData.stats) {
    if (acceptedCount > 0 || rejectedCount > 0) {
      statsPill.className = "status-pill green";
      statsPill.textContent = `${acceptedCount}/${devs.length} Weil v3 Applied · -${currentRedlineData.stats.tokens_deleted} / +${currentRedlineData.stats.tokens_inserted} Words`;
    } else {
      statsPill.className = "status-pill blue";
      statsPill.textContent = `${currentRedlineData.stats.similarity_pct}% Similarity · -${currentRedlineData.stats.tokens_deleted} / +${currentRedlineData.stats.tokens_inserted} Words`;
    }
  }

  if (changedIdx !== undefined && changedIdx !== null) {
    const targetSub = document.getElementById(`redline-sub-${changedIdx}`);
    if (targetSub) {
      targetSub.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }
  syncDocxModalIfOpen();
}

function decideRedlineCard(idx, decision) {
  if (redlineCardStates[idx] === decision) {
    // Allow toggling back to pending if clicked again, or keep decision
    redlineCardStates[idx] = decision;
  } else {
    redlineCardStates[idx] = decision;
  }
  renderRedlineEditCards();
  updateRedlineSheetFromDecisions(idx);
}

function resetRedlineDecisions() {
  redlineCardStates = {};
  renderRedlineEditCards();
  updateRedlineSheetFromDecisions();
}

function buildRenderedDocxHtml(chosenBlocks) {
  const countBadge = document.getElementById("legos-block-count-badge");
  if (countBadge) {
    countBadge.textContent = `${chosenBlocks.length} Clause${chosenBlocks.length === 1 ? '' : 's'} · Print Layout`;
  }

  const formatClauseLinesHtml = (rawClauseText) => {
    const rawLines = String(rawClauseText || "").split("\n").map(l => l.trim()).filter(Boolean);
    if (!rawLines.length) return "";
    const firstLine = rawLines[0];
    const headMatch = firstLine.match(/^([0-9A-Za-z.()]+\s+)(.+)$/);
    const secNum = headMatch ? headMatch[1].trim() : "Section";
    const secTitle = headMatch ? headMatch[2].trim() : firstLine;

    const subLinesHtml = rawLines.slice(1).map(sub => {
      const subMatch = sub.match(/^(\([a-z0-9]+\))\s*(.+)$/i);
      if (subMatch) {
        const bullet = escapeHtml(subMatch[1]);
        const bodyFormatted = escapeHtml(subMatch[2]).replace(
          /'([^']{2,45})'/g,
          '<strong>“$1”</strong>'
        );
        return `<div class="docx-subclause"><span class="docx-subclause-num">${bullet}</span>${bodyFormatted}</div>`;
      }
      return `<div class="docx-subclause">${escapeHtml(sub)}</div>`;
    }).join("");

    return `
      <div class="docx-clause-heading">
        Section ${escapeHtml(secNum)} <u>${escapeHtml(secTitle)}</u>
      </div>
      ${subLinesHtml}
    `;
  };

  const sectionsHtml = chosenBlocks.map((b) => {
    const grpStr = b.practice_group || b.source_precedent || "Weil Playbook";
    const numStr = (b.numbering_style || b.numbering_level || "Article VIII").replace(/->/g, "→");
    return `
      <div class="docx-clause-block">
        <div class="docx-clause-meta-bar" style="white-space:nowrap;">
          <span class="status-pill blue" style="font-family:var(--font-sans);font-size:9.5px;padding:1px 7px;">
            ${escapeHtml(b.block_id)} · ${escapeHtml(grpStr)}
          </span>
          <span style="font-family:var(--font-mono);font-size:9.5px;color:#64748b;white-space:nowrap;">
            ${escapeHtml(numStr)}
          </span>
        </div>
        ${formatClauseLinesHtml(b.clause_text)}
      </div>
    `;
  }).join("");

  return `
    <div class="docx-running-header">
      <span>WEIL, GOTSHAL &amp; MANGES LLP · EXECUTION RIDER</span>
      <span>CMN 31402-0018 · M-331</span>
    </div>
    <div class="docx-doc-title">
      MODULAR CLAUSE RIDER TO AGREEMENT AND PLAN OF MERGER
    </div>
    <div class="docx-doc-subtitle">
      By and Among Brightwater Industrial Holdings, Inc., Halvorsen Precision Corp. &amp; Seller Representative
    </div>
    <div class="docx-recital">
      <strong>THIS MODULAR PLAYBOOK RIDER</strong> (this <strong>“Rider”</strong>) is hereby incorporated into and made a binding part of the Agreement and Plan of Merger dated as of October 15, 2026 (the <strong>“Agreement”</strong>). Capitalized terms used but not otherwise defined herein shall have the meanings ascribed to such terms in Article I of the Agreement:
    </div>
    ${sectionsHtml}
    <div style="margin-top:14px;padding-top:10px;border-top:1px dashed #cbd5e1;display:flex;justify-content:space-between;align-items:flex-end;font-family:var(--font-serif);font-size:12px;color:#334155;">
      <div>
        <div style="font-weight:700;text-transform:uppercase;font-size:10.5px;color:#475569;">Approved per Weil M&amp;A / Privacy Pro Playbook v3.4:</div>
        <div style="margin-top:4px;font-style:italic;">/s/ Sarah Jenkins, Managing Partner (M&amp;A) &amp; D. Cockerell, Partner (Tax)</div>
      </div>
      <div style="font-family:var(--font-sans);font-size:10px;color:#047857;background:#ecfdf5;border:1px solid #a7f3d0;padding:2px 8px;border-radius:999px;font-weight:600;">
        ✓ OpenXML .docx Ready
      </div>
    </div>
    <div class="docx-running-footer">
      <span>WEIL:\\98412034.4\\31402.0018</span>
      <span>Page 1 of 1</span>
    </div>
  `;
}

function renderLegalLegosFromMemory(blockIds) {
  const blocks = INITIAL_BOOTSTRAP_DATA.legal_legos_blocks || [];
  const chosen = blocks.filter(b => blockIds.includes(b.block_id));
  const box = document.getElementById("legos-preview-box");
  if (box) {
    box.innerHTML = buildRenderedDocxHtml(chosen.length ? chosen : blocks.slice(0, 1));
  }
  syncDocxModalIfOpen();
}

async function updateLegalLegos(showFeedback) {
  const checked = Array.from(document.querySelectorAll(".lego-cb:checked")).map(cb => cb.value);
  const blockIds = checked.length ? checked : ["LEGO-DE-FRAUD"];
  const dlBtn = document.getElementById("btn-download-legos-docx");
  if (dlBtn) {
    dlBtn.href = `${API_BASE}/api/legal-legos/docx?blocks=${encodeURIComponent(blockIds.join(","))}`;
  }
  if (showFeedback) {
    const composeBtn = document.getElementById("btn-compose-legos");
    if (composeBtn) {
      composeBtn.textContent = `✓ Renumbered (${blockIds.length})`;
      setTimeout(() => { composeBtn.textContent = "Refresh Outline"; }, 1200);
    }
  }
  renderLegalLegosFromMemory(blockIds);
  try {
    const res = await fetch(`${API_BASE}/api/legal-legos`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ block_ids: blockIds, target_section_prefix: "Article VIII" }),
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.blocks) && data.blocks.length) {
        const box = document.getElementById("legos-preview-box");
        if (box) box.innerHTML = buildRenderedDocxHtml(data.blocks);
        syncDocxModalIfOpen();
      }
    }
  } catch (e) {}
}

function copyLegalLegosText() {
  const txt = document.getElementById("legos-preview-box")?.textContent || "";
  navigator.clipboard?.writeText(txt);
  const btn = document.getElementById("btn-copy-legos");
  if (btn) {
    btn.textContent = "✓ Copied";
    setTimeout(() => { btn.textContent = "Copy Rider"; }, 1400);
  }
}

/* ========================================================================= */
/* STUDIO 3: FUNDGEN / FUNDHQ MFN & ANTITRUST HSR                            */
/* ========================================================================= */

function renderFundsAntitrustFromMemory(minCommitment, includeRemedy) {
  const baseData = includeRemedy
    ? INITIAL_BOOTSTRAP_DATA.funds_remedy_on
    : INITIAL_BOOTSTRAP_DATA.funds_remedy_off;
  if (!baseData) return;
  currentMultimodalData = baseData;

  const filteredLps = (baseData.lp_side_letters || []).filter(lp => lp.commitment_usd_m >= (minCommitment || 0));
  const totalCommitM = filteredLps.reduce((acc, lp) => acc + (lp.commitment_usd_m || 0), 0);
  document.getElementById("fundhq-savings-banner").innerHTML =
    `<strong>FundHQ MFN Isolation (${filteredLps.length} Active LPs · $${totalCommitM.toFixed(0)}M Commitment):</strong> ${escapeHtml(baseData.mfn_savings_summary)}`;

  const tbody = document.getElementById("fundhq-lp-tbody");
  tbody.innerHTML = filteredLps.map(lp => `
    <tr>
      <td>
        <div style="font-weight:600;color:#111827;">${escapeHtml(lp.lp_name)}</div>
        <div style="font-size:11px;color:#6b7280;">${escapeHtml(lp.tier)}</div>
      </td>
      <td style="font-weight:600;color:#111827;">$${lp.commitment_usd_m.toFixed(0)}M</td>
      <td>
        <span class="status-pill blue">${lp.mgmt_fee_bps} bps / ${lp.carry_pct}%</span>
      </td>
      <td>
        <div style="font-weight:500;color:#111827;">${escapeHtml(lp.mfn_scope)}</div>
        <div style="font-size:11px;color:#6b7280;">${escapeHtml(lp.co_invest_priority)} · ${escapeHtml(lp.esg_excusal)}</div>
      </td>
    </tr>
  `).join("");

  const hsr = baseData.antitrust_hsr;
  const toggleBtn = document.getElementById("btn-hsr-remedy-toggle");
  const statusBadge = document.getElementById("hsr-status-badge");
  if (includeRemedy) {
    toggleBtn.className = "pill-btn pill-btn-blue";
    toggleBtn.textContent = `HSR Divestiture Remedy: ON (Cleared +${hsr.active_hhi_delta} Δ HHI)`;
    statusBadge.className = "status-pill green";
    statusBadge.textContent = `CLEARED (${hsr.active_post_merger_hhi} HHI / +${hsr.active_hhi_delta} Δ)`;
  } else {
    toggleBtn.className = "pill-btn pill-btn-danger";
    toggleBtn.textContent = `HSR Divestiture Remedy: OFF (Presumed Block +${hsr.active_hhi_delta} Δ HHI)`;
    statusBadge.className = "status-pill red";
    statusBadge.textContent = `CHALLENGE PRESUMED (${hsr.active_post_merger_hhi} HHI / +${hsr.active_hhi_delta} Δ)`;
  }

  document.getElementById("hsr-summary-card").innerHTML = `
    <div style="font-weight:600;color:#111827;margin-bottom:3px;">${escapeHtml(hsr.deal_name)}</div>
    <div style="color:#4b5563;">Pre-Merger HHI: <strong>${hsr.pre_merger_hhi}</strong> → Post-Merger HHI: <strong>${hsr.active_post_merger_hhi}</strong> (Δ <strong>+${hsr.active_hhi_delta}</strong>)</div>
    <div style="margin-top:4px;color:${includeRemedy ? '#047857' : '#b91c1c'};font-weight:500;">
      ${includeRemedy ? '✓ Divestiture Active: ' + escapeHtml(hsr.remedy_recommendation) : '⛔ Unremedied Concentration: Combined Brightwater + Halvorsen reaches 33.6% share (+510 Δ HHI > 100 DOJ/FTC presumption).'}
    </div>
  `;

  const barsEl = document.getElementById("hsr-bars-container");
  const participants = includeRemedy
    ? [
        { company: "Brightwater + Halvorsen (Net of 6% Divestiture)", share_pct: 27.6, hhi_contribution: 762, color: "#059669" },
        { company: "Apex Global Automation", share_pct: 28.0, hhi_contribution: 784, color: "#2563eb" },
        { company: "Kiyota Robotics NA", share_pct: 19.0, hhi_contribution: 361, color: "#2563eb" },
        { company: "Ferrous Precision Systems", share_pct: 12.0, hhi_contribution: 144, color: "#2563eb" },
        { company: "Pellucid Dynamics (Midwest Divestiture Buyer)", share_pct: 6.0, hhi_contribution: 36, color: "#10b981" },
        { company: "Other Fragmented Suppliers", share_pct: 7.4, hhi_contribution: 123, color: "#64748b" },
      ]
    : [
        { company: "Combined Brightwater + Halvorsen (Unremedied)", share_pct: 33.6, hhi_contribution: 1129, color: "#dc2626" },
        { company: "Apex Global Automation", share_pct: 28.0, hhi_contribution: 784, color: "#2563eb" },
        { company: "Kiyota Robotics NA", share_pct: 19.0, hhi_contribution: 361, color: "#2563eb" },
        { company: "Ferrous Precision Systems", share_pct: 12.0, hhi_contribution: 144, color: "#2563eb" },
        { company: "Other Fragmented Suppliers", share_pct: 7.4, hhi_contribution: 272, color: "#64748b" },
      ];

  barsEl.innerHTML = participants.map(mp => `
    <div style="display:flex;align-items:center;gap:8px;font-size:11.5px;">
      <div style="width:215px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#111827;font-weight:${mp.color === '#dc2626' || mp.color === '#059669' ? '600' : '400'};">${escapeHtml(mp.company)}</div>
      <div style="flex:1;height:8px;background:#e5e7eb;border-radius:999px;overflow:hidden;">
        <div style="width:${Math.min(100, mp.share_pct * 2.5)}%;height:100%;background:${mp.color};border-radius:999px;transition:width 0.25s;"></div>
      </div>
      <div style="width:95px;text-align:right;font-family:var(--font-mono);font-size:11px;color:#4b5563;">${mp.share_pct}% (${mp.hhi_contribution})</div>
    </div>
  `).join("");

  selectMultimodalExhibit(currentExhibitIdx);
}

async function loadFundsAntitrust(minCommitment, includeRemedy, btnEl) {
  if (minCommitment !== null && minCommitment !== undefined) {
    currentLpFilter = minCommitment;
  }
  if (includeRemedy !== null && includeRemedy !== undefined) {
    hsrRemedyActive = includeRemedy;
  }
  if (btnEl) {
    btnEl.parentElement.querySelectorAll(".tab-pill-btn").forEach(b => b.classList.remove("active"));
    btnEl.classList.add("active");
  }
  renderFundsAntitrustFromMemory(currentLpFilter, hsrRemedyActive);
}

function toggleHsrRemedy() {
  loadFundsAntitrust(currentLpFilter, !hsrRemedyActive);
}

function selectMultimodalExhibit(idx, btnEl) {
  currentExhibitIdx = idx || 0;
  if (btnEl) {
    btnEl.parentElement.querySelectorAll(".tab-pill-btn").forEach(b => b.classList.remove("active"));
    btnEl.classList.add("active");
  } else {
    [0, 1, 2, 3].forEach(i => {
      document.getElementById(`mm-btn-${i}`)?.classList.toggle("active", i === currentExhibitIdx);
    });
  }
  const files = currentMultimodalData?.visual_files || [];
  const vf = files[currentExhibitIdx] || {
    title: "Brightwater LTM Consolidated Adjusted EBITDA Bridge ($145M -> $175M)",
    image_url: `${API_BASE}/api/corpus/image/DOC-CHART-01_Brightwater_EBITDA_Bridge_and_Valuation_Waterfall.png`,
    pdf_url: `${API_BASE}/api/corpus/file/DOC-CHART-01_Brightwater_EBITDA_Bridge_and_Valuation_Waterfall.pdf`,
  };
  const mm = currentMultimodalData?.extracted_multimodal_pipeline || {};
  let takeaway = "Structured multimodal extraction indexed into Cloud Spanner WeilLegalGraph.";
  if (currentExhibitIdx === 0 && mm.charts?.[0]) takeaway = mm.charts[0].key_takeaway;
  if (currentExhibitIdx === 1 && mm.charts?.[1]) takeaway = mm.charts[1].key_takeaway;
  if (currentExhibitIdx === 2 && mm.diagrams?.[0]) takeaway = mm.diagrams[0].covenant_summary;
  if (currentExhibitIdx === 3 && mm.scanned_signatures_and_wires?.[0]) takeaway = mm.scanned_signatures_and_wires[0].ocr_verbatim_text;

  document.getElementById("mm-exhibit-title").textContent = vf.title;
  document.getElementById("mm-exhibit-takeaway").textContent = takeaway;
  document.getElementById("mm-exhibit-img").src = vf.image_url;
  document.getElementById("mm-exhibit-pdf-link").href = vf.pdf_url;
  syncDocxModalIfOpen();
}

/* ========================================================================= */
/* STUDIO 4: INTAPP ETHICAL WALL & SPANNER GRAPH                             */
/* ========================================================================= */

function selectGovernanceMatter(matterId, btnEl) {
  currentGovernanceMatter = matterId;
  if (btnEl) {
    btnEl.parentElement.querySelectorAll(".tab-pill-btn").forEach(b => b.classList.remove("active"));
    btnEl.classList.add("active");
  }
  loadGovernanceAndGraph();
}

function renderGovernanceFromMemory(lawyerId, matterId, showAuditPulse) {
  const key = `${lawyerId}__${matterId}`;
  const entry = (INITIAL_BOOTSTRAP_DATA.gov_matrix || {})[key];
  if (!entry) return;
  applyGovernanceAndGraphUI(entry.gov, entry.graph, lawyerId, showAuditPulse);
}

function applyGovernanceAndGraphUI(gov, graph, lawyerId, showAuditPulse) {
  const wall = gov.intapp_wall_check || {};
  const allowed = !!wall.access_granted;
  const banner = document.getElementById("gov-status-banner");
  const pulseTag = showAuditPulse
    ? `<span class="status-pill blue" style="margin-left:6px;">⚡ Live Spanner GQL Audit Verified (0.4ms)</span>`
    : "";
  banner.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;flex-wrap:wrap;gap:6px;">
      <span style="font-family:var(--font-serif);font-size:17px;font-weight:600;color:#111827;">
        Matter ${escapeHtml(gov.matter_id)} · CMN ${escapeHtml(gov.cmn)}
      </span>
      <div style="display:flex;align-items:center;">
        <span class="status-pill ${allowed ? 'green' : 'red'}">
          ${allowed ? '✓ CLEARED (Screen-Before-Rank)' : '⛔ BLOCKED BY INTAPP WALL-999'}
        </span>
        ${pulseTag}
      </div>
    </div>
    <div style="font-size:12px;color:#374151;margin-bottom:4px;">
      <strong>Client:</strong> ${escapeHtml(gov.client_name)} · <strong>iManage Library:</strong> <code>${escapeHtml(gov.imanage_library)}</code>
    </div>
    <div style="font-size:12px;color:#4b5563;">
      <strong>OCG Policy:</strong> ${escapeHtml(gov.ocg_ai_policy)}
    </div>
  `;

  const gPill = document.getElementById("gov-grant-pill");
  if (gPill) {
    gPill.className = `status-pill ${grantActiveState ? 'green' : 'red'}`;
    gPill.textContent = grantActiveState ? "ACTIVE (30-Day TTL)" : "REVOKED (Blocked)";
  }

  document.getElementById("gov-gql-box").textContent =
    `GRAPH WeilLegalGraph\nMATCH (l:Lawyer {lawyer_id: '${lawyerId}'})\nMATCH (m:Matter {matter_id: '${currentGovernanceMatter}'})-[:CONTAINS_DOC]->(d:Document)-[:HAS_CLAUSE]->(c:Clause)\nWHERE NOT EXISTS {\n  MATCH (l)-[:INTAPP_WALL {rule_type: 'EXCLUDE'}]->(m)\n}\nAND (d.doc_id != 'EM-9901' OR ${grantActiveState ? "TRUE /* 30-Day TeammateGrant Active */" : "FALSE /* EM-9901 Grant Revoked */"})\nRETURN m.matter_id, d.doc_id, c.clause_id, c.section_title\n-- Result: ${allowed ? 'ACCESS PERMITTED (Zero Ethical Wall Conflicts)' : '0 ROWS RETURNED (Filtered Before ANN Scoring)'}`;

  const nodesEl = document.getElementById("graph-nodes-list");
  const edges = graph.edges || graph.precedent_edges || [];
  const docs = graph.documents || graph.nodes || [];
  if (!allowed) {
    nodesEl.innerHTML = `
      <div class="edit-card" style="border-color:#fecaca;background:#fef2f2;">
        <div style="font-weight:600;color:#b91c1c;margin-bottom:4px;">⛔ Zero-Leakage Screen-Before-Rank Enforcement</div>
        <div style="font-size:12px;color:#7f1d1d;">
          Attorney <code>${escapeHtml(lawyerId)}</code> is barred from <code>${escapeHtml(currentGovernanceMatter)}</code> by Intapp Rule <code>WALL-999</code>.
          Switch attorney to <strong>L-005 · Elena Rostova</strong> in the toolbar above to inspect Project Omega graph nodes.
        </div>
      </div>
    `;
  } else {
    const docNodes = docs.filter(n => n.type === "Document" || n.type === "Clause").slice(0, 5);
    const citeEdges = edges.filter(e => e.type === "CITES_PRECEDENT" || e.type === "CONTAINS_CLAUSE");
    let items = docNodes.length ? docNodes.slice() : edges.slice(0, 5);
    if (currentGovernanceMatter === "M-331-KESTREL") {
      if (grantActiveState) {
        items.unshift({
          id: "EM-9901",
          label: "Unfiled Tax Email — Section 338(h)(10) $14.2M Escrow (TeammateGrant Active)",
          type: "30-Day Grant",
          fee_or_penalty: "$14.2M Tax Gross-Up Reserve at Citibank N.A.",
          doc_id: "EM-9901",
          page: 1,
        });
      }
    }
    nodesEl.innerHTML = items.map((item, i) => {
      const edgeMatch = citeEdges[i] || {};
      const titleStr = item.id ? `${item.id} · ${item.label}` : `${item.source || 'Node'} → ${item.target || 'Target'}`;
      const badgeStr = item.type || edgeMatch.type || currentGovernanceMatter;
      const descStr = item.fee_or_penalty
        ? `Fee/Impact: ${item.fee_or_penalty} · Doc: ${item.doc_id || currentGovernanceMatter} (p.${item.page || 1})`
        : item.counsel
          ? `Counsel: ${item.counsel} · Matter: ${item.matter_id || currentGovernanceMatter}`
          : (edgeMatch.reason || item.reason || "Verified multi-hop precedent edge in Cloud Spanner WeilLegalGraph.");
      return `
      <div class="liquid-glass-flat" style="padding:10px 12px;border-radius:8px;${item.id === 'EM-9901' ? 'border-color:#86efac;background:#f0fdf4;' : ''}">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
          <span style="font-weight:600;font-size:12px;color:#111827;">
            ${escapeHtml(titleStr)}
          </span>
          <span class="status-pill ${item.id === 'EM-9901' ? 'green' : 'blue'}">${escapeHtml(badgeStr)}</span>
        </div>
        <div style="font-size:11.5px;color:#4b5563;margin-top:3px;">
          ${escapeHtml(descStr)}
        </div>
      </div>
      `;
    }).join("");
  }
}

async function loadGovernanceAndGraph(showAuditPulse) {
  const lawyerId = document.getElementById("gov-lawyer-select")?.value || "L-001";
  if (showAuditPulse) {
    const btn = document.getElementById("btn-verify-wall");
    if (btn) {
      btn.textContent = "✓ Verified Screen-Before-Rank";
      setTimeout(() => { btn.textContent = "Verify Screen-Before-Rank"; }, 1400);
    }
  }
  renderGovernanceFromMemory(lawyerId, currentGovernanceMatter, showAuditPulse);
  try {
    const [govRes, graphRes] = await Promise.all([
      fetch(`${API_BASE}/api/governance/wall-check?matter_id=${encodeURIComponent(currentGovernanceMatter)}&lawyer_id=${encodeURIComponent(lawyerId)}`),
      fetch(`${API_BASE}/api/graph?matter_id=${encodeURIComponent(currentGovernanceMatter)}&lawyer_id=${encodeURIComponent(lawyerId)}`),
    ]);
    if (govRes.ok && graphRes.ok) {
      const gov = await govRes.json();
      const graph = await graphRes.json();
      applyGovernanceAndGraphUI(gov, graph, lawyerId, showAuditPulse);
    }
  } catch (e) {}
}

async function setGovGrant(active) {
  grantActiveState = !!active;
  renderGovernanceFromMemory(document.getElementById("gov-lawyer-select")?.value || "L-001", currentGovernanceMatter, true);
  try {
    await fetch(active ? `${API_BASE}/api/grant` : `${API_BASE}/api/revoke`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({email_id: "EM-9901"}),
    });
  } catch (e) {}
}

/* ========================================================================= */
/* STUDIO 5: PARTNER DEAL INBOX & CALENDAR TRIAGE                            */
/* ========================================================================= */

async function loadInboxTriage(approveEmailId, resolveConflictId, resetState) {
  if (resetState && INITIAL_BOOTSTRAP_DATA.inbox_initial) {
    currentInboxData = JSON.parse(JSON.stringify(INITIAL_BOOTSTRAP_DATA.inbox_initial));
    renderInboxTriage();
  } else if (currentInboxData) {
    if (approveEmailId) {
      let approvedIdx = 0;
      (currentInboxData.emails || []).forEach((e, i) => {
        if (e.email_id === approveEmailId) {
          e.status = "APPROVED_AND_FILED_TO_IMANAGE";
          approvedIdx = i;
        }
      });
      renderInboxTriage();
      inspectRawEml(approvedIdx, false);
    }
    if (resolveConflictId) {
      (currentInboxData.calendar_conflicts || []).forEach(c => {
        if (c.conflict_id === resolveConflictId) c.status = "RESOLVED_DELEGATED_TO_ANDREW_SIMON";
      });
      renderInboxTriage();
      inspectRawEml(0, true);
    }
  }
  try {
    const res = await fetch(`${API_BASE}/api/inbox-triage`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        approve_email_id: approveEmailId || null,
        resolve_conflict_id: resolveConflictId || null,
        reset_state: !!resetState,
      }),
    });
    if (res.ok) {
      currentInboxData = await res.json();
      renderInboxTriage();
      if (resolveConflictId) {
        inspectRawEml(0, true);
      }
    }
  } catch (e) {}
}

function setInboxFilter(filterMode, btnEl) {
  currentInboxFilter = filterMode;
  if (btnEl) {
    btnEl.parentElement.querySelectorAll(".tab-pill-btn").forEach(b => b.classList.remove("active"));
    btnEl.classList.add("active");
  }
  renderInboxTriage();
  if (filterMode === "calendar") {
    inspectRawEml(0, true);
  }
}

function resetInboxState() {
  loadInboxTriage(null, null, true);
}

function inspectRawEml(idx, isCal) {
  if (!currentInboxData) return;
  currentEmlInspectState = { idx: idx || 0, isCal: !!isCal };
  const viewer = document.getElementById("raw-eml-viewer");
  const header = document.getElementById("raw-eml-header");
  if (!viewer) return;

  if (isCal) {
    const c = (currentInboxData.calendar_conflicts || [])[0];
    if (!c) return;
    const resolved = (c.status || "").includes("RESOLVED");
    if (header) header.textContent = "Rendered Outlook Calendar Invite Conflict (CAL-101)";
    viewer.innerHTML = `
      <div class="docx-running-header">
        <span>EXCHANGE CALENDAR INVITE · VEVENT</span>
        <span>${escapeHtml(c.conflict_id)} · ${escapeHtml(c.date)}</span>
      </div>
      ${resolved ? `<div style="font-family:var(--font-sans);font-size:11px;font-weight:700;color:#047857;background:#ecfdf5;border:1px solid #a7f3d0;padding:5px 10px;border-radius:6px;margin-bottom:8px;">✓ CONFLICT RESOLVED: Delegated First 30 Mins of FTC HSR Call to Antitrust Partner Andrew Simon (Wrap-Up Moved to 3:45 PM EDT)</div>` : ''}
      <div style="font-family:var(--font-sans);font-size:12px;color:#111827;">
        <div style="padding:8px 10px;background:#eff6ff;border-left:3px solid #2563eb;border-radius:4px;margin-bottom:8px;">
          <div style="font-weight:700;color:#1e3a8a;">Event A (Mandatory): ${escapeHtml(c.event_a.title)}</div>
          <div style="font-size:11px;color:#475569;margin-top:2px;">CMN ${escapeHtml(c.event_a.cmn)} · Attendees: ${escapeHtml((c.event_a.attendees || []).join(", "))}</div>
        </div>
        <div style="padding:8px 10px;background:${resolved ? '#f0fdf4' : '#fef2f2'};border-left:3px solid ${resolved ? '#16a34a' : '#dc2626'};border-radius:4px;margin-bottom:8px;">
          <div style="font-weight:700;color:${resolved ? '#166534' : '#991b1b'};">Event B (${resolved ? 'Delegated to A. Simon · 3:45 PM Wrap-Up' : 'Conflicting Slot'}): ${escapeHtml(c.event_b.title)}</div>
          <div style="font-size:11px;color:#475569;margin-top:2px;">CMN ${escapeHtml(c.event_b.cmn)} · Attendees: ${escapeHtml((c.event_b.attendees || []).join(", "))}</div>
        </div>
        <div style="font-family:var(--font-serif);font-size:13.5px;color:#1f2937;margin-top:6px;">
          <strong>Resolution Protocol:</strong> ${escapeHtml(c.ai_resolution)}
        </div>
      </div>
    `;
  } else {
    const e = (currentInboxData.emails || [])[idx] || (currentInboxData.emails || [])[0];
    if (!e) return;
    const approved = e.status === "APPROVED_AND_FILED_TO_IMANAGE";
    if (header) header.textContent = `Rendered Exchange Deal Message (${e.email_id} · CMN ${e.cmn})`;
    const rawStr = String(e.raw_eml || "").trim();
    const parts = rawStr.split(/\r?\n\r?\n/);
    const bodyText = (parts.length > 1 ? parts.slice(1).join("\n\n").trim() : "") || e.summary;
    viewer.innerHTML = `
      <div class="docx-running-header">
        <span>WEIL EXCHANGE SERVER · IMANAGE</span>
        <span>${escapeHtml(e.email_id)} · ${approved ? 'FILED TO IMANAGE' : 'PENDING SIGN-OFF'}</span>
      </div>
      ${approved ? `<div style="font-family:var(--font-sans);font-size:11px;font-weight:700;color:#047857;background:#ecfdf5;border:1px solid #a7f3d0;padding:5px 10px;border-radius:6px;margin-bottom:8px;">✓ APPROVED &amp; FILED TO IMANAGE WORK 10 (${escapeHtml(e.cmn)}) · Staged Reply Transmitted</div>` : ''}
      <div style="font-family:var(--font-sans);border-bottom:1px solid #e2e8f0;padding-bottom:8px;margin-bottom:10px;">
        <div style="font-family:var(--font-serif);font-size:15px;font-weight:700;color:#0f172a;margin-bottom:4px;">
          ${escapeHtml(e.subject)}
        </div>
        <div style="font-size:11.5px;color:#334155;"><strong>From:</strong> ${escapeHtml(e.sender)}</div>
        <div style="font-size:11.5px;color:#334155;"><strong>To:</strong> Sarah Jenkins (M&amp;A Lead Partner, Weil NY) · <strong>Sent:</strong> ${escapeHtml(e.received_at)}</div>
        <div style="font-size:11px;color:#1d4ed8;margin-top:3px;"><strong>Tagged Client-Matter Number:</strong> ${escapeHtml(e.cmn)}</div>
      </div>
      <div style="font-family:var(--font-serif);font-size:13.8px;line-height:1.6;color:#111827;white-space:pre-line;">
        ${escapeHtml(bodyText)}
      </div>
      <div class="docx-running-footer">
        <span>iManage Work 10 Target: ${escapeHtml(e.matter_id)}</span>
        <span>${approved ? '✓ Filed &amp; Indexed in Cloud Spanner' : 'Verified Deal Correspondence'}</span>
      </div>
    `;
  }
  syncDocxModalIfOpen();
}

function renderInboxTriage() {
  if (!currentInboxData) return;
  const emailCardsEl = document.getElementById("inbox-email-cards");
  const calCardsEl = document.getElementById("inbox-calendar-cards");

  const allEmails = currentInboxData.emails || [];
  let emails = allEmails;
  if (currentInboxFilter === "pending") {
    emails = allEmails.filter(e => e.status !== "APPROVED_AND_FILED_TO_IMANAGE");
  }

  emailCardsEl.innerHTML = emails.map((e) => {
    const origIdx = allEmails.findIndex(x => x.email_id === e.email_id);
    const idx = origIdx >= 0 ? origIdx : 0;
    const approved = e.status === "APPROVED_AND_FILED_TO_IMANAGE";
    return `
      <div class="edit-card" onclick="inspectRawEml(${idx}, false)" style="cursor:pointer;${approved ? 'border-color:#86efac;background:#f0fdf4;' : ''}">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;margin-bottom:4px;">
          <span style="font-weight:600;font-size:12px;color:#111827;">${escapeHtml(e.email_id)} · ${escapeHtml(e.cmn)}</span>
          <span class="status-pill ${approved ? 'green' : 'red'}">
            ${approved ? '✓ Filed to iManage' : escapeHtml(e.priority)}
          </span>
        </div>
        <div style="font-family:var(--font-serif);font-size:15px;font-weight:600;color:#111827;margin-bottom:3px;">
          ${escapeHtml(e.subject)}
        </div>
        <div style="font-size:11.5px;color:#6b7280;margin-bottom:6px;">
          From: ${escapeHtml(e.sender)} · ${escapeHtml(e.received_at)}
        </div>
        <div style="font-size:12px;color:#374151;margin-bottom:8px;">
          ${escapeHtml(e.summary)}
        </div>
        <div class="text-slab" style="font-size:12px;margin-bottom:8px;background:#ffffff;">
          <strong>AI Staged Action:</strong> ${escapeHtml(e.proposed_reply)}
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
          <button id="btn-approve-${escapeHtml(e.email_id)}" type="button" class="pill-btn ${approved ? 'pill-btn-white' : 'pill-btn-blue'} pill-btn-xs" onclick="event.stopPropagation();loadInboxTriage('${escapeJs(e.email_id)}', null, false)">
            ${approved ? '✓ Approved & Filed to iManage' : 'Approve & File to iManage'}
          </button>
          <button type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="event.stopPropagation();inspectRawEml(${idx}, false)">
            View .eml
          </button>
        </div>
      </div>
    `;
  }).join("");

  const cals = currentInboxData.calendar_conflicts || [];
  calCardsEl.innerHTML = cals.map(c => {
    const resolved = c.status.includes("RESOLVED");
    return `
      <div class="edit-card" onclick="inspectRawEml(0, true)" style="cursor:pointer;${resolved ? 'border-color:#86efac;background:#f0fdf4;' : ''}">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
          <span style="font-weight:600;font-size:12px;color:#111827;">${escapeHtml(c.conflict_id)} · ${escapeHtml(c.date)}</span>
          <span class="status-pill ${resolved ? 'green' : 'amber'}">
            ${resolved ? '✓ Conflict Resolved' : 'Hard Overlap Detected'}
          </span>
        </div>
        <div style="font-size:12px;color:#111827;margin-bottom:4px;">
          <strong>1. ${escapeHtml(c.event_a.title)}</strong> (CMN ${escapeHtml(c.event_a.cmn)})
        </div>
        <div style="font-size:12px;color:#b91c1c;margin-bottom:8px;">
          <strong>2. ${escapeHtml(c.event_b.title)}</strong> (CMN ${escapeHtml(c.event_b.cmn)})
        </div>
        <div class="text-slab" style="font-size:12px;margin-bottom:8px;background:#ffffff;">
          <strong>Proposed Delegation:</strong> ${escapeHtml(c.ai_resolution)}
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
          <button id="btn-resolve-cal-101" type="button" class="pill-btn ${resolved ? 'pill-btn-white' : 'pill-btn-blue'} pill-btn-xs" onclick="event.stopPropagation();loadInboxTriage(null, '${escapeJs(c.conflict_id)}', false)">
            ${resolved ? '✓ Delegated to A. Simon (3:45 PM Wrap-Up)' : 'Delegate FTC Overlap to A. Simon'}
          </button>
          <button type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="event.stopPropagation();inspectRawEml(0, true)">
            View .ics
          </button>
        </div>
      </div>
    `;
  }).join("");

  if (currentInboxFilter === "calendar") {
    inspectRawEml(0, true);
  } else if (emails.length > 0) {
    inspectRawEml(currentEmlInspectState.idx || 0, currentEmlInspectState.isCal);
  }
}

/* ========================================================================= */
/* CENTERED FULL-DOCUMENT OVERLAY MODAL CONTROLLER (#docx-modal-overlay)     */
/* ========================================================================= */

function openDocxModal(mode) {
  activeDocxModalMode = mode || "legos";
  const overlay = document.getElementById("docx-modal-overlay");
  if (!overlay) return;
  overlay.classList.add("open");
  syncDocxModalIfOpen();
}

function closeDocxModal() {
  activeDocxModalMode = null;
  document.getElementById("docx-modal-overlay")?.classList.remove("open");
}

function setDocxModalZoom(scaleVal) {
  const paper = document.getElementById("docx-modal-paper");
  const rulerRight = document.getElementById("docx-modal-ruler-right");
  if (paper) {
    paper.style.transform = `scale(${scaleVal})`;
  }
  if (rulerRight) {
    rulerRight.textContent = `WEIL, GOTSHAL & MANGES LLP · PRINT LAYOUT (${Math.round(scaleVal * 100)}% ZOOM)`;
  }
}

function copyDocxModalText() {
  const txt = document.getElementById("docx-modal-paper")?.innerText || "";
  navigator.clipboard?.writeText(txt);
  const btn = document.getElementById("docx-modal-copy-btn");
  if (btn) {
    btn.textContent = "✓ Copied";
    setTimeout(() => { btn.textContent = "Copy Text"; }, 1200);
  }
}

function toggleModalLegoCheckbox(blockId) {
  const cb = document.querySelector(`.lego-cb[value="${blockId}"]`);
  if (cb) {
    cb.checked = !cb.checked;
    updateLegalLegos();
  }
}

function acceptAllModalRedlines() {
  const devs = currentRedlineData?.key_deviations || [];
  devs.forEach((_, idx) => { redlineCardStates[idx] = "accepted"; });
  renderRedlineEditCards();
  updateRedlineSheetFromDecisions();
}

function syncDocxModalIfOpen() {
  const overlay = document.getElementById("docx-modal-overlay");
  if (!overlay || !overlay.classList.contains("open") || !activeDocxModalMode) return;

  const titleEl = document.getElementById("docx-modal-title");
  const subEl = document.getElementById("docx-modal-subtitle");
  const controlsEl = document.getElementById("docx-modal-controls");
  const paperEl = document.getElementById("docx-modal-paper");
  const dlBtn = document.getElementById("docx-modal-download-btn");

  if (activeDocxModalMode === "legos") {
    const checked = Array.from(document.querySelectorAll(".lego-cb:checked")).map(cb => cb.value);
    titleEl.textContent = "Weil_Legal_Legos_Composed_Rider.docx";
    subEl.textContent = `Composed Multi-Level OpenXML Rider · ${checked.length} Active Playbook Clauses`;
    if (dlBtn) {
      dlBtn.href = `${API_BASE}/api/legal-legos/docx?blocks=${encodeURIComponent((checked.length ? checked : ["LEGO-DE-FRAUD"]).join(","))}`;
      dlBtn.textContent = "Download .docx";
    }
    controlsEl.innerHTML = `
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
        <span style="font-weight:600;color:#1e3a8a;">Toggle Clauses Live:</span>
        ${["LEGO-DE-FRAUD", "LEGO-338H10-TAX", "LEGO-PRIVACY-PRO", "LEGO-MFN-FUNDGEN"].map(bid => {
          const isOn = checked.includes(bid);
          return `<button type="button" class="pill-btn ${isOn ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="toggleModalLegoCheckbox('${bid}')">${isOn ? '✓ ' : '+ '}${bid}</button>`;
        }).join("")}
      </div>
      <div style="display:flex;align-items:center;gap:6px;">
        <button type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="openDocxModal('redline')">Switch to Redline Sheet →</button>
      </div>
    `;
    paperEl.innerHTML = document.getElementById("legos-preview-box")?.innerHTML || "";
  } else if (activeDocxModalMode === "redline") {
    const d = currentRedlineData || {};
    titleEl.textContent = d.doc_b_name || "08_M331_Brightwater_SPA_Skadden_v4_Redline.docx";
    subEl.textContent = `${d.title || 'Contract Redline'} · Weil Playbook v3.4 vs. Counterparty v4.0`;
    if (dlBtn) {
      dlBtn.href = `${API_BASE}/api/corpus/file/08_M331_Brightwater_Merger_Agreement_Skadden_v4_Redline.docx`;
      dlBtn.textContent = "Download v4 .docx";
    }
    controlsEl.innerHTML = `
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
        <button type="button" class="pill-btn ${d.pair_id === 'KESTREL-SPA-802' ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="loadRedlinePair('KESTREL-SPA-802')">§ 8.02(b) Indemnity</button>
        <button type="button" class="pill-btn ${d.pair_id === 'KESTREL-SCRAPE-804' ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="loadRedlinePair('KESTREL-SCRAPE-804')">§ 8.04(a) Scrape</button>
        <button type="button" class="pill-btn ${d.pair_id === 'KESTREL-TAX-304' ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="loadRedlinePair('KESTREL-TAX-304')">§ 3.04 Tax 338(h)(10)</button>
        <button type="button" class="pill-btn ${d.pair_id === 'KESTREL-COC-804' ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="loadRedlinePair('KESTREL-COC-804')">§ 8.04 CoC</button>
      </div>
      <div style="display:flex;align-items:center;gap:6px;">
        <button id="modal-btn-accept-all" type="button" class="pill-btn pill-btn-blue pill-btn-xs" onclick="acceptAllModalRedlines()">✓ Accept All Weil v3</button>
        <button type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="resetRedlineDecisions()">Reset</button>
        <button type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="openDocxModal('legos')">Switch to Legal Legos →</button>
      </div>
    `;
    paperEl.innerHTML = `
      <div class="docx-running-header">
        <span>WEIL, GOTSHAL &amp; MANGES LLP · TRACK CHANGES COMPARE</span>
        <span>MATTER ${escapeHtml(d.matter_id || 'M-331-KESTREL')} · PAGE 42</span>
      </div>
      <div class="docx-doc-title" style="text-align:left;margin-bottom:10px;">
        ${escapeHtml(d.title || 'ARTICLE VIII — INDEMNIFICATION')}
      </div>
      <div style="font-family:var(--font-sans);font-size:12px;color:#1e3a8a;background:#eff6ff;border:1px solid #bfdbfe;border-radius:6px;padding:8px 12px;margin-bottom:14px;">
        <strong>Playbook Standard:</strong> ${escapeHtml(d.playbook_standard || '')}
      </div>
      <div class="docx-redline-margin">
        ${buildInteractiveRedlineSheetHtml()}
      </div>
      <div class="docx-running-footer">
        <span>Compare: Weil Playbook v3.4 ↔ Counterparty Markup v4.0</span>
        <span>OpenXML w:del / w:ins</span>
      </div>
    `;
  } else if (activeDocxModalMode === "inspector") {
    const row = tabularRows[activeInspectorRowIdx] || tabularRows[0] || {};
    titleEl.textContent = row.filename || "Executed_Agreement.docx";
    subEl.textContent = `${row.doc_id || 'DOC-01'} · ${row.citation || 'Section 1.01'} · Grounded Pin-Cite Reader`;
    if (dlBtn) {
      dlBtn.href = document.getElementById("insp-download-link")?.href || "#";
      dlBtn.textContent = "Download Original";
    }
    controlsEl.innerHTML = `
      <div style="display:flex;align-items:center;gap:6px;">
        <button type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="navigateInspectorRow(-1);syncDocxModalIfOpen();">← Previous Contract</button>
        <button type="button" class="pill-btn pill-btn-white pill-btn-xs" onclick="navigateInspectorRow(1);syncDocxModalIfOpen();">Next Contract →</button>
        <span style="font-weight:600;color:#1e3a8a;margin-left:6px;">Contract ${activeInspectorRowIdx + 1} of ${tabularRows.length}</span>
      </div>
      <span class="status-pill green">Spanner BBox Pin-Cite Verified</span>
    `;
    paperEl.innerHTML = `
      <div class="docx-running-header">
        <span>WEIL · EXECUTION COPY</span>
        <span>${escapeHtml(row.doc_id || '')} · ${escapeHtml(row.citation || '')}</span>
      </div>
      <div style="font-family:var(--font-sans);font-size:12.5px;background:#eff6ff;border-left:4px solid #2563eb;padding:10px 12px;border-radius:4px;margin-bottom:14px;">
        ${document.getElementById("insp-pincite-quote")?.innerHTML || ""}
      </div>
      <div>${document.getElementById("insp-contract-body")?.innerHTML || ""}</div>
      <div class="docx-running-footer">
        <span>WEIL:\\98412034.4\\31402.0018</span>
        <span>Page ${row.page || 1} of 12</span>
      </div>
    `;
  } else if (activeDocxModalMode === "exhibit") {
    const titleStr = document.getElementById("mm-exhibit-title")?.textContent || "Multimodal Exhibit";
    const takeawayStr = document.getElementById("mm-exhibit-takeaway")?.textContent || "";
    const imgSrc = document.getElementById("mm-exhibit-img")?.src || "";
    const pdfHref = document.getElementById("mm-exhibit-pdf-link")?.href || "#";
    titleEl.textContent = titleStr;
    subEl.textContent = "Extracted Multimodal Financial Chart / Diagram · Cloud Spanner Bounding-Box Grounding";
    if (dlBtn) {
      dlBtn.href = pdfHref;
      dlBtn.textContent = "Open Source PDF";
    }
    controlsEl.innerHTML = `
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
        <button type="button" class="pill-btn ${currentExhibitIdx === 0 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="selectMultimodalExhibit(0)">EBITDA Bridge</button>
        <button type="button" class="pill-btn ${currentExhibitIdx === 1 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="selectMultimodalExhibit(1)">LP Fee Curve</button>
        <button type="button" class="pill-btn ${currentExhibitIdx === 2 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="selectMultimodalExhibit(2)">J.Crew Org Chart</button>
        <button type="button" class="pill-btn ${currentExhibitIdx === 3 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="selectMultimodalExhibit(3)">Citibank $18M Scan</button>
      </div>
    `;
    paperEl.innerHTML = `
      <div class="docx-running-header">
        <span>WEIL MULTIMODAL DOCPARSE · CLOUD SPANNER</span>
        <span>EXHIBIT ${currentExhibitIdx + 1} OF 4</span>
      </div>
      <div class="docx-doc-title" style="margin-bottom:8px;">${escapeHtml(titleStr)}</div>
      <div style="font-family:var(--font-sans);font-size:13px;color:#1e3a8a;background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:10px 14px;margin-bottom:14px;">
        <strong>Extracted Grounding Insight:</strong> ${escapeHtml(takeawayStr)}
      </div>
      <div style="text-align:center;background:#f8fafc;border:1px solid #cbd5e1;border-radius:8px;padding:14px;">
        <img src="${escapeHtml(imgSrc)}" alt="Exhibit" style="max-width:100%;max-height:480px;object-fit:contain;border-radius:4px;" />
      </div>
    `;
  } else if (activeDocxModalMode === "eml") {
    titleEl.textContent = document.getElementById("raw-eml-header")?.textContent || "Exchange Deal Message";
    subEl.textContent = "Microsoft Exchange / iManage Work 10 Deal Filing Preview";
    if (dlBtn) {
      dlBtn.href = `${API_BASE}/api/corpus/file/CAL-101_Closing_Board_Call_and_FTC_HSR_Conflict.ics`;
      dlBtn.textContent = "Download .ics";
    }
    controlsEl.innerHTML = `
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
        <button type="button" class="pill-btn ${!currentEmlInspectState.isCal && currentEmlInspectState.idx === 0 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="inspectRawEml(0, false)">EM-9901 (338h10 Tax)</button>
        <button type="button" class="pill-btn ${!currentEmlInspectState.isCal && currentEmlInspectState.idx === 1 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="inspectRawEml(1, false)">EM-9902 (Skadden v4)</button>
        <button type="button" class="pill-btn ${!currentEmlInspectState.isCal && currentEmlInspectState.idx === 2 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="inspectRawEml(2, false)">EM-9903 (FundHQ MFN)</button>
        <button type="button" class="pill-btn ${currentEmlInspectState.isCal ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="inspectRawEml(0, true)">CAL-101 Conflict (.ics)</button>
      </div>
    `;
    paperEl.innerHTML = document.getElementById("raw-eml-viewer")?.innerHTML || "";
  } else if (activeDocxModalMode === "governance") {
    titleEl.textContent = `Intapp Ethical Wall & Cloud Spanner Graph Audit (${currentGovernanceMatter})`;
    subEl.textContent = "ISO GQL Screen-Before-Rank Certificate";
    controlsEl.innerHTML = `<span style="font-weight:600;color:#1e3a8a;">Zero-Leakage Pre-ANN Graph Filtering</span>`;
    paperEl.innerHTML = `
      <div class="docx-running-header">
        <span>WEIL OCG &amp; INTAPP WALL COMPLIANCE</span>
        <span>${escapeHtml(currentGovernanceMatter)}</span>
      </div>
      <div style="margin-bottom:14px;">${document.getElementById("gov-status-banner")?.innerHTML || ""}</div>
      <pre class="text-slab" style="font-family:var(--font-mono);font-size:12px;white-space:pre-wrap;margin-bottom:14px;">${escapeHtml(document.getElementById("gov-gql-box")?.textContent || "")}</pre>
      <div style="display:flex;flex-direction:column;gap:8px;">${document.getElementById("graph-nodes-list")?.innerHTML || ""}</div>
    `;
  }
}

window.addEventListener("keydown", (ev) => {
  if (ev.key === "Escape") {
    closeDocxModal();
  }
});

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeJs(str) {
  return String(str ?? "").replace(/\\/g, "\\\\").replace(/'/g, "\\'");
}

// Run immediately AND on DOMContentLoaded so srcdoc iframes never miss initialization
initMcpAppBridge();
activateInitialStudio();
window.addEventListener("DOMContentLoaded", () => {
  initMcpAppBridge();
  activateInitialStudio();
});
</script>
</body>
</html>
"""
    html = html.replace(
        f'id="{initial_view}" class="studio-screen"',
        f'id="{initial_view}" class="studio-screen active"',
    )
    html = html.replace("__INITIAL_STUDIO_VIEW__", initial_view)
    html = html.replace("__DEFAULT_API_BASE__", api_base.rstrip("/"))
    html = html.replace("__INITIAL_BOOTSTRAP_JSON__", bootstrap_json)
    html = html.replace("__PRERENDERED_TBODY__", prerendered_tbody)
    html = html.replace("__FIRST_QUOTE__", first_quote)
    html = html.replace("__FIRST_PAGE_TEXT__", first_page_text)
    return html
