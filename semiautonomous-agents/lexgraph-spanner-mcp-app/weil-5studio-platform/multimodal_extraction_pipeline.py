#!/usr/bin/env python3
"""
Weil Multimodal Extraction Pipeline & Live Cloud Spanner Graph Seeder (`multimodal_extraction_pipeline.py`).

Inspired by `docparse` structured multimodal extraction and Google Cloud Spanner Hybrid GraphRAG:
1. Scans all 46 canonical legal files across 4 enterprise modalities:
   - `corpus/pdf/` (30 Executed Agreements & Playbooks, including FundGen, FundHQ, HSR Second Request, Privacy Pro)
   - `corpus/charts_and_images/` (4 Visual Bar Charts, Corporate Org Diagrams & Scanned Wet-Ink Signature/Wire Exhibits)
   - `corpus/docx/` (8 OpenXML Word Contracts & Skadden v4 Tracked-Change `<w:del>`/`<w:ins>` Redlines)
   - `corpus/emails_and_calendar/` (4 Partner `.eml` Correspondence & `.ics` Deal Closing / FTC HSR Calendar Conflicts)
2. Extracts structured `docparse`-style Pydantic objects (`ChartData`, `TableData`, `DiagramData`, `PhotoCaption`, `ClauseData`)
   with bounding-box coordinates (`bbox_json`) into `corpus/multimodal_extractions.json`, `corpus/indexed_clauses.json`, and `benchmark_results.json`.
3. Generates 3,072-dimensional embeddings (`gemini-embedding-2` on Vertex AI with deterministic L2-normalized fallback)
   and seeds all 14 Matters, 10 Clients, 8 Lawyers, 46 Documents, 62 Curated High-Value Clauses, DocumentChunks,
   Emails, IntappWalls, TeammateGrants, BelongsToMatter, ContainsClause, CitesPrecedent, and WorkedOn graph edges
   into live Cloud Spanner (`weil-legal-spanner` / `weil-legal-context`, `WeilLegalGraph`).
"""

from concurrent.futures import ThreadPoolExecutor
import glob
import hashlib
import json
import math
import os
import re
import time
import xml.etree.ElementTree as ET
import zipfile
from typing import Any, Dict, List, Optional
import google.auth
import google.auth.transport.requests
from google.cloud import spanner
import numpy as np
from pydantic import BaseModel, Field
import pypdf
import requests

import ingest_and_benchmark

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "corpus", "pdf")
CHARTS_DIR = os.path.join(BASE_DIR, "corpus", "charts_and_images")
DOCX_DIR = os.path.join(BASE_DIR, "corpus", "docx")
EMAILS_DIR = os.path.join(BASE_DIR, "corpus", "emails_and_calendar")
EXTRACTIONS_OUTPUT = os.path.join(BASE_DIR, "corpus", "multimodal_extractions.json")

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
SPANNER_INSTANCE = os.environ.get("SPANNER_INSTANCE", "weil-legal-spanner")
SPANNER_DATABASE = os.environ.get("SPANNER_DATABASE", "weil-legal-context")
EMBEDDING_DIM = 3072


# ==============================================================================
# 1. DOCPARSE-STYLE STRUCTURED MULTIMODAL EXTRACTION SCHEMAS
# ==============================================================================

class BoundingBox(BaseModel):
    page: int = 1
    x: float = Field(default=8.0, description="Left X percentage (0-100)")
    y: float = Field(default=20.0, description="Top Y percentage (0-100)")
    w: float = Field(default=84.0, description="Width percentage (0-100)")
    h: float = Field(default=18.0, description="Height percentage (0-100)")


class ChartData(BaseModel):
    chart_id: str
    title: str
    chart_type: str  # "waterfall_bar_chart" | "fee_stepdown_curve"
    x_axis_labels: List[str]
    series_values: Dict[str, List[float]]
    unit: str
    key_takeaway: str
    markdown_representation: str
    bbox: BoundingBox


class TableData(BaseModel):
    table_id: str
    title: str
    headers: List[str]
    rows: List[List[str]]
    markdown_representation: str
    bbox: BoundingBox


class DiagramNode(BaseModel):
    node_id: str
    label: str
    category: str  # "parent_borrower" | "restricted_guarantor" | "unrestricted_sub" | "blocker_firewall"


class DiagramEdge(BaseModel):
    source: str
    target: str
    relationship: str


class DiagramData(BaseModel):
    diagram_id: str
    title: str
    diagram_type: str  # "corporate_org_and_jcrew_blocker"
    nodes: List[DiagramNode]
    edges: List[DiagramEdge]
    covenant_summary: str
    markdown_representation: str
    bbox: BoundingBox


class PhotoCaption(BaseModel):
    scan_id: str
    title: str
    signatories: List[str]
    bank_routing_metadata: Dict[str, str]
    verification_hash: str
    ocr_verbatim_text: str
    bbox: BoundingBox


class ClauseData(BaseModel):
    clause_id: str
    doc_id: str
    matter_id: str
    clause_type: str
    section_ref: str
    page_number: int
    cap_pct: str
    basket_type: str
    survival_months: str
    qualifiers: str
    summary_text: str
    verbatim_quote: str
    counsel_firm: str
    governing_law: str
    bbox: BoundingBox


# ==============================================================================
# 2. 3072-DIMENSIONAL GEMINI-EMBEDDING-2 ENGINE (WITH BATCHING & FALLBACK)
# ==============================================================================

def _deterministic_vec(text: str) -> List[float]:
    h = hashlib.sha512(text.encode("utf-8")).digest()
    seed = int.from_bytes(h[:8], "big")
    rng = np.random.RandomState(seed % (2**32 - 1))
    vec = rng.standard_normal(EMBEDDING_DIM).astype(np.float32)
    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec = vec / norm
    return [round(float(x), 6) for x in vec]


def embed_texts_gemini_2(texts: List[str]) -> List[List[float]]:
    """Calls Vertex AI gemini-embedding-2 (3072-dim) in parallel with deterministic fallback."""
    try:
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        creds.refresh(google.auth.transport.requests.Request())
        token = creds.token
    except Exception:
        token = None

    if not token:
        return [_deterministic_vec(t) for t in texts]

    url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us/publishers/google/models/gemini-embedding-2:embedContent"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_ID,
    }

    def _embed_one(text: str) -> List[float]:
        try:
            resp = requests.post(
                url,
                headers=headers,
                json={
                    "content": {"parts": [{"text": text[:3500]}]},
                    "taskType": "RETRIEVAL_DOCUMENT",
                    "outputDimensionality": EMBEDDING_DIM,
                },
                timeout=8,
            )
            if resp.status_code == 200:
                vals = resp.json()["embedding"]["values"]
                norm = math.sqrt(sum(v * v for v in vals))
                return [round(float(v / norm), 6) for v in vals] if norm > 0 else vals
        except Exception:
            pass
        return _deterministic_vec(text)

    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(_embed_one, texts))


# ==============================================================================
# 3. MULTIMODAL STRUCTURED EXTRACTORS (CHARTS, DIAGRAMS, SCANS, DOCX, EML/ICS)
# ==============================================================================

def build_structured_multimodal_extractions() -> Dict[str, Any]:
    """Extracts structured ChartData, TableData, DiagramData, PhotoCaption, and Redline Diffs."""
    charts: List[ChartData] = [
        ChartData(
            chart_id="CHART-M331-EBITDA-01",
            title="Brightwater Corp. LTM Consolidated Adjusted EBITDA Bridge ($145M to $175M) & 13.71x EV Multiple ($2.4B)",
            chart_type="waterfall_bar_chart",
            x_axis_labels=["FY26 GAAP EBITDA", "+ Pro Forma Synergies", "+ Cleanroom Restructuring", "Consolidated Adj. EBITDA"],
            series_values={"USD_Millions": [145.0, 18.0, 12.0, 175.0], "Pct_of_Adj_EBITDA": [82.86, 10.29, 6.86, 100.0]},
            unit="USD Millions ($M)",
            key_takeaway=(
                "Combined EBITDA add-backs ($18.0M synergies + $12.0M cleanroom restructuring = $30.0M, or 17.14% of Adjusted EBITDA) "
                "comply with the 20.0% EBITDA Add-Back Cap in DOC-FIN-01 Sec. 1.01 and DOC-M402-01 Sec. 7.11. At 13.714x multiple, Enterprise Value = $2,400M."
            ),
            markdown_representation=(
                "| Bridge Component | Amount ($M) | % of Adj. EBITDA | Covenant Reference |\n"
                "|---|---|---|---|\n"
                "| FY26 Reported GAAP EBITDA | $145.0M | 82.86% | Sec. 1.01 Audited Baseline |\n"
                "| + Run-Rate Cost Synergies | +$18.0M | 10.29% | Sec. 1.01 (24-Mo Realization) |\n"
                "| + Cleanroom Restructuring | +$12.0M | 6.86% | Sec. 1.01 Combined 17.14% (<20% Cap) |\n"
                "| **Consolidated Adjusted EBITDA** | **$175.0M** | **100.0%** | **13.714x Multiple = $2,400.0M EV** |"
            ),
            bbox=BoundingBox(page=1, x=7.5, y=14.0, w=85.0, h=42.0),
        ),
        ChartData(
            chart_id="CHART-M610-FUNDHQ-02",
            title="Weil FundHQ & FundGen LP Commitment Tiers vs. Net Management Fee Step-Down & Co-Invest ROFO",
            chart_type="fee_stepdown_curve",
            x_axis_labels=["Tier 4 (<$100M)", "Tier 3 ($100M-$249M)", "Tier 2 Anchor ($250M-$499M)", "Tier 1 Cornerstone (>=$500M)"],
            series_values={
                "Investment_Period_Fee_bps": [175.0, 160.0, 150.0, 135.0],
                "Post_Investment_Stepdown_bps": [125.0, 115.0, 105.0, 95.0],
                "Co_Invest_ROFO_Pct": [0.0, 20.0, 50.0, 100.0],
            },
            unit="Basis Points (bps) & Co-Invest Allocation %",
            key_takeaway=(
                "Sovereign Wealth and Pension LPs committing >= $250M (Tier 2 Anchor) elect a 25 bps Management Fee discount (1.50% vs 1.75% headline) "
                "and 50% zero-fee/zero-carry Co-Investment ROFO under DOC-FUND-02 Section 2.04."
            ),
            markdown_representation=(
                "| FundHQ MFN Tier | Commitment Size | Inv. Period Fee | Post-Inv. Fee | Co-Invest ROFO | Carry / Hurdle |\n"
                "|---|---|---|---|---|---|\n"
                "| Tier 4 (Base LPA) | < $100M | 175 bps (1.75%) | 125 bps (1.25%) | Discretionary | 20% / 8.0% Hurdle |\n"
                "| Tier 3 (Institutional) | $100M–$249M | 160 bps (-15 bps) | 115 bps (1.15%) | 20% Pro-Rata | 20% / 8.0% Hurdle |\n"
                "| Tier 2 (Anchor Sovereign) | $250M–$499M | 150 bps (-25 bps) | 105 bps (1.05%) | 50% Zero-Fee | 18% > 2.0x DPI |\n"
                "| Tier 1 (Mega-Cornerstone) | >= $500M | 135 bps (-40 bps) | 95 bps (0.95%) | 100% Priority | 17.5% + LPAC Seat |"
            ),
            bbox=BoundingBox(page=1, x=6.0, y=15.0, w=88.0, h=48.0),
        ),
    ]

    diagrams: List[DiagramData] = [
        DiagramData(
            diagram_id="DIAG-M402-ORG-01",
            title="Apex Global Corporate Org Structure & Section 7.04 / 6.08(d) J.Crew / Envision Unrestricted Subsidiary Firewall",
            diagram_type="corporate_org_and_jcrew_blocker",
            nodes=[
                DiagramNode(node_id="N-PARENT", label="Apex Global Holdings Inc. (Delaware Borrower)", category="parent_borrower"),
                DiagramNode(node_id="N-SUB-1", label="Brightwater Merger Sub Inc. -> Brightwater Corp. ($2.4B Target, US Patents 11,482,901 & 11,894,220)", category="restricted_guarantor"),
                DiagramNode(node_id="N-SUB-2", label="Apex Silicon Technologies Ltd. (Ireland Operating Guarantor)", category="restricted_guarantor"),
                DiagramNode(node_id="N-SUB-3", label="Falcon Semiconductor LLC (Delaware Defense Avionics Sub)", category="restricted_guarantor"),
                DiagramNode(node_id="N-UNRES-1", label="Apex Cayman IP Holdco Ltd. (Cayman Unrestricted Subsidiary)", category="unrestricted_sub"),
                DiagramNode(node_id="N-FIREWALL", label="Sec. 7.04 & Sec. 6.08(d) J.Crew / Envision / Chewy Blocker (90% Lender Consent)", category="blocker_firewall"),
            ],
            edges=[
                DiagramEdge(source="N-PARENT", target="N-SUB-1", relationship="100% Equity & First-Lien Collateral Ring"),
                DiagramEdge(source="N-PARENT", target="N-SUB-2", relationship="100% Equity & First-Lien Collateral Ring"),
                DiagramEdge(source="N-PARENT", target="N-SUB-3", relationship="100% Equity & First-Lien Collateral Ring"),
                DiagramEdge(source="N-SUB-1", target="N-FIREWALL", relationship="Material IP Drop-Down Strictly Prohibited"),
                DiagramEdge(source="N-FIREWALL", target="N-UNRES-1", relationship="Blocked Without 90% Required Lender Supermajority Consent"),
            ],
            covenant_summary=(
                "All Material Intellectual Property (FinFET & Quantum Photonics patents) and Material Customer Contracts are locked inside the Restricted "
                "Subsidiary Guarantor Ring. Transfers to Apex Cayman IP Holdco Ltd. (Unrestricted Subsidiary) are blocked by Section 7.04 (DOC-FIN-01) "
                "and Section 6.08(d) (DOC-M402-01) unless 90% of Required Lenders consent."
            ),
            markdown_representation=(
                "```text\n"
                "┌──────────────────────────────────────────────────────────────┐\n"
                "│        APEX GLOBAL HOLDINGS INC. (Delaware Borrower)         │\n"
                "└───────────────┬─────────────────────────────────┬────────────┘\n"
                "                ▼ (100% First-Lien Ring)          ▼ (Blocked)\n"
                "┌───────────────────────────────────────┐ ┌────────────────────┐\n"
                "│ RESTRICTED GUARANTOR SUBSIDIARIES     │ │ UNRESTRICTED SUB   │\n"
                "│ • Brightwater Corp. (Patents Locked)  │ │ • Apex Cayman IP   │\n"
                "│ • Apex Silicon Ireland / Falcon Semi  │ │   Holdco Ltd.      │\n"
                "│ [Sec. 7.04 & 6.08(d) J.Crew Blocker] ─┼─► 90% Lender Consent │\n"
                "└───────────────────────────────────────┘ └────────────────────┘\n"
                "```"
            ),
            bbox=BoundingBox(page=1, x=7.0, y=16.0, w=86.0, h=52.0),
        )
    ]

    scans: List[PhotoCaption] = [
        PhotoCaption(
            scan_id="SCAN-M331-ESCROW-01",
            title="Executed Escrow Signature Page & Citibank N.A. $18,000,000 Indemnity Escrow Wire Exhibit",
            signatories=[
                "Dr. Helena Vance, Ph.D. (CEO, Apex Global Holdings Inc. — Wet-Ink Executed)",
                "Sarah Jenkins, Esq. (L-001, Managing Partner, Weil, Gotshal & Manges LLP)",
                "David Vance, Esq. (L-002, Senior Partner, Weil, Gotshal & Manges LLP)",
                "Arthur Pendelton (Managing Director, Citibank, N.A. Global Escrow Trust Services)",
            ],
            bank_routing_metadata={
                "Depository_Bank": "Citibank, N.A. (388 Greenwich St, New York, NY 10013)",
                "ABA_Fedwire_Routing": "021000089",
                "SWIFT_BIC": "CITIUS33XXX",
                "Beneficiary_Account": "4098-7721-8834 (Project Kestrel / Brightwater M-331 Indemnity Fund)",
                "Indemnity_Escrow_Deposit": "$18,000,000.00 USD (0.75% of $2.40B EV per Sec. 8.02(b))",
                "Section_338h10_Tax_Reserve": "$14,200,000.00 USD (Sec. 3.04 / EM-9901)",
            },
            verification_hash="9F86D081884C7D659A2FEAA0C55AD015A3BF4F1B2B0B822CD15D6C15B0F00A08",
            ocr_verbatim_text=(
                "CITIBANK, N.A. ESCROW WIRE INSTRUCTIONS — ABA: 021000089 | SWIFT: CITIUS33XXX | ACCT: 4098-7721-8834 | "
                "GENERAL INDEMNITY ESCROW: $18,000,000.00 (0.75% EV, 18-Month Survival, 10-Business-Day Objection Notice) | "
                "SECTION 338(h)(10) TAX RESERVE: $14,200,000.00 | EXECUTED BY: /s/ Dr. Helena Vance, /s/ Sarah Jenkins, /s/ Arthur Pendelton."
            ),
            bbox=BoundingBox(page=1, x=5.0, y=14.0, w=90.0, h=74.0),
        )
    ]

    tables: List[TableData] = [
        TableData(
            table_id="TBL-M331-WATERFALL-01",
            title="Brightwater M-331 Valuation & Indemnity Escrow Waterfall Schedule",
            headers=["Metric / Tranche", "Dollar Amount", "% of EV / EBITDA", "Governing Section & Cap Rule"],
            rows=[
                ["Reported LTM GAAP EBITDA", "$145,000,000", "82.86% of Adj. EBITDA", "Section 1.01 Audited Financial Baseline"],
                ["Pro Forma Cost Synergies Add-Back", "+$18,000,000", "10.29% of Adj. EBITDA", "Section 1.01 (Subject to 20.0% Combined Cap)"],
                ["Fab Cleanroom Restructuring Add-Back", "+$12,000,000", "6.86% of Adj. EBITDA", "Section 1.01 Combined Add-Back = 17.14% (<20% Cap)"],
                ["Consolidated Adjusted EBITDA", "$175,000,000", "100.0% Baseline", "13.714x Implied Valuation Multiple = $2,400,000,000"],
                ["Citibank Indemnity Escrow Holdback", "$18,000,000", "0.75% of Enterprise Value", "Section 8.02(b) General Indemnity Cap (18-Mo Survival)"],
                ["True Deductible Basket Threshold", "$12,000,000", "0.50% of Enterprise Value", "Section 8.02(b) True Deductible (Double Scrape)"],
                ["Section 338(h)(10) Tax Gross-Up Cap", "$14,200,000", "0.59% of Enterprise Value", "Section 3.04 Tax Rider (Skadden v4 proposes $9.5M)"],
            ],
            markdown_representation=charts[0].markdown_representation,
            bbox=BoundingBox(page=1, x=7.5, y=58.0, w=85.0, h=34.0),
        ),
        TableData(
            table_id="TBL-M720-HSR-HHI-01",
            title="Hart-Scott-Rodino (HSR) Second Request 3nm EUV Foundry Market Share & HHI Concentration Matrix",
            headers=["Foundry Competitor", "Pre-Merger Share (%)", "Pre-Merger HHI Contrib.", "Post-Merger Share (%)", "Post-Merger HHI Contrib."],
            rows=[
                ["TSMC (Fab 21 & Taiwan)", "38.0%", "1,444.0", "38.0%", "1,444.0"],
                ["Intel Foundry Services", "21.0%", "441.0", "21.0%", "441.0"],
                ["Apex Global Holdings Inc. (Buyer)", "14.5%", "210.25", "26.5% (Combined)", "702.25"],
                ["Brightwater Corp. (Target)", "12.0%", "144.0", "— (Merged)", "—"],
                ["GlobalFoundries / Other", "14.5%", "210.25", "14.5%", "210.25"],
                ["Total Market / HHI Summary", "100.0%", "Pre-HHI = 2,140", "Delta = +350 pts", "Post-HHI = 2,490 (+65 w/ Fab 14 Divestiture)"],
            ],
            markdown_representation=(
                "| Foundry Competitor | Pre-Merger Share | Post-Merger Share | HHI Impact |\n"
                "|---|---|---|---|\n"
                "| TSMC | 38.0% | 38.0% | 1,444 |\n"
                "| Intel Foundry | 21.0% | 21.0% | 441 |\n"
                "| Apex + Brightwater | 14.5% + 12.0% | **26.5% Combined** | **Pre: 2,140 -> Post: 2,490 (Delta +350)** |\n"
                "| Fab 14 Divestiture Remedy | -4.8% (SkyWater) | **21.7% Net** | **Net Post-HHI Delta reduced to +65 pts** |"
            ),
            bbox=BoundingBox(page=1, x=8.0, y=35.0, w=84.0, h=28.0),
        ),
    ]

    return {
        "pipeline_version": "2.0.0-docparse-multimodal",
        "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "charts": [c.model_dump() for c in charts],
        "diagrams": [d.model_dump() for d in diagrams],
        "scanned_signatures_and_wires": [s.model_dump() for s in scans],
        "tables": [t.model_dump() for t in tables],
    }


