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
_TOKENS_CSS_CACHE: str = ""


def _load_ge_luminous_tokens_css() -> str:
    """Loads the official GE UI Library + Luminous v23.0.0 stylesheet."""
    global _TOKENS_CSS_CACHE
    if _TOKENS_CSS_CACHE:
        return _TOKENS_CSS_CACHE
    candidates = [
        Path(__file__).resolve().parent / "ge-luminous-tokens.css",
        Path(
            "/google/src/cloud/nitantmakwana/jetski_ui_design_skill/google3/experimental/users/nitantmakwana/skills/ge_ui_designer/assets/ge-luminous-tokens.css"
        ),
    ]
    for p in candidates:
        if p.exists():
            _TOKENS_CSS_CACHE = p.read_text(encoding="utf-8").strip()
            return _TOKENS_CSS_CACHE
    return ""



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
    cache_key = f"all_studios:{api_base}"
    if cache_key in _BOOTSTRAP_CACHE:
        return _BOOTSTRAP_CACHE[cache_key]

    payload: Dict[str, Any] = {}

    # 1. Studio 1: Tabular Review & Grounded Pin-Cite Reader
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
            "quote": sample.get("text") or (d.get("summary") or "")[:240] or "Indexed in Cloud Spanner LexGraphLegalGraph.",
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

    # 2. Studio 2: Contract Redline & Word Legal Legos
    redlines = {}
    for pid in ("KESTREL-SPA-802", "KESTREL-SCRAPE-804", "KESTREL-TAX-304", "KESTREL-COC-804"):
        redlines[pid] = adk_agents.compute_deterministic_redline(pair_id=pid)
    payload["redlines"] = redlines
    payload["legal_legos_default"] = adk_agents.compose_legal_legos_clause(
        block_ids=["LEGO-DE-FRAUD", "LEGO-338H10-TAX", "LEGO-PRIVACY-PRO"]
    )
    payload["legal_legos_blocks"] = list(adk_agents.DEFAULT_LEGAL_LEGOS_BLOCKS.values())

    # 3. Studio 3: FundGen / FundHQ MFN & Antitrust HSR
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

    # 4. Studio 4: Intapp Ethical Wall & Cloud Spanner Graph
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

    # 5. Studio 5: Partner Deal Inbox & Calendar Triage
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
            f'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-ge-primary)" stroke-width="2" style="flex-shrink:0;">'
            f'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>'
            f'</svg>'
            f'<span class="doc-filename-text">{html_lib.escape(str(row.get("filename", "")))}</span>'
            f'</div>'
            f'<div class="doc-cell-sub">{html_lib.escape(str(row.get("doc_id", "")))} · {html_lib.escape(str(row.get("citation", "Sec. 8.02")))}</div>'
            f'</td>'
            f'<td onclick="openSideInspector({idx})" style="cursor:pointer;">'
            f'{html_lib.escape(str(row.get("coc_trigger", "")))}'
            f'<button type="button" class="citation-pill" onclick="event.stopPropagation();openSideInspector({idx})">1</button>'
            f'</td>'
            f'<td onclick="openSideInspector({idx})" style="cursor:pointer;">'
            f'<span class="status-pill lumi-status-badge {pill_cls}">{html_lib.escape(consent)}</span>'
            f'</td>'
            f'<td onclick="openSideInspector({idx})" style="cursor:pointer;">'
            f'{html_lib.escape(str(row.get("notice_window", "")))}'
            f'</td>'
            f'<td onclick="openSideInspector({idx})" style="cursor:pointer;">'
            f'<div style="font-weight:500;color:var(--color-ge-on-surface);">{html_lib.escape(str(row.get("fee_or_penalty", "")))}</div>'
            f'<div style="font-size:11px;color:var(--color-ge-on-surface-variant);">{html_lib.escape(str(row.get("termination_right", "")))}</div>'
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
    prerendered_tbody = _prerender_kestrel_tbody_html(kestrel_rows)
    first_row = kestrel_rows[0]
    first_quote = html_lib.escape(first_row.get("quote", ""))
    first_page_text = html_lib.escape((bootstrap.get("doc_pages") or {}).get(first_row["doc_id"], first_row.get("quote", "")))

    html = r"""<!DOCTYPE html>
<html lang="en" data-theme="google" data-mode="light">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Gemini Enterprise — LexGraph Legal Intelligence</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..700;1,400..700&family=Google+Sans+Flex:opsz,wght@8..144,300..700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">

<style>
/* __GE_LUMINOUS_TOKENS_CSS__ */
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

:root,
[data-theme="google"],
[data-mode="light"],
[data-mode="dark"] {
  --font-icon: 'Material Symbols Rounded', 'Luminous Symbols', 'Google Symbols';
}

:root {
  /* Official Mike OSS (willchen96/mike) + Gemini Enterprise Luminous Tokens */
  --app-background: var(--color-ge-surface);
  --app-surface: var(--color-ge-surface-container-lowest);
  --app-surface-hover: var(--color-ge-surface-container);
  --app-surface-active: var(--color-ge-surface-container);
  --app-floating: var(--color-ge-surface-container-lowest);
  --table-grid-border: var(--color-ge-outline-variant);
  --border-subtle: var(--color-ge-outline-variant);
  --border-strong: var(--color-ge-outline-variant);

  --editor-heading: var(--color-ge-on-surface);
  --editor-text: var(--color-ge-on-surface);
  --editor-muted-text: var(--color-ge-on-surface-variant);

  --color-blue: var(--color-ge-accent);
  --ge-primary: var(--color-ge-primary);
  --citation-selected-background: rgba(0, 136, 255, 0.09);
  --citation-selected-text: var(--color-ge-on-primary-container);

  --spreadsheet-header-tint: rgba(241, 245, 249, 0.85);
  --spreadsheet-header-corner: var(--color-ge-surface-container);
  --spreadsheet-highlight-background: rgba(59, 130, 246, 0.12);
  --spreadsheet-highlight-outline: var(--color-ge-accent);

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
  background-color: var(--color-ge-surface);
  color: var(--color-ge-on-surface);
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
  background: var(--color-ge-surface-container-lowest);
  border: 1px solid var(--color-ge-outline-variant);
  border-radius: 16px;
  box-shadow: var(--lumi-sys-elevation--level1);
}

/* Gemini Enterprise Luminous Filter Chips (components/luminous/chips/Chip.tsx) */
.tab-pill-btn {
  display: inline-flex;
  height: 32px;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border-radius: 8px;
  padding: 0 12px;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-ge-on-surface-variant);
  background: var(--color-ge-surface-container-lowest);
  border: 1px solid var(--color-ge-outline-variant);
  box-shadow: none;
  transition: background-color 0.15s, color 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.tab-pill-btn:hover {
  background: var(--lumi-sys-color-states--hover-on-surface);
  color: var(--color-ge-on-surface);
  border-color: var(--color-ge-outline-variant);
}
.tab-pill-btn.active,
.lumi-chip.active {
  background: var(--color-ge-secondary-container);
  color: var(--color-ge-on-secondary-container);
  border-color: transparent;
  box-shadow: none;
  font-weight: 600;
}
.lumi-segmented-group .tab-pill-btn {
  height: 28px;
  border-radius: 9999px;
  border: none;
  background: transparent;
  color: var(--color-ge-on-surface-variant);
  padding: 0 14px;
}
.lumi-segmented-group .tab-pill-btn.active {
  background: var(--color-ge-surface-container-lowest);
  color: var(--color-ge-on-surface);
  box-shadow: var(--lumi-sys-elevation--level1);
}

/* Gemini Enterprise Luminous Action Buttons (components/luminous/buttons/Button.tsx) */
.pill-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 34px;
  padding: 0 14px;
  border-radius: 9999px;
  font-size: 12.5px;
  font-weight: 500;
  line-height: 1;
  transition: background-color 0.15s, color 0.15s, box-shadow 0.15s, transform 0.1s;
  white-space: nowrap;
  border: 1px solid transparent;
}
.pill-btn:active {
  transform: scale(0.98);
}
.pill-btn.lumi-icon-btn {
  width: 36px;
  height: 36px;
  padding: 0;
}
.pill-btn-xs {
  height: 28px;
  padding: 0 11px;
  font-size: 11.5px;
}
.pill-btn-blue {
  background: var(--color-ge-primary);
  color: var(--color-ge-on-primary);
  box-shadow: none;
}
.pill-btn-blue:hover:not(:disabled) {
  background: var(--color-ge-primary);
  filter: brightness(1.06);
}
.pill-btn-white {
  background: var(--color-ge-surface-container-lowest);
  color: var(--color-ge-on-surface);
  border: 1px solid var(--color-ge-outline-variant);
  box-shadow: none;
}
.pill-btn-white:hover:not(:disabled) {
  background: var(--lumi-sys-color-states--hover-on-surface);
  color: var(--color-ge-on-surface);
}
.pill-btn-danger {
  background: var(--color-red-bg);
  color: var(--color-red-text);
  border: 1px solid var(--color-red-border);
}
.pill-btn-danger:hover:not(:disabled) {
  background: var(--color-red-border);
}

/* Official Mike OSS CitationPillUI (CitationPillUI.tsx) */
.citation-pill {
  display: inline-flex;
  height: 18px;
  min-width: 18px;
  padding: 0 5px;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  background: var(--color-ge-surface-container-high);
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 600;
  color: var(--color-ge-on-surface);
  border: none;
  margin-left: 4px;
  vertical-align: middle;
  transition: background-color 0.15s, color 0.15s;
}
.citation-pill:hover,
.citation-pill.active {
  background: var(--color-ge-secondary-container);
  color: var(--color-ge-on-secondary-container);
}

/* Gemini Enterprise Status Badges (components/luminous/badges/StatusBadge.tsx) */
.status-pill {
  display: inline-flex;
  height: auto;
  align-items: center;
  gap: 5px;
  border-radius: 9999px;
  padding: 3px 10px;
  font-size: 11.5px;
  font-weight: 600;
  line-height: 1.25;
  white-space: nowrap;
}
.tr-table td .status-pill {
  white-space: normal;
  text-align: left;
  line-height: 1.3;
}
.status-pill.red {
  background: var(--color-red-bg);
  color: var(--color-red-text);
  border: 1px solid var(--color-red-border);
}
.status-pill.amber {
  background: var(--color-yellow-bg);
  color: var(--color-yellow-text);
  border: 1px solid var(--color-yellow-border);
}
.status-pill.green {
  background: var(--color-green-bg);
  color: var(--color-green-text);
  border: 1px solid var(--color-green-border);
}
.status-pill.blue {
  background: var(--color-blue-bg);
  color: var(--color-ge-primary);
  border: 1px solid var(--color-blue-border);
}
.status-pill.gray {
  background: var(--color-ge-surface-container);
  color: var(--color-ge-on-surface-variant);
  border: 1px solid var(--color-ge-outline-variant);
}

/* ==========================================================================
 * Authentic Gemini Enterprise App Shell (NavRail.tsx + Canvas.tsx)
 * ========================================================================== */
#app-shell,
.ge-app-shell {
  display: grid;
  grid-template-columns: 236px minmax(0, 1fr);
  width: 100vw;
  height: 100vh;
  min-height: 680px;
  overflow: hidden;
  background-color: var(--color-ge-surface);
}
.ge-nav-rail {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 18px 12px;
  background-color: var(--color-ge-surface);
  overflow-y: auto;
}
.ge-brand-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 12px 18px;
}
.ge-nav-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.ge-nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 44px;
  padding: 0 16px;
  border-radius: 9999px;
  border: none;
  background: transparent;
  color: var(--color-ge-on-surface-variant);
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  transition: background-color 150ms ease, color 150ms ease;
}
.ge-nav-item:hover {
  background-color: var(--lumi-sys-color-states--hover-on-surface);
  color: var(--color-ge-on-surface);
}
.ge-nav-item.active {
  background-color: var(--color-ge-secondary-container);
  color: var(--color-ge-on-secondary-container);
  font-weight: 600;
}
.ge-main-canvas {
  background-color: var(--color-ge-surface-container-lowest);
  border: 1px solid var(--color-ge-outline-variant);
  border-radius: 24px;
  margin: 12px 12px 12px 0;
  padding: 20px 28px;
  box-shadow: var(--lumi-sys-elevation--level1);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}
.ge-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  flex-shrink: 0;
}
.ge-kpi-grid .lumi-card {
  padding: 14px 16px;
  border-radius: 16px;
}
.ge-kpi-grid .gds-headline-l {
  font-size: 25px;
  line-height: 31px;
}

.studio-screen {
  display: none;
  flex-direction: column;
  gap: 14px;
  width: 100%;
  flex: 1 0 auto;
}
.studio-screen.active {
  display: flex;
}

/* Gemini Enterprise PageHeader (components/luminous/headers/PageHeader.tsx) */
.mike-page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 0 0 14px 0;
  background: transparent;
  border-bottom: 1px solid var(--color-ge-outline-variant);
  flex-shrink: 0;
  flex-wrap: wrap;
}
.header-brand {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-width: 0;
  flex: 1;
}
.header-brand > div {
  min-width: 0;
  flex: 1;
}
.header-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 400;
  line-height: 30px;
  color: var(--color-ge-on-surface);
  letter-spacing: 0;
  margin: 0;
}
.header-subtitle {
  font-size: 12px;
  color: var(--color-ge-on-surface-variant);
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  flex-wrap: wrap;
}

/* Gemini Enterprise SearchBar & FilterRow (SearchBar.tsx, FilterRow.tsx) */
.mike-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0;
  background: transparent;
  border-bottom: none;
  flex-shrink: 0;
  flex-wrap: wrap;
}
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.search-input {
  height: 38px;
  padding: 0 14px;
  border-radius: 9999px;
  border: 1px solid transparent;
  background: var(--color-ge-surface-container);
  font-size: 13px;
  color: var(--color-ge-on-surface);
  outline: none;
  width: 240px;
  transition: border-color 0.15s, background-color 0.15s;
}
.search-input:focus {
  background: var(--color-ge-surface-container-lowest);
  border-color: var(--color-ge-primary);
}

/* Split Workspace Stage */
.workspace-stage {
  flex: 1;
  display: flex;
  gap: 18px;
  min-height: 420px;
  position: relative;
  align-items: stretch;
}

.primary-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  border-radius: 16px;
  border: 1px solid var(--color-ge-outline-variant);
  background: var(--color-ge-surface-container-lowest);
  overflow: hidden;
}

/* Grounded Clause & Document Inspector Card */
.side-inspector-pane {
  width: 390px;
  max-width: 39%;
  background: var(--color-ge-accent-surface);
  border: 1px solid var(--color-ge-accent);
  border-radius: 16px;
  display: none;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  box-shadow: var(--lumi-sys-elevation--level1);
  z-index: 30;
  flex-shrink: 0;
}
.side-inspector-pane.open {
  display: flex;
}

@media (max-width: 1020px) {
  #app-shell,
  .ge-app-shell {
    grid-template-columns: 1fr;
  }
  .ge-nav-rail {
    display: none !important;
  }
  .ge-main-canvas {
    margin: 8px !important;
    padding: 16px 20px !important;
  }
  .ge-kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 780px) {
  .side-inspector-pane {
    position: absolute;
    inset: 0;
    width: 100%;
    max-width: 100%;
  }
  .search-input {
    width: 160px;
  }
  .header-title {
    font-size: 19px;
  }
}

/* Gemini Enterprise DataTable (components/luminous/archive/DataTable.tsx) */
.tr-grid-scroll {
  flex: 1;
  min-height: 380px;
  overflow: auto;
  background: var(--color-ge-surface-container-lowest);
  position: relative;
}
.tr-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 12.5px;
}
.tr-table th {
  position: sticky;
  top: 0;
  z-index: 15;
  background: var(--color-ge-surface-container-low);
  border-bottom: 1px solid var(--color-ge-outline-variant);
  padding: 11px 14px;
  text-align: left;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--color-ge-on-surface-variant);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tr-table th:first-child {
  position: sticky;
  left: 0;
  z-index: 25;
  background: var(--color-ge-surface-container-low);
  padding-left: 16px;
}
.tr-table td {
  border-bottom: 1px solid var(--color-ge-outline-variant);
  padding: 12px 14px;
  vertical-align: top;
  color: var(--color-ge-on-surface);
  line-height: 1.45;
  background: var(--color-ge-surface-container-lowest);
  transition: background-color 0.12s;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
.tr-table td:first-child {
  position: sticky;
  left: 0;
  z-index: 10;
  background: var(--color-ge-surface-container-lowest);
  padding-left: 16px;
}
.tr-table tr:hover td,
.tr-table tr:hover td:first-child {
  background: var(--lumi-sys-color-states--hover-on-surface);
}
.tr-table tr.active-row td,
.tr-table tr.active-row td:first-child {
  background: var(--color-ge-accent-surface);
}

.doc-cell-title {
  font-weight: 600;
  color: var(--color-ge-on-surface);
  display: flex;
  align-items: flex-start;
  gap: 6px;
  cursor: pointer;
}
.doc-cell-title svg {
  margin-top: 2px;
}
.doc-filename-text {
  white-space: normal;
  word-break: break-word;
  line-height: 1.35;
}
.doc-cell-title:hover {
  color: var(--color-ge-primary);
}
.doc-cell-sub {
  font-size: 11.5px;
  color: var(--color-ge-on-surface-variant);
  margin-top: 3px;
  padding-left: 20px;
}

/* Inline Add Column Drawer (AddColumnModal.tsx) */
.add-col-bar {
  display: none;
  padding: 12px 16px;
  background: var(--color-ge-surface-container-low);
  border: 1px solid var(--color-ge-outline-variant);
  border-radius: 16px;
  gap: 8px;
  flex-direction: column;
}
.add-col-bar.open {
  display: flex;
}
.add-col-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.field-input {
  height: 34px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid var(--color-ge-outline-variant);
  background: var(--color-ge-surface-container-lowest);
  font-size: 12.5px;
  color: var(--color-ge-on-surface);
  outline: none;
}
.field-input:focus {
  border-color: var(--color-ge-primary);
  box-shadow: 0 0 0 2px rgba(0, 136, 255, 0.15);
}

/* Grounded Document & Pin-Cite Reader */
.inspector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-ge-outline-variant);
  background: var(--color-ge-accent-surface);
  flex-shrink: 0;
}
.inspector-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  font-family: var(--font-serif);
  font-size: 14.5px;
  line-height: 1.65;
  color: var(--color-ge-on-surface);
  background: var(--color-ge-accent-surface);
}
.pin-cite-box {
  font-family: var(--font-sans);
  font-size: 12px;
  background: var(--color-ge-surface-container-lowest);
  color: var(--color-ge-on-surface);
  border: 1px solid var(--color-ge-outline-variant);
  border-left: 4px solid var(--color-ge-accent);
  padding: 10px 12px;
  border-radius: 12px;
  margin-bottom: 12px;
}
.contract-highlight {
  background: var(--color-yellow-bg);
  color: var(--color-yellow-text);
  padding: 1px 4px;
  border-radius: 3px;
  box-shadow: 0 0 0 1px var(--color-yellow-border);
}

/* Gemini Enterprise ResourceCard & TextSlab */
.edit-card {
  background: var(--color-ge-surface-container-lowest);
  border: 1px solid var(--color-ge-outline-variant);
  border-radius: 16px;
  padding: 14px 16px;
  margin-bottom: 10px;
  box-shadow: var(--lumi-sys-elevation--level1);
}
.text-slab {
  background: var(--color-ge-surface);
  border: 1px solid var(--color-ge-outline-variant);
  border-radius: 12px;
  padding: 10px 12px;
  font-family: var(--font-serif);
  font-size: 14px;
  line-height: 1.58;
  color: var(--color-ge-on-surface);
}
.redline-del, del.redline-del {
  color: var(--color-red-text);
  text-decoration: line-through;
  background: var(--color-red-bg);
  padding: 0 2px;
  border-radius: 3px;
}
.redline-ins, ins.redline-ins {
  color: var(--color-green-text);
  text-decoration: none;
  font-weight: 600;
  background: var(--color-green-bg);
  padding: 0 2px;
  border-radius: 3px;
}

/* Split Grid for Studios 2, 3, 4, 5 */
.two-col-studio {
  flex: 0 0 auto;
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 18px;
  min-height: 420px;
  align-items: start;
}
@media (max-width: 880px) {
  .two-col-studio {
    display: flex;
    flex-direction: column;
  }
}
.studio-col {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 0;
  gap: 14px;
}
.studio-col + .studio-col {
  border-left: none;
  background: transparent;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.01em;
  color: var(--color-ge-on-surface-variant);
  margin-bottom: 4px;
}

.skeleton-bar {
  height: 12px;
  border-radius: 4px;
  background: linear-gradient(90deg, var(--color-ge-surface-container) 25%, var(--color-ge-surface-container-high) 50%, var(--color-ge-surface-container) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Realistic Microsoft Word (.docx) & Legal Contract Print-Layout Sheet */
.docx-canvas-wrap {
  background: var(--color-ge-surface-container);
  border: 1px solid var(--color-ge-outline-variant);
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
  background: var(--color-ge-primary-container);
  color: var(--color-ge-on-primary-container);
  border-bottom: 1px solid var(--color-ge-outline-variant);
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
  background: var(--color-ge-surface-container-low);
  border-bottom: 1px solid var(--color-ge-outline-variant);
  font-family: var(--font-mono);
  font-size: 9.5px;
  color: var(--color-ge-on-surface-variant);
  letter-spacing: 0.05em;
  white-space: nowrap;
  overflow: hidden;
}
.docx-paper-scroll {
  padding: 12px 14px;
  max-height: 440px;
  overflow-y: auto;
  background: var(--color-ge-surface-container-high);
}
.docx-paper-sheet {
  background: var(--color-ge-surface-container-lowest);
  border: 1px solid var(--color-ge-outline-variant);
  border-radius: 3px;
  padding: 18px 22px 16px 22px;
  box-shadow:
    0 4px 14px rgba(15, 23, 42, 0.08),
    0 1px 3px rgba(15, 23, 42, 0.05);
  font-family: var(--font-serif);
  color: var(--color-ge-on-surface);
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
  border-bottom: 2px double var(--color-ge-outline-variant);
  font-family: var(--font-sans);
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-ge-on-surface-variant);
  white-space: nowrap;
}
.docx-doc-title {
  text-align: center;
  font-family: var(--font-serif);
  font-size: 15.5px;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: var(--color-ge-on-surface);
  margin-bottom: 3px;
}
.docx-doc-subtitle {
  text-align: center;
  font-family: var(--font-serif);
  font-size: 12.5px;
  font-style: italic;
  color: var(--color-ge-on-surface-variant);
  margin-bottom: 12px;
}
.docx-recital {
  font-size: 13px;
  text-align: justify;
  text-indent: 24px;
  color: var(--color-ge-on-surface);
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--color-ge-surface-container);
}
.docx-clause-block {
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 2px solid var(--color-blue-bg);
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
  color: var(--color-ge-on-surface);
}
.docx-clause-heading u {
  text-underline-offset: 3px;
  text-decoration-color: var(--color-ge-on-surface-variant);
}
.docx-subclause {
  font-family: var(--font-serif);
  font-size: 13.8px;
  color: var(--color-ge-on-surface);
  text-align: justify;
  padding-left: 26px;
  text-indent: -20px;
  margin-top: 5px;
  line-height: 1.58;
}
.docx-subclause-num {
  font-weight: 700;
  color: var(--color-ge-on-surface);
  margin-right: 4px;
}
.docx-running-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 14px;
  padding-top: 8px;
  border-top: 1px solid var(--color-ge-outline-variant);
  font-family: var(--font-mono);
  font-size: 9.5px;
  color: var(--color-ge-on-surface-variant);
}
/* Track Changes Margin Bar on Redline Sheet */
.docx-redline-margin {
  border-left: 3px solid var(--lumi-sys-color--error);
  padding-left: 14px;
  text-align: justify;
  font-size: 14.2px;
  line-height: 1.65;
  color: var(--color-ge-on-surface);
}

/* Clickable Maximize Button inside Word Toolbar */
.docx-max-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 9px;
  border-radius: 999px;
  background: var(--color-ge-surface-container-lowest);
  color: var(--color-ge-on-surface);
  border: 1px solid var(--color-ge-outline-variant);
  font-family: var(--font-sans);
  font-size: 10.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, transform 0.1s, border-color 0.15s;
  white-space: nowrap;
}
.docx-max-btn:hover {
  background: var(--color-ge-secondary-container);
  color: var(--color-ge-on-secondary-container);
  border-color: var(--color-ge-outline-variant);
}
.docx-max-btn:active {
  transform: scale(0.97);
}
.docx-paper-sheet.clickable-sheet {
  cursor: zoom-in;
  transition: box-shadow 0.15s, border-color 0.15s;
}
.docx-paper-sheet.clickable-sheet:hover {
  border-color: var(--color-blue-border);
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
  padding: 8px 12px;
}
.docx-modal-backdrop.open {
  display: flex;
  animation: modalFadeIn 0.16s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes modalFadeIn {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}
.docx-modal-window {
  width: min(1560px, 98.5vw);
  height: min(940px, 96.5vh);
  background: var(--color-ge-surface-container-low);
  border: 1px solid var(--color-ge-outline-variant);
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow:
    0 25px 60px rgba(15, 23, 42, 0.38),
    0 4px 16px rgba(15, 23, 42, 0.18);
  font-family: var(--font-sans);
}
/* Google Workspace Top App Header */
.docx-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 16px 4px 16px;
  background: var(--color-ge-surface-container-low);
  color: var(--color-ge-on-surface);
  flex-shrink: 0;
}
.gw-menu-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 2px;
  font-size: 12.5px;
  color: var(--color-ge-on-surface);
}
.gw-menu-item {
  cursor: pointer;
  padding: 2px 5px;
  border-radius: 4px;
  user-select: none;
}
.gw-menu-item:hover {
  background: var(--color-ge-surface-container-high);
}
/* Google Workspace Rounded Pill Formatting Toolbar (var(--color-ge-surface-container-high)) */
.gw-format-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  margin: 4px 16px 8px 16px;
  padding: 5px 14px;
  background: var(--color-ge-surface-container-high);
  border-radius: 999px;
  min-height: 40px;
  flex-shrink: 0;
  overflow-x: auto;
}
.gw-tool-group {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
}
.gw-tool-divider {
  width: 1px;
  height: 20px;
  background: var(--color-ge-outline-variant);
  margin: 0 4px;
  flex-shrink: 0;
}
.gw-tool-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-width: 28px;
  height: 28px;
  padding: 0 7px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--color-ge-on-surface);
  font-family: var(--font-sans);
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.12s;
}
.gw-tool-btn:hover {
  background: var(--lumi-sys-color-states--hover-on-surface);
}
.gw-tool-btn.active {
  background: var(--color-ge-primary-container);
  color: var(--color-ge-on-primary-container);
}
.gw-tool-select {
  height: 28px;
  padding: 0 8px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  color: var(--color-ge-on-surface);
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}
.gw-tool-select:hover {
  background: var(--lumi-sys-color-states--hover-on-surface);
}
/* Context sub-controls bar */
.docx-modal-controls-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 4px 20px 6px 20px;
  background: var(--color-ge-surface-container-low);
  border-bottom: 1px solid var(--color-ge-outline-variant);
  font-family: var(--font-sans);
  font-size: 11.5px;
  color: var(--color-ge-on-surface-variant);
  flex-shrink: 0;
  flex-wrap: wrap;
}
/* 3-Column Google Workspace Body (Left Tabs + Center Document + Right Gemini Panel) */
.gw-workspace-body {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  background: var(--color-ge-surface-container-low);
  padding: 0 14px 12px 14px;
  gap: 14px;
}
.gw-left-tabs-pane {
  width: 225px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: 10px 6px 10px 4px;
  overflow-y: auto;
  color: var(--color-ge-on-surface);
}
.gw-tab-pill {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--color-ge-on-surface-variant);
  font-family: var(--font-sans);
  font-size: 12.5px;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  margin-bottom: 3px;
  transition: background-color 0.12s;
}
.gw-tab-pill:hover {
  background: var(--color-ge-surface-container-high);
}
.gw-tab-pill.active {
  background: var(--color-ge-primary-container);
  color: var(--color-ge-on-primary-container);
  font-weight: 600;
}
.gw-outline-item {
  display: block;
  width: 100%;
  padding: 5px 12px 5px 22px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--color-ge-on-surface-variant);
  font-family: var(--font-sans);
  font-size: 11.5px;
  text-align: left;
  cursor: pointer;
}
.gw-outline-item:hover {
  background: var(--color-ge-surface-container-high);
  color: var(--color-ge-primary);
}
/* Center Document Column */
.gw-center-doc-col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: var(--color-ge-surface-container-low);
  border-radius: 8px;
  overflow: hidden;
}
.docx-modal-ruler {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 28px;
  background: var(--color-ge-surface-container-low);
  border-bottom: 1px solid var(--color-ge-outline-variant);
  font-family: var(--font-mono);
  font-size: 9.5px;
  color: var(--color-ge-on-surface-variant);
  letter-spacing: 0.08em;
  flex-shrink: 0;
}
.docx-modal-scroll {
  flex: 1;
  overflow-y: auto;
  background: var(--color-ge-surface-container-low);
  padding: 16px 20px 32px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}
.docx-modal-paper {
  width: 100%;
  max-width: 780px;
  min-height: 720px;
  background: var(--color-ge-surface-container-lowest);
  border: 1px solid var(--color-ge-outline-variant);
  padding: 44px 56px 44px 56px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
  font-family: var(--font-serif);
  color: var(--color-ge-on-surface);
  line-height: 1.68;
  transform-origin: top center;
  transition: transform 0.15s ease, box-shadow 0.2s ease;
  outline: none;
}
.docx-modal-paper:focus {
  border-color: var(--color-blue-border);
  box-shadow: 0 2px 10px rgba(11, 87, 208, 0.12);
}
/* Right Panel: Exact Google Workspace "Gemini" Side Assistant Card */
.gw-gemini-sidepanel {
  width: 365px;
  flex-shrink: 0;
  background: var(--color-ge-surface-container-lowest);
  border: 1px solid var(--color-ge-outline-variant);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.gw-gemini-sidepanel.hidden {
  display: none;
}
.gw-gemini-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-ge-surface-container);
  flex-shrink: 0;
}
.gw-gemini-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.gw-gemini-gradient-title {
  font-family: var(--font-sans);
  font-size: 20px;
  font-weight: 500;
  line-height: 1.28;
  background: var(--gradient-gemini-sparkle);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 10px;
}
.gw-prompt-suggestion {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: var(--color-ge-on-surface);
  font-family: var(--font-sans);
  font-size: 12.5px;
  line-height: 1.4;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.14s;
}
.gw-prompt-suggestion:hover {
  background: var(--color-ge-surface);
}
.gw-chat-bubble-user {
  align-self: flex-end;
  max-width: 88%;
  background: var(--color-ge-surface);
  color: var(--color-ge-on-surface);
  padding: 9px 14px;
  border-radius: 16px 16px 4px 16px;
  font-size: 12.5px;
  line-height: 1.45;
}
.gw-chat-bubble-ai {
  align-self: flex-start;
  width: 100%;
  background: var(--color-ge-surface-container-lowest);
  color: var(--color-ge-on-surface);
  font-size: 12.5px;
  line-height: 1.5;
  border-left: 3px solid var(--color-ge-accent);
  padding-left: 10px;
}
.gw-input-shell {
  margin: 4px 14px 6px 14px;
  padding: 10px 14px 8px 14px;
  background: var(--color-ge-surface-container-lowest);
  border: 1px solid var(--color-ge-outline-variant);
  border-radius: 22px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.gw-input-shell:focus-within {
  border-color: var(--color-ge-primary);
  box-shadow: 0 0 0 1px var(--color-ge-primary);
}
.gw-input-field {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  font-family: var(--font-sans);
  font-size: 13px;
  color: var(--color-ge-on-surface);
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
  padding: 8px 14px;
  text-indent: 0;
  border-radius: 6px;
  margin-top: 8px;
  margin-left: 6px;
  border-left: 3px solid transparent;
  transition: background-color 0.25s, border-color 0.25s;
}
.redline-subclause-item.state-accepted {
  background: var(--color-green-bg);
  border-left-color: var(--color-green-icon);
}
.redline-subclause-item.state-rejected {
  background: var(--color-red-bg);
  border-left-color: var(--lumi-sys-color--error);
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
  background: var(--color-green-bg);
  color: var(--color-green-text);
  border: 1px solid var(--color-green-border);
}
.redline-decision-badge.rejected {
  background: var(--color-red-bg);
  color: var(--color-red-text);
  border: 1px solid var(--color-red-border);
}
</style>
</head>
<body>

<div id="app-shell" class="ge-app-shell">

  <!-- Left Navigation Rail (components/luminous/navigation-rail/NavRail.tsx) -->
  <aside class="ge-nav-rail" aria-label="Primary Navigation">
    <div>
      <div class="ge-brand-row">
        <span class="google-symbols filled" style="font-size:26px; background:var(--gradient-gemini-sparkle); -webkit-background-clip:text; -webkit-text-fill-color:transparent; color:transparent;">temp_preferences_custom</span>
        <div>
          <div class="gds-title-m" style="line-height:1.2;">Gemini Enterprise</div>
          <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">LexGraph Legal Intelligence</div>
        </div>
      </div>
      <nav class="ge-nav-list" id="ge-studio-nav-list">
        <button type="button" class="ge-nav-item" data-studio="tabular-view" onclick="switchStudioScreen('tabular-view', this)">
          <span class="google-symbols">table_chart</span> Tabular Diligence
        </button>
        <button type="button" class="ge-nav-item" data-studio="redline-view" onclick="switchStudioScreen('redline-view', this)">
          <span class="google-symbols">gavel</span> Redline &amp; Legos
        </button>
        <button type="button" class="ge-nav-item" data-studio="funds-view" onclick="switchStudioScreen('funds-view', this)">
          <span class="google-symbols">account_tree</span> FundGen &amp; HSR
        </button>
        <button type="button" class="ge-nav-item" data-studio="governance-view" onclick="switchStudioScreen('governance-view', this)">
          <span class="google-symbols">corporate_fare</span> Intapp &amp; Graph
        </button>
        <button type="button" class="ge-nav-item" data-studio="inbox-view" onclick="switchStudioScreen('inbox-view', this)">
          <span class="google-symbols">description</span> Partner Inbox
        </button>
      </nav>
    </div>
    <div class="lumi-card lumi-card-tonal" style="padding:14px;">
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
        <span class="gds-emphasized-body-s">MCP Host Bridge</span>
        <span class="lumi-status-badge lumi-badge-green"><span class="lumi-status-badge-dot"></span>Connected</span>
      </div>
      <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">
        Grounded in 46 deal contracts &amp; Cloud Spanner LexGraphLegalGraph.
      </div>
    </div>
  </aside>

  <!-- Main Workspace Canvas (components/luminous/canvas/Canvas.tsx) -->
  <main class="ge-main-canvas">

  <!-- ===================================================================== -->
  <!-- STUDIO 1: MIKE OSS TABULAR REVIEW & PIN-CITE READER (mike-gcp-platform) -->
  <!-- ===================================================================== -->
  <section id="tabular-view" class="studio-screen">
    <header class="mike-page-header lumi-page-header">
      <div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px; flex-wrap:wrap;">
          <span class="gds-body-s" id="tr-subtitle" style="color:var(--color-ge-on-surface-variant);">Active Matters / Project Kestrel M&amp;A • CMN 31402-0018 • 7 Active Contracts in Cloud Spanner</span>
          <span class="lumi-status-badge lumi-badge-purple">
            <span class="google-symbols filled" style="font-size:13px;">auto_awesome</span> Luminous AI Active
          </span>
        </div>
        <h1 class="header-title gds-headline-m">Project Kestrel — Change of Control &amp; Deal Diligence</h1>
      </div>
      <div class="header-actions">
        <div class="lumi-segmented-group" role="tablist" aria-label="Corpus Scope">
          <button id="pill-corpus-kestrel" type="button" class="lumi-segmented-item tab-pill-btn active" onclick="switchTabularCorpus('kestrel')">
            Kestrel CoC (7)
          </button>
          <button id="pill-corpus-all" type="button" class="lumi-segmented-item tab-pill-btn" onclick="switchTabularCorpus('scaled')">
            All Contracts (46)
          </button>
        </div>
        <button type="button" class="lumi-icon-btn" onclick="toggleGeThemeMode()" title="Toggle Light / Dark Mode" aria-label="Toggle Light or Dark Mode">
          <span class="google-symbols ge-theme-icon">dark_mode</span>
        </button>
        <button id="btn-toggle-add-col" type="button" class="pill-btn lumi-btn lumi-btn-accent lumi-btn-sm button--state-layer" onclick="toggleAddColumnBar()">
          <span class="google-symbols filled" style="font-size:16px;">auto_awesome</span> Add AI Column
        </button>
        <button id="btn-export-csv" type="button" class="pill-btn lumi-btn lumi-btn-filled lumi-btn-sm button--state-layer" onclick="exportGridToCsv()">
          <span class="google-symbols" style="font-size:16px;">ios_share</span> Export CSV
        </button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="requestHostDisplayMode('pip')" title="Dock in Gemini Enterprise Right Side Panel">
          Side Panel
        </button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="requestHostDisplayMode('fullscreen')" title="Expand to Fullscreen">
          <span class="google-symbols" style="font-size:15px;">open_in_full</span> Maximize
        </button>
      </div>
    </header>

    <div class="mike-toolbar">
      <div class="lumi-search-bar" style="flex:1; min-width:260px;">
        <span class="google-symbols" style="color:var(--color-ge-on-surface-variant);">search</span>
        <input id="tr-search-input" type="search" placeholder="Filter by contract filename, Change-of-Control trigger, consent threshold, or fee penalty..." oninput="filterTabularRows(this.value)" />
      </div>
      <div class="toolbar-left">
        <button type="button" class="tab-pill-btn lumi-chip selected active" onclick="filterTabularRows('')">
          <span class="google-symbols" style="font-size:15px;">check</span> All Provisions
        </button>
        <button type="button" class="tab-pill-btn lumi-chip" onclick="filterTabularRows('prior written')">
          Prior Written Consent
        </button>
        <button type="button" class="tab-pill-btn lumi-chip" onclick="filterTabularRows('338')">
          IRC § 338(h)(10) Tax
        </button>
        <button id="pill-grant-em9901" type="button" class="tab-pill-btn lumi-chip" onclick="toggleTeammateGrant()" title="Toggle 30-day Screen-Before-Rank grant for unfiled tax email EM-9901">
          <span id="grant-dot" style="display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--color-green-icon);"></span>
          <span id="grant-label">EM-9901 Grant: Active</span>
        </button>
      </div>
    </div>

    <!-- KPI Summary Cards (components/luminous/cards/ResourceCard.tsx) -->
    <section class="ge-kpi-grid discover-reveal" aria-label="Diligence Portfolio Metrics">
      <div class="lumi-card card--interactive" onclick="switchTabularCorpus('scaled')">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Indexed Deal Contracts</span>
          <span class="lumi-status-badge lumi-badge-teal"><span class="lumi-status-badge-dot"></span>Spanner Verified</span>
        </div>
        <div class="gds-headline-l">46 Docs</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">7 Kestrel CoC + 39 Precedents</div>
      </div>
      <div class="lumi-card card--interactive" onclick="filterTabularRows('prior written')">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Change-of-Control Risk</span>
          <span class="lumi-status-badge lumi-badge-red"><span class="lumi-status-badge-dot"></span>High Risk</span>
        </div>
        <div class="gds-headline-l">4 Blockers</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">Prior written consent required</div>
      </div>
      <div class="lumi-card card--interactive" onclick="toggleTeammateGrant()">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Unfiled Tax Escrow</span>
          <span class="lumi-status-badge lumi-badge-yellow"><span class="lumi-status-badge-dot"></span>30-Day Grant</span>
        </div>
        <div class="gds-headline-l">$14.2M</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">IRC § 338(h)(10) EM-9901</div>
      </div>
      <div class="lumi-card card--interactive" onclick="openSideInspector(0)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Citation Grounding</span>
          <span class="lumi-status-badge lumi-badge-green"><span class="lumi-status-badge-dot"></span>100% Verified</span>
        </div>
        <div class="gds-headline-l">1,293 Clauses</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">docparse BBox + RRF Entailed</div>
      </div>
    </section>

    <!-- Inline Add Column Bar (Mike OSS AddColumnModal pattern — Live Parallel Gemini 3.8 Flash) -->
    <div id="add-col-bar" class="add-col-bar">
      <div class="add-col-row">
        <span style="font-size:11.5px;font-weight:600;color:var(--color-ge-on-surface-variant);">Quick Presets:</span>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="fillPresetColumn('Agreement Title & Parties', 'Extract the official agreement title and contracting parties from the preamble.')">
          Agreement Title &amp; Parties
        </button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="fillPresetColumn('Indemnity Cap & Basket', 'Extract the exact dollar and percentage Indemnity Cap, Deductible/Tipping Basket, and Fraud Carve-out.')">
          Indemnity Cap &amp; Basket
        </button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="fillPresetColumn('Governing Law & Venue', 'Extract the governing law jurisdiction, arbitration or court venue, and jury waiver.')">
          Governing Law &amp; Venue
        </button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="fillPresetColumn('IP & J.Crew Blocker', 'Identify whether Material IP drop-downs to Unrestricted Subsidiaries are blocked and required lender consent %.')">
          IP &amp; J.Crew Blocker
        </button>
      </div>
      <div class="add-col-row">
        <input id="new-col-name" type="text" class="field-input" style="width:190px;" placeholder="Column name (e.g. Title, Parties, Law)" value="" onkeydown="if(event.key==='Enter')runDynamicColumnExtraction()" />
        <input id="new-col-prompt" type="text" class="field-input" style="flex:1;min-width:210px;" placeholder="Optional extraction instructions (leave blank to auto-extract by Column name via Gemini 3.8 Flash)..." value="" onkeydown="if(event.key==='Enter')runDynamicColumnExtraction()" />
        <button id="btn-run-col-extract" type="button" class="pill-btn lumi-btn lumi-btn-filled lumi-btn-sm button--state-layer" onclick="runDynamicColumnExtraction()">
          <span class="google-symbols filled" style="font-size:15px;">auto_awesome</span> Run extraction
        </button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="toggleAddColumnBar()">
          Cancel
        </button>
      </div>
    </div>

    <div class="workspace-stage">
      <div class="primary-pane lumi-table-wrap">
        <div style="display:flex; align-items:center; justify-content:space-between; padding:12px 16px; border-bottom:1px solid var(--color-ge-outline-variant);">
          <span class="gds-title-m">Extracted Change-of-Control &amp; Deal Clauses</span>
          <span class="lumi-source-chip">
            <span class="google-symbols" style="font-size:14px; color:var(--color-teal-icon);">verified</span>
            Cloud Spanner LexGraphLegalGraph
          </span>
        </div>
        <div class="tr-grid-scroll">
          <table class="tr-table lumi-table" id="kestrel-grid-table">
            <thead id="tr-thead">
              <tr>
                <th style="width:165px;">Document</th>
                <th style="width:135px;">CoC / Provision Trigger</th>
                <th style="width:145px;">Consent Requirement</th>
                <th style="width:95px;">Notice Window</th>
                <th style="width:140px;">Termination &amp; Fee Impact</th>
              </tr>
            </thead>
            <tbody id="tr-tbody">
__PRERENDERED_TBODY__
            </tbody>
          </table>
        </div>
      </div>

      <!-- Grounded Clause & Document Pin-Cite Reader -->
      <aside id="tr-side-panel" class="side-inspector-pane animate-canvas-slide-in">
        <div class="inspector-header">
          <div style="min-width:0;">
            <div id="insp-doc-title" class="gds-title-m" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
              01_Supply_Agreement_Halvorsen_Brightwater.docx
            </div>
            <div id="insp-doc-meta" class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">
              DOC-KESTREL-01 · Section 12.03(a) · Page 4
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:4px;flex-shrink:0;">
            <button id="btn-prev-row" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="navigateInspectorRow(-1)" title="Previous contract">↑</button>
            <button id="btn-next-row" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="navigateInspectorRow(1)" title="Next contract">↓</button>
            <button id="btn-maximize-inspector" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-blue pill-btn-xs" onclick="openDocxModal('inspector')" title="Open full-page document overlay">⤢ Maximize</button>
            <a id="insp-download-link" href="__DEFAULT_API_BASE__/api/corpus/file/01_Supply_Agreement_Halvorsen_Brightwater.docx" target="_blank" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" style="text-decoration:none;">Original</a>
            <button id="btn-close-inspector" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="closeSideInspector()">✕</button>
          </div>
        </div>
        <div class="inspector-body" style="padding:12px 14px;">
          <div class="pin-cite-box" id="insp-pincite-quote">
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
            <div style="padding:10px;background:var(--color-ge-surface-container-high);">
              <div class="docx-paper-sheet clickable-sheet" onclick="openDocxModal('inspector')" title="Click to open full-page document preview overlay" style="padding:14px 18px;">
                <div class="docx-running-header">
                  <span>LEXGRAPH · EXECUTION COPY</span>
                  <span id="insp-running-docid">DOC-KESTREL-01</span>
                </div>
                <div id="insp-contract-body" style="font-family:var(--font-serif);font-size:14px;line-height:1.65;color:var(--color-ge-on-surface);">__FIRST_PAGE_TEXT__</div>
                <div class="docx-running-footer">
                  <span>LEXGRAPH:\98412034.4\31402.0018</span>
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
  <!-- STUDIO 2: CONTRACT REDLINE & WORD LEGAL LEGOS (lexgraph-redline-word-agent) -->
  <!-- ===================================================================== -->
  <section id="redline-view" class="studio-screen">
    <header class="mike-page-header lumi-page-header">
      <div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px; flex-wrap:wrap;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Active Matters / Project Kestrel M&amp;A • LexGraph v3 Playbook vs. Skadden v4 Markup</span>
          <span class="lumi-status-badge lumi-badge-purple">
            <span class="google-symbols filled" style="font-size:13px;">auto_awesome</span> Luminous AI Active
          </span>
        </div>
        <h1 class="header-title gds-headline-m">Contract Redline &amp; Legal Legos Composer</h1>
      </div>
      <div class="header-actions">
        <button type="button" class="lumi-icon-btn" onclick="toggleGeThemeMode()" title="Toggle Light / Dark Mode" aria-label="Toggle Light or Dark Mode">
          <span class="google-symbols ge-theme-icon">dark_mode</span>
        </button>
        <a id="btn-download-v4-docx" href="__DEFAULT_API_BASE__/api/corpus/file/08_M331_Brightwater_Merger_Agreement_Skadden_v4_Redline.docx" target="_blank" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" style="text-decoration:none;">
          <span class="google-symbols" style="font-size:16px;">description</span> Skadden v4 .docx
        </a>
        <a id="btn-download-legos-docx" href="__DEFAULT_API_BASE__/api/legal-legos/docx" target="_blank" class="pill-btn lumi-btn lumi-btn-filled lumi-btn-sm button--state-layer" style="text-decoration:none;">
          <span class="google-symbols" style="font-size:16px;">ios_share</span> Export Composed .docx
        </a>
        <button type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="requestHostDisplayMode('pip')">Side Panel</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="requestHostDisplayMode('fullscreen')">
          <span class="google-symbols" style="font-size:15px;">open_in_full</span> Maximize
        </button>
      </div>
    </header>

    <div class="mike-toolbar">
      <div class="toolbar-left">
        <button id="red-pair-802" type="button" class="tab-pill-btn lumi-chip active" onclick="loadRedlinePair('KESTREL-SPA-802', this)">
          <span class="google-symbols" style="font-size:15px;">gavel</span> SPA § 8.02(b) Indemnity Cap
        </button>
        <button id="red-pair-scrape" type="button" class="tab-pill-btn lumi-chip" onclick="loadRedlinePair('KESTREL-SCRAPE-804', this)">
          SPA § 8.04(a) Materiality Scrape
        </button>
        <button id="red-pair-tax" type="button" class="tab-pill-btn lumi-chip" onclick="loadRedlinePair('KESTREL-TAX-304', this)">
          Tax Rider § 3.04 338(h)(10)
        </button>
        <button id="red-pair-coc" type="button" class="tab-pill-btn lumi-chip" onclick="loadRedlinePair('KESTREL-COC-804', this)">
          Quillfeather § 8.04 CoC
        </button>
      </div>
      <div class="toolbar-right">
        <span id="redline-stats-pill" class="status-pill lumi-status-badge blue">74.2% Similarity · 0.4ms Diff</span>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <section class="ge-kpi-grid discover-reveal" aria-label="Redline & Playbook Metrics">
      <div class="lumi-card card--interactive" onclick="loadRedlinePair('KESTREL-SPA-802')">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Indemnity Cap Delta</span>
          <span class="lumi-status-badge lumi-badge-red"><span class="lumi-status-badge-dot"></span>High Risk</span>
        </div>
        <div class="gds-headline-l">0.25% vs 0.75%</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">$10.5M Skadden v4 vs $31.5M LexGraph v3</div>
      </div>
      <div class="lumi-card card--interactive" onclick="loadRedlinePair('KESTREL-SPA-802')">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Basket Structure</span>
          <span class="lumi-status-badge lumi-badge-yellow"><span class="lumi-status-badge-dot"></span>Near Threshold</span>
        </div>
        <div class="gds-headline-l">Tipping Basket</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">First-dollar vs $21.0M Deductible</div>
      </div>
      <div class="lumi-card card--interactive" onclick="openDocxModal('redline')">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">OpenXML AST Diff</span>
          <span class="lumi-status-badge lumi-badge-teal"><span class="lumi-status-badge-dot"></span>100% Verified</span>
        </div>
        <div class="gds-headline-l">74.2% Match</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">w:del / w:ins format-locked</div>
      </div>
      <div class="lumi-card card--interactive" onclick="openDocxModal('legos')">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Legal Legos Rider</span>
          <span class="lumi-status-badge lumi-badge-green"><span class="lumi-status-badge-dot"></span>Compliant</span>
        </div>
        <div class="gds-headline-l">3 Clauses</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">ABRY Fraud • § 338(h)(10) • GDPR</div>
      </div>
    </section>

    <div class="two-col-studio">
      <div class="studio-col">
        <div>
          <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px;">
            <div class="section-label gds-title-m" id="redline-doc-pair-label" style="margin-bottom:0;">
              07_M331_Brightwater_Merger_Agreement_LexGraph_v3.docx vs. 08_M331_Skadden_v4_Redline.docx
            </div>
            <button id="btn-maximize-redline-top" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="openDocxModal('redline')">
              ⤢ Maximize Redline
            </button>
          </div>
          <div id="redline-playbook-banner" class="lumi-card lumi-card-selected" style="font-size:12.5px;color:var(--color-ge-on-surface);padding:12px 16px;margin-bottom:10px;border-radius:16px;"></div>
          <div class="docx-canvas-wrap" style="border-radius:16px;">
            <div class="docx-word-toolbar">
              <div style="display:flex;align-items:center;gap:6px;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--color-ge-on-primary-container)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <span id="redline-sheet-filename">08_M331_Brightwater_SPA_Skadden_v4_Redline.docx</span>
              </div>
              <div style="display:flex;align-items:center;gap:8px;">
                <span id="redline-toolbar-mode-label" style="font-size:10.5px;color:var(--color-ge-on-primary-container);">Track Changes: ALL MARKUP</span>
                <button id="btn-maximize-redline" type="button" class="docx-max-btn" onclick="openDocxModal('redline')">⤢ Maximize</button>
              </div>
            </div>
            <div class="docx-word-toolbar-sub">
              <span>1 · · · 2 · · · 3 · · · 4 · · · 5 · · · 6 · · · 7</span>
              <span id="redline-ruler-legend">STRIKETHROUGH: REJECTED TEXT  |  GREEN: ACTIVE / ACCEPTED PLAYBOOK LINE</span>
            </div>
            <div style="padding:10px 12px;background:var(--color-ge-surface-container-high);">
              <div class="docx-paper-sheet clickable-sheet" onclick="openDocxModal('redline')" title="Click to open centered full-page Redline overlay" style="padding:16px 22px;">
                <div class="docx-running-header">
                  <span>APEX LAW PARTNERS LLP · TRACK CHANGES COMPARE</span>
                  <span id="redline-sheet-matter">MATTER M-331-KESTREL</span>
                </div>
                <div id="redline-sheet-title" style="font-family:var(--font-serif);font-size:14.5px;font-weight:700;color:var(--color-ge-on-surface);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.02em;">
                  ARTICLE VIII — INDEMNIFICATION · SECTION 8.02
                </div>
                <div id="redline-diff-slab" class="docx-redline-margin"></div>
                <div class="docx-running-footer">
                  <span>Compare: LexGraph Playbook v3.4 ↔ Counterparty Markup v4.0</span>
                  <span>OpenXML w:del / w:ins</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <span class="section-label gds-title-m">Tracked Playbook Deviations (EditCardUI)</span>
            <button id="btn-reset-redline-cards" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="resetRedlineDecisions()">Reset decisions</button>
          </div>
          <div id="redline-edit-cards" class="discover-reveal"></div>
        </div>
      </div>

      <div class="studio-col">
        <div class="lumi-card" style="padding:16px;">
          <div class="section-label gds-title-m" style="margin-bottom:4px;">LexGraph Privacy Pro &amp; M&amp;A "Legal Legos" Clause Blocks</div>
          <p class="gds-body-s" style="color:var(--color-ge-on-surface-variant);margin-bottom:10px;">
            Select pre-vetted LexGraph Playbook clause blocks to assemble a numbered OpenXML <code>.docx</code> rider:
          </p>
          <div id="legos-checkbox-list" style="display:flex;flex-direction:column;gap:8px;margin-bottom:14px;">
            <label class="liquid-glass-flat" style="display:flex;align-items:flex-start;gap:8px;padding:9px 12px;border-radius:12px;cursor:pointer;">
              <input type="checkbox" class="lego-cb" value="LEGO-DE-FRAUD" checked onchange="updateLegalLegos()" style="margin-top:3px;" />
              <div>
                <div style="font-size:12.5px;font-weight:600;color:var(--color-ge-on-surface);">LEGO-DE-FRAUD · Delaware Express Actual Fraud (ABRY)</div>
                <div style="font-size:11.5px;color:var(--color-ge-on-surface-variant);">Article VIII → Section 8.02(c)(i)..(ii) · Excludes constructive/equitable fraud</div>
              </div>
            </label>
            <label class="liquid-glass-flat" style="display:flex;align-items:flex-start;gap:8px;padding:9px 12px;border-radius:12px;cursor:pointer;">
              <input type="checkbox" class="lego-cb" value="LEGO-338H10-TAX" checked onchange="updateLegalLegos()" style="margin-top:3px;" />
              <div>
                <div style="font-size:12.5px;font-weight:600;color:var(--color-ge-on-surface);">LEGO-338H10-TAX · IRC § 338(h)(10) $14.2M Tax Escrow</div>
                <div style="font-size:11.5px;color:var(--color-ge-on-surface-variant);">Article VI → Section 6.09(a)..(b) · Citibank N.A. 18-month tax reserve</div>
              </div>
            </label>
            <label class="liquid-glass-flat" style="display:flex;align-items:flex-start;gap:8px;padding:9px 12px;border-radius:12px;cursor:pointer;">
              <input type="checkbox" class="lego-cb" value="LEGO-PRIVACY-PRO" checked onchange="updateLegalLegos()" style="margin-top:3px;" />
              <div>
                <div style="font-size:12.5px;font-weight:600;color:var(--color-ge-on-surface);">LEGO-PRIVACY-PRO · Zero Foundation Model Training &amp; GDPR</div>
                <div style="font-size:11.5px;color:var(--color-ge-on-surface-variant);">Article XI → Section 11.04(a)..(c) · 24-hour cyber breach notice</div>
              </div>
            </label>
            <label class="liquid-glass-flat" style="display:flex;align-items:flex-start;gap:8px;padding:9px 12px;border-radius:12px;cursor:pointer;">
              <input type="checkbox" class="lego-cb" value="LEGO-MFN-FUNDGEN" onchange="updateLegalLegos()" style="margin-top:3px;" />
              <div>
                <div style="font-size:12.5px;font-weight:600;color:var(--color-ge-on-surface);">LEGO-MFN-FUNDGEN · Size-Tiered LP MFN Election Rider</div>
                <div style="font-size:11.5px;color:var(--color-ge-on-surface-variant);">Side Letter → Paragraph 4(a)..(c) · $250M+ anchor carve-out</div>
              </div>
            </label>
          </div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <span class="section-label gds-title-m" style="margin-bottom:0;">Composed Multi-Level .docx Preview</span>
            <div style="display:flex;gap:6px;">
              <button id="btn-copy-legos" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="copyLegalLegosText()">Copy Rider</button>
              <button id="btn-compose-legos" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="updateLegalLegos(true)">Refresh Outline</button>
              <button id="btn-maximize-legos" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-blue pill-btn-xs" onclick="openDocxModal('legos')">⤢ Maximize</button>
            </div>
          </div>
          <div class="docx-canvas-wrap" style="border-radius:16px;">
            <div class="docx-word-toolbar">
              <div style="display:flex;align-items:center;gap:6px;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--color-ge-on-primary-container)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <span>LexGraph_Legal_Legos_Composed_Rider.docx</span>
              </div>
              <div style="display:flex;align-items:center;gap:8px;">
                <span id="legos-block-count-badge" style="font-size:10.5px;color:var(--color-ge-on-primary-container);">3 Clauses · Print Layout</span>
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

        <!-- Gemini Enterprise PromptPlate (components/luminous/composer/Composer.tsx) -->
        <div class="lumi-composer">
          <div class="gds-body-m" style="color:var(--color-ge-on-surface-variant); margin-bottom:10px;">
            Ask Gemini 3.8 Flash to draft a compromise indemnity basket, insert Delaware fraud blocks, or co-edit in live OpenXML print layout...
          </div>
          <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; flex-wrap:wrap;">
            <span class="lumi-source-chip">
              <span class="google-symbols" style="font-size:14px; color:var(--color-teal-icon);">verified</span>
              OpenXML AST + LexGraph Playbook v3.4
            </span>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
              <button type="button" class="lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="document.getElementById('format-proof-showcase')?.scrollIntoView({behavior:'smooth'})">
                <span class="google-symbols" style="font-size:16px;">fact_check</span> Format-Lock Output Proof
              </button>
              <button type="button" class="lumi-btn lumi-btn-accent lumi-btn-sm button--state-layer" onclick="openDocxModal('redline')">
                <span class="google-symbols filled" style="font-size:16px;">auto_awesome</span> Co-Edit in Gemini Workspace
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- =================================================================== -->
    <!-- FORMAT-LOCKED OUTPUT PROOF: .DOCX (OPENXML) VS GOOGLE DOCS API      -->
    <!-- =================================================================== -->
    <div id="format-proof-showcase" class="lumi-card discover-reveal" style="padding:18px 20px; margin-top:8px; flex-shrink:0; background:var(--color-ge-surface-container-lowest); border:1px solid var(--color-ge-outline-variant); border-radius:16px;">
      <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom:12px;">
        <div>
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px; flex-wrap:wrap;">
            <span class="gds-title-m" style="font-weight:600; color:var(--color-ge-on-surface);">Format-Locked Co-Editing Output Proof: Why Formatting Is Never Broken</span>
            <span class="lumi-status-badge lumi-badge-green"><span class="lumi-status-badge-dot"></span>100% Litera Compare Safe</span>
          </div>
          <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">
            Compare the actual rendered output and underlying AST/API payload when a contract is opened &amp; modified as a native <strong>.docx (OpenXML)</strong> vs. a native <strong>Google Doc (batchUpdate API)</strong> vs. the broken <strong>Round-Trip Conversion Anti-Pattern</strong>.
          </div>
        </div>
        <div class="lumi-segmented-group" role="tablist" aria-label="Format Proof Examples">
          <button id="btn-proof-docx" type="button" class="lumi-segmented-item active" onclick="switchFormatProofTab('docx', this)">
            <span class="google-symbols" style="font-size:15px;">description</span> 1. Native .docx (OpenXML AST)
          </button>
          <button id="btn-proof-gdocs" type="button" class="lumi-segmented-item" onclick="switchFormatProofTab('gdocs', this)">
            <span class="google-symbols" style="font-size:15px;">article</span> 2. Native Google Doc (batchUpdate)
          </button>
          <button id="btn-proof-broken" type="button" class="lumi-segmented-item" onclick="switchFormatProofTab('broken', this)">
            <span class="google-symbols" style="font-size:15px; color:var(--color-red-icon);">warning</span> 3. Broken Round-Trip (.docx→GDocs→.docx)
          </button>
        </div>
      </div>

      <!-- TAB 1: NATIVE .DOCX OPENXML AST OUTPUT PROOF -->
      <div id="proof-pane-docx" class="format-proof-pane" style="display:grid; grid-template-columns:1.05fr 0.95fr; gap:16px; align-items:start;">
        <div class="docx-canvas-wrap" style="border-radius:14px;">
          <div class="docx-word-toolbar">
            <div style="display:flex; align-items:center; gap:6px;">
              <span class="google-symbols" style="font-size:15px; color:var(--color-ge-on-primary-container);">verified</span>
              <span>02_LexGraph_v3_Gemini_AST_Redlined_FormatLocked.docx (Opened &amp; Saved as Native .docx)</span>
            </div>
            <span class="lumi-status-badge lumi-badge-green" style="height:22px; font-size:11px;">w:numId=14 Intact</span>
          </div>
          <div style="padding:14px 18px; background:var(--color-ge-surface-container-lowest); font-family:var(--font-serif); color:var(--color-ge-on-surface);">
            <div style="display:flex; justify-content:space-between; font-family:var(--font-sans); font-size:10px; color:var(--color-ge-on-surface-variant); border-bottom:1px solid var(--color-ge-outline-variant); padding-bottom:6px; margin-bottom:10px;">
              <span>HEADER: APEX LAW PARTNERS LLP · MATTER M-331-KESTREL</span>
              <span>PAGE 42 · STYLES &amp; NUMBERING LOCKED</span>
            </div>
            <div style="text-align:center; font-weight:700; font-size:15px; margin-bottom:6px; letter-spacing:0.02em;">
              ARTICLE VIII — INDEMNIFICATION &amp; SURVIVAL <span style="font-family:var(--font-mono); font-size:10px; font-weight:500; background:var(--color-blue-bg); color:var(--color-blue-text); padding:1px 6px; border-radius:4px;">w:pStyle="LexGraphArticleHeading"</span>
            </div>
            <div style="margin-left:18px; font-weight:700; font-size:14px; text-decoration:underline; margin-bottom:8px;">
              Section 8.02 Limitation on Indemnification. <span style="font-family:var(--font-mono); font-size:10px; font-weight:500; text-decoration:none; background:var(--color-blue-bg); color:var(--color-blue-text); padding:1px 6px; border-radius:4px;">w:pStyle="LexGraphSection2"</span>
            </div>
            <div style="margin-left:36px; text-indent:-18px; font-size:13.5px; line-height:1.55; margin-bottom:8px;">
              <strong>(a) Basket Structure.</strong> Notwithstanding anything to the contrary in this Agreement, the Seller Parties shall have no liability under Section 8.01(a) until the aggregate amount of all Losses exceeds an amount equal to
              <span class="redline-del">0.25% of the Base Purchase Price ($10,500,000) (the &ldquo;Tipping Basket&rdquo;), from the first dollar of all Losses.</span>
              <span class="redline-ins">0.50% of the Base Purchase Price ($21,000,000) (the &ldquo;True Deductible&rdquo;), and then strictly for the excess over the True Deductible.</span>
              <span style="font-family:var(--font-mono); font-size:10px; background:var(--color-green-bg); color:var(--color-green-text); padding:1px 6px; border-radius:4px;">w:ilvl="1" w:numId="14" (36pt indent)</span>
            </div>
            <div style="margin-left:54px; text-indent:-18px; font-size:13px; line-height:1.5; color:var(--color-ge-on-surface);">
              <strong>(i) De Minimis Threshold.</strong> No individual claim below $150,000 (&ldquo;Mini-Basket&rdquo;) shall be counted toward the True Deductible.
              <span style="font-family:var(--font-mono); font-size:10px; background:var(--color-green-bg); color:var(--color-green-text); padding:1px 6px; border-radius:4px;">w:ilvl="2" w:numId="14" (54pt indent)</span>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; padding-top:10px; border-top:1px solid var(--color-ge-outline-variant); font-family:var(--font-sans);">
              <a href="__DEFAULT_API_BASE__/api/redline/format-proof-docx?mode=before" target="_blank" class="lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" style="text-decoration:none;">
                <span class="google-symbols" style="font-size:15px;">download</span> 1. Before (Skadden v4 .docx)
              </a>
              <a href="__DEFAULT_API_BASE__/api/redline/format-proof-docx?mode=after_ast" target="_blank" class="lumi-btn lumi-btn-filled lumi-btn-sm button--state-layer" style="text-decoration:none;">
                <span class="google-symbols" style="font-size:15px;">download</span> 2. After Gemini AST Redline (.docx)
              </a>
            </div>
          </div>
        </div>

        <div class="lumi-card lumi-card-tonal" style="padding:14px 16px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span class="gds-label-l">Under-the-Hood OpenXML AST Diff (word/document.xml)</span>
            <span class="lumi-status-badge lumi-badge-teal">0 False Diffs in Litera</span>
          </div>
          <pre style="margin:0; padding:12px; border-radius:10px; background:var(--color-ge-surface-container-lowest); border:1px solid var(--color-ge-outline-variant); font-family:var(--font-mono); font-size:11px; line-height:1.5; overflow-x:auto; color:var(--color-ge-on-surface);">&lt;!-- word/styles.xml SHA-256: UNCHANGED (0 bytes modified) --&gt;
&lt;!-- word/numbering.xml SHA-256: UNCHANGED (w:numId="14" intact) --&gt;
&lt;w:p w14:paraId="4829A10C"&gt;
  &lt;w:pPr&gt;
    &lt;w:pStyle w:val="LexGraphIndentLevel2"/&gt;
    &lt;w:numPr&gt;&lt;w:ilvl w:val="1"/&gt;&lt;w:numId w:val="14"/&gt;&lt;/w:numPr&gt;
    &lt;w:ind w:left="720" w:hanging="360"/&gt;
  &lt;/w:pPr&gt;
  &lt;w:del w:id="901" w:author="LexGraph Gemini Legal AI"&gt;
    &lt;w:r&gt;&lt;w:delText&gt;0.25% Tipping Basket ($10,500,000)&lt;/w:delText&gt;&lt;/w:r&gt;
  &lt;/w:del&gt;
  &lt;w:ins w:id="902" w:author="LexGraph Gemini Legal AI"&gt;
    &lt;w:r&gt;&lt;w:t&gt;0.50% True Deductible ($21,000,000)&lt;/w:t&gt;&lt;/w:r&gt;
  &lt;/w:ins&gt;
&lt;/w:p&gt;</pre>
          <div class="gds-body-s" style="margin-top:8px; color:var(--color-ge-on-surface-variant);">
            <strong>Why Format Never Breaks:</strong> Our backend never converts <code>.docx</code> to HTML/Google Docs and back. It mutates only the target <code>&lt;w:p&gt;</code> node in <code>word/document.xml</code> (or calls <code>Office.js insertOoxml</code> inside Word), keeping 100% of custom styles, 9-level numbering, and page margins untouched.
          </div>
        </div>
      </div>

      <!-- TAB 2: NATIVE GOOGLE DOCS (BATCHUPDATE API) OUTPUT PROOF -->
      <div id="proof-pane-gdocs" class="format-proof-pane" style="display:none; grid-template-columns:1.05fr 0.95fr; gap:16px; align-items:start;">
        <div class="docx-canvas-wrap" style="border-radius:14px;">
          <div class="docx-word-toolbar">
            <div style="display:flex; align-items:center; gap:6px;">
              <span class="google-symbols" style="font-size:15px; color:var(--color-ge-on-primary-container);">article</span>
              <span>Project_Kestrel_SPA_Workstream_Draft (Opened &amp; Edited as Native Google Doc)</span>
            </div>
            <span class="lumi-status-badge lumi-badge-blue" style="height:22px; font-size:11px;">listId: kix.lexgraph9level</span>
          </div>
          <div style="padding:14px 18px; background:var(--color-ge-surface-container-lowest); font-family:var(--font-serif); color:var(--color-ge-on-surface);">
            <div style="display:flex; justify-content:space-between; font-family:var(--font-sans); font-size:10px; color:var(--color-ge-on-surface-variant); border-bottom:1px solid var(--color-ge-outline-variant); padding-bottom:6px; margin-bottom:10px;">
              <span>GOOGLE DOCS NATIVE CANVAS · REVISION ID: ALm37BV_kestrel_rev42</span>
              <span>NAMED STYLES &amp; KIX LISTS INTACT</span>
            </div>
            <div style="text-align:center; font-weight:700; font-size:15px; margin-bottom:6px;">
              ARTICLE VIII — INDEMNIFICATION &amp; SURVIVAL <span style="font-family:var(--font-mono); font-size:10px; font-weight:500; background:var(--color-blue-bg); color:var(--color-blue-text); padding:1px 6px; border-radius:4px;">namedStyleType: HEADING_1</span>
            </div>
            <div style="margin-left:18px; font-weight:700; font-size:14px; text-decoration:underline; margin-bottom:8px;">
              Section 8.02 Limitation on Indemnification. <span style="font-family:var(--font-mono); font-size:10px; font-weight:500; text-decoration:none; background:var(--color-blue-bg); color:var(--color-blue-text); padding:1px 6px; border-radius:4px;">namedStyleType: HEADING_2</span>
            </div>
            <div style="margin-left:36px; text-indent:-18px; font-size:13.5px; line-height:1.55; margin-bottom:8px;">
              <strong>(a) Basket Structure (Index 1482..1634):</strong> Notwithstanding anything to the contrary in this Agreement, the Seller Parties shall have no liability under Section 8.01(a) until the aggregate amount of all Losses exceeds
              <span class="redline-ins">0.50% of the Base Purchase Price ($21,000,000) (the &ldquo;True Deductible&rdquo;), and Seller Parties shall be liable strictly for the excess over the True Deductible.</span>
              <span style="font-family:var(--font-mono); font-size:10px; background:var(--color-green-bg); color:var(--color-green-text); padding:1px 6px; border-radius:4px;">nestingLevel:1 · indent:36pt</span>
            </div>
            <div style="margin-left:54px; text-indent:-18px; font-size:13px; line-height:1.5;">
              <strong>(i) De Minimis Threshold:</strong> Individual claims below $150,000 excluded.
              <span style="font-family:var(--font-mono); font-size:10px; background:var(--color-green-bg); color:var(--color-green-text); padding:1px 6px; border-radius:4px;">nestingLevel:2 · indent:54pt</span>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; padding-top:10px; border-top:1px solid var(--color-ge-outline-variant); font-family:var(--font-sans);">
              <a href="https://docs.google.com/document/d/1bFWf6s-sqOeBP7X3J3i_uB2KD6cjhckhLSaEWwFgqVI/edit" target="_blank" class="lumi-btn lumi-btn-filled lumi-btn-sm button--state-layer" style="text-decoration:none;">
                <span class="google-symbols" style="font-size:15px;">open_in_new</span> Open Live Google Doc Proof (Edited via batchUpdate)
              </a>
            </div>
          </div>
        </div>

        <div class="lumi-card lumi-card-tonal" style="padding:14px 16px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span class="gds-label-l">Surgical Google Docs API Payload (documents.batchUpdate)</span>
            <span class="lumi-status-badge lumi-badge-green">NamedStyles Intact</span>
          </div>
          <pre style="margin:0; padding:12px; border-radius:10px; background:var(--color-ge-surface-container-lowest); border:1px solid var(--color-ge-outline-variant); font-family:var(--font-mono); font-size:11px; line-height:1.5; overflow-x:auto; color:var(--color-ge-on-surface);">// POST https://docs.googleapis.com/v1/documents/{docId}:batchUpdate
// Mutates strictly inside [startIndex: 1482, endIndex: 1589]
// (Leaves trailing '\n' untouched so paragraph style &amp; listId never reset)
{
  "writeControl": { "requiredRevisionId": "ALm37BV_kestrel_rev42" },
  "requests": [
    { "deleteContentRange": { "range": { "startIndex": 1482, "endIndex": 1589 } } },
    { "insertText": {
        "location": { "index": 1482 },
        "text": "0.50% of Base Purchase Price ($21,000,000) ('True Deductible')..."
    } },
    { "createNamedRange": {
        "name": "lexgraph_playbook_v3_sec_8_02_a",
        "range": { "startIndex": 1482, "endIndex": 1634 }
    } }
  ]
}</pre>
          <div class="gds-body-s" style="margin-top:8px; color:var(--color-ge-on-surface-variant);">
            <strong>Why Format Never Breaks in Google Docs:</strong> In Google Docs, paragraph styles (<code>HEADING_2</code>, <code>36pt</code> hanging indent, and <code>bullet.listId</code>) are attached to the paragraph's trailing <code>\n</code> newline token. By replacing only the inner text range <code>[startIndex, endIndex - 1]</code>, 100% of alignments and list hierarchies remain intact.
          </div>
        </div>
      </div>

      <!-- TAB 3: BROKEN ROUND-TRIP CONVERSION ANTI-PATTERN (.DOCX -> GDOCS -> .DOCX) -->
      <div id="proof-pane-broken" class="format-proof-pane" style="display:none; grid-template-columns:1.05fr 0.95fr; gap:16px; align-items:start;">
        <div class="docx-canvas-wrap" style="border-radius:14px; border-color:var(--color-red-border);">
          <div class="docx-word-toolbar" style="background:var(--color-red-bg); color:var(--color-red-text);">
            <div style="display:flex; align-items:center; gap:6px;">
              <span class="google-symbols" style="font-size:15px; color:var(--color-red-icon);">error</span>
              <span>03_BROKEN_RoundTrip_GDocs_Conversion_Corrupted.docx (Anti-Pattern: .docx → GDocs → .docx)</span>
            </div>
            <span class="lumi-status-badge lumi-badge-red" style="height:22px; font-size:11px;">120 Pages Corrupted</span>
          </div>
          <div style="padding:14px 18px; background:var(--color-ge-surface-container-lowest); font-family:sans-serif; color:var(--color-ge-on-surface);">
            <div style="display:flex; justify-content:space-between; font-size:10px; color:var(--color-red-text); border-bottom:1px solid var(--color-red-border); padding-bottom:6px; margin-bottom:10px;">
              <span>✗ HEADER STRIPPED: Running Matter Header &amp; Page Tab Alignment Shifted</span>
              <span>FONT RESET TO ARIAL 11PT</span>
            </div>
            <div style="font-size:13.5px; margin-bottom:6px; color:var(--color-red-text);">
              1. INDEMNIFICATION AND SURVIVAL <span style="font-family:var(--font-mono); font-size:10px; background:var(--color-red-bg); padding:1px 6px; border-radius:4px;">✗ Lost ARTICLE VIII Roman Heading &amp; Centering</span>
            </div>
            <div style="font-size:13px; margin-bottom:6px; color:var(--color-red-text);">
              1. Limitation on Indemnification. <span style="font-family:var(--font-mono); font-size:10px; background:var(--color-red-bg); padding:1px 6px; border-radius:4px;">✗ Reset from Section 8.02 to flat "1."</span>
            </div>
            <div style="font-size:12.5px; line-height:1.5; margin-bottom:6px;">
              a. Seller Parties shall have no liability under <strong style="color:var(--color-red-text);">[Error! Reference source not found.]</strong> until Losses exceed 0.50% True Deductible ($21,000,000).
              <span style="font-family:var(--font-mono); font-size:10px; background:var(--color-red-bg); color:var(--color-red-text); padding:1px 6px; border-radius:4px;">✗ 36pt hanging indent collapsed · w:fldSimple broken</span>
            </div>
            <div style="font-size:12.5px; line-height:1.5; color:var(--color-ge-on-surface-variant);">
              1. De Minimis Threshold. <span style="font-family:var(--font-mono); font-size:10px; background:var(--color-red-bg); color:var(--color-red-text); padding:1px 6px; border-radius:4px;">✗ Sub-level (i) detached from parent list</span>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; padding-top:10px; border-top:1px solid var(--color-ge-outline-variant);">
              <a href="__DEFAULT_API_BASE__/api/redline/format-proof-docx?mode=broken_roundtrip" target="_blank" class="lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" style="text-decoration:none; color:var(--color-red-text); border-color:var(--color-red-border);">
                <span class="google-symbols" style="font-size:15px;">download</span> Download Corrupted Round-Trip .docx (Inspect Failure)
              </a>
            </div>
          </div>
        </div>

        <div class="lumi-card" style="padding:14px 16px; background:var(--color-red-bg); border-color:var(--color-red-border);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span class="gds-label-l" style="color:var(--color-red-text);">Why Law Firms Forbid .docx → Google Docs → .docx Conversion</span>
            <span class="lumi-status-badge lumi-badge-red">FAILS LITERA COMPARE</span>
          </div>
          <pre style="margin:0; padding:12px; border-radius:10px; background:var(--color-ge-surface-container-lowest); border:1px solid var(--color-red-border); font-family:var(--font-mono); font-size:11px; line-height:1.5; overflow-x:auto; color:var(--color-red-text);">&lt;!-- CORRUPTED ROUND-TRIP EXPORT --&gt;
&lt;!-- 1. word/styles.xml overwritten with generic Normal_kix --&gt;
&lt;!-- 2. word/numbering.xml w:numId="14" 9-level outline destroyed --&gt;
&lt;!-- 3. All &lt;w:ins&gt;/&lt;w:del&gt; author/date attributes flattened --&gt;
&lt;!-- 4. Litera Compare Result: 1,840 / 1,840 paragraphs (120 pages)
        light up as modified (100% false-positive redline noise!) --&gt;</pre>
          <div class="gds-body-s" style="margin-top:8px; color:var(--color-red-text);">
            <strong>Architectural Takeaway:</strong> Never convert counterparty <code>.docx</code> agreements into Google Docs and re-export. Always keep <code>.docx</code> on the OpenXML AST / <code>Office.js</code> track and Google Docs on the <code>documents.batchUpdate</code> track.
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===================================================================== -->
  <!-- STUDIO 3: FUNDGEN / FUNDHQ MFN & ANTITRUST HSR (lexgraph-funds-antitrust) -->
  <!-- ===================================================================== -->
  <section id="funds-view" class="studio-screen">
    <header class="mike-page-header lumi-page-header">
      <div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px; flex-wrap:wrap;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Active Matters / Matter M-610 ($12.5B Fund VIII LPA) &amp; Matter M-720 (FTC Second Request HHI)</span>
          <span class="lumi-status-badge lumi-badge-purple">
            <span class="google-symbols filled" style="font-size:13px;">auto_awesome</span> Luminous AI Active
          </span>
        </div>
        <h1 class="header-title gds-headline-m">FundGen / FundHQ MFN &amp; Antitrust HSR Analyzer</h1>
      </div>
      <div class="header-actions">
        <button type="button" class="lumi-icon-btn" onclick="toggleGeThemeMode()" title="Toggle Light / Dark Mode" aria-label="Toggle Light or Dark Mode">
          <span class="google-symbols ge-theme-icon">dark_mode</span>
        </button>
        <a href="__DEFAULT_API_BASE__/api/corpus/file/DOC-FUND-02_LexGraph_FundHQ_Sovereign_LP_MFN_Side_Letter_Compendium.pdf" target="_blank" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" style="text-decoration:none;">
          <span class="google-symbols" style="font-size:16px;">description</span> FundHQ PDF
        </a>
        <a href="__DEFAULT_API_BASE__/api/corpus/file/DOC-HSR-01_Hart_Scott_Rodino_Second_Request_Market_Share_Filing.pdf" target="_blank" class="pill-btn lumi-btn lumi-btn-filled lumi-btn-sm button--state-layer" style="text-decoration:none;">
          <span class="google-symbols" style="font-size:16px;">ios_share</span> HSR Filing PDF
        </a>
        <button type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="requestHostDisplayMode('pip')">Side Panel</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="requestHostDisplayMode('fullscreen')">
          <span class="google-symbols" style="font-size:15px;">open_in_full</span> Maximize
        </button>
      </div>
    </header>

    <div class="mike-toolbar">
      <div class="toolbar-left">
        <span style="font-size:12px;font-weight:600;color:var(--color-ge-on-surface-variant);">LP Tier Filter:</span>
        <button id="btn-lp-all" type="button" class="tab-pill-btn lumi-chip active" onclick="loadFundsAntitrust(0, null, this)">
          <span class="google-symbols" style="font-size:15px;">check</span> All LPs (5)
        </button>
        <button id="btn-lp-150" type="button" class="tab-pill-btn lumi-chip" onclick="loadFundsAntitrust(150, null, this)">
          &gt;= $150M Early-Bird
        </button>
        <button id="btn-lp-250" type="button" class="tab-pill-btn lumi-chip" onclick="loadFundsAntitrust(250, null, this)">
          &gt;= $250M Sovereign Anchor
        </button>
      </div>
      <div class="toolbar-right">
        <button id="btn-hsr-remedy-toggle" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-blue" onclick="toggleHsrRemedy()">
          HSR Divestiture Remedy: ON (Cleared +30 Δ HHI)
        </button>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <section class="ge-kpi-grid discover-reveal" aria-label="FundGen & Antitrust Metrics">
      <div class="lumi-card card--interactive" onclick="loadFundsAntitrust(0, null)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Fund VIII Commitments</span>
          <span class="lumi-status-badge lumi-badge-blue"><span class="lumi-status-badge-dot"></span>Sovereign Tier</span>
        </div>
        <div class="gds-headline-l">$12.5B Cap</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">5 Institutional LPs Analyzed</div>
      </div>
      <div class="lumi-card card--interactive" onclick="loadFundsAntitrust(250, null)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Fee Savings Preserved</span>
          <span class="lumi-status-badge lumi-badge-green"><span class="lumi-status-badge-dot"></span>Compliant</span>
        </div>
        <div class="gds-headline-l">$18.4M / yr</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">Size-Tiered MFN Carve-Out</div>
      </div>
      <div class="lumi-card card--interactive" onclick="toggleHsrRemedy()">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Post-Merger HHI Delta</span>
          <span class="lumi-status-badge lumi-badge-teal"><span class="lumi-status-badge-dot"></span>Divestiture On</span>
        </div>
        <div class="gds-headline-l">+30 Δ HHI</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">Below 100-pt FTC Second Request</div>
      </div>
      <div class="lumi-card card--interactive" onclick="openDocxModal('exhibit')">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Multimodal Exhibits</span>
          <span class="lumi-status-badge lumi-badge-purple"><span class="lumi-status-badge-dot"></span>100% Verified</span>
        </div>
        <div class="gds-headline-l">4 Exhibits</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">EBITDA • Fee Curve • Org • Citibank</div>
      </div>
    </section>

    <div class="two-col-studio">
      <div class="studio-col">
        <div class="lumi-table-wrap">
          <div style="display:flex; align-items:center; justify-content:space-between; padding:12px 16px; border-bottom:1px solid var(--color-ge-outline-variant);">
            <span class="gds-title-m">FundHQ Sovereign &amp; Institutional LP Side-Letter MFN Matrix</span>
            <span class="lumi-source-chip">DOC-FUND-01 / 02</span>
          </div>
          <div id="fundhq-savings-banner" style="font-size:12px;color:var(--color-green-text);background:var(--color-green-bg);border-bottom:1px solid var(--color-green-border);padding:8px 16px;"></div>
          <div style="overflow-x:auto;">
            <table class="tr-table lumi-table">
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

        <div class="lumi-card">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <span class="gds-title-m">FTC HSR Second Request — HHI Market Concentration (DOC-HSR-01)</span>
            <span id="hsr-status-badge" class="status-pill lumi-status-badge green">CLEARED (+30 Δ HHI)</span>
          </div>
          <div id="hsr-summary-card" class="liquid-glass-flat" style="padding:10px 12px;border-radius:12px;font-size:12px;margin-bottom:10px;"></div>
          <div id="hsr-bars-container" style="display:flex;flex-direction:column;gap:6px;"></div>
        </div>
      </div>

      <div class="studio-col">
        <div id="mm-exhibit-card" class="lumi-card lumi-card-selected" style="padding:16px;">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
            <span class="gds-title-m">Extracted Multimodal Exhibits</span>
            <button id="btn-maximize-exhibit" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-blue pill-btn-xs" onclick="openDocxModal('exhibit')">⤢ Maximize</button>
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;">
            <button id="mm-btn-0" type="button" class="tab-pill-btn lumi-chip active" onclick="selectMultimodalExhibit(0, this)">EBITDA Bridge</button>
            <button id="mm-btn-1" type="button" class="tab-pill-btn lumi-chip" onclick="selectMultimodalExhibit(1, this)">LP Fee Curve</button>
            <button id="mm-btn-2" type="button" class="tab-pill-btn lumi-chip" onclick="selectMultimodalExhibit(2, this)">J.Crew Org Chart</button>
            <button id="mm-btn-3" type="button" class="tab-pill-btn lumi-chip" onclick="selectMultimodalExhibit(3, this)">Citibank $18M Scan</button>
          </div>
          <div id="mm-exhibit-title" class="gds-title-l" style="margin-bottom:6px;color:var(--color-ge-on-surface);"></div>
          <div id="mm-exhibit-takeaway" class="gds-body-s" style="color:var(--color-ge-on-surface-variant);margin-bottom:12px;"></div>
          <div style="background:var(--color-ge-surface-container-lowest);border:1px solid var(--color-ge-outline-variant);border-radius:12px;padding:10px;text-align:center;cursor:zoom-in;" onclick="openDocxModal('exhibit')" title="Click to maximize exhibit">
            <img id="mm-exhibit-img" src="__DEFAULT_API_BASE__/api/corpus/image/DOC-CHART-01_Brightwater_EBITDA_Bridge_and_Valuation_Waterfall.png" alt="Multimodal Exhibit" style="max-width:100%;max-height:260px;border-radius:6px;object-fit:contain;" />
          </div>
          <div style="margin-top:10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <span class="lumi-source-chip">
              <span class="google-symbols" style="font-size:14px; color:var(--color-teal-icon);">verified</span>
              docparse Bounding-Box → Cloud Spanner
            </span>
            <a id="mm-exhibit-pdf-link" href="__DEFAULT_API_BASE__/api/corpus/file/DOC-CHART-01_Brightwater_EBITDA_Bridge_and_Valuation_Waterfall.pdf" target="_blank" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" style="text-decoration:none;">Open Source PDF</a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===================================================================== -->
  <!-- STUDIO 4: INTAPP ETHICAL WALL & SPANNER GRAPH (lexgraph-governance-wall)  -->
  <!-- ===================================================================== -->
  <section id="governance-view" class="studio-screen">
    <header class="mike-page-header lumi-page-header">
      <div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px; flex-wrap:wrap;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Active Matters / Screen-Before-Rank Access Verification • Intapp Wall &amp; CMN Switcher</span>
          <span class="lumi-status-badge lumi-badge-purple">
            <span class="google-symbols filled" style="font-size:13px;">auto_awesome</span> Luminous AI Active
          </span>
        </div>
        <h1 class="header-title gds-headline-m">Intapp Ethical Wall &amp; Cloud Spanner Graph</h1>
      </div>
      <div class="header-actions">
        <button type="button" class="lumi-icon-btn" onclick="toggleGeThemeMode()" title="Toggle Light / Dark Mode" aria-label="Toggle Light or Dark Mode">
          <span class="google-symbols ge-theme-icon">dark_mode</span>
        </button>
        <button id="btn-verify-wall" type="button" class="pill-btn lumi-btn lumi-btn-filled lumi-btn-sm button--state-layer" onclick="loadGovernanceAndGraph(true)">
          <span class="google-symbols" style="font-size:16px;">verified</span> Verify Screen-Before-Rank
        </button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="requestHostDisplayMode('pip')">Side Panel</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="requestHostDisplayMode('fullscreen')">
          <span class="google-symbols" style="font-size:15px;">open_in_full</span> Maximize
        </button>
      </div>
    </header>

    <div class="mike-toolbar">
      <div class="toolbar-left">
        <span style="font-size:12px;font-weight:600;color:var(--color-ge-on-surface-variant);">Attorney:</span>
        <select id="gov-lawyer-select" class="field-input" style="border-radius:9999px;" onchange="loadGovernanceAndGraph()">
          <option value="L-001">L-001 · Sarah Jenkins (M&amp;A Managing Partner — Walled from M-999)</option>
          <option value="L-002">L-002 · David Vance (Senior M&amp;A Partner)</option>
          <option value="L-003">L-003 · Marcus Thorne (Tax Partner — Owner of EM-9901)</option>
          <option value="L-005">L-005 · Elena Rostova (Restructuring Partner — Cleared for M-999)</option>
        </select>
      </div>
      <div class="toolbar-right" style="flex-wrap:wrap;">
        <button id="cmn-btn-m331" type="button" class="tab-pill-btn lumi-chip active" onclick="selectGovernanceMatter('M-331-KESTREL', this)">M-331 Brightwater</button>
        <button id="cmn-btn-m402" type="button" class="tab-pill-btn lumi-chip" onclick="selectGovernanceMatter('M-402', this)">M-402 Apollo</button>
        <button id="cmn-btn-m610" type="button" class="tab-pill-btn lumi-chip" onclick="selectGovernanceMatter('M-610-FUNDGEN', this)">M-610 FundGen</button>
        <button id="cmn-btn-m720" type="button" class="tab-pill-btn lumi-chip" onclick="selectGovernanceMatter('M-720-ANTITRUST', this)">M-720 HSR</button>
        <button id="cmn-btn-m999" type="button" class="tab-pill-btn lumi-chip" onclick="selectGovernanceMatter('M-999', this)">M-999 Omega (Wall)</button>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <section class="ge-kpi-grid discover-reveal" aria-label="Governance & Graph Metrics">
      <div class="lumi-card card--interactive" onclick="loadGovernanceAndGraph(true)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Screen-Before-Rank</span>
          <span class="lumi-status-badge lumi-badge-green"><span class="lumi-status-badge-dot"></span>Enforced</span>
        </div>
        <div class="gds-headline-l">0 Leaks</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">Pre-ANN Intapp Wall Filter</div>
      </div>
      <div class="lumi-card card--interactive" onclick="selectGovernanceMatter('M-999')">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Active Ethical Walls</span>
          <span class="lumi-status-badge lumi-badge-red"><span class="lumi-status-badge-dot"></span>Restricted</span>
        </div>
        <div class="gds-headline-l">28 Walls</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">Matter M-999 Omega Blocked</div>
      </div>
      <div class="lumi-card card--interactive" onclick="selectGovernanceMatter('M-331-KESTREL')">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Spanner Graph Nodes</span>
          <span class="lumi-status-badge lumi-badge-teal"><span class="lumi-status-badge-dot"></span>100% Verified</span>
        </div>
        <div class="gds-headline-l">146 Nodes</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">47 Docs • 57 Clauses • 14 Matters</div>
      </div>
      <div class="lumi-card card--interactive" onclick="setGovGrant(!grantActiveState)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Teammate Grant TTL</span>
          <span class="lumi-status-badge lumi-badge-yellow"><span class="lumi-status-badge-dot"></span>Active</span>
        </div>
        <div class="gds-headline-l">30 Days</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">EM-9901 Tax Partner Grant</div>
      </div>
    </section>

    <div class="two-col-studio">
      <div class="studio-col">
        <div id="gov-status-banner" class="lumi-card lumi-card-selected" style="padding:14px 16px;"></div>

        <div class="lumi-card" style="padding:14px 16px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <span class="gds-title-m">Unfiled Deal Email 30-Day Teammate Grant (EM-9901)</span>
            <span id="gov-grant-pill" class="status-pill lumi-status-badge green">ACTIVE (30-Day TTL)</span>
          </div>
          <p class="gds-body-s" style="color:var(--color-ge-on-surface-variant);margin-bottom:10px;">
            Controls whether Marcus Thorne's unfiled Exchange tax email (<code>EM-9901</code> · $14.2M IRC § 338(h)(10) Gross-Up) is traversable in Cloud Spanner <code>TeammateGrants</code>:
          </p>
          <div style="display:flex;gap:8px;">
            <button id="btn-gov-grant" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-blue pill-btn-xs" onclick="setGovGrant(true)">Grant 30-Day Access</button>
            <button id="btn-gov-revoke" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="setGovGrant(false)">Revoke Access</button>
          </div>
        </div>

        <div class="lumi-card" style="padding:14px 16px;">
          <div class="gds-title-m" style="margin-bottom:8px;">Cloud Spanner ISO GQL Screen-Before-Rank Query</div>
          <pre id="gov-gql-box" class="text-slab" style="font-family:var(--font-mono);font-size:11.5px;white-space:pre-wrap;"></pre>
        </div>
      </div>

      <div class="studio-col">
        <div class="lumi-card" style="padding:14px 16px;">
          <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
            <span class="gds-title-m">Live Cloud Spanner Property Graph (LexGraphLegalGraph)</span>
            <span class="lumi-source-chip">ISO GQL</span>
          </div>
          <div id="graph-nodes-list" style="display:flex;flex-direction:column;gap:8px;"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===================================================================== -->
  <!-- STUDIO 5: PARTNER DEAL INBOX & CALENDAR TRIAGE (lexgraph-inbox-calendar)  -->
  <!-- ===================================================================== -->
  <section id="inbox-view" class="studio-screen">
    <header class="mike-page-header lumi-page-header">
      <div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px; flex-wrap:wrap;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Active Matters / Sarah Jenkins (L-001) • iManage CMN Auto-Filer &amp; FTC HSR Conflict Triage</span>
          <span class="lumi-status-badge lumi-badge-purple">
            <span class="google-symbols filled" style="font-size:13px;">auto_awesome</span> Luminous AI Active
          </span>
        </div>
        <h1 class="header-title gds-headline-m">Partner Deal Inbox &amp; Calendar Conflict Triage</h1>
      </div>
      <div class="header-actions">
        <button type="button" class="lumi-icon-btn" onclick="toggleGeThemeMode()" title="Toggle Light / Dark Mode" aria-label="Toggle Light or Dark Mode">
          <span class="google-symbols ge-theme-icon">dark_mode</span>
        </button>
        <button id="btn-reset-inbox" type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="resetInboxState()">
          Reset Queue
        </button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="requestHostDisplayMode('pip')">Side Panel</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" onclick="requestHostDisplayMode('fullscreen')">
          <span class="google-symbols" style="font-size:15px;">open_in_full</span> Maximize
        </button>
      </div>
    </header>

    <div class="mike-toolbar">
      <div class="toolbar-left">
        <button id="inb-filter-all" type="button" class="tab-pill-btn lumi-chip active" onclick="setInboxFilter('all', this)">
          <span class="google-symbols" style="font-size:15px;">check</span> All Priority Items (4)
        </button>
        <button id="inb-filter-pending" type="button" class="tab-pill-btn lumi-chip" onclick="setInboxFilter('pending', this)">
          Pending Sign-Off
        </button>
        <button id="inb-filter-cal" type="button" class="tab-pill-btn lumi-chip" onclick="setInboxFilter('calendar', this)">
          Calendar Conflicts (CAL-101)
        </button>
      </div>
      <div class="toolbar-right">
        <a href="__DEFAULT_API_BASE__/api/corpus/file/CAL-101_Closing_Board_Call_and_FTC_HSR_Conflict.ics" target="_blank" class="pill-btn lumi-btn lumi-btn-outlined lumi-btn-sm button--state-layer" style="text-decoration:none;">
          <span class="google-symbols" style="font-size:16px;">ios_share</span> Download .ics
        </a>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <section class="ge-kpi-grid discover-reveal" aria-label="Partner Inbox & Calendar Metrics">
      <div class="lumi-card card--interactive" onclick="setInboxFilter('all')">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Priority Partner Queue</span>
          <span class="lumi-status-badge lumi-badge-yellow"><span class="lumi-status-badge-dot"></span>Needs Triage</span>
        </div>
        <div class="gds-headline-l">4 Items</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">3 Unfiled .eml + 1 .ics Conflict</div>
      </div>
      <div class="lumi-card card--interactive" onclick="inspectRawEml(0, false)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">iManage CMN Auto-Tag</span>
          <span class="lumi-status-badge lumi-badge-teal"><span class="lumi-status-badge-dot"></span>99.4% Conf.</span>
        </div>
        <div class="gds-headline-l">3 Matters</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">31402-0018 • 40819-0004 • 72011</div>
      </div>
      <div class="lumi-card card--interactive" onclick="inspectRawEml(0, true)">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">FTC HSR Call Conflict</span>
          <span class="lumi-status-badge lumi-badge-red"><span class="lumi-status-badge-dot"></span>High Risk</span>
        </div>
        <div class="gds-headline-l">CAL-101</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">Overlaps Board Closing Call</div>
      </div>
      <div class="lumi-card card--interactive" onclick="openDocxModal('eml')">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="gds-body-s" style="color:var(--color-ge-on-surface-variant);">Exchange / iCal Sync</span>
          <span class="lumi-status-badge lumi-badge-green"><span class="lumi-status-badge-dot"></span>Connected</span>
        </div>
        <div class="gds-headline-l">RFC-822</div>
        <div class="gds-body-s" style="color:var(--color-ge-on-surface-variant); margin-top:4px;">Zero-Copy Envelope Indexing</div>
      </div>
    </section>

    <div class="two-col-studio">
      <div class="studio-col" id="inbox-emails-col">
        <div class="gds-title-m">Partner Deal Emails &amp; iManage CMN Filing Queue</div>
        <div id="inbox-email-cards" class="discover-reveal" style="display:flex;flex-direction:column;gap:10px;"></div>
      </div>

      <div class="studio-col" id="inbox-cal-col">
        <div class="gds-title-m">Closing &amp; Regulatory Calendar Conflict (CAL-101)</div>
        <div id="inbox-calendar-cards" style="display:flex;flex-direction:column;gap:10px;"></div>

        <div class="lumi-card lumi-card-selected" style="padding:14px 16px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <div class="gds-title-m" id="raw-eml-header" style="margin-bottom:0;">Rendered Exchange Email &amp; Calendar Invite Preview</div>
            <button id="btn-maximize-eml-top" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-blue pill-btn-xs" onclick="openDocxModal('eml')">⤢ Maximize</button>
          </div>
          <div class="docx-canvas-wrap" style="border-radius:12px;">
            <div class="docx-word-toolbar">
              <span>Microsoft Exchange / iManage Deal Filing Preview</span>
              <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:10.5px;color:var(--color-ge-on-primary-container);">RFC-822 / iCalendar Verified</span>
                <button id="btn-maximize-eml" type="button" class="docx-max-btn" onclick="openDocxModal('eml')">⤢ Maximize</button>
              </div>
            </div>
            <div style="padding:10px;background:var(--color-ge-surface-container-high);">
              <div id="raw-eml-viewer" class="docx-paper-sheet clickable-sheet" onclick="openDocxModal('eml')" title="Click to open centered full-page preview" style="padding:14px 18px;max-height:250px;overflow-y:auto;"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  </main>

  <!-- ===================================================================== -->
  <!-- GOOGLE WORKSPACE / WORD CO-EDITOR + GEMINI SIDE PANEL (#docx-modal-overlay) -->
  <!-- ===================================================================== -->
  <div id="docx-modal-overlay" class="docx-modal-backdrop" onclick="if(event.target===this)closeDocxModal()">
    <div class="docx-modal-window" role="dialog" aria-modal="true" aria-labelledby="docx-modal-title">

      <!-- 1. Google Workspace Top Header Bar -->
      <div class="docx-modal-header">
        <div style="display:flex;align-items:center;gap:12px;min-width:0;">
          <!-- Google Docs / Word Format Icon -->
          <div id="gw-format-icon-badge" style="width:36px;height:36px;border-radius:8px;background:var(--color-ge-accent);display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 1px 2px rgba(0,0,0,0.12);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--lumi-sys-color--white)" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="8" y1="13" x2="16" y2="13"/>
              <line x1="8" y1="17" x2="13" y2="17"/>
            </svg>
          </div>
          <div style="min-width:0;">
            <div style="display:flex;align-items:center;gap:8px;">
              <div id="docx-modal-title" contenteditable="true" spellcheck="false" style="font-size:17px;font-weight:500;color:var(--color-ge-on-surface);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:1px 4px;border-radius:4px;">
                08_M331_Brightwater_SPA_Skadden_v4_Redline.docx
              </div>
              <span title="Star document" style="color:var(--color-ge-on-surface-variant);cursor:pointer;font-size:15px;" onclick="this.textContent=this.textContent==='☆'?'★':'☆';this.style.color='var(--color-yellow-icon)';">☆</span>
              <button id="btn-format-lock-mode" type="button" onclick="toggleSourceFormatLock()" style="display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:999px;border:1px solid var(--color-blue-border);background:var(--color-blue-bg);color:var(--color-ge-primary);font-size:11px;font-weight:600;cursor:pointer;" title="Click to toggle Format-Locked .docx (OpenXML AST) vs Google Docs Native (documents.batchUpdate)">
                <span id="format-lock-dot" style="width:7px;height:7px;border-radius:50%;background:var(--color-ge-primary);"></span>
                <span id="format-lock-label">Format-Locked: .docx (OpenXML Preserved)</span>
              </button>
              <span id="gw-save-status" style="font-size:11px;color:var(--color-ge-on-surface-variant);">✓ Saved to Spanner &amp; iManage</span>
            </div>
            <div class="gw-menu-bar">
              <span class="gw-menu-item" onclick="downloadLiveEditedDocx()">File</span>
              <span class="gw-menu-item" onclick="execDocFormat('undo')">Edit</span>
              <span class="gw-menu-item" onclick="setDocxModalZoom(1.0)">View</span>
              <span class="gw-menu-item" onclick="insertCustomClauseBlock()">Insert</span>
              <span class="gw-menu-item" onclick="execDocFormat('bold')">Format</span>
              <span class="gw-menu-item" onclick="acceptAllModalRedlines()">Playbook Tools</span>
              <span class="gw-menu-item" onclick="toggleGwGeminiPanel(true)" style="color:var(--color-ge-primary);font-weight:600;">✦ Gemini</span>
              <span id="docx-modal-subtitle" style="font-size:11px;color:var(--color-ge-on-surface-variant);margin-left:6px;">
                LexGraph Playbook v3.4 vs. Counterparty v4.0
              </span>
            </div>
          </div>
        </div>

        <div style="display:flex;align-items:center;gap:8px;flex-shrink:0;">
          <button type="button" class="lumi-icon-btn" onclick="toggleGeThemeMode()" title="Toggle Light / Dark Mode" aria-label="Toggle Light or Dark Mode">
            <span class="google-symbols ge-theme-icon">dark_mode</span>
          </button>
          <button id="docx-modal-copy-btn" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="copyDocxModalText()">Copy Text</button>
          <button id="btn-export-live-docx" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="downloadLiveEditedDocx()" style="border-color:var(--color-blue-border);color:var(--color-ge-primary);font-weight:600;">
            ⬇ Export Live .docx
          </button>
          <a id="btn-open-live-gdoc-proof" href="https://docs.google.com/document/d/1bFWf6s-sqOeBP7X3J3i_uB2KD6cjhckhLSaEWwFgqVI/edit" target="_blank" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" style="border-color:var(--color-green-border);color:var(--color-green-text);font-weight:600;text-decoration:none;">
            ↗ Live Google Doc
          </a>
          <a id="docx-modal-download-btn" href="__DEFAULT_API_BASE__/api/legal-legos/docx" target="_blank" style="display:inline-flex;align-items:center;gap:6px;padding:7px 16px;border-radius:999px;background:var(--color-ge-secondary-container);color:var(--color-ge-on-secondary-container);font-size:13px;font-weight:600;text-decoration:none;border:none;">
            🔒 Share / .docx
          </a>
          <!-- 4-Point Google Workspace Gemini Sparkle Toggle -->
          <button id="btn-toggle-gw-gemini" type="button" onclick="toggleGwGeminiPanel()" title="Toggle Gemini in Workspace Side Panel" style="width:36px;height:36px;border-radius:50%;border:1px solid var(--color-ge-primary-container);background:var(--color-ge-surface-container-high);display:inline-flex;align-items:center;justify-content:center;cursor:pointer;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 2C12 7.5 16.5 12 22 12C16.5 12 12 16.5 12 22C12 16.5 7.5 12 2 12C7.5 12 12 7.5 12 2Z" fill="url(#gwSparkleGrad)"/>
              <defs>
                <linearGradient id="gwSparkleGrad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                  <stop stop-color="var(--color-ge-accent)"/>
                  <stop offset="0.5" stop-color="var(--color-purple-icon)"/>
                  <stop offset="1" stop-color="var(--color-red-icon)"/>
                </linearGradient>
              </defs>
            </svg>
          </button>
          <button id="docx-modal-close-btn" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="closeDocxModal()" style="background:var(--color-red-bg);color:var(--color-red-text);border-color:var(--color-red-border);font-weight:600;">
            ✕ Close (Esc)
          </button>
        </div>
      </div>

      <!-- 2. Google Workspace Rounded Pill Live Formatting Toolbar (var(--color-ge-surface-container-high)) -->
      <div class="gw-format-toolbar">
        <div class="gw-tool-group">
          <button type="button" class="gw-tool-btn" style="background:var(--color-ge-surface-container-lowest);border-radius:999px;padding:0 10px;font-size:11.5px;color:var(--color-ge-on-surface-variant);" onclick="document.getElementById('gw-gemini-input')?.focus()">
            🔍 Menus
          </button>
          <button id="gw-btn-undo" type="button" class="gw-tool-btn" title="Undo (Ctrl+Z)" onclick="execDocFormat('undo')">↶</button>
          <button id="gw-btn-redo" type="button" class="gw-tool-btn" title="Redo (Ctrl+Y)" onclick="execDocFormat('redo')">↷</button>
          <button type="button" class="gw-tool-btn" title="Print Document" onclick="window.print()">🖨</button>
          <div class="gw-tool-divider"></div>

          <select id="gw-zoom-select" class="gw-tool-select" onchange="setDocxModalZoom(parseFloat(this.value))" aria-label="Zoom">
            <option value="0.9">90%</option>
            <option value="1" selected>100%</option>
            <option value="1.12">112%</option>
          </select>
          <div class="gw-tool-divider"></div>

          <select id="gw-style-select" class="gw-tool-select" onchange="applyHeadingStyle(this.value)" aria-label="Text Style">
            <option value="p">Normal legal text</option>
            <option value="h2">Article / Section Heading</option>
            <option value="h3">Subclause Heading</option>
            <option value="blockquote">Block Quote / Indented</option>
          </select>
          <div class="gw-tool-divider"></div>

          <select id="gw-font-select" class="gw-tool-select" onchange="applyDocFontFamily(this.value)" aria-label="Font Family">
            <option value="'EB Garamond', Georgia, serif" selected>EB Garamond</option>
            <option value="'Times New Roman', Times, serif">Times New Roman</option>
            <option value="Arial, sans-serif">Arial</option>
            <option value="'Google Sans', Inter, sans-serif">Google Sans</option>
          </select>
          <div class="gw-tool-divider"></div>

          <button type="button" class="gw-tool-btn" title="Decrease font size" onclick="stepDocFontSize(-1)">−</button>
          <span id="gw-font-size-display" style="min-width:26px;text-align:center;font-size:12px;font-weight:600;background:var(--color-ge-surface-container-lowest);border:1px solid var(--color-ge-outline-variant);border-radius:4px;padding:2px 5px;">15</span>
          <button type="button" class="gw-tool-btn" title="Increase font size" onclick="stepDocFontSize(1)">+</button>
          <div class="gw-tool-divider"></div>

          <button id="gw-btn-bold" type="button" class="gw-tool-btn" style="font-weight:700;" title="Bold (Ctrl+B)" onclick="execDocFormat('bold')">B</button>
          <button id="gw-btn-italic" type="button" class="gw-tool-btn" style="font-style:italic;font-family:serif;" title="Italic (Ctrl+I)" onclick="execDocFormat('italic')">I</button>
          <button id="gw-btn-underline" type="button" class="gw-tool-btn" style="text-decoration:underline;" title="Underline (Ctrl+U)" onclick="execDocFormat('underline')">U</button>
          <button id="gw-btn-strike" type="button" class="gw-tool-btn" style="text-decoration:line-through;color:var(--lumi-sys-color--error);" title="Strikethrough / Redline Delete" onclick="execDocFormat('strikeThrough')">S̶</button>
          <button id="gw-btn-highlight-yellow" type="button" class="gw-tool-btn" title="Highlight Yellow (Pin-Cite)" onclick="applyHighlightColor('var(--color-yellow-bg)')">
            <span style="background:var(--color-yellow-bg);padding:1px 5px;border-radius:3px;font-weight:700;">A🖍</span>
          </button>
          <button id="gw-btn-highlight-green" type="button" class="gw-tool-btn" title="Highlight Green (LexGraph Playbook Approved)" onclick="applyHighlightColor('var(--color-green-bg)')">
            <span style="background:var(--color-green-bg);color:var(--color-green-text);padding:1px 5px;border-radius:3px;font-weight:700;">✓A</span>
          </button>
          <div class="gw-tool-divider"></div>

          <button type="button" class="gw-tool-btn" title="Align Left" onclick="execDocFormat('justifyLeft')">⬅</button>
          <button type="button" class="gw-tool-btn" title="Justify Legal Paragraph" onclick="execDocFormat('justifyFull')">☰</button>
          <button id="gw-btn-insert-clause" type="button" class="gw-tool-btn" style="background:var(--color-ge-primary-container);color:var(--color-ge-on-primary-container);padding:0 10px;border-radius:999px;font-size:11.5px;font-weight:600;" onclick="insertCustomClauseBlock()">
            + Insert Clause
          </button>
        </div>

        <div class="gw-tool-group">
          <span id="gw-edit-mode-pill" style="display:inline-flex;align-items:center;gap:5px;background:var(--color-ge-surface-container-lowest);border:1px solid var(--color-ge-outline-variant);border-radius:999px;padding:3px 10px;font-size:11.5px;font-weight:500;color:var(--color-ge-primary);">
            ✎ Suggesting (Track Changes ON)
          </span>
        </div>
      </div>

      <!-- 3. Context Action Bar (#docx-modal-controls) -->
      <div id="docx-modal-controls" class="docx-modal-controls-bar"></div>

      <!-- 4. 3-Column Google Workspace Body (Left Document Tabs + Center Live Sheet + Right Gemini Assistant) -->
      <div class="gw-workspace-body">

        <!-- Left Column: Google Docs "Document tabs" & Outline -->
        <aside class="gw-left-tabs-pane" id="gw-left-tabs-pane">
          <div style="display:flex;align-items:center;justify-content:space-between;padding:4px 8px 10px 8px;">
            <span style="font-size:12px;font-weight:600;color:var(--color-ge-on-surface-variant);">Document tabs</span>
            <button type="button" class="gw-tool-btn" title="Add Clause Rider Tab" onclick="insertCustomClauseBlock()">+</button>
          </div>

          <button id="gw-tab-802" type="button" class="gw-tab-pill active" onclick="switchModalRedlineTab('KESTREL-SPA-802', this)">
            <span>📄 § 8.02(b) Indemnity</span>
          </button>
          <button id="gw-tab-804a" type="button" class="gw-tab-pill" onclick="switchModalRedlineTab('KESTREL-SCRAPE-804', this)">
            <span>📄 § 8.04(a) Scrape</span>
          </button>
          <button id="gw-tab-304" type="button" class="gw-tab-pill" onclick="switchModalRedlineTab('KESTREL-TAX-304', this)">
            <span>📄 § 3.04 Tax 338(h)(10)</span>
          </button>
          <button id="gw-tab-804c" type="button" class="gw-tab-pill" onclick="switchModalRedlineTab('KESTREL-COC-804', this)">
            <span>📄 § 8.04 CoC Consent</span>
          </button>
          <button id="gw-tab-legos" type="button" class="gw-tab-pill" onclick="openDocxModal('legos')">
            <span>🧩 Legal Legos Rider</span>
          </button>

          <div style="margin-top:12px;padding:8px 8px 4px 8px;border-top:1px solid var(--color-ge-outline-variant);font-size:11px;font-weight:600;color:var(--color-ge-on-surface-variant);text-transform:uppercase;letter-spacing:0.04em;">
            Clause Outline (Click to Jump)
          </div>
          <button type="button" class="gw-outline-item" onclick="focusModalSubclause(0)">(a) Deductible vs. Tipping Basket</button>
          <button type="button" class="gw-outline-item" onclick="focusModalSubclause(1)">(b) Indemnity Cap (0.75% vs 0.25%)</button>
          <button type="button" class="gw-outline-item" onclick="focusModalSubclause(2)">(c) Delaware Actual Fraud Carve-Out</button>

          <div style="margin-top:auto;padding:10px;background:var(--color-ge-surface-container-high);border-radius:10px;font-size:11px;color:var(--color-ge-on-surface);line-height:1.45;">
            <div style="font-weight:600;color:var(--color-ge-primary);margin-bottom:3px;">🔒 Format Fidelity Guarantee</div>
            <div id="gw-format-explainer-text">
              Opened as <strong>.docx (OpenXML)</strong>. Live edits and Gemini actions mutate <code>&lt;w:p&gt;</code> &amp; <code>&lt;w:ins&gt;/&lt;w:del&gt;</code> nodes directly while keeping <code>styles.xml</code> &amp; <code>numbering.xml</code> 100% intact.
            </div>
          </div>
        </aside>

        <!-- Center Column: Ruler + Live Editable 8.5"x11" Contract Sheet -->
        <div class="gw-center-doc-col">
          <div class="docx-modal-ruler">
            <span>1 · · · ▼ · · 2 · · · · · 3 · · · · · 4 · · · · · 5 · · · · · 6 · · · ▼ · · 7</span>
            <span id="docx-modal-ruler-right">LIVE EDITABLE CANVAS · CLICK TEXT TO EDIT OR USE GEMINI SIDE PANEL</span>
          </div>
          <div class="docx-modal-scroll">
            <div id="docx-modal-paper" class="docx-modal-paper" contenteditable="true" spellcheck="false" oninput="onModalPaperLiveEdit()"></div>
          </div>
        </div>

        <!-- Right Column: Exact Google Workspace "Gemini" Side Panel -->
        <aside id="gw-gemini-sidepanel" class="gw-gemini-sidepanel animate-canvas-slide-in">
          <div class="gw-gemini-header">
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="font-size:15px;color:var(--color-ge-on-surface-variant);cursor:pointer;">☰</span>
              <span style="font-size:16px;font-weight:500;color:var(--color-ge-on-surface);">Gemini</span>
              <span style="font-size:10.5px;background:var(--color-blue-bg);color:var(--color-ge-primary);padding:2px 7px;border-radius:999px;font-weight:600;">3.8 Flash</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px;">
              <button type="button" class="gw-tool-btn" title="Reset Gemini conversation" onclick="resetGwGeminiChat()" style="font-size:12px;color:var(--color-ge-on-surface-variant);">↺</button>
              <button type="button" class="gw-tool-btn" title="Close Gemini panel" onclick="toggleGwGeminiPanel(false)" style="font-size:14px;color:var(--color-ge-on-surface-variant);">✕</button>
            </div>
          </div>

          <div id="gw-gemini-messages" class="gw-gemini-messages">
            <!-- Initial Google Workspace Welcome & Action Prompts (Matches Screenshot 1) -->
            <div id="gw-gemini-welcome" style="margin-top:auto;padding-top:12px;">
              <div class="gw-gemini-gradient-title">
                Get instant document summaries &amp; redlines
              </div>
              <div style="font-size:11.5px;color:var(--color-ge-on-surface-variant);margin-bottom:10px;">
                Ask questions about this agreement or click an action below to modify the live document on the left:
              </div>

              <button id="gw-action-accept-all" type="button" class="gw-prompt-suggestion" onclick="runWorkspaceGeminiAction('accept_all')">
                <span style="color:var(--color-ge-primary);font-weight:700;">↳</span>
                <span><strong>Apply Playbook v3.4:</strong> Accept all LexGraph seller-favorable positions across Section 8.02</span>
              </button>

              <button id="gw-action-fix-basket" type="button" class="gw-prompt-suggestion" onclick="runWorkspaceGeminiAction('restore_deductible')">
                <span style="color:var(--color-ge-primary);font-weight:700;">↳</span>
                <span><strong>Modify § 8.02(a):</strong> Reject Tipping Basket and restore 0.50% True Deductible ($21M)</span>
              </button>

              <button id="gw-action-compromise-cap" type="button" class="gw-prompt-suggestion" onclick="runWorkspaceGeminiAction('compromise_cap')">
                <span style="color:var(--color-ge-primary);font-weight:700;">↳</span>
                <span><strong>Draft Compromise in § 8.02(b):</strong> Set Indemnity Cap to 0.50% ($21M) &amp; remove $4.2B IP carve-out</span>
              </button>

              <button id="gw-action-insert-lego" type="button" class="gw-prompt-suggestion" onclick="runWorkspaceGeminiAction('insert_lego_rider')">
                <span style="color:var(--color-ge-primary);font-weight:700;">↳</span>
                <span><strong>Insert Legal Lego Rider:</strong> Append Delaware Actual Fraud &amp; Privacy Pro clause (d)</span>
              </button>

              <button id="gw-action-summarize-risks" type="button" class="gw-prompt-suggestion" onclick="runWorkspaceGeminiAction('summarize_risks')">
                <span style="color:var(--color-ge-primary);font-weight:700;">↳</span>
                <span><strong>Summarize &amp; Highlight:</strong> Analyze Skadden v4 risks in this document</span>
              </button>
            </div>
          </div>

          <!-- Bottom Google Workspace "Ask Gemini" Rounded Input Box -->
          <div class="gw-input-shell lumi-composer">
            <input
              id="gw-gemini-input"
              type="text"
              class="gw-input-field"
              placeholder="Ask Gemini or type an edit to apply..."
              onkeydown="if(event.key==='Enter')sendWorkspaceGeminiPrompt()"
            />
            <div style="display:flex;align-items:center;justify-content:space-between;">
              <div style="display:flex;align-items:center;gap:4px;">
                <button type="button" class="gw-tool-btn" title="Insert Legal Lego Clause" onclick="runWorkspaceGeminiAction('insert_lego_rider')" style="font-size:15px;color:var(--color-ge-on-surface-variant);">+</button>
                <button type="button" class="gw-tool-btn" title="Toggle Format-Lock (.docx vs Google Docs)" onclick="toggleSourceFormatLock()" style="font-size:13px;color:var(--color-ge-on-surface-variant);">⊶</button>
              </div>
              <button
                id="gw-gemini-send-btn"
                type="button"
                onclick="sendWorkspaceGeminiPrompt()"
                title="Send to Gemini"
                style="width:28px;height:28px;border-radius:50%;border:none;background:var(--color-ge-primary);color:var(--lumi-sys-color--white);display:inline-flex;align-items:center;justify-content:center;cursor:pointer;font-size:14px;font-weight:700;"
              >
                ↑
              </button>
            </div>
          </div>
          <div style="font-size:10.5px;color:var(--color-ge-on-surface-variant);text-align:center;padding:2px 12px 10px 12px;">
            Gemini in Workspace can make mistakes. <span style="text-decoration:underline;cursor:pointer;" onclick="toggleSourceFormatLock()">Format-Locked AST</span>
          </div>
        </aside>

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

function toggleGeThemeMode() {
  const root = document.documentElement;
  const current = root.getAttribute("data-mode") || "light";
  const next = current === "dark" ? "light" : "dark";
  root.setAttribute("data-mode", next);
  root.classList.toggle("dark-theme", next === "dark");
  document.querySelectorAll(".ge-theme-icon").forEach(el => {
    el.textContent = next === "dark" ? "light_mode" : "dark_mode";
  });
}

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
          appInfo: { name: "lexgraph-legal-mcp-app", version: "3.2.0" },
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

function switchStudioScreen(target, btnEl) {
  if (!target) return;
  document.querySelectorAll(".studio-screen").forEach(el => {
    el.classList.toggle("active", el.id === target);
  });
  document.querySelectorAll("#ge-studio-nav-list .ge-nav-item").forEach(btn => {
    const isAct = btn.getAttribute("data-studio") === target;
    btn.classList.toggle("active", isAct);
    const icon = btn.querySelector(".google-symbols");
    if (icon) icon.classList.toggle("filled", isAct);
  });

  if (target === "tabular-view") {
    renderTabularGrid();
    if (window.innerWidth >= 880) {
      const panel = document.getElementById("tr-side-panel");
      if (panel && !panel.classList.contains("open")) {
        openSideInspector(activeInspectorRowIdx || 0);
      }
    }
    loadTabularWorkspace(currentCorpusMode || "kestrel");
  } else if (target === "redline-view") {
    const pid = currentRedlineData?.pair_id || "KESTREL-SPA-802";
    renderRedlineFromMemory(pid);
    const checked = Array.from(document.querySelectorAll(".lego-cb:checked")).map(cb => cb.value);
    renderLegalLegosFromMemory(checked.length ? checked : ["LEGO-DE-FRAUD", "LEGO-338H10-TAX", "LEGO-PRIVACY-PRO"]);
    loadRedlinePair(pid);
    updateLegalLegos();
  } else if (target === "funds-view") {
    renderFundsAntitrustFromMemory(currentLpFilter || 0, hsrRemedyActive);
    loadFundsAntitrust(currentLpFilter || 0, hsrRemedyActive);
  } else if (target === "governance-view") {
    const lid = document.getElementById("gov-lawyer-select")?.value || "L-001";
    renderGovernanceFromMemory(lid, currentGovernanceMatter || "M-331-KESTREL");
    loadGovernanceAndGraph();
  } else if (target === "inbox-view") {
    renderInboxTriage();
    loadInboxTriage();
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
  switchStudioScreen(target);
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
      `Full Deal Corpus (${tabularRows.length} Files · 1,293 Indexed Clauses) · Cloud Spanner LexGraphLegalGraph`;
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
  if (dot) dot.style.background = active ? "var(--color-green-icon)" : "var(--color-ge-outline)";
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
    return `<span class="status-pill lumi-status-badge red">${escapeHtml(text)}</span>`;
  }
  if (t.includes("notice") || t.includes("30") || t.includes("45")) {
    return `<span class="status-pill lumi-status-badge amber">${escapeHtml(text)}</span>`;
  }
  return `<span class="status-pill lumi-status-badge green">${escapeHtml(text)}</span>`;
}

function renderTabularGrid() {
  const thead = document.getElementById("tr-thead");
  const tbody = document.getElementById("tr-tbody");
  if (!thead || !tbody) return;

  let colsHtml = `
    <tr>
      <th style="width:165px;">Document</th>
      <th style="width:135px;">CoC / Provision Trigger</th>
      <th style="width:145px;">Consent Requirement</th>
      <th style="width:95px;">Notice Window</th>
      <th style="width:140px;">Termination &amp; Fee Impact</th>
  `;
  dynamicColumns.forEach((dc, colIdx) => {
    const progressText = (dc.totalCount && dc.completedCount < dc.totalCount)
      ? ` <span style="font-size:10px;font-weight:500;color:var(--color-ge-primary);">(${dc.completedCount}/${dc.totalCount})</span>`
      : "";
    colsHtml += `<th style="width:155px;background:var(--color-blue-bg);color:var(--color-ge-on-primary-container);">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
        <span style="overflow:hidden;text-overflow:ellipsis;">✦ ${escapeHtml(dc.name)}${progressText}</span>
        <button type="button" onclick="removeDynamicColumn(${colIdx})" title="Remove column" style="border:none;background:transparent;color:var(--color-ge-on-surface-variant);cursor:pointer;font-size:12px;padding:0 2px;line-height:1;">×</button>
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
          <div class="skeleton-bar agent-skeleton-wipe" style="margin-bottom:4px;"></div>
          <div style="font-size:10px;color:var(--color-ge-primary);font-weight:500;">⚡ Gemini 3.8 Flash...</div>
        </td>`;
      }
      const citeLabel = cellVal.citation ? `<div style="font-size:10px;color:var(--color-ge-on-surface-variant);margin-top:2px;">${escapeHtml(cellVal.citation)} · p.${cellVal.page || row.page || 1}</div>` : "";
      return `<td onclick="openSideInspector(${idx}, '${escapeJs(cellVal.quote || row.quote)}', '${escapeJs(cellVal.citation || row.citation)}')" style="cursor:pointer;">
        <div style="font-weight:500;color:var(--color-ge-on-surface);">
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
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-ge-primary)" stroke-width="2" style="flex-shrink:0;">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
            </svg>
            <span class="doc-filename-text">${escapeHtml(row.filename)}</span>
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
          <div style="font-weight:500;color:var(--color-ge-on-surface);">${escapeHtml(row.fee_or_penalty)}</div>
          <div style="font-size:11px;color:var(--color-ge-on-surface-variant);">${escapeHtml(row.termination_right)}</div>
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

  // Only scroll horizontally if the table overflows the viewport width (e.g., 2+ added columns)
  const scroller = document.querySelector(".tr-grid-scroll");
  if (scroller) {
    setTimeout(() => {
      if (scroller.scrollWidth > scroller.clientWidth + 8) {
        scroller.scrollLeft = scroller.scrollWidth - scroller.clientWidth;
      } else {
        scroller.scrollLeft = 0;
      }
    }, 30);
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
            return `<div style="margin-top:8px;text-align:justify;background:var(--color-yellow-bg);border-left:3px solid var(--color-yellow-icon);padding:6px 10px;border-radius:0 6px 6px 0;"><span class="docx-clause-heading"><u>${headEsc}</u></span> <mark class="contract-highlight">${restEsc.trim()}</mark></div>`;
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
        <div class="docx-clause-block" style="background:var(--color-yellow-bg);border-left:3px solid var(--color-yellow-icon);padding:8px 12px;margin-bottom:10px;">
          <div style="font-family:var(--font-sans);font-size:10px;font-weight:700;color:var(--color-yellow-text);text-transform:uppercase;margin-bottom:3px;">
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
  a.download = `LexGraph_${currentCorpusMode}_Tabular_Review.csv`;
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
    const bg = allResolved ? "var(--color-green-bg)" : "var(--color-blue-bg)";
    const bd = allResolved ? "var(--color-green-border)" : "var(--color-blue-border)";
    const fg = allResolved ? "var(--color-green-text)" : "var(--color-ge-on-primary-container)";
    summaryBanner = `
      <div style="font-family:var(--font-sans);font-size:11px;font-weight:600;color:${fg};background:${bg};border:1px solid ${bd};padding:5px 10px;border-radius:6px;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between;">
        <span>${allResolved ? '✓ All Playbook Deviations Resolved in Redline Sheet' : 'Track Changes Active in Document Preview'}</span>
        <span>${acceptedCount}/${devs.length} Accepted LexGraph v3 · ${rejectedCount} Rejected</span>
      </div>
    `;
  }

  const inlineSubActions = (idx, state) => `
    <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;margin-bottom:5px;font-family:var(--font-sans);">
      <div>
        ${state === "accepted"
          ? `<span class="redline-decision-badge accepted" style="margin-bottom:0;">✓ Card #${idx + 1} Accepted · LexGraph v3 Playbook Counter-Redline Applied</span>`
          : state === "rejected"
            ? `<span class="redline-decision-badge rejected" style="margin-bottom:0;">✗ Card #${idx + 1} · Counterparty v4 Markup Rejected</span>`
            : `<span class="status-pill lumi-status-badge amber" style="font-size:10px;padding:1px 7px;">Card #${idx + 1} Pending · Incoming Counterparty v4 Redline</span>`}
      </div>
      <div style="display:flex;align-items:center;gap:4px;" onclick="event.stopPropagation();">
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${state === 'accepted' ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" style="height:20px;padding:0 7px;font-size:10px;" onclick="event.stopPropagation();decideRedlineCard(${idx}, 'accepted')">
          ${state === 'accepted' ? '✓ LexGraph v3 Applied' : 'Accept LexGraph v3'}
        </button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${state === 'rejected' ? 'pill-btn-danger' : 'pill-btn-white'} pill-btn-xs" style="height:20px;padding:0 7px;font-size:10px;" onclick="event.stopPropagation();decideRedlineCard(${idx}, 'rejected')">
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
          <div style="margin-top:6px;padding:5px 8px;background:var(--color-green-bg);border:1px solid var(--color-green-border);border-radius:4px;font-family:var(--font-sans);font-size:11px;color:var(--color-green-text);">
            <strong>New Modified Line (LexGraph v3 Playbook):</strong> Seller liable solely for Losses exceeding <strong>0.50% EV True Deductible ($21.0M)</strong> (or <strong>0.375% EV</strong> compromise per Project Titan DOC-402-A).
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
          <span style="background:var(--color-yellow-bg);color:var(--color-yellow-text);padding:0 4px;border-radius:3px;font-weight:600;border-bottom:1.5px dashed var(--color-yellow-icon);">0.25% of the Base Purchase Price ($10,500,000) (the 'Tipping Basket')</span>, in which case Seller Parties shall be liable
          <del class="redline-del">only for the excess over the Deductible.</del>
          <span style="background:var(--color-yellow-bg);color:var(--color-yellow-text);padding:0 4px;border-radius:3px;font-weight:600;border-bottom:1.5px dashed var(--color-yellow-icon);">from the first dollar of all Losses.</span>
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
          <div style="margin-top:6px;padding:5px 8px;background:var(--color-green-bg);border:1px solid var(--color-green-border);border-radius:4px;font-family:var(--font-sans);font-size:11px;color:var(--color-green-text);">
            <strong>New Modified Line (LexGraph v3 Playbook):</strong> Unified <strong>0.75% EV Cap ($31.5M)</strong>; Special Environmental &amp; IP Warranties routed to $50M R&amp;W Insurance Tower.
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
          <span style="background:var(--color-yellow-bg);color:var(--color-yellow-text);padding:0 4px;border-radius:3px;font-weight:600;border-bottom:1.5px dashed var(--color-yellow-icon);">0.25% of the Base Purchase Price ($10,500,000) for general representations and 100% of the Base Purchase Price ($4,200,000,000) for Special Environmental &amp; IP Warranties</span> (the 'Indemnity Cap').
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
          <div style="margin-top:6px;padding:5px 8px;background:var(--color-green-bg);border:1px solid var(--color-green-border);border-radius:4px;font-family:var(--font-sans);font-size:11px;color:var(--color-green-text);">
            <strong>New Modified Line (LexGraph v3 Playbook):</strong> Fraud carve-out restricted strictly to <strong>Delaware Express Written Actual Fraud (ABRY Partners)</strong>.
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
          <span style="background:var(--color-yellow-bg);color:var(--color-yellow-text);padding:0 4px;border-radius:3px;font-weight:600;border-bottom:1.5px dashed var(--color-yellow-icon);">in the case of Actual or Constructive Fraud, equitable fraud, reckless misrepresentation, or willful breach.</span>
        </div>
      `;
    }

    return `
      ${summaryBanner}
      <div style="font-weight:700;color:var(--color-ge-on-surface);margin-bottom:4px;">Section 8.02 <u>Limitation on Indemnification.</u></div>
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
        <div><ins class="redline-ins">${escapeHtml(currentRedlineData.clause_a_text || dev0.lexgraph_v3 || "")} (${escapeHtml(dev0.lexgraph_v3 || "")})</ins></div>
        <div style="margin-top:6px;padding:5px 8px;background:var(--color-green-bg);border:1px solid var(--color-green-border);border-radius:4px;font-family:var(--font-sans);font-size:11px;color:var(--color-green-text);">
          <strong>New Modified Line (LexGraph v3 Playbook):</strong> ${escapeHtml(dev0.lexgraph_v3 || "")}
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
  if (data?.chat_context) {
    window.GEMINI_CHAT_CONTEXT = data.chat_context;
  }
  document.getElementById("redline-doc-pair-label").textContent = `${data.doc_a_name} vs. ${data.doc_b_name}`;
  document.getElementById("redline-playbook-banner").innerHTML =
    `<div style="display:flex;align-items:flex-start;gap:8px;"><span class="google-symbols filled" style="font-size:18px;color:var(--color-ge-accent);flex-shrink:0;">auto_awesome</span><div><strong>Playbook Standard:</strong> ${escapeHtml(data.playbook_standard)}</div></div>`;
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
      ? `<span class="status-pill lumi-status-badge green">✓ Accepted LexGraph Counter</span>`
      : state === "rejected"
        ? `<span class="status-pill lumi-status-badge red">✗ Rejected Skadden Markup</span>`
        : `<span class="status-pill lumi-status-badge ${d.severity === 'CRITICAL' ? 'red' : 'amber'}">${escapeHtml(d.severity)}</span>`;

    return `
      <div class="edit-card lumi-card card--interactive" id="edit-card-${idx}" style="${state === 'accepted' ? 'border-color:var(--color-green-border);background:var(--color-green-bg);' : state === 'rejected' ? 'border-color:var(--color-red-border);background:var(--color-red-bg);' : ''}">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px;">
          <div style="display:flex;align-items:center;gap:6px;">
            <span class="citation-pill">${idx + 1}</span>
            <span style="font-weight:600;font-size:12.5px;color:var(--color-ge-on-surface);">${escapeHtml(d.issue)}</span>
          </div>
          ${statusBadge}
        </div>
        <div class="text-slab" style="font-size:12px;margin-bottom:6px;background:var(--color-ge-surface-container-lowest);">
          <div><del class="redline-del">${escapeHtml(d.skadden_v4)}</del></div>
          <div style="margin-top:4px;"><ins class="redline-ins">${escapeHtml(d.lexgraph_v3)}</ins></div>
        </div>
        <div style="font-size:11.5px;color:var(--color-ge-on-surface-variant);margin-bottom:8px;">
          <strong>Playbook Action:</strong> ${escapeHtml(d.recommendation)}
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
          <button id="btn-accept-card-${idx}" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${state === 'accepted' ? 'pill-btn-blue' : 'pill-btn-blue'} pill-btn-xs" onclick="decideRedlineCard(${idx}, 'accepted')">
            ${state === 'accepted' ? '✓ Accepted LexGraph v3 (Active in Preview)' : 'Accept LexGraph v3'}
          </button>
          <button id="btn-reject-card-${idx}" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${state === 'rejected' ? 'pill-btn-danger' : 'pill-btn-white'} pill-btn-xs" onclick="decideRedlineCard(${idx}, 'rejected')">
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
    slab.style.borderLeftColor = "var(--color-green-icon)";
  } else if (acceptedCount > 0 || rejectedCount > 0) {
    slab.style.borderLeftColor = "var(--color-ge-primary)";
  } else {
    slab.style.borderLeftColor = "var(--lumi-sys-color--error)";
  }

  const statsPill = document.getElementById("redline-stats-pill");
  if (statsPill && currentRedlineData.stats) {
    if (acceptedCount > 0 || rejectedCount > 0) {
      statsPill.className = "status-pill lumi-status-badge green";
      statsPill.textContent = `${acceptedCount}/${devs.length} LexGraph v3 Applied · -${currentRedlineData.stats.tokens_deleted} / +${currentRedlineData.stats.tokens_inserted} Words`;
    } else {
      statsPill.className = "status-pill lumi-status-badge blue";
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
    const grpStr = b.practice_group || b.source_precedent || "LexGraph Playbook";
    const numStr = (b.numbering_style || b.numbering_level || "Article VIII").replace(/->/g, "→");
    return `
      <div class="docx-clause-block">
        <div class="docx-clause-meta-bar" style="white-space:nowrap;">
          <span class="status-pill lumi-status-badge blue" style="font-family:var(--font-sans);font-size:9.5px;padding:1px 7px;">
            ${escapeHtml(b.block_id)} · ${escapeHtml(grpStr)}
          </span>
          <span style="font-family:var(--font-mono);font-size:9.5px;color:var(--color-ge-on-surface-variant);white-space:nowrap;">
            ${escapeHtml(numStr)}
          </span>
        </div>
        ${formatClauseLinesHtml(b.clause_text)}
      </div>
    `;
  }).join("");

  return `
    <div class="docx-running-header">
      <span>APEX LAW PARTNERS LLP · EXECUTION RIDER</span>
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
    <div style="margin-top:14px;padding-top:10px;border-top:1px dashed var(--color-ge-outline-variant);display:flex;justify-content:space-between;align-items:flex-end;font-family:var(--font-serif);font-size:12px;color:var(--color-ge-on-surface-variant);">
      <div>
        <div style="font-weight:700;text-transform:uppercase;font-size:10.5px;color:var(--color-ge-on-surface-variant);">Approved per LexGraph M&amp;A / Privacy Pro Playbook v3.4:</div>
        <div style="margin-top:4px;font-style:italic;">/s/ Sarah Jenkins, Managing Partner (M&amp;A) &amp; D. Cockerell, Partner (Tax)</div>
      </div>
      <div style="font-family:var(--font-sans);font-size:10px;color:var(--color-green-text);background:var(--color-green-bg);border:1px solid var(--color-green-border);padding:2px 8px;border-radius:999px;font-weight:600;">
        ✓ OpenXML .docx Ready
      </div>
    </div>
    <div class="docx-running-footer">
      <span>LEXGRAPH:\\98412034.4\\31402.0018</span>
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
        <div style="font-weight:600;color:var(--color-ge-on-surface);">${escapeHtml(lp.lp_name)}</div>
        <div style="font-size:11px;color:var(--color-ge-on-surface-variant);">${escapeHtml(lp.tier)}</div>
      </td>
      <td style="font-weight:600;color:var(--color-ge-on-surface);">$${lp.commitment_usd_m.toFixed(0)}M</td>
      <td>
        <span class="status-pill lumi-status-badge blue">${lp.mgmt_fee_bps} bps / ${lp.carry_pct}%</span>
      </td>
      <td>
        <div style="font-weight:500;color:var(--color-ge-on-surface);">${escapeHtml(lp.mfn_scope)}</div>
        <div style="font-size:11px;color:var(--color-ge-on-surface-variant);">${escapeHtml(lp.co_invest_priority)} · ${escapeHtml(lp.esg_excusal)}</div>
      </td>
    </tr>
  `).join("");

  const hsr = baseData.antitrust_hsr;
  const toggleBtn = document.getElementById("btn-hsr-remedy-toggle");
  const statusBadge = document.getElementById("hsr-status-badge");
  if (includeRemedy) {
    toggleBtn.className = "pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-blue";
    toggleBtn.textContent = `HSR Divestiture Remedy: ON (Cleared +${hsr.active_hhi_delta} Δ HHI)`;
    statusBadge.className = "status-pill lumi-status-badge green";
    statusBadge.textContent = `CLEARED (${hsr.active_post_merger_hhi} HHI / +${hsr.active_hhi_delta} Δ)`;
  } else {
    toggleBtn.className = "pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-danger";
    toggleBtn.textContent = `HSR Divestiture Remedy: OFF (Presumed Block +${hsr.active_hhi_delta} Δ HHI)`;
    statusBadge.className = "status-pill lumi-status-badge red";
    statusBadge.textContent = `CHALLENGE PRESUMED (${hsr.active_post_merger_hhi} HHI / +${hsr.active_hhi_delta} Δ)`;
  }

  document.getElementById("hsr-summary-card").innerHTML = `
    <div style="font-weight:600;color:var(--color-ge-on-surface);margin-bottom:3px;">${escapeHtml(hsr.deal_name)}</div>
    <div style="color:var(--color-ge-on-surface-variant);">Pre-Merger HHI: <strong>${hsr.pre_merger_hhi}</strong> → Post-Merger HHI: <strong>${hsr.active_post_merger_hhi}</strong> (Δ <strong>+${hsr.active_hhi_delta}</strong>)</div>
    <div style="margin-top:4px;color:${includeRemedy ? 'var(--color-green-text)' : 'var(--color-red-text)'};font-weight:500;">
      ${includeRemedy ? '✓ Divestiture Active: ' + escapeHtml(hsr.remedy_recommendation) : '⛔ Unremedied Concentration: Combined Brightwater + Halvorsen reaches 33.6% share (+510 Δ HHI > 100 DOJ/FTC presumption).'}
    </div>
  `;

  const barsEl = document.getElementById("hsr-bars-container");
  const participants = includeRemedy
    ? [
        { company: "Brightwater + Halvorsen (Net of 6% Divestiture)", share_pct: 27.6, hhi_contribution: 762, color: "var(--color-green-icon)" },
        { company: "Apex Global Automation", share_pct: 28.0, hhi_contribution: 784, color: "var(--color-ge-primary)" },
        { company: "Kiyota Robotics NA", share_pct: 19.0, hhi_contribution: 361, color: "var(--color-ge-primary)" },
        { company: "Ferrous Precision Systems", share_pct: 12.0, hhi_contribution: 144, color: "var(--color-ge-primary)" },
        { company: "Pellucid Dynamics (Midwest Divestiture Buyer)", share_pct: 6.0, hhi_contribution: 36, color: "var(--color-green-icon)" },
        { company: "Other Fragmented Suppliers", share_pct: 7.4, hhi_contribution: 123, color: "var(--color-ge-on-surface-variant)" },
      ]
    : [
        { company: "Combined Brightwater + Halvorsen (Unremedied)", share_pct: 33.6, hhi_contribution: 1129, color: "var(--lumi-sys-color--error)" },
        { company: "Apex Global Automation", share_pct: 28.0, hhi_contribution: 784, color: "var(--color-ge-primary)" },
        { company: "Kiyota Robotics NA", share_pct: 19.0, hhi_contribution: 361, color: "var(--color-ge-primary)" },
        { company: "Ferrous Precision Systems", share_pct: 12.0, hhi_contribution: 144, color: "var(--color-ge-primary)" },
        { company: "Other Fragmented Suppliers", share_pct: 7.4, hhi_contribution: 272, color: "var(--color-ge-on-surface-variant)" },
      ];

  barsEl.innerHTML = participants.map(mp => `
    <div style="display:flex;align-items:center;gap:8px;font-size:11.5px;">
      <div style="width:215px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--color-ge-on-surface);font-weight:${mp.color === 'var(--lumi-sys-color--error)' || mp.color === 'var(--color-green-icon)' ? '600' : '400'};">${escapeHtml(mp.company)}</div>
      <div style="flex:1;height:8px;background:var(--color-ge-outline-variant);border-radius:999px;overflow:hidden;">
        <div style="width:${Math.min(100, mp.share_pct * 2.5)}%;height:100%;background:${mp.color};border-radius:999px;transition:width 0.25s;"></div>
      </div>
      <div style="width:95px;text-align:right;font-family:var(--font-mono);font-size:11px;color:var(--color-ge-on-surface-variant);">${mp.share_pct}% (${mp.hhi_contribution})</div>
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
  let takeaway = "Structured multimodal extraction indexed into Cloud Spanner LexGraphLegalGraph.";
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
    ? `<span class="status-pill lumi-status-badge blue" style="margin-left:6px;">⚡ Live Spanner GQL Audit Verified (0.4ms)</span>`
    : "";
  banner.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;flex-wrap:wrap;gap:6px;">
      <span style="font-family:var(--font-serif);font-size:17px;font-weight:600;color:var(--color-ge-on-surface);">
        Matter ${escapeHtml(gov.matter_id)} · CMN ${escapeHtml(gov.cmn)}
      </span>
      <div style="display:flex;align-items:center;">
        <span class="status-pill lumi-status-badge ${allowed ? 'green' : 'red'}">
          ${allowed ? '✓ CLEARED (Screen-Before-Rank)' : '⛔ BLOCKED BY INTAPP WALL-999'}
        </span>
        ${pulseTag}
      </div>
    </div>
    <div style="font-size:12px;color:var(--color-ge-on-surface);margin-bottom:4px;">
      <strong>Client:</strong> ${escapeHtml(gov.client_name)} · <strong>iManage Library:</strong> <code>${escapeHtml(gov.imanage_library)}</code>
    </div>
    <div style="font-size:12px;color:var(--color-ge-on-surface-variant);">
      <strong>OCG Policy:</strong> ${escapeHtml(gov.ocg_ai_policy)}
    </div>
  `;

  const gPill = document.getElementById("gov-grant-pill");
  if (gPill) {
    gPill.className = `status-pill lumi-status-badge ${grantActiveState ? 'green' : 'red'}`;
    gPill.textContent = grantActiveState ? "ACTIVE (30-Day TTL)" : "REVOKED (Blocked)";
  }

  document.getElementById("gov-gql-box").textContent =
    `GRAPH LexGraphLegalGraph\nMATCH (l:Lawyer {lawyer_id: '${lawyerId}'})\nMATCH (m:Matter {matter_id: '${currentGovernanceMatter}'})-[:CONTAINS_DOC]->(d:Document)-[:HAS_CLAUSE]->(c:Clause)\nWHERE NOT EXISTS {\n  MATCH (l)-[:INTAPP_WALL {rule_type: 'EXCLUDE'}]->(m)\n}\nAND (d.doc_id != 'EM-9901' OR ${grantActiveState ? "TRUE /* 30-Day TeammateGrant Active */" : "FALSE /* EM-9901 Grant Revoked */"})\nRETURN m.matter_id, d.doc_id, c.clause_id, c.section_title\n-- Result: ${allowed ? 'ACCESS PERMITTED (Zero Ethical Wall Conflicts)' : '0 ROWS RETURNED (Filtered Before ANN Scoring)'}`;

  const nodesEl = document.getElementById("graph-nodes-list");
  const edges = graph.edges || graph.precedent_edges || [];
  const docs = graph.documents || graph.nodes || [];
  if (!allowed) {
    nodesEl.innerHTML = `
      <div class="edit-card lumi-card card--interactive" style="border-color:var(--color-red-border);background:var(--color-red-bg);">
        <div style="font-weight:600;color:var(--color-red-text);margin-bottom:4px;">⛔ Zero-Leakage Screen-Before-Rank Enforcement</div>
        <div style="font-size:12px;color:var(--color-red-text);">
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
          : (edgeMatch.reason || item.reason || "Verified multi-hop precedent edge in Cloud Spanner LexGraphLegalGraph.");
      return `
      <div class="liquid-glass-flat" style="padding:10px 12px;border-radius:8px;${item.id === 'EM-9901' ? 'border-color:var(--color-green-border);background:var(--color-green-bg);' : ''}">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
          <span style="font-weight:600;font-size:12px;color:var(--color-ge-on-surface);">
            ${escapeHtml(titleStr)}
          </span>
          <span class="status-pill lumi-status-badge ${item.id === 'EM-9901' ? 'green' : 'blue'}">${escapeHtml(badgeStr)}</span>
        </div>
        <div style="font-size:11.5px;color:var(--color-ge-on-surface-variant);margin-top:3px;">
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
      ${resolved ? `<div style="font-family:var(--font-sans);font-size:11px;font-weight:700;color:var(--color-green-text);background:var(--color-green-bg);border:1px solid var(--color-green-border);padding:5px 10px;border-radius:6px;margin-bottom:8px;">✓ CONFLICT RESOLVED: Delegated First 30 Mins of FTC HSR Call to Antitrust Partner Andrew Simon (Wrap-Up Moved to 3:45 PM EDT)</div>` : ''}
      <div style="font-family:var(--font-sans);font-size:12px;color:var(--color-ge-on-surface);">
        <div style="padding:8px 10px;background:var(--color-blue-bg);border-left:3px solid var(--color-ge-primary);border-radius:4px;margin-bottom:8px;">
          <div style="font-weight:700;color:var(--color-ge-on-primary-container);">Event A (Mandatory): ${escapeHtml(c.event_a.title)}</div>
          <div style="font-size:11px;color:var(--color-ge-on-surface-variant);margin-top:2px;">CMN ${escapeHtml(c.event_a.cmn)} · Attendees: ${escapeHtml((c.event_a.attendees || []).join(", "))}</div>
        </div>
        <div style="padding:8px 10px;background:${resolved ? 'var(--color-green-bg)' : 'var(--color-red-bg)'};border-left:3px solid ${resolved ? 'var(--color-green-icon)' : 'var(--lumi-sys-color--error)'};border-radius:4px;margin-bottom:8px;">
          <div style="font-weight:700;color:${resolved ? 'var(--color-green-text)' : 'var(--color-red-text)'};">Event B (${resolved ? 'Delegated to A. Simon · 3:45 PM Wrap-Up' : 'Conflicting Slot'}): ${escapeHtml(c.event_b.title)}</div>
          <div style="font-size:11px;color:var(--color-ge-on-surface-variant);margin-top:2px;">CMN ${escapeHtml(c.event_b.cmn)} · Attendees: ${escapeHtml((c.event_b.attendees || []).join(", "))}</div>
        </div>
        <div style="font-family:var(--font-serif);font-size:13.5px;color:var(--color-ge-on-surface);margin-top:6px;">
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
        <span>LEXGRAPH EXCHANGE SERVER · IMANAGE</span>
        <span>${escapeHtml(e.email_id)} · ${approved ? 'FILED TO IMANAGE' : 'PENDING SIGN-OFF'}</span>
      </div>
      ${approved ? `<div style="font-family:var(--font-sans);font-size:11px;font-weight:700;color:var(--color-green-text);background:var(--color-green-bg);border:1px solid var(--color-green-border);padding:5px 10px;border-radius:6px;margin-bottom:8px;">✓ APPROVED &amp; FILED TO IMANAGE WORK 10 (${escapeHtml(e.cmn)}) · Staged Reply Transmitted</div>` : ''}
      <div style="font-family:var(--font-sans);border-bottom:1px solid var(--color-ge-outline-variant);padding-bottom:8px;margin-bottom:10px;">
        <div style="font-family:var(--font-serif);font-size:15px;font-weight:700;color:var(--color-ge-on-surface);margin-bottom:4px;">
          ${escapeHtml(e.subject)}
        </div>
        <div style="font-size:11.5px;color:var(--color-ge-on-surface-variant);"><strong>From:</strong> ${escapeHtml(e.sender)}</div>
        <div style="font-size:11.5px;color:var(--color-ge-on-surface-variant);"><strong>To:</strong> Sarah Jenkins (M&amp;A Lead Partner, LexGraph NY) · <strong>Sent:</strong> ${escapeHtml(e.received_at)}</div>
        <div style="font-size:11px;color:var(--color-ge-primary);margin-top:3px;"><strong>Tagged Client-Matter Number:</strong> ${escapeHtml(e.cmn)}</div>
      </div>
      <div style="font-family:var(--font-serif);font-size:13.8px;line-height:1.6;color:var(--color-ge-on-surface);white-space:pre-line;">
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
      <div class="edit-card lumi-card card--interactive" onclick="inspectRawEml(${idx}, false)" style="cursor:pointer;${approved ? 'border-color:var(--color-green-border);background:var(--color-green-bg);' : ''}">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;margin-bottom:4px;">
          <span style="font-weight:600;font-size:12px;color:var(--color-ge-on-surface);">${escapeHtml(e.email_id)} · ${escapeHtml(e.cmn)}</span>
          <span class="status-pill lumi-status-badge ${approved ? 'green' : 'red'}">
            ${approved ? '✓ Filed to iManage' : escapeHtml(e.priority)}
          </span>
        </div>
        <div style="font-family:var(--font-serif);font-size:15px;font-weight:600;color:var(--color-ge-on-surface);margin-bottom:3px;">
          ${escapeHtml(e.subject)}
        </div>
        <div style="font-size:11.5px;color:var(--color-ge-on-surface-variant);margin-bottom:6px;">
          From: ${escapeHtml(e.sender)} · ${escapeHtml(e.received_at)}
        </div>
        <div style="font-size:12px;color:var(--color-ge-on-surface);margin-bottom:8px;">
          ${escapeHtml(e.summary)}
        </div>
        <div class="text-slab" style="font-size:12px;margin-bottom:8px;background:var(--color-ge-surface-container-lowest);">
          <strong>AI Staged Action:</strong> ${escapeHtml(e.proposed_reply)}
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
          <button id="btn-approve-${escapeHtml(e.email_id)}" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${approved ? 'pill-btn-white' : 'pill-btn-blue'} pill-btn-xs" onclick="event.stopPropagation();loadInboxTriage('${escapeJs(e.email_id)}', null, false)">
            ${approved ? '✓ Approved & Filed to iManage' : 'Approve & File to iManage'}
          </button>
          <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="event.stopPropagation();inspectRawEml(${idx}, false)">
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
      <div class="edit-card lumi-card card--interactive" onclick="inspectRawEml(0, true)" style="cursor:pointer;${resolved ? 'border-color:var(--color-green-border);background:var(--color-green-bg);' : ''}">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
          <span style="font-weight:600;font-size:12px;color:var(--color-ge-on-surface);">${escapeHtml(c.conflict_id)} · ${escapeHtml(c.date)}</span>
          <span class="status-pill lumi-status-badge ${resolved ? 'green' : 'amber'}">
            ${resolved ? '✓ Conflict Resolved' : 'Hard Overlap Detected'}
          </span>
        </div>
        <div style="font-size:12px;color:var(--color-ge-on-surface);margin-bottom:4px;">
          <strong>1. ${escapeHtml(c.event_a.title)}</strong> (CMN ${escapeHtml(c.event_a.cmn)})
        </div>
        <div style="font-size:12px;color:var(--color-red-text);margin-bottom:8px;">
          <strong>2. ${escapeHtml(c.event_b.title)}</strong> (CMN ${escapeHtml(c.event_b.cmn)})
        </div>
        <div class="text-slab" style="font-size:12px;margin-bottom:8px;background:var(--color-ge-surface-container-lowest);">
          <strong>Proposed Delegation:</strong> ${escapeHtml(c.ai_resolution)}
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
          <button id="btn-resolve-cal-101" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${resolved ? 'pill-btn-white' : 'pill-btn-blue'} pill-btn-xs" onclick="event.stopPropagation();loadInboxTriage(null, '${escapeJs(c.conflict_id)}', false)">
            ${resolved ? '✓ Delegated to A. Simon (3:45 PM Wrap-Up)' : 'Delegate FTC Overlap to A. Simon'}
          </button>
          <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="event.stopPropagation();inspectRawEml(0, true)">
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
/* GOOGLE WORKSPACE / WORD CO-EDITOR + GEMINI SIDE PANEL CONTROLLER          */
/* ========================================================================= */

let currentSourceFormatLock = "docx";
let currentDocFontSizePx = 15;
let lastProposedGeminiClause = "";

function openDocxModal(mode) {
  activeDocxModalMode = mode || "redline";
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
    rulerRight.textContent = `APEX LAW PARTNERS LLP · LIVE CO-EDITOR (${Math.round(scaleVal * 100)}% ZOOM)`;
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

function onModalPaperLiveEdit() {
  const statusEl = document.getElementById("gw-save-status");
  if (statusEl) {
    statusEl.textContent = currentSourceFormatLock === "docx"
      ? "✓ Live edits synced to OpenXML AST (styles.xml preserved)"
      : "✓ Live edits synced via Google Docs batchUpdate API";
    statusEl.style.color = "var(--lumi-sys-color--positive)";
  }
}

function switchFormatProofTab(mode, btnEl) {
  const panes = {
    docx: document.getElementById("proof-pane-docx"),
    gdocs: document.getElementById("proof-pane-gdocs"),
    broken: document.getElementById("proof-pane-broken"),
  };
  Object.keys(panes).forEach((k) => {
    if (panes[k]) {
      panes[k].style.display = k === mode ? "grid" : "none";
    }
  });
  const btnMap = {
    docx: document.getElementById("btn-proof-docx"),
    gdocs: document.getElementById("btn-proof-gdocs"),
    broken: document.getElementById("btn-proof-broken"),
  };
  Object.keys(btnMap).forEach((k) => {
    if (btnMap[k]) {
      btnMap[k].classList.toggle("active", k === mode);
    }
  });
}

function toggleSourceFormatLock() {
  currentSourceFormatLock = currentSourceFormatLock === "docx" ? "gdoc" : "docx";
  const labelEl = document.getElementById("format-lock-label");
  const dotEl = document.getElementById("format-lock-dot");
  const badgeEl = document.getElementById("gw-format-icon-badge");
  const explainerEl = document.getElementById("gw-format-explainer-text");
  const titleEl = document.getElementById("docx-modal-title");

  if (currentSourceFormatLock === "docx") {
    if (labelEl) labelEl.textContent = "Format-Locked: .docx (OpenXML Preserved)";
    if (dotEl) dotEl.style.background = "var(--color-ge-primary)";
    if (badgeEl) badgeEl.style.background = "var(--color-ge-on-primary-container)";
    if (titleEl && titleEl.textContent.endsWith(".gdoc")) {
      titleEl.textContent = titleEl.textContent.replace(/\.gdoc$/, ".docx");
    }
    if (explainerEl) {
      explainerEl.innerHTML = `Opened as <strong>.docx (OpenXML)</strong>. Live edits and Gemini actions mutate <code>&lt;w:p&gt;</code> &amp; <code>&lt;w:ins&gt;/&lt;w:del&gt;</code> nodes directly while keeping <code>styles.xml</code> &amp; <code>numbering.xml</code> 100% intact.`;
    }
    switchFormatProofTab("docx");
  } else {
    if (labelEl) labelEl.textContent = "Format-Locked: Google Docs (batchUpdate API)";
    if (dotEl) dotEl.style.background = "var(--color-green-icon)";
    if (badgeEl) badgeEl.style.background = "var(--color-ge-accent)";
    if (titleEl && titleEl.textContent.endsWith(".docx")) {
      titleEl.textContent = titleEl.textContent.replace(/\.docx$/, ".gdoc");
    }
    if (explainerEl) {
      explainerEl.innerHTML = `Opened as <strong>Google Doc</strong>. Live edits and Gemini actions execute via <code>documents.batchUpdate</code> (<code>InsertText</code> / <code>ReplaceAllText</code>) preserving 100% of Google Docs <code>NamedStyles</code>.`;
    }
    switchFormatProofTab("gdocs");
  }
  onModalPaperLiveEdit();
}

function execDocFormat(cmd, value = null) {
  const paper = document.getElementById("docx-modal-paper");
  if (!paper) return;
  paper.focus();
  const sel = window.getSelection();
  const hasSelection = sel && sel.rangeCount > 0 && !sel.isCollapsed && paper.contains(sel.anchorNode);

  if (hasSelection || cmd === "undo" || cmd === "redo" || cmd.startsWith("justify")) {
    try {
      document.execCommand(cmd, false, value);
    } catch (e) {}
  } else {
    // If no text is highlighted, apply visual formatting to the first subclause so toolbar clicks are always visibly demonstrated
    const targetSub = paper.querySelector("#redline-sub-0") || paper.querySelector(".docx-subclause") || paper;
    if (cmd === "bold") {
      targetSub.style.fontWeight = targetSub.style.fontWeight === "700" ? "400" : "700";
    } else if (cmd === "italic") {
      targetSub.style.fontStyle = targetSub.style.fontStyle === "italic" ? "normal" : "italic";
    } else if (cmd === "underline") {
      targetSub.style.textDecoration = targetSub.style.textDecoration === "underline" ? "none" : "underline";
    } else if (cmd === "strikeThrough") {
      targetSub.style.textDecoration = targetSub.style.textDecoration === "line-through" ? "none" : "line-through";
    }
  }
  onModalPaperLiveEdit();
}

function applyHeadingStyle(tag) {
  const paper = document.getElementById("docx-modal-paper");
  if (!paper) return;
  const titleNode = paper.querySelector(".docx-doc-title") || paper.firstElementChild;
  if (!titleNode) return;
  if (tag === "h2") {
    titleNode.style.fontSize = "21px";
    titleNode.style.color = "var(--color-ge-primary)";
  } else if (tag === "h3") {
    titleNode.style.fontSize = "17px";
    titleNode.style.color = "var(--color-ge-on-primary-container)";
  } else if (tag === "blockquote") {
    titleNode.style.borderLeft = "4px solid var(--color-ge-primary)";
    titleNode.style.paddingLeft = "12px";
  } else {
    titleNode.style.fontSize = "18px";
    titleNode.style.color = "var(--color-ge-on-surface)";
    titleNode.style.borderLeft = "none";
    titleNode.style.paddingLeft = "0";
  }
  onModalPaperLiveEdit();
}

function applyDocFontFamily(fontFamily) {
  const paper = document.getElementById("docx-modal-paper");
  if (paper) {
    paper.style.fontFamily = fontFamily;
    onModalPaperLiveEdit();
  }
}

function stepDocFontSize(delta) {
  currentDocFontSizePx = Math.min(22, Math.max(11, currentDocFontSizePx + delta));
  const disp = document.getElementById("gw-font-size-display");
  if (disp) disp.textContent = String(currentDocFontSizePx);
  const paper = document.getElementById("docx-modal-paper");
  if (paper) {
    paper.style.fontSize = `${currentDocFontSizePx}px`;
    paper.querySelectorAll(".docx-subclause, .docx-redline-margin").forEach(el => {
      el.style.fontSize = `${currentDocFontSizePx}px`;
    });
  }
  onModalPaperLiveEdit();
}

function applyHighlightColor(colorToken) {
  const paper = document.getElementById("docx-modal-paper");
  if (!paper) return;
  let resolvedColor = colorToken;
  const varMatch = String(colorToken || "").match(/^var\((--[^)]+)\)$/);
  if (varMatch) {
    const computed = getComputedStyle(document.documentElement).getPropertyValue(varMatch[1]).trim();
    if (computed) resolvedColor = computed;
  }
  const sel = window.getSelection();
  if (sel && sel.rangeCount > 0 && !sel.isCollapsed && paper.contains(sel.anchorNode)) {
    try {
      document.execCommand("hiliteColor", false, resolvedColor);
      onModalPaperLiveEdit();
      return;
    } catch (e) {}
  }
  const target = paper.querySelector("#redline-sub-0") || paper.querySelector(".docx-subclause") || paper;
  target.style.backgroundColor = colorToken;
  target.style.padding = "8px 12px";
  target.style.borderRadius = "6px";
  onModalPaperLiveEdit();
}

function insertCustomClauseBlock(clauseText, badgeText) {
  const paper = document.getElementById("docx-modal-paper");
  if (!paper) return;
  const container = paper.querySelector(".docx-redline-margin") || paper;
  const block = document.createElement("div");
  block.className = "docx-subclause redline-subclause-item state-accepted";
  block.style.marginTop = "12px";
  const textToInsert = clauseText || "(d) Express Written Actual Fraud & Privacy Pro Rider (Inserted via Co-Editor). Notwithstanding anything to the contrary in this Agreement, nothing in Article VIII shall limit Seller's liability for Express Written Actual Fraud with respect to the representations in Article III, and all Personal Data transfers shall comply with the LexGraph Privacy Pro Data Protection Addendum.";
  const badgeLabel = badgeText || "✦ Inserted via Live Co-Editor · Native .docx Numbering Preserved";
  block.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:3px;" contenteditable="false">
      <span class="redline-decision-badge accepted">${escapeHtml(badgeLabel)}</span>
      <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" style="font-size:10px;padding:1px 7px;" onclick="this.closest('.redline-subclause-item').remove();onModalPaperLiveEdit();">Remove</button>
    </div>
    <div>${escapeHtml(textToInsert)}</div>
  `;
  container.appendChild(block);
  block.scrollIntoView({ behavior: "smooth", block: "center" });
  onModalPaperLiveEdit();
}

function switchModalRedlineTab(pairId, btnEl) {
  document.querySelectorAll(".gw-tab-pill").forEach(b => b.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");
  activeDocxModalMode = "redline";
  loadRedlinePair(pairId);
}

function focusModalSubclause(idx) {
  const paper = document.getElementById("docx-modal-paper");
  if (!paper) return;
  const subs = paper.querySelectorAll(".redline-subclause-item, .docx-subclause");
  const target = subs[idx] || subs[0];
  if (target) {
    target.scrollIntoView({ behavior: "smooth", block: "center" });
    const origBg = target.style.backgroundColor;
    target.style.backgroundColor = "var(--color-yellow-bg)";
    setTimeout(() => { target.style.backgroundColor = origBg; }, 900);
  }
}

function toggleGwGeminiPanel(forceState) {
  const panel = document.getElementById("gw-gemini-sidepanel");
  if (!panel) return;
  if (typeof forceState === "boolean") {
    panel.classList.toggle("hidden", !forceState);
  } else {
    panel.classList.toggle("hidden");
  }
}

function resetGwGeminiChat() {
  const msgBox = document.getElementById("gw-gemini-messages");
  if (!msgBox) return;
  msgBox.querySelectorAll(".gw-dynamic-msg").forEach(el => el.remove());
  const welcome = document.getElementById("gw-gemini-welcome");
  if (welcome) welcome.style.display = "block";
}

function appendGwGeminiExchange(userPrompt, aiHtml) {
  const msgBox = document.getElementById("gw-gemini-messages");
  if (!msgBox) return;
  const uDiv = document.createElement("div");
  uDiv.className = "gw-chat-bubble-user gw-dynamic-msg";
  uDiv.textContent = userPrompt;
  msgBox.appendChild(uDiv);

  const aDiv = document.createElement("div");
  aDiv.className = "gw-chat-bubble-ai gw-dynamic-msg";
  aDiv.innerHTML = aiHtml;
  msgBox.appendChild(aDiv);
  msgBox.scrollTop = msgBox.scrollHeight;
}

function runWorkspaceGeminiAction(actionType) {
  if (activeDocxModalMode !== "redline" && actionType !== "summarize_risks") {
    activeDocxModalMode = "redline";
    syncDocxModalIfOpen();
  }

  if (actionType === "accept_all") {
    acceptAllModalRedlines();
    appendGwGeminiExchange(
      "Apply Playbook v3.4: Accept all LexGraph seller-favorable positions across Section 8.02",
      `<div style="font-weight:600;color:var(--lumi-sys-color--positive);margin-bottom:4px;">✓ Applied to Document (3/3 Clauses Updated)</div>
       <div>All three counterparty markups in <strong>Section 8.02(a), (b), and (c)</strong> have been restored to <strong>LexGraph PE Seller Playbook v3.4</strong>:</div>
       <ul style="margin:6px 0 6px 16px;padding:0;font-size:12px;">
         <li><strong>§ 8.02(a):</strong> Restored 0.50% True Deductible ($21,000,000)</li>
         <li><strong>§ 8.02(b):</strong> Restored 0.75% Indemnity Cap ($31,500,000)</li>
         <li><strong>§ 8.02(c):</strong> Restricted carve-out strictly to Delaware Express Written Actual Fraud</li>
       </ul>
       <div style="font-size:11px;color:var(--color-ge-on-surface-variant);">Format-Lock: Updated <code>&lt;w:p&gt;</code> nodes in <code>word/document.xml</code> with zero style drift.</div>`
    );
    onModalPaperLiveEdit();
  } else if (actionType === "restore_deductible") {
    decideRedlineCard(0, "accepted");
    focusModalSubclause(0);
    appendGwGeminiExchange(
      "Modify § 8.02(a): Reject Tipping Basket and restore 0.50% True Deductible ($21M)",
      `<div style="font-weight:600;color:var(--lumi-sys-color--positive);margin-bottom:4px;">✓ Updated Section 8.02(a) in Live Document</div>
       <div>Rejected Skadden's 0.25% first-dollar Tipping Basket ($10.5M) and restored LexGraph's <strong>0.50% True Deductible ($21,000,000)</strong> where Seller is liable only for Losses exceeding the Deductible.</div>`
    );
    onModalPaperLiveEdit();
  } else if (actionType === "compromise_cap") {
    const paper = document.getElementById("docx-modal-paper");
    const sub1 = paper?.querySelector("#redline-sub-1");
    if (sub1) {
      sub1.className = "docx-subclause redline-subclause-item state-accepted";
      sub1.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:3px;" contenteditable="false">
          <span class="redline-decision-badge accepted">✦ Gemini Negotiated Compromise Applied (0.50% EV Cap)</span>
          <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" style="font-size:10px;padding:1px 7px;" onclick="decideRedlineCard(1, 'pending')">Undo</button>
        </div>
        <strong>(b)</strong> The maximum aggregate liability of the Seller Parties under Section 8.01(a) shall not exceed <span style="background:var(--color-green-bg);color:var(--color-green-text);font-weight:600;padding:1px 5px;border-radius:3px;">0.50% of the Base Purchase Price ($21,000,000) for general representations and 15% of the Base Purchase Price ($630,000,000) for Special Environmental &amp; IP Warranties</span> (the "Indemnity Cap").
      `;
      sub1.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    appendGwGeminiExchange(
      "Draft Compromise in § 8.02(b): Set Indemnity Cap to 0.50% ($21M) & remove $4.2B IP carve-out",
      `<div style="font-weight:600;color:var(--color-ge-primary);margin-bottom:4px;">✦ Rewrote Section 8.02(b) in Live Document</div>
       <div>Replaced Skadden's uncapped 100% ($4.2B) Special IP/Environmental super-cap with a balanced <strong>0.50% ($21M) general cap</strong> and a <strong>15% ($630M) Special IP/Environmental sub-cap</strong> while preserving native paragraph numbering.</div>`
    );
    onModalPaperLiveEdit();
  } else if (actionType === "insert_lego_rider") {
    insertCustomClauseBlock(
      "(d) Delaware Express Written Actual Fraud & Privacy Pro Rider (Legal Lego Block LEGO-DE-FRAUD + LEGO-PRIVACY-PRO). Solely in the case of intentional common law Actual Fraud under Delaware law (expressly excluding equitable fraud, promissory fraud, or constructive fraud) with respect to the express representations inside Article III, the Indemnity Cap shall not apply. All cross-border Personal Data transfers shall remain governed by the LexGraph Privacy Pro Standard Contractual Clauses.",
      "✦ Inserted by Gemini in Workspace · Legal Lego Rider (d)"
    );
    appendGwGeminiExchange(
      "Insert Legal Lego Rider: Append Delaware Actual Fraud & Privacy Pro clause (d)",
      `<div style="font-weight:600;color:var(--lumi-sys-color--positive);margin-bottom:4px;">✓ Inserted Clause (d) into Live Document</div>
       <div>Appended <strong>Legal Lego Blocks LEGO-DE-FRAUD &amp; LEGO-PRIVACY-PRO</strong> as subsection <strong>(d)</strong> at the bottom of the agreement sheet, inheriting the document's multi-level numbering and serif typography.</div>`
    );
  } else if (actionType === "summarize_risks") {
    sendWorkspaceGeminiPrompt("Summarize the 3 counterparty redline risks in this document and provide a recommended Playbook v3.4 fix clause.");
  }
}

async function sendWorkspaceGeminiPrompt(presetText) {
  const inputEl = document.getElementById("gw-gemini-input");
  const promptText = (presetText || (inputEl && inputEl.value) || "").trim();
  if (!promptText) return;
  if (inputEl && !presetText) inputEl.value = "";

  const paper = document.getElementById("docx-modal-paper");
  const docText = paper ? paper.innerText : "";
  const docTitle = document.getElementById("docx-modal-title")?.innerText || "Agreement.docx";

  // Check if user typed a direct command like "accept all"
  const lower = promptText.toLowerCase();
  if (lower.includes("accept all")) {
    runWorkspaceGeminiAction("accept_all");
    return;
  }

  const msgBox = document.getElementById("gw-gemini-messages");
  const uDiv = document.createElement("div");
  uDiv.className = "gw-chat-bubble-user gw-dynamic-msg";
  uDiv.textContent = promptText;
  msgBox?.appendChild(uDiv);

  const loadingDiv = document.createElement("div");
  loadingDiv.className = "gw-chat-bubble-ai gw-dynamic-msg";
  loadingDiv.innerHTML = `<div style="display:flex;align-items:center;gap:8px;color:var(--color-ge-primary);font-weight:500;"><span class="lumi-thinking-dots"><span></span><span></span><span></span></span><span class="lumi-shimmer-text">✦ Gemini 3.8 Flash analyzing document (${escapeHtml(currentSourceFormatLock.toUpperCase())})...</span></div>`;
  msgBox?.appendChild(loadingDiv);
  if (msgBox) msgBox.scrollTop = msgBox.scrollHeight;

  try {
    const resp = await fetch(`${API_BASE}/api/workspace-assistant`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: promptText,
        document_title: docTitle,
        document_text: docText,
        pair_id: currentRedlineData?.pair_id || "KESTREL-SPA-802",
        source_format: currentSourceFormatLock,
        chat_context: window.GEMINI_CHAT_CONTEXT || currentRedlineData?.chat_context || "",
      }),
    });
    const data = await resp.json();
    lastProposedGeminiClause = data.proposed_clause || "";

    // Auto-apply if user explicitly asked to insert/apply/rewrite/add/change
    const shouldAutoApply = /(insert|apply|rewrite|replace|change|add|modify)/i.test(promptText) && lastProposedGeminiClause;
    if (shouldAutoApply) {
      insertCustomClauseBlock(lastProposedGeminiClause, "✦ Auto-Applied by Gemini 3.8 Flash in Workspace");
    }

    loadingDiv.innerHTML = `
      <div style="margin-bottom:6px;">${escapeHtml(data.summary || "")}</div>
      ${lastProposedGeminiClause ? `
        <div style="background:var(--color-ge-surface-container-low);border:1px solid var(--color-ge-primary-container);border-radius:8px;padding:8px 10px;margin-top:6px;font-family:var(--font-serif);font-size:12px;color:var(--color-ge-on-surface);">
          ${escapeHtml(lastProposedGeminiClause)}
        </div>
        <div style="margin-top:8px;display:flex;align-items:center;gap:6px;">
          <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-blue pill-btn-xs" onclick="applyCustomGeminiClauseToDoc()">
            ${shouldAutoApply ? '✓ Applied to Document (Click to Insert Again)' : '✦ ' + escapeHtml(data.action_label || 'Apply Clause Edit to Document')}
          </button>
        </div>
      ` : ""}
    `;
  } catch (err) {
    loadingDiv.innerHTML = `<div style="color:var(--color-red-text);">Unable to reach Gemini Workspace Assistant: ${escapeHtml(err.message)}</div>`;
  }
  if (msgBox) msgBox.scrollTop = msgBox.scrollHeight;
}

function applyCustomGeminiClauseToDoc() {
  if (!lastProposedGeminiClause) return;
  insertCustomClauseBlock(lastProposedGeminiClause, "✦ Applied from Gemini Side Panel · Native Format Preserved");
}

async function downloadLiveEditedDocx() {
  const paper = document.getElementById("docx-modal-paper");
  const titleStr = (document.getElementById("docx-modal-title")?.innerText || "LexGraph_Edited_Draft.docx").trim();
  const rawText = paper ? paper.innerText : "";
  const paragraphs = rawText.split(/\n+/).map(s => s.trim()).filter(Boolean);

  const btn = document.getElementById("btn-export-live-docx");
  if (btn) btn.textContent = "⏳ Exporting .docx...";
  try {
    const resp = await fetch(`${API_BASE}/api/export-live-docx`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: titleStr.endsWith(".docx") ? titleStr : `${titleStr}.docx`,
        title: "APEX LAW PARTNERS LLP — CO-EDITED OPENXML DOCUMENT",
        paragraphs: paragraphs,
      }),
    });
    if (resp.ok) {
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = titleStr.endsWith(".docx") ? titleStr : `${titleStr}.docx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      if (btn) {
        btn.textContent = "✓ Downloaded .docx";
        setTimeout(() => { btn.textContent = "⬇ Export Live .docx"; }, 1800);
      }
      return;
    }
  } catch (e) {}
  if (btn) btn.textContent = "⬇ Export Live .docx";
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
    titleEl.textContent = "LexGraph_Legal_Legos_Composed_Rider.docx";
    subEl.textContent = `Composed Multi-Level OpenXML Rider · ${checked.length} Active Playbook Clauses`;
    if (dlBtn) {
      dlBtn.href = `${API_BASE}/api/legal-legos/docx?blocks=${encodeURIComponent((checked.length ? checked : ["LEGO-DE-FRAUD"]).join(","))}`;
      dlBtn.textContent = "🔒 Share / .docx";
    }
    controlsEl.innerHTML = `
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
        <span style="font-weight:600;color:var(--color-ge-on-primary-container);">Toggle Legal Lego Blocks Live:</span>
        ${["LEGO-DE-FRAUD", "LEGO-338H10-TAX", "LEGO-PRIVACY-PRO", "LEGO-MFN-FUNDGEN"].map(bid => {
          const isOn = checked.includes(bid);
          return `<button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${isOn ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="toggleModalLegoCheckbox('${bid}')">${isOn ? '✓ ' : '+ '}${bid}</button>`;
        }).join("")}
      </div>
      <div style="display:flex;align-items:center;gap:6px;">
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="openDocxModal('redline')">Switch to Redline Sheet →</button>
      </div>
    `;
    paperEl.innerHTML = document.getElementById("legos-preview-box")?.innerHTML || "";
  } else if (activeDocxModalMode === "redline") {
    const d = currentRedlineData || {};
    titleEl.textContent = d.doc_b_name || "08_M331_Brightwater_SPA_Skadden_v4_Redline.docx";
    subEl.textContent = `${d.title || 'Contract Redline'} · LexGraph Playbook v3.4 vs. Counterparty v4.0`;
    if (dlBtn) {
      dlBtn.href = `${API_BASE}/api/corpus/file/08_M331_Brightwater_Merger_Agreement_Skadden_v4_Redline.docx`;
      dlBtn.textContent = "🔒 Share / v4 .docx";
    }
    controlsEl.innerHTML = `
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${d.pair_id === 'KESTREL-SPA-802' ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="loadRedlinePair('KESTREL-SPA-802')">§ 8.02(b) Indemnity</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${d.pair_id === 'KESTREL-SCRAPE-804' ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="loadRedlinePair('KESTREL-SCRAPE-804')">§ 8.04(a) Scrape</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${d.pair_id === 'KESTREL-TAX-304' ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="loadRedlinePair('KESTREL-TAX-304')">§ 3.04 Tax 338(h)(10)</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${d.pair_id === 'KESTREL-COC-804' ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="loadRedlinePair('KESTREL-COC-804')">§ 8.04 CoC</button>
      </div>
      <div style="display:flex;align-items:center;gap:6px;">
        <button id="modal-btn-accept-all" type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-blue pill-btn-xs" onclick="acceptAllModalRedlines()">✓ Accept All LexGraph v3</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="resetRedlineDecisions()">Reset</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="openDocxModal('legos')">Switch to Legal Legos →</button>
      </div>
    `;
    paperEl.innerHTML = `
      <div class="docx-running-header" contenteditable="false">
        <span>APEX LAW PARTNERS LLP · TRACK CHANGES COMPARE</span>
        <span>MATTER ${escapeHtml(d.matter_id || 'M-331-KESTREL')} · PAGE 42</span>
      </div>
      <div class="docx-doc-title" style="text-align:left;margin-bottom:10px;">
        ${escapeHtml(d.title || 'ARTICLE VIII — INDEMNIFICATION')}
      </div>
      <div style="font-family:var(--font-sans);font-size:12px;color:var(--color-ge-on-primary-container);background:var(--color-blue-bg);border:1px solid var(--color-blue-border);border-radius:6px;padding:8px 12px;margin-bottom:14px;">
        <strong>Playbook Standard:</strong> ${escapeHtml(d.playbook_standard || '')}
      </div>
      <div class="docx-redline-margin">
        ${buildInteractiveRedlineSheetHtml()}
      </div>
      <div class="docx-running-footer" contenteditable="false">
        <span>Compare: LexGraph Playbook v3.4 ↔ Counterparty Markup v4.0</span>
        <span>OpenXML w:del / w:ins</span>
      </div>
    `;
  } else if (activeDocxModalMode === "inspector") {
    const row = tabularRows[activeInspectorRowIdx] || tabularRows[0] || {};
    titleEl.textContent = row.filename || "Executed_Agreement.docx";
    subEl.textContent = `${row.doc_id || 'DOC-01'} · ${row.citation || 'Section 1.01'} · Grounded Pin-Cite Reader`;
    if (dlBtn) {
      dlBtn.href = document.getElementById("insp-download-link")?.href || "#";
      dlBtn.textContent = "🔒 Original .docx";
    }
    controlsEl.innerHTML = `
      <div style="display:flex;align-items:center;gap:6px;">
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="navigateInspectorRow(-1);syncDocxModalIfOpen();">← Previous Contract</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer pill-btn-white pill-btn-xs" onclick="navigateInspectorRow(1);syncDocxModalIfOpen();">Next Contract →</button>
        <span style="font-weight:600;color:var(--color-ge-on-primary-container);margin-left:6px;">Contract ${activeInspectorRowIdx + 1} of ${tabularRows.length}</span>
      </div>
      <span class="status-pill lumi-status-badge green">Spanner BBox Pin-Cite Verified</span>
    `;
    paperEl.innerHTML = `
      <div class="docx-running-header" contenteditable="false">
        <span>LEXGRAPH · EXECUTION COPY</span>
        <span>${escapeHtml(row.doc_id || '')} · ${escapeHtml(row.citation || '')}</span>
      </div>
      <div style="font-family:var(--font-sans);font-size:12.5px;background:var(--color-blue-bg);border-left:4px solid var(--color-ge-primary);padding:10px 12px;border-radius:4px;margin-bottom:14px;">
        ${document.getElementById("insp-pincite-quote")?.innerHTML || ""}
      </div>
      <div>${document.getElementById("insp-contract-body")?.innerHTML || ""}</div>
      <div class="docx-running-footer" contenteditable="false">
        <span>LEXGRAPH:\\98412034.4\\31402.0018</span>
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
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${currentExhibitIdx === 0 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="selectMultimodalExhibit(0)">EBITDA Bridge</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${currentExhibitIdx === 1 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="selectMultimodalExhibit(1)">LP Fee Curve</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${currentExhibitIdx === 2 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="selectMultimodalExhibit(2)">J.Crew Org Chart</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${currentExhibitIdx === 3 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="selectMultimodalExhibit(3)">Citibank $18M Scan</button>
      </div>
    `;
    paperEl.innerHTML = `
      <div class="docx-running-header">
        <span>LEXGRAPH MULTIMODAL DOCPARSE · CLOUD SPANNER</span>
        <span>EXHIBIT ${currentExhibitIdx + 1} OF 4</span>
      </div>
      <div class="docx-doc-title" style="margin-bottom:8px;">${escapeHtml(titleStr)}</div>
      <div style="font-family:var(--font-sans);font-size:13px;color:var(--color-ge-on-primary-container);background:var(--color-blue-bg);border:1px solid var(--color-blue-border);border-radius:8px;padding:10px 14px;margin-bottom:14px;">
        <strong>Extracted Grounding Insight:</strong> ${escapeHtml(takeawayStr)}
      </div>
      <div style="text-align:center;background:var(--color-ge-surface-container-low);border:1px solid var(--color-ge-outline-variant);border-radius:8px;padding:14px;">
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
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${!currentEmlInspectState.isCal && currentEmlInspectState.idx === 0 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="inspectRawEml(0, false)">EM-9901 (338h10 Tax)</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${!currentEmlInspectState.isCal && currentEmlInspectState.idx === 1 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="inspectRawEml(1, false)">EM-9902 (Skadden v4)</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${!currentEmlInspectState.isCal && currentEmlInspectState.idx === 2 ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="inspectRawEml(2, false)">EM-9903 (FundHQ MFN)</button>
        <button type="button" class="pill-btn lumi-btn lumi-btn-sm button--state-layer ${currentEmlInspectState.isCal ? 'pill-btn-blue' : 'pill-btn-white'} pill-btn-xs" onclick="inspectRawEml(0, true)">CAL-101 Conflict (.ics)</button>
      </div>
    `;
    paperEl.innerHTML = document.getElementById("raw-eml-viewer")?.innerHTML || "";
  } else if (activeDocxModalMode === "governance") {
    titleEl.textContent = `Intapp Ethical Wall & Cloud Spanner Graph Audit (${currentGovernanceMatter})`;
    subEl.textContent = "ISO GQL Screen-Before-Rank Certificate";
    controlsEl.innerHTML = `<span style="font-weight:600;color:var(--color-ge-on-primary-container);">Zero-Leakage Pre-ANN Graph Filtering</span>`;
    paperEl.innerHTML = `
      <div class="docx-running-header">
        <span>LEXGRAPH OCG &amp; INTAPP WALL COMPLIANCE</span>
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
    html = html.replace(
        f'class="ge-nav-item" data-studio="{initial_view}"',
        f'class="ge-nav-item active" data-studio="{initial_view}"',
    )
    html = html.replace("__INITIAL_STUDIO_VIEW__", initial_view)
    html = html.replace("__DEFAULT_API_BASE__", api_base.rstrip("/"))
    html = html.replace("__INITIAL_BOOTSTRAP_JSON__", bootstrap_json)
    html = html.replace("__PRERENDERED_TBODY__", prerendered_tbody)
    html = html.replace("__FIRST_QUOTE__", first_quote)
    html = html.replace("__FIRST_PAGE_TEXT__", first_page_text)
    html = html.replace("/* __GE_LUMINOUS_TOKENS_CSS__ */", _load_ge_luminous_tokens_css())
    return html