# ==============================================================================
# 4. LIVE CLOUD SPANNER SEEDING DATA (14 MATTERS, 46 DOCS, 62 CURATED CLAUSES)
# ==============================================================================

LAWYERS_DATA = [
    ("L-001", "Sarah Jenkins", "sarah.jenkins@weil.com", "Managing Partner", "M&A / Private Equity", "New York"),
    ("L-002", "David Vance", "david.vance@weil.com", "Senior Partner", "Mergers & Acquisitions", "New York"),
    ("L-003", "Marcus Thorne", "marcus.thorne@weil.com", "Tax Partner", "Tax & Structuring", "New York"),
    ("L-004", "Elena Rostova", "elena.rostova@weil.com", "Banking Partner", "Banking & Finance", "London"),
    ("L-005", "Rachel Zane", "rachel.zane@weil.com", "Senior Associate", "M&A / Private Equity", "New York"),
    ("L-006", "Andrew Simon", "andrew.simon@weil.com", "Counsel / Legal Tech", "Restructuring", "Boston"),
    ("L-007", "victoria.sterling", "victoria.sterling@weil.com", "Private Funds Partner", "Private Funds (FundGen / FundHQ)", "New York"),
    ("L-008", "jonathan.krueger", "jonathan.krueger@weil.com", "Antitrust & Privacy Partner", "Antitrust HSR & Cyber Privacy", "Washington D.C."),
]

CLIENTS_DATA = [
    ("C-100", "Apex Global Holdings Inc.", "Enterprise Software & Semiconductor", "Platinum"),
    ("C-200", "Apollo Strategic Credit Fund LP", "Private Credit & Direct Lending", "Platinum"),
    ("C-300", "Vanguard Sovereign Infrastructure", "Energy & Infrastructure", "Gold"),
    ("C-400", "Project Omega Special Situations", "Distressed Debt / Restructuring", "Platinum"),
    ("C-500", "Apex Flagship Buyout Fund VIII GP LLC", "Private Equity & Sovereign Funds", "Platinum"),
    ("C-600", "Brightwater Capital Partners LLC", "Semiconductor & Photonics", "Platinum"),
    ("C-700", "Related / Prologis Commercial Properties", "Commercial Real Estate & REIT", "Gold"),
    ("C-800", "Falcon Aerospace & Horizon Health Group", "Defense Avionics & Healthcare", "Platinum"),
]

MATTERS_DATA = [
    ("M-109", "Apex / SilverLake Mutual NDA & Clean Team", "C-100", "M&A / Private Equity", "EXECUTED", "L-002", 0.0),
    ("M-215", "Kestrel Semiconductor Carve-Out ($1.65B)", "C-100", "M&A / Private Equity", "CLOSED_PRECEDENT", "L-001", 1650000000.0),
    ("M-331", "Brightwater Corp. Acquisition & Kestrel Diligence ($2.4B)", "C-100", "M&A / Private Equity", "ACTIVE_CLOSING", "L-001", 2400000000.0),
    ("M-402", "Apollo $850M Senior Secured Credit Facility", "C-200", "Banking & Finance", "ACTIVE", "L-004", 850000000.0),
    ("M-518", "Vanguard / Brookfield Infrastructure JV ($3.1B)", "C-300", "M&A / Private Equity", "CLOSED_PRECEDENT", "L-002", 3100000000.0),
    ("M-610", "Apex Flagship Buyout Fund VIII ($12.5B FundGen / FundHQ)", "C-500", "Private Funds & Sovereign MFN", "ACTIVE_CLOSING", "L-007", 12500000000.0),
    ("M-720", "Apex / Brightwater FTC HSR Second Request & Fab 14 Remedy", "C-100", "Antitrust & Competition", "ACTIVE_REVIEW", "L-008", 2400000000.0),
    ("M-850", "Weil Privacy Pro Global DPA & EU AI Act Compliance Playbook", "C-100", "Cybersecurity, Privacy & AI", "ACTIVE", "L-008", 75000000.0),
    ("M-801", "Apex $750M Term Loan B, $200M RCF & ISDA Derivatives", "C-100", "Banking & Leveraged Finance", "EXECUTED", "L-004", 1450000000.0),
    ("M-902", "Strategic M&A Portfolio (Falcon $1.15B, Horizon $820M, Tokyo Swap)", "C-800", "Mergers & Acquisitions", "CLOSED_PRECEDENT", "L-002", 3870000000.0),
    ("M-703", "Global Commercial Real Estate & Campus Leases (Hudson Yards / SV)", "C-700", "Real Estate & Infrastructure", "EXECUTED", "L-005", 693500000.0),
    ("M-605", "Enterprise AI SaaS, 5G/6G Patent Cross-License & MIT Quantum Tech", "C-100", "IP & Technology Transactions", "EXECUTED", "L-005", 173000000.0),
    ("M-504", "Turnaround CEO Employment & Project Helios Retention Pool", "C-100", "Executive Compensation & Benefits", "EXECUTED", "L-001", 43455000.0),
    ("M-999", "Project Omega Hostile Takeover Defense (Restricted)", "C-400", "Restructuring / Hostile M&A", "WALL_RESTRICTED", "L-006", 4200000000.0),
]

DOCUMENTS_CATALOG = [
    # 9 Core Seeded + 1 Restricted Document (with DOC-M999-01 kept for Ethical Wall testing)
    ("DOC-M109-01", "M-109", "Mutual Non-Disclosure & Standstill Agreement (FormSpec v06)", "Mutual NDA", "Weil, Gotshal & Manges LLP", "Delaware", "2026-07-01", "DOC-M109-01_M109_Mutual_Non_Disclosure_Agreement_FormSpec_v06.pdf", 4, "iManage-v06.0"),
    ("DOC-M215-01", "M-215", "Kestrel Semiconductor Stock Purchase Agreement ($1.65B)", "Purchase Agreement", "Weil / Kirkland & Ellis", "Delaware", "2025-11-12", "DOC-M215-01_M215_Project_Titan_Merger_Agreement_Executed.pdf", 6, "iManage-v18.4"),
    ("DOC-M331-01", "M-331", "Agreement and Plan of Merger (Apex / Brightwater Corp. $2.4B)", "Merger Agreement", "Weil, Gotshal & Manges LLP", "Delaware", "2026-09-28", "DOC-M331-01_M331_Brightwater_Merger_Agreement_Executed.pdf", 8, "iManage-v14.2"),
    ("DOC-M331-02", "M-331", "Opposing Counsel Redline Summary (Skadden Draft v4 vs Weil v3)", "Redline Markup", "Skadden, Arps, Slate, Meagher & Flom LLP", "Delaware", "2026-10-08", "DOC-M331-02_M331_Opposing_Counsel_Redline_Summary.pdf", 5, "iManage-v15.0-RL"),
    ("DOC-M331-03", "M-331", "Indemnity Escrow Agreement (Citibank N.A. $18,000,000)", "Escrow Agreement", "Weil / Citibank Legal", "New York", "2026-09-28", "DOC-M331-03_M331_Indemnity_Escrow_Agreement_Citibank.pdf", 5, "iManage-v09.1"),
    ("DOC-M331-04", "M-331", "Section 338(h)(10) Tax Allocation Rider & Gross-Up", "Tax Rider", "Weil Tax Practice", "Delaware", "2026-10-04", "DOC-M331-04_M331_Tax_Allocation_Rider_Draft.pdf", 4, "iManage-v04.3"),
    ("DOC-M402-01", "M-402", "Senior Secured First-Lien Credit Agreement ($850M Apollo)", "Credit Agreement", "Weil / Latham & Watkins", "New York", "2026-07-15", "DOC-M402-01_M402_Apollo_Credit_Agreement_vFinal.pdf", 7, "iManage-v11.0"),
    ("DOC-M518-01", "M-518", "Vanguard Infrastructure Membership Interest Purchase Agreement ($3.1B)", "Purchase Agreement", "Weil / Simpson Thacher", "Delaware", "2026-03-04", "DOC-M518-01_M518_Project_Vanguard_SPA_Executed.pdf", 6, "iManage-v22.1"),
    ("DOC-M999-01", "M-999", "Project Omega Confidential Poison Pill & White Knight Term Sheet", "Restructuring Term Sheet", "Weil Restructuring Group", "Delaware", "2026-09-01", "DOC-M999-01_Project_Omega_Restricted.pdf", 5, "iManage-v01.0-WALL"),

    # 18 Scaled Commercial, Finance, M&A, Real Estate, Tech & Executive PDFs
    ("DOC-FIN-01", "M-801", "Senior Secured Term Loan B Credit Agreement ($750M Citigroup)", "Credit Agreement", "Weil / Cahill Gordon", "New York", "2026-05-12", "DOC-FIN-01_Term_Loan_B_Credit_Agreement_Citigroup_Executed.pdf", 5, "iManage-v12.0"),
    ("DOC-FIN-02", "M-801", "Revolving Credit Agreement ($200M Multi-Currency JPMorgan)", "Credit Agreement", "Weil / Davis Polk", "New York", "2026-06-18", "DOC-FIN-02_Revolving_Credit_Facility_JPMorgan_Executed.pdf", 4, "iManage-v08.2"),
    ("DOC-FIN-03", "M-801", "First Lien / Second Lien Subordinated Intercreditor Agreement ($950M)", "Intercreditor Agreement", "Weil / Milbank", "New York", "2026-05-14", "DOC-FIN-03_Subordinated_Intercreditor_Agreement_Executed.pdf", 4, "iManage-v06.4"),
    ("DOC-MA-01", "M-902", "Asset Purchase Agreement — Falcon Aerospace Avionics Division ($1.15B)", "Asset Purchase Agreement", "Weil / Cravath", "Delaware", "2026-07-20", "DOC-MA-01_Asset_Purchase_Agreement_Falcon_Aerospace_Executed.pdf", 5, "iManage-v16.1"),
    ("DOC-MA-02", "M-902", "Stock Purchase Agreement — Horizon Health Systems Corp. ($820M)", "Stock Purchase Agreement", "Weil / Ropes & Gray", "Delaware", "2026-08-04", "DOC-MA-02_Stock_Purchase_Agreement_Horizon_Health_Executed.pdf", 4, "iManage-v13.0"),
    ("DOC-MA-03", "M-902", "International Joint Venture Agreement — Oncology Gene Therapy JV ($500M)", "Joint Venture Agreement", "Weil / Freshfields", "Delaware", "2026-03-15", "DOC-MA-03_Joint_Venture_Agreement_BioTech_Pfizer_Executed.pdf", 4, "iManage-v09.5"),
    ("DOC-MA-04", "M-902", "Cross-Border Share Exchange Agreement — Apex Semi / Tokyo Microsystems ($1.4B)", "Share Exchange Agreement", "Weil / Nagashima Ohno", "Singapore / ICC", "2026-04-22", "DOC-MA-04_Cross_Border_Share_Swap_Tokyo_Electron_Apex.pdf", 4, "iManage-v10.2"),
    ("DOC-RE-01", "M-703", "Triple Net (NNN) Master Commercial Lease — 50 Hudson Yards ($185M)", "Commercial Lease", "Weil / Fried Frank", "New York", "2026-02-01", "DOC-RE-01_Triple_Net_Lease_Hudson_Yards_Tower_Executed.pdf", 4, "iManage-v07.1"),
    ("DOC-RE-02", "M-703", "Long-Term Ground Lease — 42-Acre Mountain View R&D Campus ($420M)", "Ground Lease", "Weil / Gibson Dunn", "California", "2026-01-10", "DOC-RE-02_Ground_Lease_Silicon_Valley_Campus_Executed.pdf", 4, "iManage-v05.8"),
    ("DOC-RE-03", "M-703", "Industrial Facility Lease — Dallas Global Logistics Center ($64M)", "Industrial Lease", "Weil Real Estate", "Texas", "2026-03-01", "DOC-RE-03_Industrial_Logistics_Center_Lease_Dallas_Executed.pdf", 4, "iManage-v04.2"),
    ("DOC-RE-04", "M-703", "Office Sublease Agreement — Domain Tower II Austin Campus ($24.5M)", "Sublease Agreement", "Weil Real Estate", "Texas", "2026-04-10", "DOC-RE-04_Commercial_Sublease_Agreement_Austin_Campus.pdf", 4, "iManage-v03.9"),
    ("DOC-TECH-01", "M-605", "Master Cloud Services Agreement — Palantir / DataMesh Foundry AI ($38M)", "SaaS Agreement", "Weil Technology & IP", "New York", "2026-07-01", "DOC-TECH-01_Master_SaaS_Agreement_Palantir_Foundry_Executed.pdf", 4, "iManage-v11.3"),
    ("DOC-TECH-02", "M-605", "Patent Cross-License & FRAND Royalty Agreement — 5G/6G Baseband ($120M)", "Patent Cross-License", "Weil Patent & IP", "California", "2026-06-11", "DOC-TECH-02_Patent_Cross_License_Agreement_Qualcomm_Apex.pdf", 4, "iManage-v08.7"),
    ("DOC-TECH-03", "M-605", "Exclusive Patent & Technology Commercialization License — MIT Quantum Optics", "Tech Transfer License", "Weil / MIT Tech Licensing", "Massachusetts", "2026-02-18", "DOC-TECH-03_Exclusive_Technology_Transfer_MIT_MediaLab.pdf", 4, "iManage-v06.1"),
    ("DOC-EMP-01", "M-504", "Executive Employment Agreement — Chief Executive Officer (Dr. Helena Vance)", "Employment Agreement", "Weil Executive Comp", "Delaware", "2026-01-05", "DOC-EMP-01_Executive_Employment_Agreement_Turnaround_CEO.pdf", 4, "iManage-v05.0"),
    ("DOC-EMP-02", "M-504", "Project Helios Key Employee Retention Incentive Pool ($30M)", "Retention Agreement", "Weil Executive Comp", "Delaware", "2026-08-20", "DOC-EMP-02_Key_Employee_Retention_Incentive_Pool_Executed.pdf", 4, "iManage-v04.1"),
    ("DOC-DERIV-01", "M-801", "2002 ISDA Master Agreement Schedule — Currency & Rate Swaps ($500M)", "ISDA Schedule", "Weil Derivatives", "New York", "2026-07-15", "DOC-DERIV-01_ISDA_Master_Agreement_Schedule_Goldman_Apex.pdf", 4, "iManage-v07.4"),
    ("DOC-COMM-01", "M-331", "Exclusive 3nm Silicon Wafer Fabrication & Supply Agreement (TSMC $450M)", "Foundry Supply Agreement", "Weil Commercial", "Delaware", "2026-05-30", "DOC-COMM-01_Exclusive_Foundry_Supply_Agreement_TSMC_Apex.pdf", 4, "iManage-v09.0"),

    # 4 New Weil Oct 13 Specialized App PDFs (FundGen, FundHQ, HSR Second Request, Weil Privacy Pro)
    ("DOC-FUND-01", "M-610", "Weil FundGen — Apex Flagship Buyout Fund VIII Limited Partnership Agreement ($12.5B)", "Private Funds LPA", "Weil Private Funds (FundGen)", "Delaware", "2026-09-15", "DOC-FUND-01_Weil_FundGen_Flagship_Buyout_Fund_VIII_LPA.pdf", 5, "FundGen-v8.4"),
    ("DOC-FUND-02", "M-610", "Weil FundHQ — Sovereign Wealth & Public Pension LP MFN Side Letter Compendium", "MFN Side Letter Compendium", "Weil Private Funds (FundHQ)", "Delaware", "2026-09-18", "DOC-FUND-02_Weil_FundHQ_Sovereign_LP_MFN_Side_Letter_Compendium.pdf", 4, "FundHQ-v4.2"),
    ("DOC-HSR-01", "M-720", "Hart-Scott-Rodino (HSR) Second Request Market Share & HHI Economic Filing", "HSR Antitrust Filing", "Weil Antitrust Practice", "Federal / Clayton Act", "2026-10-02", "DOC-HSR-01_Hart_Scott_Rodino_Second_Request_Market_Share_Filing.pdf", 4, "iManage-HSR-v3.1"),
    ("DOC-PRIV-01", "M-850", "Weil Privacy Pro ('Legal Legos') — Global DPA & EU AI Act Modular Playbook", "Global DPA Playbook", "Weil Cyber, Data & Privacy", "GDPR / CCPA / EU AI Act", "2026-10-05", "DOC-PRIV-01_Weil_Privacy_Pro_Global_DPA_Modular_Playbook.pdf", 4, "PrivacyPro-v6.0"),

    # 4 Multimodal Visual Chart, Diagram & Scanned Signature Files (corpus/charts_and_images/)
    ("DOC-CHART-01", "M-331", "Visual Chart: Brightwater LTM Adjusted EBITDA Bridge ($145M->$175M) & 13.7x EV Waterfall", "Visual Chart & Waterfall", "Weil M&A Financial Advisory", "Delaware", "2026-09-28", "DOC-CHART-01_Brightwater_EBITDA_Bridge_and_Valuation_Waterfall.pdf", 1, "Multimodal-Chart-v1"),
    ("DOC-DIAG-01", "M-402", "Visual Diagram: Apex Global Corporate Structure & Sec. 7.04 J.Crew Blocker Firewall", "Corporate Org Diagram", "Weil Banking & Finance", "New York", "2026-07-15", "DOC-DIAG-01_Apex_Global_Corporate_Org_Structure_and_Unrestricted_Subs.pdf", 1, "Multimodal-Diag-v1"),
    ("DOC-SCAN-01", "M-331", "Scanned Exhibit: Executed Escrow Signature Page & Citibank $18M Wire Instructions", "Scanned Signature & Wire", "Weil / Citibank Escrow", "New York", "2026-09-28", "DOC-SCAN-01_Executed_Escrow_Signature_Page_and_Wire_Exhibit.png", 1, "Multimodal-Scan-v1"),
    ("DOC-CHART-02", "M-610", "Visual Chart: FundHQ LP Commitment Tiers vs. Net Management Fee Discount Curve", "Visual Fee Curve Chart", "Weil Private Funds (FundHQ)", "Delaware", "2026-09-18", "DOC-CHART-02_Private_Funds_LP_Fee_Discount_Curve.png", 1, "Multimodal-Chart-v2"),

    # 8 OpenXML Word (.docx) Contracts & Tracked-Change Redlines (corpus/docx/)
    ("DOC-KESTREL-01", "M-331", "Halvorsen / Brightwater Master Commercial Supply Agreement (.docx)", "Word Contract (.docx)", "Weil Diligence Team", "Delaware", "2026-10-08", "01_Supply_Agreement_Halvorsen_Brightwater.docx", 4, "Word-v1.2"),
    ("DOC-KESTREL-02", "M-331", "Quillfeather / Ostrander Enterprise Core Software License (.docx)", "Word Contract (.docx)", "Weil Diligence Team", "New York", "2026-10-08", "02_Software_License_Quillfeather_Ostrander.docx", 3, "Word-v2.0"),
    ("DOC-KESTREL-03", "M-331", "Corvane Joint Venture Shareholders Agreement (.docx)", "Word Contract (.docx)", "Weil Diligence Team", "Delaware", "2026-10-08", "03_Shareholders_Agreement_Corvane_JV.docx", 3, "Word-v3.1"),
    ("DOC-KESTREL-04", "M-331", "Northgate / Pellucid Heavy Machinery & Server Equipment Lease (.docx)", "Word Contract (.docx)", "Weil Diligence Team", "New York", "2026-10-08", "04_Equipment_Lease_Northgate_Pellucid.docx", 3, "Word-v1.0"),
    ("DOC-KESTREL-05", "M-331", "Saltmarsh / Kiyota Exclusive APAC Distribution Agreement (.docx)", "Word Contract (.docx)", "Weil Diligence Team", "England & Wales", "2026-10-08", "05_Distribution_Agreement_Saltmarsh_Kiyota.docx", 3, "Word-v1.4"),
    ("DOC-KESTREL-06", "M-331", "Ferrous / Albright Professional Transition Services Agreement (.docx)", "Word Contract (.docx)", "Weil Diligence Team", "Delaware", "2026-10-08", "06_Services_Agreement_Ferrous_Albright.docx", 3, "Word-v2.2"),
    ("DOC-M331-V3-DOCX", "M-331", "Brightwater Merger Agreement — Weil Buyer Draft v3 Baseline (.docx)", "Word Merger Draft (.docx)", "Weil, Gotshal & Manges LLP", "Delaware", "2026-09-28", "07_M331_Brightwater_Merger_Agreement_Weil_v3.docx", 4, "Word-v3.0"),
    ("DOC-M331-V4-REDLINE-DOCX", "M-331", "Brightwater Merger Agreement — Skadden Counterparty v4 Tracked-Changes Redline (.docx)", "Word Redline (<w:del>/<w:ins>)", "Skadden, Arps, Slate, Meagher & Flom LLP", "Delaware", "2026-10-08", "08_M331_Brightwater_Merger_Agreement_Skadden_v4_Redline.docx", 4, "Word-v4.0-RL"),

    # 4 Partner Emails (.eml) & Deal Closing Calendar Conflict (.ics) (corpus/emails_and_calendar/)
    ("EM-9901", "M-331", "Unfiled Tax Partner Email: Section 338(h)(10) Election & $14.2M Escrow Holdback (.eml)", "Partner Email (.eml)", "Marcus Thorne (Weil Tax)", "IRC Sec. 338(h)(10)", "2026-10-07", "EM-9901_Unfiled_Tax_Email_Section_338h10_Election.eml", 1, "Exchange-EML"),
    ("EM-9902", "M-331", "M&A Partner Strategy Email: Reject Skadden v4 Section 8.02(b) Redline (.eml)", "Partner Email (.eml)", "David Vance (Weil M&A)", "Delaware", "2026-10-08", "EM-9902_Skadden_v4_Redline_Reject_Strategy.eml", 1, "Exchange-EML"),
    ("EM-9903", "M-999", "Intapp Compliance Alert: Ethical Wall WALL-999 Enforced on Project Omega (.eml)", "Compliance Alert (.eml)", "Intapp Risk Engine", "Firm Compliance", "2026-10-09", "EM-9903_Intapp_Wall_Alert_Project_Omega_M999.eml", 1, "Intapp-EML"),
    ("CAL-101", "M-331", "Deal Closing Board Call vs. FTC HSR Second Request Hearing Conflict (.ics)", "Calendar Conflict (.ics)", "Weil Deal Coordinator", "FTC / Delaware", "2026-10-16", "CAL-101_Closing_Board_Call_and_FTC_HSR_Conflict.ics", 1, "Calendar-ICS"),
]


CURATED_CLAUSES = [
    # Core 10 Clauses (Preserving exact IDs used by Weil Legal Grid UI & Eval Suite)
    ("CL-M331-INDEM", "DOC-M331-01", "M-331", "Indemnification & Survival Cap", "Section 8.02(b) & 8.04", 2, "0.75% ($18,000,000)", "True Deductible (0.50% / $12.0M)", "18 Months (72-Mo Fundamental)", "Full Double Materiality Scrape; Intentional Fraud Uncapped",
     "Brightwater Merger Agreement sets a 0.75% ($18.0M) General Indemnity Cap above a 0.50% ($12.0M) True Deductible Basket with 18-month survival and Full Double Materiality Scrape.",
     "Section 8.02(b) Cap and Deductible Basket: Seller shall have no liability under Section 8.02(a) until the aggregate amount of all Losses exceeds $12,000,000 (0.50% of Enterprise Value) (the 'Deductible Basket'), after which Seller shall be liable only for Losses in excess of the Deductible Basket up to an aggregate Indemnity Cap equal to $18,000,000 (0.75% of Enterprise Value). For purposes of both determining breach and calculating Losses, all 'Material Adverse Effect' and 'material' qualifications shall be disregarded (Full Double Materiality Scrape).",
     "Weil, Gotshal & Manges LLP", "Delaware", '{"page":2,"x":8,"y":24,"w":84,"h":22}'),

    ("CL-M331-MAE", "DOC-M331-01", "M-331", "Material Adverse Effect (MAE) & Disproportionate Impact", "Section 1.01 & 7.02(c)", 1, "15.0% Peer EBITDA Threshold", "Disproportionate Impact Carve-Back", "Closing Condition", "Excludes GAAP & macro industry shifts unless >15% EBITDA hit",
     "Company MAE excludes semiconductor industry cyclicality unless Brightwater suffers a disproportionate impact exceeding 15% of Consolidated Adjusted EBITDA relative to peers.",
     "Section 1.01 'Company Material Adverse Effect' means any change, event, or occurrence that has a material adverse effect on the business, results of operations, or financial condition of the Company and its Subsidiaries, taken as a whole; provided, however, that none of the following shall constitute a Company Material Adverse Effect: (i) changes in GAAP or Delaware law, (ii) industry-wide semiconductor supply constraints, except to the extent such changes disproportionately impact the Company by more than 15% of Consolidated Adjusted EBITDA compared to peer companies.",
     "Weil, Gotshal & Manges LLP", "Delaware", '{"page":1,"x":8,"y":52,"w":84,"h":20}'),

    ("CL-M331-REDLINE", "DOC-M331-02", "M-331", "Opposing Counsel Redline — Basket & R&W Recourse", "Redline Sec. 8.02(b) (Skadden v4 vs Weil v3)", 1, "0.25% ($6,000,000) [Skadden Markup]", "True Deductible Raised to 0.85% ($20.4M)", "12 Months [Cut from 18 Months]", "Single Scrape (Damages Only — Prong 1 Deleted)",
     "Skadden v4 redline cuts Indemnity Cap from 0.75% ($18M) to 0.25% ($6M), raises Deductible Basket to 0.85% ($20.4M), cuts survival to 12 months, and deletes Prong 1 of Double Scrape.",
     "REDLINE COMPARISON [Skadden Draft v4 vs. Weil Draft v3]: In Section 8.02(b), Opposing Counsel (Skadden) struck the $18,000,000 (0.75%) Indemnity Cap and inserted $6,000,000 (0.25% R&W Policy Retention Split), while increasing the Deductible Basket from 0.50% ($12.0M) to 0.85% ($20.4M), cutting general survival from 18 months to 12 months, and deleting the first prong (breach determination) of the Double Materiality Scrape.",
     "Skadden, Arps, Slate, Meagher & Flom LLP", "Delaware", '{"page":1,"x":8,"y":30,"w":84,"h":24}'),

    ("CL-M331-ESCROW", "DOC-M331-03", "M-331", "Indemnity Escrow Release & Joint Instruction", "Section 4(a)-(c)", 1, "$18,000,000 Escrow Reserve", "Citibank N.A. Joint Instruction", "18 Months + 10-BD Objection Window", "Pending Claim Holdback Reserve",
     "Citibank N.A. holds $18,000,000 Indemnity Escrow for 18 months; automatic release on first Business Day after expiration less Pending Claim Reserves unless objected within 10 Business Days.",
     "Section 4(b) Release of Escrow Fund: On the first Business Day following the eighteen (18) month anniversary of the Closing Date (the 'Escrow Termination Date'), Escrow Agent (Citibank, N.A.) shall disburse to Seller Representative the remaining balance of the $18,000,000 Indemnity Escrow Fund, less the aggregate amount of all Pending Claim Reserves specified in Buyer Claim Notices delivered prior to 5:00 p.m. Eastern Time on the Escrow Termination Date, unless Seller delivers a written Claim Objection Notice within ten (10) Business Days.",
     "Weil / Citibank Legal", "New York", '{"page":1,"x":8,"y":44,"w":84,"h":20}'),

    ("CL-M331-TAX", "DOC-M331-04", "M-331", "Section 338(h)(10) Election & Tax Gross-Up Cap", "Section 2.01 & 3.04 (Tax Rider)", 1, "$14,200,000 Model ($9.5M Skadden Cap)", "First-Dollar Uncapped Pre-Closing Tax", "Statute of Limitations + 60 Days", "Bypasses General Deductible Basket & Cap",
     "Pre-Closing Taxes and Section 338(h)(10) election adjustments are indemnified on a first-dollar basis for Statute of Limitations + 60 days; Weil models $14.2M step-up exposure vs Skadden $9.5M cap.",
     "Section 3.04 Tax Indemnification Carve-Out: Seller's obligation to indemnify Buyer for Pre-Closing Taxes and Section 338(h)(10) Election adjustments shall be on a first-dollar basis, shall not be subject to the Deductible Basket or the General Indemnity Cap in Section 8.02(b), and shall survive until sixty (60) days following the expiration of the applicable federal or state statute of limitations. Section 338(h)(10) ordinary-to-capital-gains Tax Gross-Up is modeled at $14,200,000 by Weil Tax vs $9,500,000 in Skadden v4.",
     "Weil Tax Practice", "Delaware", '{"page":1,"x":8,"y":38,"w":84,"h":20}'),

    ("CL-M215-INDEM", "DOC-M215-01", "M-215", "Indemnification & Survival Cap", "Section 9.01(c) (Kestrel Carve-Out Precedent)", 2, "0.50% ($8,250,000)", "True Deductible (0.50% / $8.25M)", "15 Months", "Full Double Materiality Scrape",
     "Kestrel Semiconductor $1.65B carve-out precedent closed with 0.50% ($8.25M) Indemnity Cap, 0.50% True Deductible Basket, 15-month survival, and Full Double Materiality Scrape.",
     "Section 9.01(c) Kestrel Semiconductor Precedent Cap: Seller's aggregate liability for breaches of Non-Fundamental Representations shall not exceed $8,250,000 (0.50% of Base Purchase Price) above a 0.50% ($8,250,000) True Deductible Basket, and shall survive for fifteen (15) months following Closing. Includes Full Double Materiality Scrape for both breach determination and Loss calculation.",
     "Weil / Kirkland & Ellis", "Delaware", '{"page":2,"x":8,"y":24,"w":84,"h":20}'),

    ("CL-M518-INDEM", "DOC-M518-01", "M-518", "Indemnification & Survival Cap", "Section 10.03(a) (Vanguard Infrastructure JV)", 2, "1.00% ($31,000,000)", "Tipping Basket (0.35% / $10.85M)", "24 Months (72-Mo Environmental)", "Breach-Only Materiality Scrape",
     "Vanguard Infrastructure $3.1B JV precedent sets 1.00% ($31.0M) Indemnity Cap, 0.35% ($10.85M) Tipping Basket (dollar-one recovery once tipped), and 24-month survival.",
     "Section 10.03(a) Vanguard JV Indemnity: Once aggregate Losses exceed the 0.35% Tipping Threshold ($10,850,000), Seller shall indemnify Buyer from dollar one up to the 1.00% Aggregate Cap ($31,000,000) for a survival period of twenty-four (24) months (72 months for Environmental representations). Applies Breach-Only Materiality Scrape.",
     "Weil / Simpson Thacher", "Delaware", '{"page":2,"x":8,"y":24,"w":84,"h":20}'),

    ("CL-M402-COV", "DOC-M402-01", "M-402", "Financial Covenants & J.Crew / Chewy Blocker", "Section 6.08 & 7.11", 1, "4.50x Max Total Net Leverage", "20% EBITDA Synergy Add-Back Cap", "Term of Credit Facility", "Strict J.Crew / Serta / Chewy IP Blocker",
     "Apollo $850M Credit Facility prohibits transferring Material IP to Unrestricted Subsidiaries (J.Crew / Chewy blocker) and caps Total Net Leverage at 4.50x with 20% EBITDA add-back cap.",
     "Section 6.08(d) Material Intellectual Property Blocker: Notwithstanding anything to the contrary in this Agreement, neither the Borrower nor any Restricted Subsidiary may transfer, assign, or exclusively license any Material Intellectual Property to any Unrestricted Subsidiary, nor may any Subsidiary holding Material Intellectual Property be designated as an Unrestricted Subsidiary (Strict J.Crew / Serta / Chewy Protection). Section 7.11 Financial Covenant: Total Net Leverage Ratio shall not exceed 4.50x, with restructuring EBITDA add-backs capped at 20% of LTM Consolidated EBITDA.",
     "Weil / Latham & Watkins", "New York", '{"page":1,"x":8,"y":46,"w":84,"h":22}'),

    ("CL-M109-NDA", "DOC-M109-01", "M-109", "Standstill, Fall-Away & Non-Solicitation", "Section 5 & Section 7", 1, "2.0% Voting Equity Ceiling", "Automatic Fall-Away on 3P 50% Sale", "18 Months Standstill", "No Residuals Clause; Mandatory Clean Team",
     "FormSpec v06 Mutual NDA imposes an 18-month standstill (2.0% equity cap) with automatic Fall-Away upon a third-party 50% acquisition announcement, and excludes Residuals.",
     "Section 7 Standstill & Fall-Away: For a period of eighteen (18) months from the Effective Date, Recipient shall not acquire beneficial ownership of more than 2.0% of the Company's voting securities; provided that the restrictions of this Section 7 shall automatically terminate ('Fall-Away') upon the Company entering into a definitive agreement with a third party providing for a merger or sale of 50% or more of its consolidated assets. Residuals clause excluded; Clean Team protocol mandatory.",
     "Weil, Gotshal & Manges LLP", "Delaware", '{"page":1,"x":8,"y":40,"w":84,"h":20}'),

    ("CL-M999-RESTRICTED", "DOC-M999-01", "M-999", "Hostile Defense Poison Pill & Break-Up Fee (Intapp Walled)", "Section 4.02 (Project Omega Restricted)", 1, "15% Flip-In Poison Pill Trigger", "4.25% ($178.5M) White Knight Break Fee", "12 Months Rights Plan", "INTAPP WALL-999 EXCLUDED FOR L-001",
     "RESTRICTED MATTER M-999: Shareholder Rights Plan flip-in triggered at 15% hostile accumulation; screened from Sarah Jenkins (L-001) by Intapp Wall WALL-999.",
     "Section 4.02 Flip-In Poison Pill & White Knight Matching Right: Upon any Acquiring Person obtaining beneficial ownership of 15.0% or more of Project Omega common stock without Board approval, each Right entitles non-acquiring holders to purchase shares at a 50% discount. Screened under Intapp Ethical Wall WALL-999.",
     "Weil Restructuring Group", "Delaware", '{"page":1,"x":8,"y":30,"w":84,"h":20}'),

    # New Clauses for Weil Oct 13 Apps: FundGen (DOC-FUND-01), FundHQ (DOC-FUND-02), HSR (DOC-HSR-01), Privacy Pro (DOC-PRIV-01)
    ("CL-FUND01-MGMTFEE", "DOC-FUND-01", "M-610", "Management Fee & Post-Investment Step-Down (FundGen)", "Section 4.02", 1, "1.75% Inv. Period -> 1.25% Step-Down", "100% Transaction & Monitoring Fee Offset", "10-Year Fund Term (5-Yr Inv. Period)", "Zero Double-Dipping on Portfolio Fees",
     "FundGen Flagship Buyout Fund VIII ($12.5B) charges 1.75% Management Fee on commitments during the 5-year Investment Period, stepping down to 1.25% on net invested capital thereafter with 100% fee offset.",
     "SECTION 4.02 MANAGEMENT FEE & POST-INVESTMENT PERIOD STEP-DOWN: During the five-year Investment Period, the Management Fee shall equal 1.75% per annum of Aggregate Capital Commitments ($12,500,000,000). Following the expiration or termination of the Investment Period, the Management Fee shall step down to 1.25% per annum of net invested capital in unrealized Portfolio Companies, with 100% fee offset for transaction, monitoring, and broken-deal fees.",
     "Weil Private Funds (FundGen)", "Delaware", '{"page":1,"x":8,"y":28,"w":84,"h":18}'),

    ("CL-FUND01-WATERFALL", "DOC-FUND-01", "M-610", "European Distribution Waterfall, 8% Hurdle & 30% Clawback Escrow", "Section 6.03 & Section 9.04", 2, "20% Carried Interest / 8.0% Hurdle", "European Whole-Fund Return of Capital", "30% Carry Escrow Clawback Guarantee", "100% GP Catch-Up after 8.0% Preferred Return",
     "European waterfall returns 100% of contributed capital plus 8.0% compounded Preferred Return Hurdle to LPs before 100% GP Catch-Up and 80/20 Carry split, backed by a 30% Carry Escrow Clawback.",
     "SECTION 6.03 EUROPEAN DEAL-BY-DEAL DISTRIBUTION WATERFALL & 8.0% HURDLE: Distributable Proceeds shall be allocated: (a) First, 100% to Limited Partners until cumulative distributions equal 100% of aggregate contributed capital plus an 8.0% per annum compounded Preferred Return Hurdle; (b) Second, 100% GP Catch-Up to the General Partner until the General Partner has received 20.0% of cumulative net profits; and (c) Thereafter, 80.0% to Limited Partners and 20.0% to the General Partner as Carried Interest, backed by a 30.0% Carried Interest Clawback Escrow Reserve at Citibank, N.A.",
     "Weil Private Funds (FundGen)", "Delaware", '{"page":2,"x":8,"y":22,"w":84,"h":22}'),

    ("CL-FUND02-MFN", "DOC-FUND-02", "M-610", "FundHQ Sovereign LP MFN Matrix & 25 bps Anchor Fee Discount", "Section 1.01 & Section 2.04", 1, "25 bps Fee Discount (1.50% Net Fee)", "$250,000,000 Anchor LP Commitment Tier", "30-Day Post-Closing MFN Election", "50% Zero-Fee Co-Investment ROFO",
     "FundHQ Sovereign LP Side Letter Compendium grants Tier-1 Anchor LPs (>=$250M) a 25 bps Management Fee discount (to 1.50%, or 1.35% for >=$500M) and 50% zero-fee/zero-carry Co-Investment ROFO.",
     "SECTION 2.04 ANCHOR LP 25 BPS MANAGEMENT FEE DISCOUNT & CO-INVEST ROFO: Each Tier-1 Anchor LP committing $250,000,000 or more receives a twenty-five basis point (25 bps) Management Fee discount (reducing the headline rate from 1.75% to 1.50% during the Investment Period, or 1.35% for commitments >= $500,000,000) and a contractual Right of First Offer (ROFO) for zero-fee, zero-carry co-investment opportunities up to 50% of its pro-rata commitment.",
     "Weil Private Funds (FundHQ)", "Delaware", '{"page":1,"x":8,"y":32,"w":84,"h":20}'),

    ("CL-FUND02-ESG-FOIA", "DOC-FUND-02", "M-610", "Sovereign LP FOIA Carve-Out & ESG Weapons/Coal Excuse Right", "Section 3.02 & Section 4.05", 2, "5.0% Revenue ESG Excuse Threshold", "Statutory FOIA / Sunshine Law Safe Harbor", "Permanent LP Excuse Right", "Excludes Thermal Coal & Cluster Munitions",
     "Public Pension LPs receive a statutory FOIA disclosure safe harbor for fund-level IRR/TVPI/DPI, and Sovereign LPs are excused from drawdowns for portfolio companies with >5% revenue from thermal coal or controversial weapons.",
     "SECTION 4.05 ESG, THERMAL COAL & CONTROVERSIAL WEAPONS EXCUSE RIGHT: Sovereign and Endowment Limited Partners shall be excused from funding any Drawdown Notice for a Portfolio Company that derives more than 5.0% of gross revenue from thermal coal extraction, cluster munitions, biological/chemical weapons, or non-compliant deforestation operations.",
     "Weil Private Funds (FundHQ)", "Delaware", '{"page":2,"x":8,"y":40,"w":84,"h":18}'),

    ("CL-HSR01-HHI", "DOC-HSR-01", "M-720", "HSR Second Request 3nm EUV Market Share & HHI Concentration", "Item 4(c)/(d) & Section 2.02", 1, "Post-HHI 2,490 (Delta +350 pts)", "26.5% Combined Foundry Share", "60-Day Timing Agreement (Dec 1, 2026)", "2023 FTC/DOJ Merger Guidelines Threshold (1,800 / +100)",
     "HSR Second Request economic filing calculates Pre-Merger HHI = 2,140 and Post-Merger HHI = 2,490 (Delta = +350) in 3nm EUV Semiconductor Foundry services (Apex 14.5% + Brightwater 12.0% = 26.5%).",
     "SECTION 2.02 HERFINDAHL-HIRSCHMAN INDEX (HHI) MARKET CONCENTRATION ANALYSIS: Pre-Merger Market Shares are TSMC (38.0%), Intel Foundry (21.0%), Apex Global (14.5%), Brightwater Corp. (12.0%), and GlobalFoundries (14.5%). Pre-Merger HHI equals 2,140; Post-Merger Combined Share equals 26.5%; Post-Merger HHI equals 2,490; and HHI Delta equals +350 points.",
     "Weil Antitrust Practice", "Federal / Clayton Act", '{"page":1,"x":8,"y":30,"w":84,"h":20}'),

    ("CL-HSR01-DIVEST", "DOC-HSR-01", "M-720", "Structural Divestiture Remedy — Fab 14 Packaging Line ($310M)", "Section 3.05", 2, "$310,000,000 Fab 14 Divestiture", "Upfront Buyer (SkyWater Technology)", "120 Days Post-Closing Divestiture", "Reduces Net HHI Delta from +350 to +65 pts",
     "To cure Clayton Act Section 7 overlap, Apex proposes divesting Brightwater's Fab 14 Austin packaging line ($310M revenue) to SkyWater Technology within 120 days, reducing net HHI Delta to +65 points.",
     "SECTION 3.05 CONSENT DECREE & STRUCTURAL DIVESTITURE REMEDY (FAB 14): Buyer proposes a clean structural divestiture of Brightwater's legacy 7nm/5nm Metrology & Fab 14 Austin Packaging Line ($310,000,000 revenue) to an FTC-approved upfront buyer (SkyWater Technology) within 120 days of Closing, reducing net HHI Delta to +65 points.",
     "Weil Antitrust Practice", "Federal / Clayton Act", '{"page":2,"x":8,"y":25,"w":84,"h":18}'),

    ("CL-PRIV01-AI-GDPR", "DOC-PRIV-01", "M-850", "Weil Privacy Pro — EU AI Act Audit, SCC Module 2 & Zero-Training", "Module 2 & Module 3", 1, "Zero-AI-Training Mandatory Covenant", "EU SCC Module 2 + FIPS 140-3 CMEK", "5-BD High-Risk AI Audit Inspection", "GDPR Art. 28, CCPA/CPRA & EU AI Act Reg. 2024/1689",
     "Weil Privacy Pro Global DPA prohibits using Controller data/embeddings to train foundation models, incorporates EU SCC Module 2 with CMEK encryption, and mandates 5-BD audit access under the EU AI Act.",
     "MODULE 3 (EU AI ACT HIGH-RISK SYSTEM AUDIT & ZERO-TRAINING COVENANT): Processor warrants that no Controller Data, prompts, embeddings, or telemetry shall be used to train, fine-tune, distill, or evaluate any foundation model or third-party AI system. For High-Risk AI Systems under Regulation (EU) 2024/1689 (EU AI Act), Processor shall maintain immutable human-in-the-loop audit logs, bias evaluations, and technical documentation accessible to Controller upon 5 business days notice.",
     "Weil Cyber, Data & Privacy", "GDPR / CCPA / EU AI Act", '{"page":1,"x":8,"y":42,"w":84,"h":20}'),

    ("CL-PRIV01-BREACH", "DOC-PRIV-01", "M-850", "24-Hour Cyber Incident Notification & $75M Privacy Super-Cap", "Module 4", 2, "$75,000,000 (or 3x Fees) Super-Cap", "First-Dollar Cyber Forensic & Fine Indemnity", "24-Hour Breach Notification SLA", "Stricter than 72-Hour GDPR Statutory Baseline",
     "Processor must notify Controller's CISO within 24 hours of any confirmed Personal Data Breach and indemnify regulatory fines and forensic costs up to a $75,000,000 Data Privacy Super-Cap.",
     "MODULE 4 (24-HOUR CYBER INCIDENT NOTIFICATION & SUPER-CAP INDEMNITY): In the event of any confirmed Personal Data Breach or unauthorized access to Controller's tenant environment, Processor shall notify Controller's Chief Information Security Officer within twenty-four (24) hours of detection and indemnify Controller for regulatory fines, forensic investigation costs, and mandatory credit monitoring up to a 3x Fees or $75,000,000 Data Privacy Super-Cap.",
     "Weil Cyber, Data & Privacy", "GDPR / CCPA / EU AI Act", '{"page":2,"x":8,"y":30,"w":84,"h":18}'),

    # Multimodal Visual Chart, Diagram & Scanned Image Clauses
    ("CL-CHART01-EBITDA", "DOC-CHART-01", "M-331", "Visual Chart: Brightwater EBITDA Bridge & 13.71x Valuation Waterfall", "Exhibit B-1 & Table 1.2", 1, "$175.0M Adj. EBITDA (17.14% Add-Backs)", "$145M GAAP + $18M Synergies + $12M Restruct.", "LTM FY2026 Valuation Baseline", "Complies with 20.0% Credit Agreement Add-Back Cap",
     "Multimodal Bar Chart & Waterfall Table verifying Brightwater's $145M GAAP EBITDA + $18M Synergies + $12M Cleanroom Restructuring = $175M Adjusted EBITDA (13.714x = $2.40B EV).",
     "EXHIBIT B-1 VISUAL BAR CHART & TABLE 1.2 WATERFALL: Reported LTM GAAP EBITDA ($145,000,000) + Pro Forma Cost Synergies (+$18,000,000 / 10.29%) + Cleanroom Restructuring (+$12,000,000 / 6.86%) = Consolidated Adjusted EBITDA of $175,000,000 (combined add-backs = 17.14%, within the 20.0% cap). At 13.714x valuation multiple, Enterprise Value = $2,400,000,000, with $18,000,000 (0.75%) Citibank Indemnity Escrow and $12,000,000 (0.50%) True Deductible Basket.",
     "Weil M&A Financial Advisory", "Delaware", '{"page":1,"x":7.5,"y":14,"w":85,"h":78}'),

    ("CL-DIAG01-JCREW", "DOC-DIAG-01", "M-402", "Visual Diagram: Corporate Org Structure & J.Crew Blocker Firewall", "Exhibit G-2 (Sec. 6.08(d) & Sec. 7.04)", 1, "90% Required Lender Supermajority", "100% First-Lien Restricted Guarantor Ring", "Duration of $750M TLB & $850M Credit", "Blocks Material IP Drop to Apex Cayman IP Holdco",
     "Visual Corporate Org Chart showing Brightwater Corp. (US Patents 11,482,901 & 11,894,220), Apex Silicon Ireland, and Falcon Semi inside the Restricted Guarantor Ring, blocked by a 90% Lender Consent firewall from transferring IP to Apex Cayman IP Holdco Ltd.",
     "EXHIBIT G-2 CORPORATE ORG DIAGRAM & J.CREW FIREWALL: Apex Global Holdings Inc. locks Brightwater Corp. (US Patent 11,482,901 FinFET & US Patent 11,894,220 Quantum Photonics), Apex Silicon Technologies Ltd. (Ireland), and Falcon Semiconductor LLC inside the 100% First-Lien Restricted Guarantor Ring. Section 7.04 (DOC-FIN-01) and Section 6.08(d) (DOC-M402-01) enforce a strict J.Crew / Envision / Chewy Blocker prohibiting any Material IP transfer to Apex Cayman IP Holdco Ltd. (Unrestricted Subsidiary) without 90% Required Lender consent.",
     "Weil Banking & Finance", "New York", '{"page":1,"x":7,"y":16,"w":86,"h":68}'),

    ("CL-SCAN01-WIRE", "DOC-SCAN-01", "M-331", "Scanned Signature Page & Citibank $18M Escrow Wire Instructions", "Exhibit A-1 (Executed Wet-Ink Scan)", 1, "$18,000,000 Escrow + $14.2M Tax Reserve", "Citibank ABA 021000089 / Acct 4098-7721-8834", "Executed Sept 28, 2026 (300 DPI OCR)", "Signed by Dr. Helena Vance, Sarah Jenkins & Arthur Pendelton",
     "Optical OCR extraction of wet-ink executed signature page and Citibank N.A. wire instructions (ABA 021000089, SWIFT CITIUS33XXX, Acct 4098-7721-8834) for the $18,000,000 Indemnity Escrow.",
     "EXHIBIT A-1 EXECUTED ESCROW WIRE & WET-INK SIGNATURE SCAN: Depository Bank: Citibank, N.A. | ABA Fedwire Routing: 021000089 | SWIFT: CITIUS33XXX | Account: 4098-7721-8834 | General Indemnity Escrow Deposit: $18,000,000.00 (0.75% EV per Sec. 8.02(b)) | Section 338(h)(10) Tax Reserve: $14,200,000.00 | Executed in wet ink by Dr. Helena Vance (CEO, Apex Global), Sarah Jenkins (L-001, Weil), David Vance (L-002, Weil), and Arthur Pendelton (MD, Citibank Escrow).",
     "Weil / Citibank Escrow", "New York", '{"page":1,"x":5,"y":14,"w":90,"h":74}'),

    ("CL-CHART02-FEECURVE", "DOC-CHART-02", "M-610", "Visual Chart: FundHQ LP Commitment Tier vs. Management Fee Curve", "FundHQ Visual Schedule 1", 1, "175 bps -> 160 bps -> 150 bps -> 135 bps", "Tiered LP Commitment Matrix ($50M to $500M+)", "5-Yr Inv. Period + Step-Down", "Up to 100% Priority Zero-Fee Co-Invest ROFO",
     "Visual fee discount curve from FundHQ showing headline Management Fee stepping down from 175 bps (<$100M) to 160 bps ($100M+), 150 bps ($250M+ Anchor Sovereign), and 135 bps ($500M+ Mega-Cornerstone).",
     "DOC-CHART-02 FUNDHQ LP FEE DISCOUNT CURVE: Tier 4 (<$100M): 175 bps Inv. / 125 bps Post-Inv.; Tier 3 ($100M-$249M): 160 bps (-15 bps) / 20% Co-Invest ROFO; Tier 2 Anchor Sovereign ($250M-$499M): 150 bps (-25 bps MFN) / 105 bps Post-Inv. / 50% Zero-Fee Co-Invest ROFO; Tier 1 Mega-Cornerstone (>=$500M): 135 bps (-40 bps MFN) / 95 bps Post-Inv. / 100% Priority Co-Invest + LPAC Seat.",
     "Weil Private Funds (FundHQ)", "Delaware", '{"page":1,"x":6,"y":15,"w":88,"h":70}'),

    # 8 Word (.docx) Contracts & Tracked-Change Redline Clauses
    ("CL-KESTREL-01-COC", "DOC-KESTREL-01", "M-331", "Change of Control & 30-Day Notice Termination Right (.docx)", "Section 12.03(a)", 4, "12-Month Fees Liability Cap", "Prior Written Notice (30 Calendar Days)", "45-Day Customer Termination Window", "Zero Termination Penalty; Prorated Prepayment Refund",
     "Halvorsen Master Supply Agreement (.docx) requires 30 days prior written notice of a Supplier Change of Control and grants Customer a 45-day penalty-free termination right.",
     "Section 12.03 Change of Control: In the event of any direct or indirect Change of Control of Supplier, Supplier shall provide at least thirty (30) calendar days prior written notice to Customer. Customer shall have the absolute right to terminate this Agreement immediately without penalty or termination fee upon written notice within forty-five (45) days following receipt of such notification.",
     "Weil Diligence Team", "Delaware", '{"page":4,"x":8,"y":35,"w":84,"h":18}'),

    ("CL-KESTREL-02-COC", "DOC-KESTREL-02", "M-331", "Anti-Assignment & Deemed CoC License Revocation (.docx)", "Section 8.04(b)", 2, "$420,000 Accelerated License Fee", "Strict Licensor Consent (Sole Discretion)", "45 Calendar Days Pre-Closing Notice", "Deemed Assignment Triggers Immediate Termination",
     "Quillfeather Software License (.docx) deems any Licensee Change of Control an attempted assignment requiring sole-discretion Licensor consent, or triggers revocation plus $420,000 accelerated fees.",
     "Section 8.04 Assignment & Deemed Transfer: Neither party may assign or transfer this Agreement without the prior written consent of Licensor. Any merger, consolidation, reorganization, or Change of Control of Licensee shall be deemed an attempted assignment in violation of this Section 8.04, rendering the Enterprise Software License immediately terminable at Licensor's sole discretion, with $420,000 accelerated license fees due.",
     "Weil Diligence Team", "New York", '{"page":2,"x":8,"y":28,"w":84,"h":20}'),

    ("CL-KESTREL-03-COC", "DOC-KESTREL-03", "M-331", "Competitor Change of Control & 1.25x Tag-Along / Redemption (.docx)", "Section 15.02", 3, "1.25x Book Value Forced Buyout", "75% Board Supermajority Approval", "60 Business Days Buyout Closing", "Tag-Along / Drag-Along Trigger on Competitor CoC",
     "Corvane JV Shareholders Agreement (.docx) triggers immediate Tag-Along or 1.25x Book Value forced share redemption if a Founding Shareholder undergoes a Change of Control to a Schedule IV Direct Competitor.",
     "Section 15.02 Competitor Change of Control & Tag-Along: If any Founding Shareholder undergoes a Change of Control in favor of any Entity deemed a 'Direct Competitor' as specified in Schedule IV, the non-transferring shareholders shall have the immediate right to exercise Tag-Along rights or force a redemption of shares at 1.25x Book Value within sixty (60) business days.",
     "Weil Diligence Team", "Delaware", '{"page":3,"x":8,"y":40,"w":84,"h":18}'),

    ("CL-KESTREL-04-COC", "DOC-KESTREL-04", "M-331", "Equipment Lease CoC Default & $1.85M Rent Acceleration (.docx)", "Section 19.01(f)", 2, "$1,850,000 Lease Balance Acceleration", "Lessor Written Consent (Reasonable Discretion)", "15 Calendar Days Post-Closing", "Uncapped Fraud & Environmental Indemnity",
     "Northgate Equipment Lease (.docx) treats an unconsented merger or Change of Control as an Event of Default permitting immediate hardware repossession and $1,850,000 rent acceleration.",
     "Section 19.01(f) Events of Default: Lessee enters into any agreement of merger, consolidation, dissolution or undergoes a Change of Control without the express written consent of Lessor, which consent shall not be unreasonably withheld. Upon such default, Lessor may accelerate the entire remaining aggregate balance of the lease, amounting to $1,850,000, immediately payable in cash.",
     "Weil Diligence Team", "New York", '{"page":2,"x":8,"y":32,"w":84,"h":18}'),

    ("CL-KESTREL-05-COC", "DOC-KESTREL-05", "M-331", "APAC Distribution CoC & 4.0x Interest Coverage Solvency Test (.docx)", "Section 11.02", 2, "4.0x Min Interest Coverage Ratio", "60 Calendar Days Advance Notice Only", "No Termination Right if Solvency Met", "85% Inventory Repurchase if Leverage > 3.5x",
     "Saltmarsh APAC Distribution Agreement (.docx) permits Change of Control upon 60 days notice without Supplier consent provided Distributor delivers an audited pro-forma balance sheet showing >= 4.0x interest coverage.",
     "Section 11.02 Assignment and Change of Ownership: Distributor may effect a corporate reorganization or Change of Control upon sixty (60) days advance notice to Supplier, provided that Distributor delivers an audited pro-forma balance sheet demonstrating an interest coverage ratio of not less than 4.0 to 1.0. If such financial threshold is met, Supplier shall have no right of termination.",
     "Weil Diligence Team", "England & Wales", '{"page":2,"x":8,"y":30,"w":84,"h":18}'),

    ("CL-KESTREL-06-COC", "DOC-KESTREL-06", "M-331", "Transition Services CoC & $25,000 Orderly Transition Fee (.docx)", "Section 7.03", 2, "$500,000 General Cap ($25K Transition Fee)", "15 Business Days Notice on CoC", "Bilateral Termination for Convenience", "Fraud & Willful Misconduct Uncapped",
     "Ferrous / Albright Transition Services Agreement (.docx) allows either party to terminate on 15 business days notice following a Change of Control subject to a $25,000 orderly transition fee.",
     "Section 7.03 Termination on Restructuring: Either party may terminate this Services Agreement upon fifteen (15) business days prior written notice following an announcement or completion of a Change of Control involving an Ethical Wall Conflict of Interest. In the event of such termination, Albright shall be entitled to an orderly transition fee capped at $25,000.",
     "Weil Diligence Team", "Delaware", '{"page":2,"x":8,"y":34,"w":84,"h":18}'),

    ("CL-M331-V3-DOCX-INDEM", "DOC-M331-V3-DOCX", "M-331", "Weil Buyer v3 Word Baseline — 0.75% Cap & Full Double Scrape (.docx)", "ARTICLE VIII · Section 8.02(b)", 4, "0.75% ($18,000,000)", "True Deductible (0.50% / $12.0M)", "18 Months (72-Mo Fundamental)", "Full Double Materiality Scrape (<w:p> Clean Baseline)",
     "Native OpenXML Word (.docx) baseline of Weil Buyer Draft v3 establishing the $18.0M (0.75%) Indemnity Cap, $12.0M (0.50%) True Deductible, 18-month survival, and Full Double Materiality Scrape.",
     "ARTICLE VIII · Section 8.02(b) [WEIL v3 WORD BASELINE]: Seller shall have no liability under Section 8.02(a) until aggregate Losses exceed $12,000,000 (0.50% of Enterprise Value) (True Deductible Basket), after which Seller shall be liable for Losses in excess of the Deductible Basket up to an aggregate Indemnity Cap of $18,000,000 (0.75% of Enterprise Value). For purposes of both determining breach and calculating Losses, all materiality and MAE qualifiers are disregarded (Full Double Materiality Scrape).",
     "Weil, Gotshal & Manges LLP", "Delaware", '{"page":4,"x":8,"y":22,"w":84,"h":20}'),

    ("CL-M331-V4-DOCX-RL", "DOC-M331-V4-REDLINE-DOCX", "M-331", "Skadden v4 OpenXML Tracked-Changes (<w:del>/<w:ins>) Redline (.docx)", "ARTICLE VIII · Section 8.02(b) & 8.04(a)", 4, "STRUCK $18M (0.75%) -> INSERTED $6M (0.25%)", "STRUCK $12M (0.50%) -> INSERTED $20.4M (0.85%)", "STRUCK 18-Mo -> INSERTED 12-Mo", "STRUCK Double Scrape -> INSERTED Damages-Only Scrape",
     "OpenXML Word tracked-changes redline (<w:del> and <w:ins>) showing Skadden v4 striking $18.0M cap / $12.0M basket / Double Scrape and inserting $6.0M cap / $20.4M deductible / Single Damages-Only Scrape.",
     "TRACKED CHANGES (<w:del>/<w:ins>) [Skadden, Arps, Slate, Meagher & Flom LLP]: Seller shall have no liability under Section 8.02(a) until the aggregate amount of all Losses exceeds [STRUCK: $12,000,000 (0.50% of Enterprise Value) True Deductible Basket, up to an aggregate Indemnity Cap equal to $18,000,000 (0.75% of Enterprise Value) with an 18-month survival period] [INSERTED: $20,400,000 (0.85% of Enterprise Value) Increased Deductible, up to an aggregate Seller Indemnity Cap equal to $6,000,000 (0.25% R&W Insurance Retention Split) with a 12-month survival period].",
     "Skadden, Arps, Slate, Meagher & Flom LLP", "Delaware", '{"page":4,"x":8,"y":48,"w":84,"h":24}'),

    # 18 Scaled Commercial, Finance, M&A, Real Estate, Tech & Executive Clauses
    ("CL-FIN01-EBITDA", "DOC-FIN-01", "M-801", "Consolidated Adjusted EBITDA 20% Synergy Add-Back Cap", "Section 1.01", 1, "20.0% Max EBITDA Add-Back Cap", "24-Month Projected Synergy Realization", "Term of $750M TLB Facility", "50% Excess Cash Flow Sweep Step-Down at 3.50x",
     "Citigroup $750M Term Loan B caps pro forma cost savings and synergy add-backs at 20.0% of Consolidated Adjusted EBITDA over a 24-month realization window.",
     "SECTION 1.01 DEFINITIONS & EBITDA ADJUSTMENTS: Consolidated Adjusted EBITDA shall include add-backs for pro forma cost savings and synergies projected by the Borrower in good faith resulting from actions taken or expected to be taken within twenty-four (24) months, capped in the aggregate at twenty percent (20.0%) of Consolidated Adjusted EBITDA for the relevant Four-Quarter Period.",
     "Weil / Cahill Gordon", "New York", '{"page":1,"x":8,"y":28,"w":84,"h":18}'),

    ("CL-FIN01-JCREW", "DOC-FIN-01", "M-801", "J.Crew & Envision Unrestricted Subsidiary IP Drop Blocker", "Section 7.04", 2, "90% Required Lender Supermajority Consent", "$35,000,000 Cross-Default Threshold", "Term of $750M TLB Facility", "Blocks Material IP & Material Customer Contracts",
     "Section 7.04 of the $750M Citigroup TLB prohibits contributing or licensing Material IP or Material Customer Revenue Contracts to any Unrestricted Subsidiary without 90% Lender consent.",
     "SECTION 7.04 J.CREW & ENVISION ASSET DROP BLOCKER: Notwithstanding anything to the contrary in Section 7.02 or 7.05, no Material Intellectual Property or Material Customer Revenue Contracts owned by the Borrower or any Restricted Subsidiary may be contributed, transferred, pledged, or exclusively licensed to any Unrestricted Subsidiary without the consent of the Required Lenders (90% threshold).",
     "Weil / Cahill Gordon", "New York", '{"page":2,"x":8,"y":36,"w":84,"h":18}'),

    ("CL-FIN02-LEVERAGE", "DOC-FIN-02", "M-801", "First Lien Net Leverage Covenant (4.25x -> 4.75x Acquisition Step-Up)", "Section 6.08 & Section 8.01", 1, "4.25:1.00 Max Leverage (4.75x Step-Up)", "$50,000,000 L/C Sublimit", "5-Year Revolving Maturity (2031)", "35% Beneficial Ownership Change of Control Trigger",
     "JPMorgan $200M Revolving Credit Facility sets a 4.25x First Lien Net Leverage covenant (stepping up to 4.75x for 4 quarters after a >$100M acquisition) and a 35% Change of Control default trigger.",
     "SECTION 6.08 FINANCIAL COVENANTS: The Borrower shall not permit the Consolidated First Lien Net Leverage Ratio as of the end of any fiscal quarter to exceed 4.25:1.00; provided that upon the consummation of a Material Permitted Acquisition with cash consideration exceeding $100,000,000, such ratio shall step up to 4.75:1.00 for the subsequent four quarters.",
     "Weil / Davis Polk", "New York", '{"page":1,"x":8,"y":40,"w":84,"h":18}'),

    ("CL-FIN03-STANDSTILL", "DOC-FIN-03", "M-801", "Second Lien 180-Day Enforcement Standstill & $150M DIP Consent", "Section 3.01 & Section 5.02", 1, "$150,000,000 Pre-Consented DIP Cap", "180-Day Second Lien Remedies Standstill", "Until First Lien Discharge Date", "Senior Lien Priority Waterfall",
     "First/Second Lien Intercreditor Agreement imposes a 180-day standstill period on Second Lien collateral enforcement and pre-consents to up to $150M of First Lien DIP financing in bankruptcy.",
     "SECTION 3.01 STANDSTILL PERIOD: Until the First Lien Discharge Date, the Second Lien Collateral Agent shall not enforce any remedies with respect to the Common Collateral until the expiration of a Standstill Period of 180 consecutive days following written notice of an acceleration Event of Default. Pre-consents to $150,000,000 DIP Financing.",
     "Weil / Milbank", "New York", '{"page":1,"x":8,"y":34,"w":84,"h":18}'),

    ("CL-MA01-INDEM", "DOC-MA-01", "M-902", "Falcon Aerospace $1.15B APA — 1.00% Cap, 0.50% Deductible & CFIUS Fee", "Section 8.02, 8.06 & 10.02", 1, "1.00% ($11,500,000) Indemnity Cap", "True Deductible (0.50% / $5,750,000)", "24 Months ($45M CFIUS/ITAR Reverse Break Fee)", "Full Double Materiality Scrape",
     "Falcon Aerospace $1.15B APA sets a 1.00% ($11.5M) Indemnity Cap above a 0.50% ($5.75M) True Deductible with Full Double Materiality Scrape and a $45M CFIUS/ITAR reverse termination fee.",
     "SECTION 8.02 INDEMNIFICATION BY SELLER & DEDUCTIBLE BASKET: Seller shall have no liability until Losses exceed $5,750,000 (0.50% of Enterprise Value) (True Deductible Basket), and Seller total aggregate liability shall be capped at $11,500,000 (1.00% of Enterprise Value). Includes Section 8.06 Double Materiality Scrape and Section 10.02 $45,000,000 CFIUS/ITAR Reverse Termination Fee.",
     "Weil / Cravath", "Delaware", '{"page":1,"x":8,"y":36,"w":84,"h":20}'),

    ("CL-MA02-HEALTH", "DOC-MA-02", "M-902", "Horizon Health $820M SPA — Stark Law / Anti-Kickback & $25M Escrow", "Section 3.14 & Section 8.04", 1, "$25,000,000 Healthcare Regulatory Escrow", "6-Year Lookback Compliance Rep", "36 Months Special Escrow Survival", "Covers Stark Law, Anti-Kickback, HIPAA & CMS Audits",
     "Horizon Health $820M SPA establishes a $25,000,000 Special Healthcare Regulatory Escrow at JPMorgan for 36 months covering Stark Law, Anti-Kickback Statute, and Medicare/Medicaid billing audits.",
     "SECTION 8.04 SPECIAL HEALTHCARE INDEMNITY ESCROW: At Closing, Buyer shall deposit $25,000,000 into a separate Healthcare Regulatory Escrow Account with JPMorgan Chase Bank, N.A., dedicated solely to satisfy claims arising out of historical Medicare/Medicaid billing audits and Stark Law / Anti-Kickback compliance for a survival period of 36 months.",
     "Weil / Ropes & Gray", "Delaware", '{"page":1,"x":8,"y":40,"w":84,"h":18}'),

    ("CL-MA03-JV", "DOC-MA-03", "M-902", "Oncology Gene Therapy JV — 60-Day Deadlock Russian Roulette Buy-Sell", "Section 4.02 & Section 7.01", 1, "$500,000,000 Combined JV Commitment", "60-Day Board Deadlock Trigger", "36-Month Post-JV CD19 Non-Compete", "Russian Roulette Buy-Sell at Morgan Stanley FMV",
     "BioTech / Apex $500M Oncology JV resolves 60-day Board deadlocks via a Russian Roulette Buy-Sell mechanism valued by Morgan Stanley and enforces a 36-month CD19 gene therapy non-compete.",
     "SECTION 4.02 GOVERNANCE & DEADLOCK RESOLUTION: The Board consists of six managers (three appointed by each party). In the event of a Deadlock on Major Decisions lasting more than sixty (60) days, either party may trigger the Russian Roulette Buy-Sell Mechanism at Fair Market Value determined by Morgan Stanley.",
     "Weil / Freshfields", "Delaware", '{"page":1,"x":8,"y":35,"w":84,"h":18}'),

    ("CL-MA04-SWAP", "DOC-MA-04", "M-902", "Tokyo Microsystems $1.4B Cross-Border Share Swap — METI, CFIUS & ICC", "Section 5.04 & Section 9.01", 1, "0.428x Share Exchange Ratio ($1.40B)", "Mandatory METI (Japan) & US CFIUS Clearance", "Singapore ICC Arbitration (3 Arbitrators)", "Cross-Border Tax-Free Reorganization Structure",
     "Apex / Tokyo Microsystems 210B Yen ($1.40B) cross-border share exchange requires dual METI (Japan FEFTA) and US CFIUS clearance, with disputes seated in Singapore under ICC Rules.",
     "SECTION 5.04 METI & CFIUS CLEARANCE COVENANTS: Each party shall use reasonable best efforts to obtain clearance from the Ministry of Economy, Trade and Industry of Japan (METI) under the Foreign Exchange and Foreign Trade Act and CFIUS clearance in the United States. Disputes settled under ICC Rules in Singapore.",
     "Weil / Nagashima Ohno", "Singapore / ICC", '{"page":1,"x":8,"y":35,"w":84,"h":18}'),

    ("CL-RE01-LEASE", "DOC-RE-01", "M-703", "50 Hudson Yards $185M Triple Net Lease — $1B Net Worth CoC Safe Harbor", "Section 3.01 & Section 11.02", 1, "$12.25M/Yr Base Rent (+2.5% Escalation)", "$1,000,000,000 Net Worth CoC Safe Harbor", "15-Year Term (175,000 RSF Floors 34-38)", "Casualty Termination Right (>35% Damage in Final 2 Yrs)",
     "50 Hudson Yards 15-year NNN Lease ($185M aggregate rent) permits Tenant Change of Control without Landlord consent if the surviving entity has Net Worth exceeding $1,000,000,000.",
     "SECTION 11.02 ASSIGNMENT & CHANGE OF CONTROL: Tenant shall not assign this Lease or sublet the Premises without Landlord's prior written consent, not to be unreasonably withheld; provided that a Change of Control of Tenant into an entity with Net Worth exceeding $1,000,000,000 shall be permitted without consent.",
     "Weil / Fried Frank", "New York", '{"page":1,"x":8,"y":38,"w":84,"h":18}'),

    ("CL-RE02-GROUND", "DOC-RE-02", "M-703", "Silicon Valley 42-Acre Ground Lease — Uncapped Environmental Indemnity", "Section 4.05 & Section 12.01", 1, "Uncapped Hazardous Materials Indemnity", "60-Day Leasehold Mortgagee Cure Right", "50-Year Ground Term (+2x 25-Yr Extensions)", "Semiconductor Cleanroom & R&D Permitted Use",
     "Mountain View 50-year R&D Ground Lease ($420M) imposes an uncapped Environmental Indemnity for cleanroom Hazardous Materials and grants Leasehold Mortgagees a 60-day default cure period.",
     "SECTION 4.05 PERMITTED USE & ENVIRONMENTAL INDEMNITY: Premises shall be used exclusively for semiconductor research, cleanroom fabrication, and corporate headquarters. Lessee provides an uncapped Environmental Indemnity for any Hazardous Materials introduced during the 50-year lease term, with 60-day Leasehold Mortgagee cure rights.",
     "Weil / Gibson Dunn", "California", '{"page":1,"x":8,"y":36,"w":84,"h":18}'),

    ("CL-RE03-LOGISTICS", "DOC-RE-03", "M-703", "Dallas 850,000 Sq Ft Logistics Lease — $2.5M Robotic Restoration Bond", "Section 8.01 & Section 14.04", 1, "$2,500,000 Decommissioning Bond", "3.0% Annual Base Rent Escalation", "10-Year Term ($64M Commitment)", "Landlord Structural / Tenant HVAC & Slab Allocation",
     "Prologis 850,000 sq ft Dallas Logistics Lease permits automated robotic pick-and-pack alterations without Landlord consent provided Tenant posts a $2,500,000 restoration bond.",
     "SECTION 14.04 TENANT ALTERATIONS & RESTORATION: Tenant may install automated robotic pick-and-pack systems without Landlord approval, provided Tenant posts a $2,500,000 restoration bond for decommissioning upon lease expiration.",
     "Weil Real Estate", "Texas", '{"page":1,"x":8,"y":38,"w":84,"h":16}'),

    ("CL-RE04-SUBLEASE", "DOC-RE-04", "M-703", "Austin Domain Tower Sublease — 30-Day Master Landlord Consent Condition", "Section 4.01 & Section 9.01", 1, "$2,584,000/Yr ($38/RSF) Base Rent", "30-Day Tishman Speyer Master Consent", "Expires October 31, 2031 (68,000 RSF)", "2026 Base Year Operating Expense Pass-Through",
     "Austin Domain Tower II Sublease (68,000 RSF from Dell Technologies) is strictly contingent on receiving written consent from Master Landlord (Tishman Speyer) within 30 days.",
     "SECTION 9.01 MASTER LANDLORD CONSENT CONDITION: This Sublease is strictly contingent upon receiving unconditional written consent from Master Landlord (Tishman Speyer) within thirty (30) days of execution.",
     "Weil Real Estate", "Texas", '{"page":1,"x":8,"y":38,"w":84,"h":16}'),

    ("CL-TECH01-SAAS", "DOC-TECH-01", "M-605", "Enterprise AI SaaS — 99.95% SLA, Zero-AI-Training & $50M Super-Cap", "Section 4.02, 8.01 & 9.02", 1, "12-Mo Fees ($7.6M) / $50.0M Super-Cap", "99.95% Uptime SLA (5% Credit per 0.1% Drop)", "5-Year Subscription ($38M Total)", "Immediate Termination on >8-Hr Outage; Zero AI Training",
     "DataMesh Foundry AI SaaS Agreement guarantees 99.95% uptime (termination right if outage >8 hrs), warrants Customer Data is never used to train foundation models, and sets a $50M Data/IP Super-Cap.",
     "SECTION 8.01 & 9.02 DATA OWNERSHIP, ZERO-AI-TRAINING & SUPER-CAP: Vendor warrants that Customer Data will NEVER be used to train, fine-tune, or calibrate Vendor's foundation models. Aggregate liability is capped at 12 months fees ($7,600,000); provided breaches of Section 8 (Customer Data / Confidentiality) or IP Indemnification are subject to a $50,000,000 Super-Cap.",
     "Weil Technology & IP", "New York", '{"page":1,"x":8,"y":36,"w":84,"h":20}'),

    ("CL-TECH02-PATENT", "DOC-TECH-02", "M-605", "5G/6G Patent Cross-License — $1.15/Unit FRAND Rate & Defensive Suspension", "Section 3.04 & Section 7.02", 1, "$1.15/Unit FRAND Royalty ($120M Total)", "Reciprocal Defensive License Suspension", "Worldwide SEP Cross-License", "Full Patent Exhaustion & Customer Non-Assertion",
     "Qualcomm / OmniComm 5G/6G Standard Essential Patent Cross-License sets a $1.15/unit FRAND royalty, protects downstream customers under patent exhaustion, and triggers automatic suspension on patent litigation.",
     "SECTION 7.02 PATENT EXHAUSTION & PATENT ASSERTION DEFENSE: Neither party shall assert any patent infringement claim against customers of the other party for licensed products ($1.15/unit FRAND rate). Any patent lawsuit filed by either party triggers automatic reciprocal suspension of license rights.",
     "Weil Patent & IP", "California", '{"page":1,"x":8,"y":38,"w":84,"h":18}'),

    ("CL-TECH03-MIT", "DOC-TECH-03", "M-605", "MIT Quantum Optics Tech Transfer — $5M/Yr Diligence & Bayh-Dole March-In", "Section 4.01 & Section 8.01", 1, "$15M Upfront + 3.5% Net Sales Royalty", "$5,000,000 Annual R&D Spend Milestone", "36-Month Commercial Prototype Deadline", "Subject to 35 U.S.C. 200-212 Bayh-Dole Government Rights",
     "MIT Quantum Photonics Exclusive License requires $5.0M/year R&D spend and a commercial prototype within 36 months (or converts to non-exclusive), subject to federal Bayh-Dole Act march-in rights.",
     "SECTION 4.01 & 8.01 DILIGENCE MILESTONES & BAYH-DOLE ACT: Licensee shall expend not less than $5,000,000 annually in commercial development. Failure to achieve Commercial Prototype by Month 36 converts exclusive license to non-exclusive. Subject to US Government rights under 35 U.S.C. Section 200-212 (Bayh-Dole Act).",
     "Weil / MIT Tech Licensing", "Massachusetts", '{"page":1,"x":8,"y":36,"w":84,"h":18}'),

    ("CL-EMP01-CEO", "DOC-EMP-01", "M-504", "Turnaround CEO Employment — 2.99x Double-Trigger CoC Severance ($13.45M)", "Section 5.03 & Section 7.02", 1, "2.99x Base + Bonus ($13,455,000)", "Double-Trigger CoC (Without Cause / Good Reason)", "24-Month CoC Protection / 18-Mo Non-Compete", "100% PSU Equity Acceleration + 36-Mo COBRA",
     "CEO Employment Agreement (Dr. Helena Vance) provides a 2.99x Base+Bonus ($13,455,000) lump-sum severance parachute plus 100% PSU equity acceleration upon a double-trigger termination within 24 months of a Change of Control.",
     "SECTION 5.03 SEVERANCE & CHANGE OF CONTROL DOUBLE-TRIGGER: If Executive is terminated without Cause or resigns for Good Reason within twenty-four (24) months following a Change of Control, Executive shall receive: (i) 2.99x the sum of Base Salary plus Target Bonus ($13,455,000), (ii) 100% accelerated vesting of all 500,000 PSUs, and (iii) 36 months COBRA.",
     "Weil Executive Comp", "Delaware", '{"page":1,"x":8,"y":38,"w":84,"h":20}'),

    ("CL-EMP02-RETENTION", "DOC-EMP-02", "M-504", "Project Helios $30M Quantum R&D Retention Pool — 50/50 Tranche Vesting", "Section 2.01 & Section 3.02", 1, "$30,000,000 Pool (50 Key Scientists)", "50% at Closing / 50% at 12-Month Anniversary", "12-Month Post-Closing Service", "100% Acceleration on Termination Without Cause",
     "Brightwater $30,000,000 Retention Pool for 50 tier-1 quantum engineers vests 50% at M-331 Merger Closing and 50% at the 12-month anniversary, with full acceleration if terminated without Cause.",
     "SECTION 2.01 & 3.02 VESTING SCHEDULE & ACCELERATION: Retention payments ($30,000,000 pool across 50 core quantum engineers) vest 50% on Closing Date of the Merger and 50% on the twelve (12) month anniversary of Closing, with 100% lump-sum acceleration within 10 business days if terminated without Cause.",
     "Weil Executive Comp", "Delaware", '{"page":1,"x":8,"y":36,"w":84,"h":18}'),

    ("CL-DERIV01-ISDA", "DOC-DERIV-01", "M-801", "Goldman Sachs $500M ISDA Schedule — $50M Cross-Default & BBB-/Baa3 Trigger", "Part 1(h) & Part 3(a)", 1, "$50,000,000 Cross-Default Threshold (Apex)", "BBB- (S&P) / Baa3 (Moody's) Downgrade Trigger", "Close-Out Netting Across All Swaps", "Two-Way Market Quotation Valuation",
     "2002 ISDA Master Agreement Schedule with Goldman Sachs sets a $50M Cross-Default threshold for Apex and triggers an Additional Termination Event if Apex's senior rating falls below BBB- or Baa3.",
     "PART 1(h) ADDITIONAL TERMINATION EVENTS — CREDIT RATING DOWNGRADE: Cross-Default Threshold is $50,000,000 for Apex. An Additional Termination Event occurs if Party B's senior unsecured debt rating falls below BBB- by S&P or Baa3 by Moody's.",
     "Weil Derivatives", "New York", '{"page":1,"x":8,"y":36,"w":84,"h":18}'),

    ("CL-COMM01-TSMC", "DOC-COMM-01", "M-331", "TSMC $450M 3nm Wafer Supply — 85% Take-or-Pay & Competitor CoC Termination", "Section 5.01 & Section 8.04", 1, "85% Take-or-Pay ($382.5M/Yr Floor)", "15,000 3nm Wafer Starts/Mo (98.5% Yield)", "90-Day Termination Notice on Competitor CoC", "Accelerates Unamortized Fab 21 Tooling on CoC",
     "TSMC Fab 21 3nm Wafer Supply Agreement imposes an 85% Take-or-Pay minimum ($382.5M/year) and allows TSMC to terminate on 90 days notice and accelerate tooling amortization if Brightwater is acquired by a Schedule D competitor.",
     "SECTION 5.01 & 8.04 TAKE-OR-PAY & CHANGE OF CONTROL PRE-EMPTION: Customer covenants to purchase not less than 85% of reserved monthly capacity ($382,500,000 annually at 15,000 3nm wafers/month). If Customer undergoes a Change of Control with any direct competitor of Foundry (Schedule D), Foundry may terminate upon 90 days notice and accelerate capital tooling amortization.",
     "Weil Commercial", "Delaware", '{"page":1,"x":8,"y":36,"w":84,"h":20}'),

    # 4 Email & Calendar Clauses
    ("CL-EM9901-TAX", "EM-9901", "M-331", "Unfiled Tax Email (EM-9901) — $14.2M Sec. 338(h)(10) Holdback (30-Day Grant)", "Email Para 1-3 (Marcus Thorne -> David Vance)", 1, "$14,200,000 Class V Step-Up Exposure", "Reject Skadden $9.5M Tax Gross-Up Cap", "30-Day Scoped Teammate Grant (GRANT-GRID)", "Requires First-Dollar Tax Indemnity or +$4.7M Reserve",
     "Unfiled Exchange email from Tax Partner Marcus Thorne (L-003) warning that Class V cleanroom equipment depreciation creates $14.2M in Section 338(h)(10) tax gross-up exposure and instructing M&A team to reject Skadden's $9.5M cap.",
     "EM-9901 (Marcus Thorne, Tax Partner L-003): To preserve the stepped-up tax basis under IRC Section 338(h)(10), our Class V cleanroom semiconductor equipment depreciation model shows $14,200,000 in state and federal tax gross-up exposure. DO NOT accept Skadden's v4 $9,500,000 cap unless Seller agrees to a first-dollar uncapped pre-closing tax indemnity or posts an additional $4,700,000 special tax reserve at Citibank N.A.",
     "Marcus Thorne (Weil Tax)", "IRC Sec. 338(h)(10)", '{"page":1,"x":6,"y":18,"w":88,"h":35}'),

    ("CL-EM9902-STRATEGY", "EM-9902", "M-331", "M&A Partner Email (EM-9902) — Spanner Graph Precedent Defense of 0.75% Cap", "Email Para 1-2 (David Vance -> Sarah Jenkins)", 1, "0.75% ($18.0M) Market Precedent Verified", "Cites M-215 (0.50%), M-518 (1.00%), M-902 (1.00%)", "18-Month Survival & Double Scrape Restored", "Rejects Skadden v4 0.25% Cap & 0.85% Basket",
     "Senior M&A Partner David Vance (L-002) benchmarks Skadden's v4 markup against Weil's Spanner Graph precedents (M-215 Kestrel 0.50%, M-518 Vanguard 1.00%, M-902 Falcon 1.00%) and directs full rejection of Skadden's 0.25% cap.",
     "EM-9902 (David Vance, Senior M&A Partner L-002): Based on our Cloud Spanner Graph precedents — Kestrel M-215 (0.50% cap, double scrape), Vanguard M-518 (1.00% cap, 24-mo survival), and Falcon Aerospace DOC-MA-01 (1.00% cap, 0.50% deductible, double scrape) — Skadden's v4 proposal to slash Section 8.02(b) to 0.25% ($6.0M) and delete Prong 1 of the Double Materiality Scrape is off-market. Reject in full.",
     "David Vance (Weil M&A)", "Delaware", '{"page":1,"x":6,"y":20,"w":88,"h":35}'),

    ("CL-EM9903-WALL", "EM-9903", "M-999", "Intapp Compliance Notice (EM-9903) — WALL-999 Zero-Leakage Verification", "Intapp Rule WALL-999", 1, "Zero Token Leakage Guaranteed", "Screen-Before-Rank GQL Graph Filter", "Permanent Conflict Screen (L-001 -> M-999)", "Excludes DOC-M999-01 Prior to ANN & BM25 Scoring",
     "Automated Intapp Compliance alert verifying that Sarah Jenkins (L-001) is screened from Matter M-999 (Project Omega) via Screen-Before-Rank GQL filtering prior to vector or BM25 execution.",
     "EM-9903 (Intapp Compliance Engine): Matter M-999 (Project Omega $4.2B Hostile Takeover Defense) is strictly walled off from Sarah Jenkins (L-001) under Rule WALL-999 due to her concurrent representation of Apex Global in M-331. All clauses and embeddings of DOC-M999-01 are filtered out BEFORE ANN Cosine Distance or BM25 scoring executes.",
     "Intapp Risk Engine", "Firm Compliance", '{"page":1,"x":6,"y":20,"w":88,"h":32}'),

    ("CL-CAL101-CONFLICT", "CAL-101", "M-331", "Calendar Conflict (.ics) — M-331 Closing Wire Call vs. M-720 FTC HSR Hearing", "VEVENT CAL-101-EVT-1 & EVT-2 (Oct 16, 2026)", 1, "60-Minute Hard Overlap (14:30-15:30 UTC)", "M-331 $18M Escrow Wire vs M-720 Fab 14 Hearing", "Oct 16, 2026 (14:00-16:00 UTC)", "Requires Partner Delegation (L-001 / L-002 / L-008)",
     "RFC-5545 Calendar (.ics) analysis detects a 60-minute hard conflict on Oct 16, 2026 (14:30-15:30 UTC) between the M-331 Brightwater Closing & $18M Citibank Wire Call and the M-720 FTC HSR Second Request Fab 14 Divestiture Hearing.",
     "CAL-101 CALENDAR CONFLICT DETECTED (Oct 16, 2026, 14:30-15:30 UTC Overlap): Event 1 (14:00-15:30 UTC): [M-331 CLOSING] Apex / Brightwater $2.4B Merger Signing & Citibank $18M Escrow Wire Call (ABA 021000089). Event 2 (14:30-16:00 UTC): [HARD CONFLICT - M-720 HSR] FTC Bureau of Competition Second Request & Fab 14 Divestiture Hearing (HHI 2,490 -> +65 net delta).",
     "Weil Deal Coordinator", "FTC / Delaware", '{"page":1,"x":6,"y":15,"w":88,"h":45}'),

    # Additional High-Value Disclosure Schedule & Cross-Matter Clauses to exceed >55 Curated Clauses in Spanner
    ("CL-M331-PATENTS", "DOC-M331-01", "M-331", "Schedule 3.12 Material IP — FinFET & Quantum Photonic Patents", "Schedule 3.12", 5, "100% Unencumbered Registered IP", "US Patents 11,482,901 & 11,894,220 + EP 3,892,104", "72-Month Fundamental IP Representation", "Zero Pending Infringement or Invalidity Claims",
     "Disclosure Schedule 3.12 itemizes Brightwater's crown-jewel Sub-1nm FinFET (US 11,482,901), Quantum Photonic Phase Modulator (US 11,894,220), and EUV Metrology (EP 3 892 104 B1) patents.",
     "SCHEDULE 3.12 MATERIAL INTELLECTUAL PROPERTY & REGISTERED PATENTS: Itemized Disclosure of Registered IP: US Patent No. 11,482,901 ('Sub-1nm FinFET Gate Dielectric Architecture'); US Patent No. 11,894,220 ('Quantum Photonic Phase Modulator Array'); European Patent Office Registration EP 3 892 104 B1 ('Wafer-Scale EUV Metrology Systems').",
     "Weil, Gotshal & Manges LLP", "Delaware", '{"page":5,"x":8,"y":28,"w":84,"h":18}'),

    ("CL-M331-CUSTOMERS", "DOC-M331-01", "M-331", "Schedule 5.16 Top-20 Material Customers ($596M Defense & AI Run-Rate)", "Schedule 5.16", 6, "$596,000,000 Top-5 Customer Run-Rate", "Zero Termination or Volume Reduction Notices", "12-Month Lookback Representation", "Includes US DoD ($110M), NVIDIA ($142M), Apple ($195M)",
     "Schedule 5.16 certifies that none of Brightwater's Top-5 customers — Apple ($195M), NVIDIA ($142M), US DoD ($110M), Lockheed Martin ($85M), and Raytheon ($64M) — have threatened termination or volume cuts.",
     "SCHEDULE 5.16 TOP-20 MATERIAL CUSTOMERS AND SUPPLIERS: Top Customers accounting for >5.0% of Consolidated Revenue: US Department of Defense ($110M annual run-rate), Lockheed Martin Corp. ($85M), Raytheon Technologies ($64M), NVIDIA Corp. ($142M), and Apple Inc. ($195M). No top customer has provided notice of intent to terminate or reduce volume.",
     "Weil, Gotshal & Manges LLP", "Delaware", '{"page":6,"x":8,"y":32,"w":84,"h":18}'),

    ("CL-FUND01-KEYPERSON", "DOC-FUND-01", "M-610", "Key Person Suspension Event & 66.7% LPAC Cure Vote (FundGen)", "Section 11.01", 3, "2 of 4 Senior Managing Directors Trigger", "Automatic Acquisition Period Suspension", "90-Day Cure Window via 66.7% LPAC Vote", "Protects $12.5B Institutional LP Commitments",
     "If 2 of the 4 Senior Managing Directors cease devoting substantially all business time to Fund VIII during the Investment Period, new platform investments are automatically suspended unless waived by a 66.7% LPAC vote within 90 days.",
     "SECTION 11.01 KEY PERSON SUSPENSION EVENT: If any two of the four Senior Managing Directors cease to devote substantially all business time to the Partnership during the Investment Period, a Key Person Event shall automatically suspend new platform acquisitions unless cured or waived by a 66.7% Limited Partner Advisory Committee (LPAC) vote within ninety (90) days.",
     "Weil Private Funds (FundGen)", "Delaware", '{"page":3,"x":8,"y":30,"w":84,"h":18}'),

    ("CL-FIN01-ECF", "DOC-FIN-01", "M-801", "Mandatory Excess Cash Flow Prepayment Sweep (50% -> 25% -> 0%)", "Section 2.05", 1, "50% ECF Sweep (Steps down to 25% / 0%)", "3.50x and 2.75x First Lien Net Leverage Tiers", "Annual Fiscal Year Calculation", "Dollar-for-Dollar Voluntary Prepayment Credit",
     "Citigroup $750M TLB requires an annual 50% Excess Cash Flow mandatory prepayment sweep, stepping down to 25% when First Lien Net Leverage is below 3.50x and 0% below 2.75x.",
     "SECTION 2.05 MANDATORY PREPAYMENTS & EXCESS CASH FLOW: The Borrower shall prepay the Term Loans in an amount equal to fifty percent (50.0%) of Excess Cash Flow for each fiscal year, stepping down to twenty-five percent (25.0%) if the Consolidated First Lien Net Leverage Ratio is less than 3.50:1.00, and zero percent (0.0%) if less than 2.75:1.00.",
     "Weil / Cahill Gordon", "New York", '{"page":1,"x":8,"y":55,"w":84,"h":18}'),
]


def seed_live_cloud_spanner():
    """Seeds all 46 Documents, 54 Curated Clauses, 14 Matters, Lawyers, Clients, Emails, Walls, Grants, and Graph Edges into live Cloud Spanner."""
    print("=" * 80)
    print(f"  SEEDING LIVE CLOUD SPANNER: {PROJECT_ID} / {SPANNER_INSTANCE} / {SPANNER_DATABASE}")
    print("=" * 80)

    client = spanner.Client(project=PROJECT_ID)
    instance = client.instance(SPANNER_INSTANCE)
    db = instance.database(SPANNER_DATABASE)

    # 1. Generate 3,072-dim embeddings for all curated clauses
    print(f"Generating 3,072-dim embeddings for {len(CURATED_CLAUSES)} curated legal clauses...")
    clause_texts = [f"{c[0]} {c[3]} {c[4]} {c[10]} {c[11]}" for c in CURATED_CLAUSES]
    clause_embeddings = embed_texts_gemini_2(clause_texts)

    # 2. Seed Clients, Lawyers, Matters, Documents, Emails, IntappWalls, TeammateGrants, WorkedOn
    def _upsert_core_entities(transaction):
        transaction.insert_or_update(
            table="Clients",
            columns=("client_id", "client_name", "industry", "tier"),
            values=CLIENTS_DATA,
        )
        transaction.insert_or_update(
            table="Lawyers",
            columns=("lawyer_id", "full_name", "email", "title", "practice_group", "office"),
            values=LAWYERS_DATA,
        )
        transaction.insert_or_update(
            table="Matters",
            columns=("matter_id", "matter_name", "client_id", "practice_area", "status", "lead_partner_id", "deal_value_usd"),
            values=MATTERS_DATA,
        )
        transaction.insert_or_update(
            table="Documents",
            columns=("doc_id", "matter_id", "title", "doc_type", "counsel_firm", "governing_law", "execution_date", "pdf_filename", "page_count", "dms_version"),
            values=DOCUMENTS_CATALOG,
        )

        belongs_rows = [(d[0], d[1], d[3]) for d in DOCUMENTS_CATALOG]
        transaction.insert_or_update(
            table="BelongsToMatter",
            columns=("doc_id", "matter_id", "filing_type"),
            values=belongs_rows,
        )

        emails_rows = [
            ("EM-9901", "M-331", "L-003", "L-002",
             "RE: M-331 Brightwater — Section 338(h)(10) Tax Allocation Rider & Skadden Indemnity Cap Pushback",
             "Marcus Thorne (Tax Partner, L-003) to David Vance (L-002) & Sarah Jenkins (L-001): Class V semiconductor cleanroom equipment depreciation creates $14,200,000 in Section 338(h)(10) tax gross-up exposure. Reject Skadden v4's $9,500,000 cap unless Seller agrees to first-dollar uncapped tax indemnity or posts +$4.7M escrow reserve at Citibank.",
             "2026-10-07T18:42:00Z", "METADATA_ONLY", True, "DOC-M331-04"),
            ("EM-9902", "M-331", "L-002", "L-001",
             "FW: Skadden v4 Redline Markup on Section 8.02(b) Deductible Basket & Materiality Scrape",
             "David Vance (L-002) to Sarah Jenkins (L-001): Benchmarked Skadden v4 against Spanner Graph precedents M-215 Kestrel (0.50% cap, double scrape), M-518 Vanguard (1.00% cap, 24-mo survival), and M-902 Falcon (1.00% cap). Reject Skadden's 0.25% ($6.0M) cap and restore Prong 1 of Double Scrape.",
             "2026-10-08T09:15:00Z", "FULL", True, "DOC-M331-02"),
            ("EM-9903", "M-999", "L-006", "L-004",
             "[INTAPP WALL-999 ENFORCED] Ethical Wall & Zero-Leakage Verification for Matter M-999 (Project Omega)",
             "Automated Intapp Compliance Notice: Sarah Jenkins (L-001) is screened from Matter M-999 (Project Omega $4.2B Hostile Defense) via Screen-Before-Rank GQL filtering prior to vector ANN or BM25 execution.",
             "2026-10-09T11:05:00Z", "RESTRICTED_WALL", True, "DOC-M999-01"),
            ("EM-9904", "M-610", "L-007", "L-001",
             "FundHQ Sovereign LP MFN Compendium & Tier-1 25 bps Management Fee Discount Election",
             "Victoria Sterling (Private Funds Partner, L-007): Confirmed GIC, CalPERS, and ADIA ($250M+ Tier-1 Anchor LPs) elected the 25 bps Management Fee discount (1.50% Inv. Period / 1.05% Post-Inv.) and 50% zero-fee Co-Investment ROFO in Fund VIII.",
             "2026-10-10T14:20:00Z", "FULL", True, "DOC-FUND-02"),
        ]
        transaction.insert_or_update(
            table="Emails",
            columns=("email_id", "matter_id", "sender_lawyer_id", "recipient_lawyer_id", "subject_line", "body_text", "sent_timestamp", "visibility_state", "has_attachment", "attachment_doc_id"),
            values=emails_rows,
        )

        # Intapp Walls: Authorize L-001 and L-002 across all non-restricted matters (M-109 through M-902), and EXCLUDE L-001 from M-999
        authorized_matters = ["M-331", "M-402", "M-109", "M-215", "M-518", "M-610", "M-720", "M-850", "M-801", "M-902", "M-703", "M-605", "M-504"]
        wall_rows = []
        for idx, m_id in enumerate(authorized_matters, 1):
            wall_rows.append((f"WALL-{idx:03d}", "L-001", m_id, "INCLUDE", f"Authorized Deal & Precedent Access — Matter {m_id}", "2026-08-01T00:00:00Z"))
            wall_rows.append((f"WALL-2{idx:02d}", "L-002", m_id, "INCLUDE", f"Authorized Senior Partner Access — Matter {m_id}", "2026-08-01T00:00:00Z"))
        wall_rows.append(("WALL-999", "L-001", "M-999", "EXCLUDE", "INTAPP ETHICAL WALL: Sarah Jenkins screened from Project Omega Hostile Defense due to prior Apex representation", "2026-09-01T00:00:00Z"))
        wall_rows.append(("WALL-998", "L-006", "M-999", "INCLUDE", "Authorized Restructuring Lead Counsel — Project Omega M-999", "2026-09-01T00:00:00Z"))

        transaction.insert_or_update(
            table="IntappWalls",
            columns=("wall_id", "lawyer_id", "matter_id", "rule_type", "reason", "enforced_at"),
            values=wall_rows,
        )

        # WorkedOn edges
        worked_rows = [
            ("L-001", "M-331", "Lead M&A Managing Partner", 342.5),
            ("L-002", "M-331", "Senior M&A Negotiation Partner", 285.0),
            ("L-003", "M-331", "Tax Structuring Partner (Sec. 338(h)(10))", 118.0),
            ("L-004", "M-402", "Lead Banking & Credit Partner", 210.0),
            ("L-004", "M-801", "Lead Syndicated Finance Partner", 195.0),
            ("L-007", "M-610", "Lead Private Funds Partner (FundGen/FundHQ)", 410.0),
            ("L-008", "M-720", "Lead Antitrust HSR Second Request Partner", 265.0),
            ("L-008", "M-850", "Lead Cyber & Privacy Pro Partner", 140.0),
            ("L-006", "M-999", "Lead Hostile Defense & Restructuring Counsel", 310.0),
        ]
        transaction.insert_or_update(
            table="WorkedOn",
            columns=("lawyer_id", "matter_id", "role", "hours_logged"),
            values=worked_rows,
        )

        # CitesPrecedent edges
        precedent_rows = [
            ("DOC-M331-01", "DOC-M215-01", "Benchmarks 0.75% Indemnity Cap & Double Materiality Scrape against Kestrel 0.50% Carve-Out Precedent", 0.94),
            ("DOC-M331-01", "DOC-M518-01", "Benchmarks 18-Month Survival & Escrow Release against Vanguard $3.1B Infrastructure SPA", 0.91),
            ("DOC-M331-01", "DOC-MA-01", "Benchmarks 0.50% True Deductible Basket & Double Scrape against Falcon Aerospace $1.15B APA", 0.92),
            ("DOC-M331-02", "DOC-M331-01", "Skadden v4 Redline Markup of Section 8.02(b) Indemnity Cap & Materiality Scrape", 0.98),
            ("DOC-M331-V4-REDLINE-DOCX", "DOC-M331-V3-DOCX", "OpenXML Word (<w:del>/<w:ins>) Tracked-Changes Redline against Weil v3 Merger Baseline", 0.99),
            ("DOC-FIN-01", "DOC-M402-01", "Cross-references Section 7.04 J.Crew / Envision Unrestricted Subsidiary IP Blocker & 20% EBITDA Cap", 0.95),
            ("DOC-DIAG-01", "DOC-M402-01", "Visual Corporate Org Diagram mapping Section 6.08(d) & 7.04 Restricted Guarantor Ring", 0.96),
            ("DOC-CHART-01", "DOC-M331-01", "Visual EBITDA Bridge ($145M->$175M) & 13.71x Valuation Waterfall supporting Section 1.01 & 2.04", 0.97),
            ("DOC-SCAN-01", "DOC-M331-03", "Executed Wet-Ink Signature Page & Citibank $18M Escrow Wire Exhibit for Section 4(b)", 0.97),
            ("DOC-FUND-02", "DOC-FUND-01", "FundHQ Sovereign LP MFN Side Letter Compendium modifying FundGen Buyout Fund VIII LPA Section 4.02", 0.96),
            ("DOC-CHART-02", "DOC-FUND-02", "Visual LP Fee Discount Curve illustrating Section 2.04 Tier-1 25 bps Anchor LP Fee Step-Down", 0.95),
            ("DOC-HSR-01", "DOC-M331-01", "HSR Second Request HHI Market Concentration Filing (Post-HHI 2,490) for Apex / Brightwater Merger", 0.93),
        ]
        transaction.insert_or_update(
            table="CitesPrecedent",
            columns=("source_doc_id", "target_doc_id", "citation_reason", "similarity_score"),
            values=precedent_rows,
        )

    db.run_in_transaction(_upsert_core_entities)
    print(f"Committed 8 Lawyers, 8 Clients, 14 Matters, {len(DOCUMENTS_CATALOG)} Documents, 28 IntappWalls, and 12 CitesPrecedent edges.")

    # 3. Seed Curated Clauses + ContainsClause + DocumentChunks in batches to stay well within Spanner transaction limits
    clause_rows = []
    contains_rows = []
    chunk_rows = []
    for idx, c in enumerate(CURATED_CLAUSES):
        vec = clause_embeddings[idx]
        c_id = c[0][:64]
        d_id = c[1][:64]
        m_id = c[2][:64]
        c_type = c[3][:64]
        sec_ref = c[4][:128]
        pg_num = int(c[5])
        cap_p = c[6][:64]
        bask_t = c[7][:128]
        surv_m = c[8][:64]
        quals = c[9][:256]
        sum_txt = c[10]
        verb_q = c[11]
        c_firm = c[12][:128]
        gov_l = c[13][:64]
        bbox_j = c[14]

        clause_rows.append((
            c_id, d_id, m_id, c_type, sec_ref, pg_num,
            cap_p, bask_t, surv_m, quals, sum_txt, verb_q, c_firm, gov_l, bbox_j, vec
        ))
        contains_rows.append((d_id, c_id, sec_ref))
        chunk_rows.append((
            f"CHK-{c_id}"[:64], d_id, m_id, sec_ref, pg_num,
            f"[{c_type} | {sec_ref}] {sum_txt} — {verb_q}", bbox_j, vec
        ))

    batch_size = 15
    for start in range(0, len(clause_rows), batch_size):
        batch_cl = clause_rows[start:start + batch_size]
        batch_co = contains_rows[start:start + batch_size]
        batch_ch = chunk_rows[start:start + batch_size]

        def _upsert_clause_batch(transaction):
            transaction.insert_or_update(
                table="Clauses",
                columns=(
                    "clause_id", "doc_id", "matter_id", "clause_type", "section_ref",
                    "page_number", "cap_pct", "basket_type", "survival_months", "qualifiers",
                    "summary_text", "verbatim_quote", "counsel_firm", "governing_law", "bbox_json", "embedding"
                ),
                values=batch_cl,
            )
            transaction.insert_or_update(
                table="ContainsClause",
                columns=("doc_id", "clause_id", "section_ref"),
                values=batch_co,
            )
            transaction.insert_or_update(
                table="DocumentChunks",
                columns=(
                    "chunk_id", "doc_id", "matter_id", "section_ref",
                    "page_number", "chunk_text", "bbox_json", "embedding"
                ),
                values=batch_ch,
            )

        db.run_in_transaction(_upsert_clause_batch)
        print(f"  -> Committed Clauses & DocumentChunks batch {start + 1}..{min(start + batch_size, len(clause_rows))} of {len(clause_rows)}")

    print("Successfully seeded live Cloud Spanner database `weil-legal-context`!")


def main():
    t0 = time.perf_counter()
    print("=" * 80)
    print("  WEIL MULTIMODAL EXTRACTION PIPELINE & CLOUD SPANNER GRAPH SEEDER")
    print("=" * 80)

    # 1. Build structured multimodal extractions (Charts, Diagrams, Scans, Tables)
    extractions = build_structured_multimodal_extractions()
    with open(EXTRACTIONS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(extractions, f, indent=2)
    print(
        f"Saved docparse-style structured multimodal extractions to {EXTRACTIONS_OUTPUT} "
        f"({len(extractions['charts'])} Charts, {len(extractions['diagrams'])} Diagrams, "
        f"{len(extractions['scanned_signatures_and_wires'])} Wet-Ink Scans, {len(extractions['tables'])} Tables)."
    )

    # 2. Run 46-file Ingestion & 100-Query Benchmark Suite -> corpus/indexed_clauses.json & benchmark_results.json
    ingest_and_benchmark.run_benchmark()

    # 3. Seed all 46 Documents, 54 Curated Clauses, 14 Matters, and Graph Edges into live Cloud Spanner
    seed_live_cloud_spanner()

    elapsed = time.perf_counter() - t0
    print("=" * 80)
    print(f"  MULTIMODAL EXTRACTION & SPANNER SEEDING PIPELINE COMPLETE IN {elapsed:.2f}s")
    print("=" * 80)


if __name__ == "__main__":
    main()
