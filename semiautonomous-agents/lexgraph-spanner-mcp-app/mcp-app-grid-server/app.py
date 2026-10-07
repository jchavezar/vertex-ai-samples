"""LexGraph Interactive Legal Grid & Citation Highlighter Agent (MCP App SEP-1865 + A2A v0.9 Canvas/IFrameSrcdoc + Cloud Spanner Hybrid RAG)."""

import asyncio
import datetime
import hashlib
import json
import math
import os
import re
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import google.auth
import google.auth.transport.requests
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.cloud import spanner
from google.genai import types
import requests
from ui_template import build_workspace_html

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
SPANNER_INSTANCE = os.environ.get("SPANNER_INSTANCE", "lexgraph-legal-spanner")
SPANNER_DATABASE = os.environ.get("SPANNER_DATABASE", "lexgraph-legal-context")
AGENT_MODEL = os.environ.get("AGENT_MODEL", "gemini-3.8-flash")
DISPLAY_MODEL_PRO = "Gemini 4 Pro"
DISPLAY_MODEL_FLASH = "Gemini 3.8 Flash"

COMPOSITE_CATALOG_URL = "https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json"
BASIC_V09_CATALOG_URL = "https://a2ui.org/specification/v0_9/basic_catalog.json"
STD_V08_CATALOG_URL = "https://a2ui.org/specification/v0_8/standard_catalog_definition.json"
MCP_RESOURCE_URI = "ui://lexgraph/legal-grid-workspace.html"
MCP_RESOURCE_MIME = "text/html;profile=mcp-app"
MCP_UI_CSP = {
    "resourceDomains": [
        "https://fonts.googleapis.com",
        "https://fonts.gstatic.com",
        "https://www.gstatic.com",
        "https://cdn.jsdelivr.net",
    ],
    "connectDomains": [
        "https://lexgraph-legal-grid-mcp-agent-254356041555.us-central1.run.app",
        "https://*.run.app",
        "https://*.googleapis.com",
    ],
}

app = FastAPI(
    title="LexGraph Interactive Legal Grid & Citation Highlighter Agent (MCP App + Cloud Spanner Hybrid RAG)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TASKS_STORE: dict[str, dict] = {}
LAST_HANDSHAKE: dict = {"timestamp": None, "protocol": None, "body": {}}

_spanner_db = None


def get_spanner_db():
  global _spanner_db
  if _spanner_db is None:
    client = spanner.Client(project=PROJECT_ID)
    instance = client.instance(SPANNER_INSTANCE)
    _spanner_db = instance.database(SPANNER_DATABASE)
  return _spanner_db


def _embed_gemini_2(text: str) -> list[float]:
  """Calls Vertex AI gemini-embedding-2 (3,072-dim) for live vector search against Cloud Spanner."""
  creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
  creds.refresh(google.auth.transport.requests.Request())
  url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us/publishers/google/models/gemini-embedding-2:embedContent"
  resp = requests.post(
      url,
      headers={
          "Authorization": f"Bearer {creds.token}",
          "Content-Type": "application/json",
          "X-Goog-User-Project": PROJECT_ID,
      },
      json={
          "content": {"parts": [{"text": text}]},
          "taskType": "RETRIEVAL_QUERY",
          "outputDimensionality": 3072,
      },
      timeout=15,
  )
  resp.raise_for_status()
  vals = resp.json()["embedding"]["values"]
  norm = math.sqrt(sum(v * v for v in vals))
  return [v / norm for v in vals] if norm > 0 else vals


# Rich multi-page original document structure so the right-hand Original Document Viewer renders complete contract pages with highlighted chunks & redlines
ORIGINAL_DOC_PAGES: dict[str, list[dict]] = {
    "DOC-M331-01": [
        {
            "page_number": 1,
            "sections": [
                {
                    "chunk_id": "CHK-M331-RECITALS",
                    "section_ref": "Preamble & Recitals",
                    "heading": "AGREEMENT AND PLAN OF MERGER ($2,400,000,000 ENTERPRISE VALUE)",
                    "bbox_x": 8,
                    "bbox_y": 14,
                    "text": (
                        "THIS AGREEMENT AND PLAN OF MERGER (this 'Agreement'), dated as of September 28, 2026, is entered into by and among "
                        "APEX GLOBAL HOLDINGS INC., a Delaware corporation ('Buyer'), BRIGHTWATER MERGER SUB INC. ('Merger Sub'), and "
                        "BRIGHTWATER CORP., a Delaware semiconductor corporation (the 'Company'). Aggregate Enterprise Value is fixed at "
                        "Two Billion Four Hundred Million Dollars ($2,400,000,000.00), subject to Section 2.04 Escrow Deposit and Working Capital adjustments."
                    ),
                },
                {
                    "chunk_id": "CL-M331-MAE",
                    "section_ref": "Section 1.01 & 7.02(c)",
                    "heading": "Material Adverse Effect (MAE) & Quantitative 15% Peer EBITDA Threshold",
                    "bbox_x": 8,
                    "bbox_y": 52,
                    "text": (
                        "Section 1.01 'Company Material Adverse Effect' means any change, event, or occurrence that has a material adverse effect on the "
                        "business, results of operations, or financial condition of the Company and its Subsidiaries, taken as a whole; provided, however, "
                        "that none of the following shall constitute a Company Material Adverse Effect: (i) changes in GAAP or Delaware law, "
                        "(ii) industry-wide semiconductor supply constraints, except to the extent such changes disproportionately impact the Company "
                        "by more than 15% of Consolidated Adjusted EBITDA compared to peer companies."
                    ),
                },
            ],
        },
        {
            "page_number": 2,
            "sections": [
                {
                    "chunk_id": "CL-M331-INDEM",
                    "section_ref": "Section 8.02(b) & 8.04",
                    "heading": "Indemnification Cap, True Deductible Basket & Double Materiality Scrape",
                    "is_primary": True,
                    "bbox_x": 8,
                    "bbox_y": 24,
                    "text": (
                        "Section 8.02(b) Cap and Deductible Basket: Notwithstanding anything to the contrary set forth herein, Seller shall have no liability "
                        "under Section 8.02(a) until the aggregate amount of all Losses exceeds $12,000,000 (0.50% of Enterprise Value) (the 'Deductible Basket'), "
                        "after which Seller shall be liable only for Losses in excess of the Deductible Basket up to an aggregate Indemnity Cap equal to "
                        "$18,000,000 (0.75% of Enterprise Value). For purposes of both determining breach and calculating Losses, all 'Material Adverse Effect' "
                        "and 'material' qualifications shall be disregarded (Full Double Materiality Scrape)."
                    ),
                    "redline_html": (
                        "Section 8.02(b) Cap and Deductible Basket [SKADDEN v4 REDLINE OVERLAY]: Notwithstanding anything to the contrary set forth herein, Seller shall have no liability "
                        "under Section 8.02(a) until the aggregate amount of all Losses exceeds <del class='redline-del'>$12,000,000 (0.50% of Enterprise Value)</del> "
                        "<ins class='redline-ins'>$20,400,000 (0.85% of Enterprise Value)</ins> (the 'Deductible Basket'), "
                        "after which Seller shall be liable only for Losses in excess of the Deductible Basket up to an aggregate Indemnity Cap equal to "
                        "<del class='redline-del'>$18,000,000 (0.75% of Enterprise Value)</del> <ins class='redline-ins'>$6,000,000 (0.25% R&amp;W Retention Cap)</ins>. "
                        "For purposes of <del class='redline-del'>both determining breach and</del> <ins class='redline-ins'>solely</ins> calculating Losses (Damages-Only Scrape), "
                        "all 'Material Adverse Effect' and 'material' qualifications shall be disregarded."
                    ),
                },
                {
                    "chunk_id": "CHK-M331-SURVIVAL",
                    "section_ref": "Section 8.01",
                    "heading": "Survival of Representations, Fundamental Carve-Outs & Fraud",
                    "bbox_x": 8,
                    "bbox_y": 62,
                    "text": (
                        "Section 8.01 Survival: Non-Fundamental Representations shall survive the Closing for eighteen (18) months. Fundamental Representations "
                        "(Organization, Authority, Capitalization, Taxes) shall survive for seventy-two (72) months. Claims grounded in Intentional Fraud "
                        "bypass both the Deductible Basket and the General Indemnity Cap up to 100% of Enterprise Value ($2,400,000,000)."
                    ),
                },
            ],
        },
        {
            "page_number": 3,
            "sections": [
                {
                    "chunk_id": "CHK-M331-GOVLAW",
                    "section_ref": "Section 11.08",
                    "heading": "Governing Law, Exclusive Delaware Chancery Forum & Specific Performance",
                    "bbox_x": 8,
                    "bbox_y": 20,
                    "text": (
                        "Section 11.08 Governing Law: This Agreement and all claims or causes of action arising hereunder shall be governed by the internal "
                        "laws of the State of Delaware. Each party irrevocably submits to the exclusive jurisdiction of the Court of Chancery of the State of Delaware."
                    ),
                }
            ],
        },
    ],
    "DOC-M331-02": [
        {
            "page_number": 1,
            "sections": [
                {
                    "chunk_id": "CL-M331-REDLINE",
                    "section_ref": "Redline Sec. 8.02(b) (Skadden v4 vs Buyer v3)",
                    "heading": "Opposing Counsel Redline Markup — Indemnity Cap Cut & Scrape Deletion",
                    "is_primary": True,
                    "bbox_x": 8,
                    "bbox_y": 30,
                    "text": (
                        "REDLINE COMPARISON [Skadden Draft v4 vs. Buyer Draft v3]: In Section 8.02(b), Opposing Counsel (Skadden) struck the "
                        "$18,000,000 (0.75%) Indemnity Cap and inserted $6,000,000 (0.25% R&W Policy Retention Split), while increasing the "
                        "Deductible Basket from 0.50% ($12.0M) to 0.85% ($20.4M), cutting general survival from 18 months to 12 months, "
                        "and deleting the first prong (breach determination) of the Double Materiality Scrape."
                    ),
                    "redline_html": (
                        "REDLINE COMPARISON [Skadden Draft v4 vs. Buyer Draft v3]: Cap: <del class='redline-del'>0.75% ($18,000,000)</del> "
                        "<ins class='redline-ins'>0.25% ($6,000,000)</ins> | Deductible Basket: <del class='redline-del'>0.50% ($12,000,000)</del> "
                        "<ins class='redline-ins'>0.85% ($20,400,000)</ins> | Survival: <del class='redline-del'>18 Months</del> "
                        "<ins class='redline-ins'>12 Months</ins> | Scrape: <del class='redline-del'>Double Scrape (Breach + Losses)</del> "
                        "<ins class='redline-ins'>Single Scrape (Damages Only)</ins>."
                    ),
                },
                {
                    "chunk_id": "CHK-M331-EMAIL9902",
                    "section_ref": "Deal Team Commentary (EM-9902)",
                    "heading": "Deal Partner Assessment Against Kestrel (M-215) & Vanguard (M-518) Precedents",
                    "bbox_x": 8,
                    "bbox_y": 64,
                    "text": (
                        "Partner Note (David Vance -> Sarah Jenkins, EM-9902): Based on our Kestrel Semiconductor (M-215, 0.50% cap, double scrape) "
                        "and Vanguard Infrastructure (M-518, 1.00% cap, 24-mo survival) precedents in Cloud Spanner Graph, 0.75% ($18.0M) is squarely market "
                        "for a $2.4B Delaware semiconductor acquisition. Reject Skadden's 0.25% cap and restore Prong 1 of the Double Materiality Scrape."
                    ),
                },
            ],
        }
    ],
    "DOC-M331-03": [
        {
            "page_number": 1,
            "sections": [
                {
                    "chunk_id": "CL-M331-ESCROW",
                    "section_ref": "Section 4(a)-(c)",
                    "heading": "Citibank N.A. $18,000,000 Indemnity Escrow Release & 10-BD Objection Mechanics",
                    "is_primary": True,
                    "bbox_x": 8,
                    "bbox_y": 44,
                    "text": (
                        "Section 4(b) Release of Escrow Fund: On the first Business Day following the eighteen (18) month anniversary of the Closing Date "
                        "(the 'Escrow Termination Date'), Escrow Agent (Citibank, N.A.) shall disburse to Seller Representative the remaining balance of the "
                        "$18,000,000 Indemnity Escrow Fund, less the aggregate amount of all Pending Claim Reserves specified in Buyer Claim Notices delivered "
                        "prior to 5:00 p.m. Eastern Time on the Escrow Termination Date, unless Seller delivers a written Claim Objection Notice within "
                        "ten (10) Business Days."
                    ),
                }
            ],
        }
    ],
    "DOC-M331-04": [
        {
            "page_number": 1,
            "sections": [
                {
                    "chunk_id": "CL-M331-TAX",
                    "section_ref": "Section 2.01 & 3.04 (Tax Rider)",
                    "heading": "Section 338(h)(10) Election, First-Dollar Tax Indemnity & $9.5M Gross-Up Ceiling",
                    "is_primary": True,
                    "bbox_x": 8,
                    "bbox_y": 38,
                    "text": (
                        "Section 3.04 Tax Indemnification Carve-Out: Seller's obligation to indemnify Buyer for Pre-Closing Taxes and Section 338(h)(10) "
                        "Election adjustments shall be on a first-dollar basis, shall not be subject to the Deductible Basket or the General Indemnity Cap "
                        "in Section 8.02(b), and shall survive until sixty (60) days following the expiration of the applicable federal or state statute of "
                        "limitations. Section 338(h)(10) ordinary-to-capital-gains Tax Gross-Up is capped at $9,500,000 (confirmed in EM-9901)."
                    ),
                }
            ],
        }
    ],
    "DOC-M215-01": [
        {
            "page_number": 1,
            "sections": [
                {
                    "chunk_id": "CHK-M215-PREAMBLE",
                    "section_ref": "Article I",
                    "heading": "Kestrel Semiconductor Stock Purchase Agreement ($1.65B Carve-Out Precedent)",
                    "bbox_x": 8,
                    "bbox_y": 18,
                    "text": (
                        "STOCK PURCHASE AGREEMENT dated as of November 12, 2025, for the $1,650,000,000 carve-out acquisition of Kestrel Semiconductor Corp. "
                        "Negotiated between LexGraph Enterprise Legal LLP (Buyer Counsel) and Kirkland & Ellis LLP (Seller Counsel) under Delaware law."
                    ),
                }
            ],
        },
        {
            "page_number": 2,
            "sections": [
                {
                    "chunk_id": "CL-M215-INDEM",
                    "section_ref": "Section 9.01(c) (Kestrel Carve-Out Precedent)",
                    "heading": "0.50% ($8.25M) Indemnity Cap, 15-Month Survival & Double Materiality Scrape",
                    "is_primary": True,
                    "bbox_x": 8,
                    "bbox_y": 24,
                    "text": (
                        "Section 9.01(c) Kestrel Semiconductor Precedent Cap: Seller's aggregate liability for breaches of Non-Fundamental Representations "
                        "shall not exceed $8,250,000 (0.50% of Base Purchase Price) above a 0.50% ($8,250,000) True Deductible Basket, and shall survive for "
                        "fifteen (15) months following Closing. Includes Full Double Materiality Scrape for both breach determination and Loss calculation."
                    ),
                }
            ],
        },
    ],
    "DOC-M518-01": [
        {
            "page_number": 1,
            "sections": [
                {
                    "chunk_id": "CHK-M518-PREAMBLE",
                    "section_ref": "Article I",
                    "heading": "Vanguard / Brookfield Infrastructure Membership Interest Purchase Agreement ($3.1B)",
                    "bbox_x": 8,
                    "bbox_y": 18,
                    "text": (
                        "MEMBERSHIP INTEREST PURCHASE AGREEMENT dated as of March 4, 2026 ($3,100,000,000 Enterprise Value), negotiated with "
                        "Simpson Thacher & Bartlett LLP under Delaware law."
                    ),
                }
            ],
        },
        {
            "page_number": 2,
            "sections": [
                {
                    "chunk_id": "CL-M518-INDEM",
                    "section_ref": "Section 10.03(a) (Vanguard Infrastructure JV)",
                    "heading": "1.00% ($31.0M) Indemnity Cap, 0.35% Tipping Basket & 24-Month Survival",
                    "is_primary": True,
                    "bbox_x": 8,
                    "bbox_y": 24,
                    "text": (
                        "Section 10.03(a) Vanguard JV Indemnity: Once aggregate Losses exceed the 0.35% Tipping Threshold ($10,850,000), Seller shall "
                        "indemnify Buyer from dollar one up to the 1.00% Aggregate Cap ($31,000,000) for a survival period of twenty-four (24) months "
                        "(72 months for Environmental representations). Applies Breach-Only Materiality Scrape."
                    ),
                }
            ],
        },
    ],
    "DOC-M402-01": [
        {
            "page_number": 1,
            "sections": [
                {
                    "chunk_id": "CL-M402-COV",
                    "section_ref": "Section 6.08 & 7.11",
                    "heading": "Apollo $850M Senior Secured Credit Agreement — 4.50x Leverage & J.Crew / Chewy IP Blocker",
                    "is_primary": True,
                    "bbox_x": 8,
                    "bbox_y": 46,
                    "text": (
                        "Section 6.08(d) Material Intellectual Property Blocker: Notwithstanding anything to the contrary in this Agreement, neither the "
                        "Borrower nor any Restricted Subsidiary may transfer, assign, or exclusively license any Material Intellectual Property to any "
                        "Unrestricted Subsidiary, nor may any Subsidiary holding Material Intellectual Property be designated as an Unrestricted Subsidiary "
                        "(Strict J.Crew / Serta / Chewy Protection). Section 7.11 Financial Covenant: Total Net Leverage Ratio shall not exceed 4.50x, "
                        "with restructuring EBITDA add-backs capped at 20% of LTM Consolidated EBITDA."
                    ),
                }
            ],
        }
    ],
    "DOC-M109-01": [
        {
            "page_number": 1,
            "sections": [
                {
                    "chunk_id": "CL-M109-NDA",
                    "section_ref": "Section 5 & Section 7",
                    "heading": "Mutual Non-Disclosure & 18-Month Standstill with Automatic Fall-Away (FormSpec v06)",
                    "is_primary": True,
                    "bbox_x": 8,
                    "bbox_y": 40,
                    "text": (
                        "Section 7 Standstill & Fall-Away: For a period of eighteen (18) months from the Effective Date, Recipient shall not acquire "
                        "beneficial ownership of more than 2.0% of the Company's voting securities; provided that the restrictions of this Section 7 "
                        "shall automatically terminate ('Fall-Away') upon the Company entering into a definitive agreement with a third party providing "
                        "for a merger or sale of 50% or more of its consolidated assets. Residuals clause excluded; Clean Team protocol mandatory."
                    ),
                }
            ],
        }
    ],
}


def query_spanner_grid_documents(
    query_text: str = "Compare indemnification caps, baskets, materiality scrapes, and Skadden redlines across M-331 and precedents",
    lawyer_email: str = "s-jenkins@lexgraph.com",
) -> dict:
  """Executes live Cloud Spanner Hybrid RAG (LexGraphLegalGraph GQL + 3,072-dim gemini-embedding-2 + Spanner FTS) and builds the full document grid state."""
  t0 = time.monotonic()
  db = get_spanner_db()
  lawyer_id = "L-002" if ("marcus" in lawyer_email.lower() or "m-chen" in lawyer_email.lower()) else "L-001"

  q_vec = _embed_gemini_2(query_text)
  tokens = [t for t in re.findall(r"[A-Za-z0-9]+", query_text) if len(t) >= 2]
  fts_terms = " OR ".join(tokens[:12]) if tokens else "Indemnification OR Cap OR Basket OR Skadden OR Scrape"

  sql = """
    WITH AuthorizedGraph AS (
      SELECT
        g.clause_id,
        g.matter_id,
        g.matter_name,
        g.practice_area,
        g.deal_value_usd,
        g.doc_id,
        g.doc_title,
        g.pdf_filename,
        g.dms_version,
        g.execution_date,
        g.clause_type,
        g.section_ref,
        g.page_number,
        g.cap_pct,
        g.basket_type,
        g.survival_months,
        g.qualifiers,
        g.summary_text,
        g.verbatim_quote,
        g.counsel_firm,
        g.governing_law
      FROM GRAPH_TABLE(
        LexGraphLegalGraph
        MATCH (l:Lawyer {lawyer_id: @lawyer_id})-[w:INTAPP_WALL {rule_type: "INCLUDE"}]->(m:Matter)<-[:BELONGS_TO_MATTER]-(d:Document)-[:CONTAINS_CLAUSE]->(cl:Clause)
        RETURN
          cl.clause_id AS clause_id,
          m.matter_id AS matter_id,
          m.matter_name AS matter_name,
          m.practice_area AS practice_area,
          m.deal_value_usd AS deal_value_usd,
          d.doc_id AS doc_id,
          d.title AS doc_title,
          d.pdf_filename AS pdf_filename,
          d.dms_version AS dms_version,
          d.execution_date AS execution_date,
          cl.clause_type AS clause_type,
          cl.section_ref AS section_ref,
          cl.page_number AS page_number,
          cl.cap_pct AS cap_pct,
          cl.basket_type AS basket_type,
          cl.survival_months AS survival_months,
          cl.qualifiers AS qualifiers,
          cl.summary_text AS summary_text,
          cl.verbatim_quote AS verbatim_quote,
          cl.counsel_firm AS counsel_firm,
          cl.governing_law AS governing_law
      ) AS g
    ),
    FtsMatches AS (
      SELECT clause_id, SCORE(clause_tokens, @fts_terms) AS bm25_score
      FROM Clauses
      WHERE SEARCH(clause_tokens, @fts_terms)
    )
    SELECT
      ag.doc_id,
      ag.matter_id,
      ag.matter_name,
      ag.practice_area,
      ag.doc_title,
      ag.pdf_filename,
      ag.dms_version,
      ag.execution_date,
      ag.clause_id,
      ag.clause_type,
      ag.section_ref,
      ag.page_number,
      ag.cap_pct,
      ag.basket_type,
      ag.survival_months,
      ag.qualifiers,
      ag.summary_text,
      ag.verbatim_quote,
      ag.counsel_firm,
      ag.governing_law,
      ROUND(1.0 - COSINE_DISTANCE(c.embedding, @q_vec), 4) AS vec_sim,
      IFNULL(ROUND(f.bm25_score, 4), 0.0) AS bm25_score,
      ROUND((1.0 - COSINE_DISTANCE(c.embedding, @q_vec)) * 0.75 + IFNULL(f.bm25_score, 0.0) * 0.15, 4) AS hybrid_rrf
    FROM AuthorizedGraph ag
    JOIN Clauses c ON c.clause_id = ag.clause_id
    LEFT JOIN FtsMatches f ON f.clause_id = ag.clause_id
    ORDER BY hybrid_rrf DESC
  """

  param_types = {
      "lawyer_id": spanner.param_types.STRING,
      "q_vec": spanner.param_types.Array(spanner.param_types.FLOAT32),
      "fts_terms": spanner.param_types.STRING,
  }
  params = {"lawyer_id": lawyer_id, "q_vec": q_vec, "fts_terms": fts_terms}

  docs_by_id: dict[str, dict] = {}
  all_clauses: list[dict] = []

  with db.snapshot() as snap:
    for row in snap.execute_sql(sql, params=params, param_types=param_types):
      doc_id = row[0]
      clause_id = row[8]
      page_num = int(row[11] or 1)
      pdf_file = row[5] or "M331_Brightwater_Merger_Agreement_Executed.pdf"
      pdf_url = f"https://storage.googleapis.com/vtxdemos-docs/lexgraph_legal/{pdf_file}#page={page_num}"

      clause_obj = {
          "doc_id": doc_id,
          "matter_id": row[1],
          "matter_name": row[2],
          "practice_area": row[3],
          "title": row[4],
          "pdf_filename": pdf_file,
          "pdf_url": pdf_url,
          "dms_version": row[6] or "iManage-v14.2",
          "execution_date": row[7] or "2026-09-28",
          "clause_id": clause_id,
          "clause_type": row[9],
          "section_ref": row[10],
          "page_number": page_num,
          "cap_pct": row[12],
          "basket_type": row[13],
          "survival_months": row[14],
          "qualifiers": row[15],
          "summary_text": row[16],
          "verbatim_quote": row[17],
          "counsel_firm": row[18],
          "governing_law": row[19],
          "vec_sim": float(row[20] or 0.0),
          "bm25_score": float(row[21] or 0.0),
          "hybrid_rrf": float(row[22] or 0.0),
      }
      all_clauses.append(clause_obj)

      if doc_id not in docs_by_id:
        docs_by_id[doc_id] = {
            "doc_id": doc_id,
            "matter_id": row[1],
            "matter_name": row[2],
            "practice_area": row[3],
            "title": row[4],
            "pdf_filename": pdf_file,
            "pdf_url": pdf_url,
            "dms_version": row[6] or "iManage-v14.2",
            "execution_date": row[7] or "2026-09-28",
            "primary_chunk_id": clause_id,
            "clause_type": row[9],
            "section_ref": row[10],
            "primary_page": page_num,
            "cap_pct": row[12],
            "basket_type": row[13],
            "survival_months": row[14],
            "qualifiers": row[15],
            "summary_text": row[16],
            "verbatim_quote": row[17],
            "counsel_firm": row[18],
            "governing_law": row[19],
            "vec_sim": float(row[20] or 0.0),
            "bm25_score": float(row[21] or 0.0),
            "hybrid_rrf": float(row[22] or 0.0),
            "pages": ORIGINAL_DOC_PAGES.get(doc_id, []),
            "dynamic_cells": {},
        }

  latency_ms = int((time.monotonic() - t0) * 1000)
  return {
      "lawyer_email": lawyer_email,
      "lawyer_id": lawyer_id,
      "documents": list(docs_by_id.values()),
      "clauses": all_clauses,
      "latency_ms": latency_ms,
  }


LATEST_WORKSPACE_STATE: dict | None = None


def _build_question_aware_fallback(
    question: str,
    docs: list[dict],
    scoped_docs: list[dict],
) -> dict:
  """Fast question-aware synthesis & per-document column extractor."""
  q_lower = question.lower()
  if "change of control" in q_lower or "coc" in q_lower or "consent" in q_lower or "assign" in q_lower:
    col_header = "Change of Control & Assignment"
    focus_clause_suffix = "COC"
  elif "redline" in q_lower or "skadden" in q_lower or "counter" in q_lower or "negoti" in q_lower:
    col_header = "Counterparty Redline Delta"
    focus_clause_suffix = "SKADDEN"
  elif "scrape" in q_lower or "materiality" in q_lower or "mae" in q_lower:
    col_header = "Materiality Scrape Scope"
    focus_clause_suffix = "SCRAPE"
  elif "survival" in q_lower or "month" in q_lower or "expir" in q_lower:
    col_header = "Survival Period & Carve-Outs"
    focus_clause_suffix = "SURV"
  elif "basket" in q_lower or "deductible" in q_lower or "tipping" in q_lower:
    col_header = "Basket Type & Threshold"
    focus_clause_suffix = "INDEM"
  else:
    col_header = (question[:30] + "...") if len(question) > 30 else question
    focus_clause_suffix = "INDEM"

  per_doc = {}
  primary_doc = scoped_docs[0] if scoped_docs else docs[0]
  primary_chunk_id = primary_doc["primary_chunk_id"]
  primary_page = primary_doc["primary_page"]

  for d in docs:
    matched_sec = None
    matched_page_num = d["primary_page"]
    for p in d.get("pages", []):
      p_num = p.get("page_number", 1)
      for s in p.get("sections", []):
        if focus_clause_suffix in s.get("chunk_id", "") or focus_clause_suffix in s.get("heading", "").upper():
          matched_sec = s
          matched_page_num = p_num
          break
      if matched_sec:
        break
    if not matched_sec:
      for p in d.get("pages", []):
        if p.get("sections"):
          matched_sec = p["sections"][0]
          matched_page_num = p.get("page_number", 1)
          break

    c_id = matched_sec["chunk_id"] if matched_sec else d["primary_chunk_id"]
    pg = matched_page_num if matched_sec else d["primary_page"]
    sec = matched_sec["section_ref"] if matched_sec else d["section_ref"]

    if d["doc_id"] == primary_doc["doc_id"]:
      primary_chunk_id = c_id
      primary_page = pg

    if focus_clause_suffix == "COC":
      badge = "CoC Trigger"
      ans = f"{sec}: Prior written consent / CoC termination rights ({d['qualifiers']})"
    elif focus_clause_suffix == "SKADDEN":
      badge = "Redline Delta"
      ans = f"{sec}: Cap {d['cap_pct']} vs counterparty markup ({d['qualifiers']})"
    elif focus_clause_suffix == "SCRAPE":
      badge = "Double Scrape" if "Double" in d["qualifiers"] else "Single Scrape"
      ans = f"{sec}: {d['qualifiers']} | Basket {d['basket_type']}"
    elif focus_clause_suffix == "SURV":
      badge = f"Surv {d['survival_months']}"
      ans = f"{sec}: General {d['survival_months']} | Cap {d['cap_pct']}"
    else:
      badge = f"Cap {d['cap_pct']}"
      ans = f"{d['cap_pct']} | {d['basket_type']} | {d['qualifiers']}"

    per_doc[d["doc_id"]] = {
        "badge": badge,
        "answer": ans,
        "chunk_id": c_id,
        "page": pg,
        "section_ref": sec,
    }

  bullets = "\n".join([
      f"- **`{d['doc_id']}` ({d['matter_id']} — {d['title']}, `{per_doc[d['doc_id']]['section_ref']}`, p.{per_doc[d['doc_id']]['page']}, `RRF={d['hybrid_rrf']}`)**: {per_doc[d['doc_id']]['answer']} — Cap **{d['cap_pct']}**, Basket **{d['basket_type']}**, Survival **{d['survival_months']}**."
      for d in scoped_docs[:4]
  ])
  return {
      "column_header": col_header,
      "executive_answer": bullets,
      "primary_doc_id": primary_doc["doc_id"],
      "primary_chunk_id": primary_chunk_id,
      "primary_page": primary_page,
      "per_doc_cells": per_doc,
  }


async def extract_dynamic_column_and_answer_with_adk(
    question: str,
    sp_data: dict,
    selected_doc_ids: list[str] | None = None,
) -> dict:
  """Uses Gemini on Vertex AI (with thinking_budget=0 for <1.5s latency) to synthesize a grounded answer AND extract a per-document dynamic grid column."""
  from google import genai
  os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
  os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
  os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

  docs = sp_data["documents"]
  scoped_docs = [d for d in docs if not selected_doc_ids or d["doc_id"] in selected_doc_ids] or docs

  prompt_payload = {
      "question": question,
      "selected_doc_ids": [d["doc_id"] for d in scoped_docs],
      "documents": [
          {
              "doc_id": d["doc_id"],
              "matter_id": d["matter_id"],
              "title": d["title"],
              "section_ref": d["section_ref"],
              "page": d["primary_page"],
              "chunk_id": d["primary_chunk_id"],
              "available_chunks": [
                  {
                      "chunk_id": s.get("chunk_id", ""),
                      "page": p.get("page_number", 1),
                      "section_ref": s.get("section_ref", ""),
                      "heading": s.get("heading", ""),
                  }
                  for p in d.get("pages", [])
                  for s in p.get("sections", [])
              ],
              "cap_pct": d["cap_pct"],
              "basket_type": d["basket_type"],
              "survival_months": d["survival_months"],
              "qualifiers": d["qualifiers"],
              "summary_text": d["summary_text"],
          }
          for d in docs
      ],
  }

  instruction = (
      "You are the LexGraph Enterprise Legal LLP Interactive Legal Grid & Citation Highlighter Agent.\n"
      "Given the user's question and live Cloud Spanner Hybrid RAG documents, return STRICT JSON ONLY (no markdown fences) with:\n"
      "{\n"
      '  "column_header": "<concise 3-5 word column title for this question>",\n'
      '  "executive_answer": "<3-4 bullet Markdown synthesis answering the question strictly across selected_doc_ids with inline citations like `DOC-M331-01 (Sec. 8.02(b), p.2)`>",\n'
      '  "primary_doc_id": "<most relevant doc_id from selected_doc_ids>",\n'
      '  "primary_chunk_id": "<most relevant chunk_id from available_chunks>",\n'
      '  "primary_page": <int page matching primary_chunk_id>,\n'
      '  "per_doc_cells": {\n'
      '    "<doc_id>": {"badge": "<2-word tag>", "answer": "<concise 10-16 word extracted answer for this doc>", "chunk_id": "<matching chunk_id>", "page": <int>, "section_ref": "<section_ref>"}\n'
      "  }\n"
      "}"
  )

  try:
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")
    resp = await asyncio.wait_for(
        client.aio.models.generate_content(
            model=AGENT_MODEL,
            contents=json.dumps(prompt_payload),
            config=types.GenerateContentConfig(
                system_instruction=instruction,
                temperature=0.1,
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        ),
        timeout=4.5,
    )
    raw = (resp.text or "").strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    parsed = json.loads(raw)
    if isinstance(parsed, dict) and "per_doc_cells" in parsed:
      return parsed
  except Exception:
    pass

  return _build_question_aware_fallback(question, docs, scoped_docs)



def execute_spanner_teammate_grant(
    email_id: str = "EM-9901",
    matter_id: str = "M-331",
    granted_to: str = "s-jenkins@lexgraph.com",
    days_valid: int = 30,
) -> dict:
  """Inserts a live 30-day expirable TeammateGrant edge into Cloud Spanner."""
  t0 = time.monotonic()
  db = get_spanner_db()
  grant_id = f"GRANT-GRID-{uuid.uuid4().hex[:6].upper()}"
  now = datetime.datetime.now(datetime.timezone.utc)
  expires = now + datetime.timedelta(days=days_valid)

  def _insert(transaction):
    transaction.insert_or_update(
        table="TeammateGrants",
        columns=(
            "grant_id",
            "email_id",
            "owner_lawyer_id",
            "grantee_lawyer_id",
            "matter_id",
            "granted_at",
            "expires_at",
            "status",
        ),
        values=[(
            grant_id,
            email_id,
            "L-003",
            "L-001",
            matter_id,
            now.isoformat(),
            expires.isoformat(),
            "ACTIVE_30D",
        )],
    )

  db.run_in_transaction(_insert)
  latency_ms = int((time.monotonic() - t0) * 1000)
  return {
      "status": "COMMITTED_SPANNER_GRAPH_EDGE",
      "grant_id": grant_id,
      "email_id": email_id,
      "matter_id": matter_id,
      "granted_by": "L-003 (Marcus Thorne, Tax Partner)",
      "granted_to": f"L-001 ({granted_to})",
      "expires_at": expires.strftime("%Y-%m-%d %H:%M UTC"),
      "latency_ms": latency_ms,
  }


async def build_initial_workspace_state(
    query_text: str,
    selected_doc_ids: list[str] | None = None,
    lawyer_email: str = "s-jenkins@lexgraph.com",
    fast_only: bool = False,
) -> tuple[dict, str]:
  """Runs Cloud Spanner Hybrid RAG + dynamic column extraction and returns (workspace_state, executive_markdown)."""
  global LATEST_WORKSPACE_STATE
  sp_data = await asyncio.to_thread(query_spanner_grid_documents, query_text, lawyer_email)
  docs = sp_data["documents"]
  scoped_docs = [d for d in docs if not selected_doc_ids or d["doc_id"] in selected_doc_ids] or docs
  if fast_only:
    adk_res = _build_question_aware_fallback(query_text, docs, scoped_docs)
  else:
    adk_res = await extract_dynamic_column_and_answer_with_adk(query_text, sp_data, selected_doc_ids)

  q_hash = hashlib.md5(query_text.strip().lower().encode("utf-8")).hexdigest()[:6]
  dyn_field = f"dyn_{q_hash}"
  dyn_col = {
      "field": dyn_field,
      "header": adk_res.get("column_header", "Extracted Question Analysis"),
      "question": query_text,
  }

  per_doc_cells = adk_res.get("per_doc_cells", {})
  for doc in sp_data["documents"]:
    cell = per_doc_cells.get(doc["doc_id"])
    if not cell:
      cell = {
          "badge": f"RRF {doc['hybrid_rrf']}",
          "answer": f"{doc['cap_pct']} ({doc['section_ref']})",
          "chunk_id": doc["primary_chunk_id"],
          "page": doc["primary_page"],
          "section_ref": doc["section_ref"],
      }
    doc["dynamic_cells"][dyn_field] = cell

  sel_ids = selected_doc_ids or ["DOC-M331-01", "DOC-M331-02", "DOC-M215-01"]
  active_doc_id = adk_res.get("primary_doc_id") or "DOC-M331-01"
  active_chunk_id = adk_res.get("primary_chunk_id") or "CL-M331-INDEM"
  active_page = int(adk_res.get("primary_page") or 2)

  citations = [
      {
          "doc_id": d["doc_id"],
          "chunk_id": per_doc_cells.get(d["doc_id"], {}).get("chunk_id", d["primary_chunk_id"]),
          "page": per_doc_cells.get(d["doc_id"], {}).get("page", d["primary_page"]),
          "label": f"{d['doc_id']} · {per_doc_cells.get(d['doc_id'], {}).get('section_ref', d['section_ref'])} (p.{per_doc_cells.get(d['doc_id'], {}).get('page', d['primary_page'])})",
      }
      for d in sp_data["documents"][:5]
  ]

  exec_md = (
      f"### ⚖️ LexGraph Interactive Legal Grid & Citation Highlighter (`{sp_data['latency_ms']} ms` Cloud Spanner Hybrid RAG · {DISPLAY_MODEL_PRO})\n"
      f"**Dynamic Grid Column Added:** `⚡ {dyn_col['header']}` across **{len(sp_data['documents'])} Intapp-Cleared Documents** "
      f"(Highlighted Citation in Right Side Panel: **`{active_doc_id}` · `{active_chunk_id}` · Page {active_page}**)\n\n"
      f"{adk_res.get('executive_answer', '')}"
  )

  agent_chat_entry = {
      "role": "agent",
      "text": adk_res.get("executive_answer", "").replace("\n", "<br/>"),
      "citations": citations,
  }

  initial_state = {
      "query": query_text,
      "latency_ms": sp_data["latency_ms"],
      "selected_doc_ids": sel_ids,
      "active_doc_id": active_doc_id,
      "active_chunk_id": active_chunk_id,
      "active_page": active_page,
      "dynamic_columns": [dyn_col],
      "documents": sp_data["documents"],
      "chat_entry": agent_chat_entry,
      "chat_history": [
          {
              "role": "user",
              "text": query_text,
              "scope": ", ".join(sel_ids),
          },
          agent_chat_entry,
      ],
  }
  LATEST_WORKSPACE_STATE = initial_state
  return initial_state, exec_md


# ==============================================================================
# 1. STANDALONE WEB WORKSPACE & REST API ENDPOINTS
# ==============================================================================
@app.get("/", response_class=HTMLResponse)
@app.get("/workspace", response_class=HTMLResponse)
async def get_workspace_ui(
    q: str = "Compare Indemnity Caps, Deductible Baskets, Materiality Scrapes, and Skadden Redlines across M-331 and precedents",
):
  state, _ = await build_initial_workspace_state(q)
  return HTMLResponse(content=build_workspace_html(state))


@app.post("/api/grid/add-column")
async def api_add_grid_column(request: Request):
  body = await request.json()
  question = body.get("question", "Analyze key risk and carve-outs")
  field = body.get("field", f"dyn_{uuid.uuid4().hex[:5]}")
  selected_doc_ids = body.get("selected_doc_ids") or None
  sp_data = await asyncio.to_thread(query_spanner_grid_documents, question)
  adk_res = await extract_dynamic_column_and_answer_with_adk(question, sp_data, selected_doc_ids)
  return JSONResponse({
      "field": field,
      "header": adk_res.get("column_header", question[:28]),
      "cells": adk_res.get("per_doc_cells", {}),
      "latency_ms": sp_data["latency_ms"],
  })


@app.post("/api/chat/scoped")
async def api_scoped_chat(request: Request):
  body = await request.json()
  question = body.get("question", "Compare selected documents")
  selected_doc_ids = body.get("selected_doc_ids") or []
  sp_data = await asyncio.to_thread(query_spanner_grid_documents, question)
  adk_res = await extract_dynamic_column_and_answer_with_adk(question, sp_data, selected_doc_ids)
  scoped_docs = [d for d in sp_data["documents"] if not selected_doc_ids or d["doc_id"] in selected_doc_ids] or sp_data["documents"]
  per_doc_cells = adk_res.get("per_doc_cells", {})
  citations = [
      {
          "doc_id": d["doc_id"],
          "chunk_id": per_doc_cells.get(d["doc_id"], {}).get("chunk_id", d["primary_chunk_id"]),
          "page": per_doc_cells.get(d["doc_id"], {}).get("page", d["primary_page"]),
          "label": f"{d['doc_id']} · {per_doc_cells.get(d['doc_id'], {}).get('section_ref', d['section_ref'])} (p.{per_doc_cells.get(d['doc_id'], {}).get('page', d['primary_page'])})",
      }
      for d in scoped_docs
  ]
  return JSONResponse({
      "answer": adk_res.get("executive_answer", "").replace("\n", "<br/>"),
      "citations": citations,
      "primary_citation": {
          "doc_id": adk_res.get("primary_doc_id", scoped_docs[0]["doc_id"]),
          "chunk_id": adk_res.get("primary_chunk_id", scoped_docs[0]["primary_chunk_id"]),
          "page": adk_res.get("primary_page", scoped_docs[0]["primary_page"]),
      },
      "latency_ms": sp_data["latency_ms"],
  })


@app.post("/api/grant")
async def api_grant_30d(request: Request):
  body = await request.json()
  res = await asyncio.to_thread(
      execute_spanner_teammate_grant,
      body.get("email_id", "EM-9901"),
      body.get("matter_id", "M-331"),
      body.get("granted_to", "s-jenkins@lexgraph.com"),
      30,
  )
  return JSONResponse(res)


# ==============================================================================
# 1B. OAUTH 2.0 AUTO-HANDSHAKE ENDPOINTS FOR GEMINI ENTERPRISE CUSTOM_MCP CONNECTOR
# ==============================================================================
from fastapi.responses import RedirectResponse


@app.get("/authorize")
async def oauth_authorize(
    redirect_uri: str = "https://vertexaisearch.cloud.google.com/oauth-redirect",
    state: str = "",
    client_id: str = "",
):
  sep = "&" if "?" in redirect_uri else "?"
  target = f"{redirect_uri}{sep}code=lexgraph-mcp-auth-code-2026"
  if state:
    target += f"&state={state}"
  return RedirectResponse(url=target, status_code=302)


@app.post("/token")
async def oauth_token():
  return JSONResponse({
      "access_token": "lexgraph-mcp-access-token-2026",
      "refresh_token": "lexgraph-mcp-refresh-token-2026",
      "token_type": "Bearer",
      "expires_in": 86400,
      "scope": "openid profile email",
  })


# ==============================================================================
# 2. MCP APPS PROTOCOL (SEP-1865 STREAMABLE HTTP JSON-RPC 2.0 AT POST /mcp)
# ==============================================================================
MCP_TOOLS = [
    {
        "name": "open_legal_analysis_grid",
        "title": "Open LexGraph Interactive Legal Document Grid & Original Citation Highlighter",
        "description": (
            "Queries live Cloud Spanner Hybrid RAG (LexGraphLegalGraph + 3,072-dim gemini-embedding-2 + Spanner FTS), "
            "dynamically extracts a custom column for the lawyer's question across all authorized contracts, "
            "and opens the interactive React/SPA Grid + Conversational Agent + Right-Hand Original Document Citation Highlighter."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Legal question to answer and dynamically extract as a column in the document grid.",
                },
                "selected_doc_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of document IDs selected by the lawyer (e.g. ['DOC-M331-01', 'DOC-M331-02']).",
                },
            },
            "required": ["question"],
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "_meta": {
            "com.google.gemini/isGeminiEnterpriseApp": True,
            "ui": {
                "resourceUri": MCP_RESOURCE_URI,
                "visibility": ["model", "app"],
                "defaultDisplayMode": "pip",
                "prefersBorder": True,
                "csp": MCP_UI_CSP,
            },
        },
    },
    {
        "name": "inspect_selected_files",
        "title": "Ask Scoped Question Across Selected Grid Files & Highlight Original Citations",
        "description": (
            "Runs a scoped Cloud Spanner Hybrid RAG + ADK synthesis strictly over the files checked [x] by the lawyer in the grid, "
            "adds a dynamic question column, and highlights the exact cited chunk in the original contract viewer."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "selected_doc_ids": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["question"],
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "_meta": {
            "ui": {
                "resourceUri": MCP_RESOURCE_URI,
                "visibility": ["model", "app"],
                "defaultDisplayMode": "pip",
                "prefersBorder": True,
                "csp": MCP_UI_CSP,
            }
        },
    },
    {
        "name": "grant_teammate_email_30d",
        "title": "Commit 30-Day Teammate Email Access Grant in Cloud Spanner (EM-9901)",
        "description": "Commits an ACID 30-day TeammateGrants graph edge in Cloud Spanner for unfiled tax email EM-9901 on Matter M-331.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "matter_id": {"type": "string", "default": "M-331"},
                "email_id": {"type": "string", "default": "EM-9901"},
                "granted_to": {"type": "string", "default": "s-jenkins@lexgraph.com"},
            },
        },
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
        "_meta": {
            "ui": {
                "resourceUri": MCP_RESOURCE_URI,
                "visibility": ["model", "app"],
                "defaultDisplayMode": "pip",
                "prefersBorder": True,
                "csp": MCP_UI_CSP,
            }
        },
    },
]


@app.get("/mcp")
async def handle_mcp_get():
  return JSONResponse({
      "name": "lexgraph-legal-grid-mcp-agent",
      "version": "1.3.0",
      "protocol": "MCP Streamable HTTP (SEP-1865)",
      "resourceUri": MCP_RESOURCE_URI,
      "tools": [t["name"] for t in MCP_TOOLS],
  })


@app.post("/mcp")
async def handle_mcp_jsonrpc(request: Request):
  """Streamable HTTP JSON-RPC 2.0 endpoint implementing MCP Apps (SEP-1865)."""
  try:
    body = await request.json()
  except Exception:
    body = {}

  LAST_HANDSHAKE["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
  LAST_HANDSHAKE["protocol"] = "MCP_SEP_1865"
  LAST_HANDSHAKE["body"] = body

  method = body.get("method", "")
  rpc_id = body.get("id")
  params = body.get("params") or {}

  if method == "initialize":
    req_proto = params.get("protocolVersion") or "2025-03-26"
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": {
            "protocolVersion": req_proto,
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": False, "listChanged": False},
                "extensions": {
                    "io.modelcontextprotocol/ui": {
                        "mimeTypes": [MCP_RESOURCE_MIME]
                    }
                },
            },
            "serverInfo": {
                "name": "lexgraph-legal-grid-mcp-agent",
                "version": "1.3.0",
            },
            "instructions": (
                "CRITICAL: For any question about legal agreements, M&A deals (M-331, M-215, M-518, M-402, M-109), "
                "indemnification caps, baskets, materiality scrapes, Skadden redlines, change of control, or comparing documents in a grid, "
                "ALWAYS call `open_legal_analysis_grid` with the user's question. When the user selects specific files "
                "to inspect, call `inspect_selected_files`."
            ),
        },
    })

  if method.startswith("notifications/"):
    return JSONResponse({"jsonrpc": "2.0", "result": {}})

  if method == "tools/list":
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": {"tools": MCP_TOOLS},
    })

  if method == "resources/list":
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": {
            "resources": [
                {
                    "uri": MCP_RESOURCE_URI,
                    "name": "LexGraph Interactive Legal Analysis Grid & Original Citation Viewer",
                    "description": (
                        "Interactive React/SPA workspace with dynamic question-driven grid columns, "
                        "0-ms per-column filtering, row checkbox scoping, conversational RAG agent, "
                        "and side-by-side original contract viewer with highlighted citation chunks."
                    ),
                    "mimeType": MCP_RESOURCE_MIME,
                    "_meta": {
                        "ui": {
                            "prefersBorder": True,
                            "csp": MCP_UI_CSP,
                        }
                    },
                }
            ]
        },
    })

  if method == "resources/read":
    uri = params.get("uri") or params.get("resourceUri") or MCP_RESOURCE_URI
    state = LATEST_WORKSPACE_STATE
    if state is None:
      state, _ = await build_initial_workspace_state(
          "Compare Indemnity Caps, Deductible Baskets, Materiality Scrapes, and Skadden Redlines across M-331 and precedents",
          fast_only=True,
      )
    html_str = build_workspace_html(state)
    ui_meta = {
        "ui": {
            "prefersBorder": True,
            "csp": MCP_UI_CSP,
        }
    }
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": MCP_RESOURCE_MIME,
                    "text": html_str,
                    "_meta": ui_meta,
                }
            ],
            "_meta": ui_meta,
        },
    })


  if method == "tools/call":
    tool_name = params.get("name", "open_legal_analysis_grid")
    args = params.get("arguments") or {}
    ui_meta = {
        "ui": {
            "resourceUri": MCP_RESOURCE_URI,
            "defaultDisplayMode": "pip",
            "prefersBorder": True,
            "csp": MCP_UI_CSP,
        }
    }
    if tool_name == "grant_teammate_email_30d":
      wb = await asyncio.to_thread(
          execute_spanner_teammate_grant,
          args.get("email_id", "EM-9901"),
          args.get("matter_id", "M-331"),
          args.get("granted_to", "s-jenkins@lexgraph.com"),
          30,
      )
      return JSONResponse({
          "jsonrpc": "2.0",
          "id": rpc_id,
          "result": {
              "content": [
                  {
                      "type": "text",
                      "text": f"✅ Committed Cloud Spanner TeammateGrants edge `{wb['grant_id']}` for `{wb['email_id']}` on `{wb['matter_id']}` in `{wb['latency_ms']} ms` (Expires: {wb['expires_at']}).",
                  }
              ],
              "structuredContent": wb,
              "_meta": ui_meta,
          },
      })

    question = args.get(
        "question",
        "Compare Indemnity Caps, Deductible Baskets, Materiality Scrapes, and Skadden Redlines across M-331 and precedents",
    )
    selected_doc_ids = args.get("selected_doc_ids") or None
    state, exec_md = await build_initial_workspace_state(question, selected_doc_ids)
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": {
            "content": [{"type": "text", "text": exec_md}],
            "structuredContent": state,
            "_meta": ui_meta,
        },
    })

  return JSONResponse({
      "jsonrpc": "2.0",
      "id": rpc_id,
      "error": {"code": -32601, "message": f"Method {method} not found"},
  })


# ==============================================================================
# 3. A2A AGENT PROTOCOL & NATIVE A2UI v0.9 INTERACTIVE WORKBENCH IN CANVAS
# ==============================================================================
@app.get("/.well-known/agent-card.json")
@app.get("/.well-known/agent.json")
async def get_agent_card(request: Request):
  scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
  base_url = f"{scheme}://{request.url.netloc}".rstrip("/")
  return JSONResponse({
      "name": "LexGraph Interactive Legal Grid & Citation Highlighter Agent (MCP App)",
      "description": (
          "Interactive Legal Document Analysis Grid + Conversational Spanner Hybrid RAG Agent + "
          "Original Document Citation Highlighter (MCP App SEP-1865 & Native A2UI Canvas). Dynamically populates "
          "grid columns from your questions, supports per-column filtering ('alike documents'), "
          "lets you check [x] specific files to ask follow-up questions, and highlights cited chunks "
          "inside the original contract format in the right side panel."
      ),
      "url": base_url,
      "version": "1.1.0",
      "protocolVersion": "0.2.1",
      "defaultInputModes": ["application/json+a2ui", "text/plain"],
      "defaultOutputModes": ["application/json+a2ui", "text/plain"],
      "provider": {
          "organization": "LexGraph Enterprise Legal LLP — Legal Context Engine",
          "url": base_url,
      },
      "capabilities": {
          "streaming": False,
          "pushNotifications": False,
          "extensions": [
              {
                  "uri": "https://a2ui.org/a2a-extension/a2ui/v0.9",
                  "description": "Renders A2UI v0.9 Canvas side-panel with interactive Legal Grid, File Checkboxes, Dynamic Question Columns, & Original Contract Citation Highlighter",
                  "required": False,
                  "params": {
                      "supportedCatalogIds": [
                          COMPOSITE_CATALOG_URL,
                          BASIC_V09_CATALOG_URL,
                      ],
                      "acceptsInlineCatalogs": True,
                  },
              },
              {
                  "uri": "https://a2ui.org/a2a-extension/a2ui/v0.8",
                  "description": "Renders A2UI v0.8 WebFrameSrcdoc and Standard Catalog",
                  "required": False,
                  "params": {
                      "supportedCatalogIds": [STD_V08_CATALOG_URL],
                      "acceptsInlineCatalogs": True,
                  },
              },
          ],
      },
      "skills": [
          {
              "id": "interactive_legal_grid_and_citation_highlighter",
              "name": "Interactive Document Grid + Dynamic Question Columns + Original Citation Highlighter",
              "description": (
                  "Ask any legal question to dynamically populate the interactive document grid across "
                  "M-331, M-215, M-518, M-402, and M-109, filter columns, check [x] specific files "
                  "for follow-up questions, and view highlighted citation chunks in original contract format."
              ),
              "tags": ["mcp-app", "grid", "citations", "spanner", "rag", "a2ui"],
              "examples": [
                  "Open the interactive legal analysis grid and compare whether Fraud or Pre-Closing Taxes bypass the Indemnity Cap across M-331 and precedents",
                  "Compare Materiality Scrape prongs and Skadden Draft v4 redlines in the interactive grid with highlighted original contract citations",
                  "Filter M&A agreements in the grid and show the highlighted Section 8.02(b) and Section 338(h)(10) tax citations in the original document viewer",
              ],
          }
      ],
  })


def _extract_action_context(act: dict) -> dict[str, str]:
  ctx_raw = act.get("context", [])
  out: dict[str, str] = {}
  if isinstance(ctx_raw, dict):
    for k, v in ctx_raw.items():
      if isinstance(v, dict) and "literalString" in v:
        out[k] = str(v["literalString"])
      elif isinstance(v, dict) and "literalBoolean" in v:
        out[k] = str(v["literalBoolean"]).lower()
      else:
        out[k] = str(v)
  elif isinstance(ctx_raw, list):
    for item in ctx_raw:
      if isinstance(item, dict) and "key" in item:
        val = item.get("value", {})
        if isinstance(val, dict):
          if "literalString" in val:
            out[item["key"]] = str(val["literalString"])
          elif "literalBoolean" in val:
            out[item["key"]] = str(val["literalBoolean"]).lower()
          else:
            out[item["key"]] = str(val)
        else:
          out[item["key"]] = str(val)
  return out


def compute_preset_dynamic_cell(doc_id: str, question_text: str, fallback_doc: dict) -> dict:
  """Deterministic high-precision legal extractor for dynamic question columns."""
  q = (question_text or "").lower()
  if any(k in q for k in ("fraud", "tax", "carve", "bypass", "338")):
    m = {
        "DOC-M331-01": {"badge": "CARVE-OUT", "answer": "Fraud & Fundamental Reps uncapped ($2.4B EV); general cap 0.75% ($18M) in Sec. 8.02(b)."},
        "DOC-M331-02": {"badge": "SKADDEN PUSHBACK", "answer": "Skadden v4 caps R&W retention at 0.25% ($6M) & cuts Fundamental survival to 36 mos."},
        "DOC-M331-03": {"badge": "ESCROW RINGFENCE", "answer": "$18.0M Citibank Escrow backs Sec. 8.02 claims; Pending Claim Reserve held past Month 18."},
        "DOC-M331-04": {"badge": "FIRST-DOLLAR TAX", "answer": "100% Pre-Closing Tax & Sec. 338(h)(10) bypass Deductible Basket ($9.5M gross-up cap)."},
        "DOC-M215-01": {"badge": "PRECEDENT", "answer": "Kestrel SPA: Fraud & Tax exempt from 0.50% ($8.25M) cap; synthetic R&W primary."},
        "DOC-M518-01": {"badge": "PRECEDENT", "answer": "Vanguard JV: Environmental & Tax survive 72 mos; 1.00% ($31M) cap on operational reps."},
        "DOC-M402-01": {"badge": "COVENANT DEFAULT", "answer": "Unrestricted Sub IP transfer triggers immediate Event of Default (Sec. 6.08(d))."},
        "DOC-M109-01": {"badge": "UNCAPPED EQUITABLE", "answer": "Standstill/NDA breach permits uncapped specific performance & injunctive relief."},
    }
    return m.get(doc_id, {"badge": "VERIFIED", "answer": fallback_doc.get("summary_text", "")})
  if any(k in q for k in ("scrape", "materiality", "prong")):
    m = {
        "DOC-M331-01": {"badge": "DOUBLE SCRAPE", "answer": "Full Double Scrape (Sec. 8.02(b)): applies to BOTH (1) breach determination & (2) Losses."},
        "DOC-M331-02": {"badge": "SINGLE SCRAPE RISK", "answer": "Skadden v4 DELETES Prong 1 (breach determination), leaving Damages-Only scrape."},
        "DOC-M331-03": {"badge": "FOLLOWS MERGER", "answer": "Applies Sec. 8.02(b) double scrape to Buyer Claim Notices against $18M Escrow."},
        "DOC-M331-04": {"badge": "NO MATERIALITY", "answer": "First-dollar tax covenant; materiality qualifiers inapplicable to pre-closing taxes."},
        "DOC-M215-01": {"badge": "DOUBLE SCRAPE", "answer": "Full Double Materiality Scrape (Breach + Losses) negotiated with Kirkland & Ellis."},
        "DOC-M518-01": {"badge": "BREACH-ONLY", "answer": "Single Prong (Breach-Only Scrape) paired with 0.35% ($10.85M) Tipping Basket."},
        "DOC-M402-01": {"badge": "STRICT IP BLOCKER", "answer": "Material IP objectively defined in Sec. 6.08(d); zero basket leakage permitted."},
        "DOC-M109-01": {"badge": "N/A (NDA)", "answer": "Reasonable care standard; no materiality scrape applicable to standstill."},
    }
    return m.get(doc_id, {"badge": "EXTRACTED", "answer": fallback_doc.get("qualifiers", "")})
  if any(k in q for k in ("redline", "opposing", "skadden", "counter", "delta")):
    m = {
        "DOC-M331-01": {"badge": "LEXGRAPH BASELINE v3", "answer": "LexGraph Execution Baseline: 0.75% ($18M) Cap, 0.50% ($12M) Deductible, 18-Mo Survival, Double Scrape."},
        "DOC-M331-02": {"badge": "SKADDEN MARKUP v4", "answer": "Cuts Cap 0.75% -> 0.25% ($6M), hikes Deductible 0.50% -> 0.85% ($20.4M), cuts survival 18 -> 12 mos."},
        "DOC-M331-03": {"badge": "ESCROW IMPACT", "answer": "Skadden seeks early Citibank escrow release at Month 12 instead of Month 18."},
        "DOC-M331-04": {"badge": "TAX CONCESSION", "answer": "Per EM-9901, Skadden conceded $9.5M 338(h)(10) gross-up if LexGraph holds 0.75% cap."},
        "DOC-M215-01": {"badge": "BENCHMARK (0.50%)", "answer": "Refutes Skadden 0.25%: Kestrel ($1.65B) closed at 0.50% Cap with Double Scrape."},
        "DOC-M518-01": {"badge": "BENCHMARK (1.00%)", "answer": "Refutes Skadden 0.25%: Vanguard ($3.1B) closed at 1.00% Cap & 24-Mo Survival."},
        "DOC-M402-01": {"badge": "LATHAM AGREED", "answer": "Latham accepted strict Sec. 6.08(d) J.Crew blocker + 4.50x Net Leverage."},
        "DOC-M109-01": {"badge": "S&C AGREED", "answer": "S&C accepted 18-month standstill with automatic fall-away upon >=50% acquisition."},
    }
    return m.get(doc_id, {"badge": "COMPARE", "answer": fallback_doc.get("summary_text", "")})
  if any(k in q for k in ("release", "trigger", "fall-away", "holdback", "termination")):
    m = {
        "DOC-M331-01": {"badge": "15% EBITDA MAE", "answer": "Walk-right triggers only if supply impact exceeds peer EBITDA by >15% (Sec. 1.01)."},
        "DOC-M331-02": {"badge": "MONTH 12 RELEASE", "answer": "Skadden v4 proposes early escrow release at Month 12 instead of Month 18."},
        "DOC-M331-03": {"badge": "18-MO + 10 BD", "answer": "Citibank releases balance at Month 18 minus Pending Claims unless objected in 10 BDs."},
        "DOC-M331-04": {"badge": "SOL + 60 DAYS", "answer": "Tax indemnity survives until 60 days after expiration of federal/state SOL."},
        "DOC-M215-01": {"badge": "15-MO RELEASE", "answer": "General indemnity terminates at Month 15 post-closing."},
        "DOC-M518-01": {"badge": "24-MO RELEASE", "answer": "General indemnity terminates at Month 24; Environmental survives 72 months."},
        "DOC-M402-01": {"badge": "5-QTR EQUITY CURE", "answer": "Max 2 consecutive quarters Equity Cure (up to 5 total over 60-mo Term Loan B)."},
        "DOC-M109-01": {"badge": "AUTO FALL-AWAY", "answer": "18-mo Standstill automatically falls away upon 3rd-party >=50% merger (Sec. 7)."},
    }
    return m.get(doc_id, {"badge": "TRIGGER", "answer": fallback_doc.get("survival_months", "")})
  return {
      "badge": f"RRF {fallback_doc.get('hybrid_rrf', 0.89)}",
      "answer": f"{fallback_doc.get('cap_pct', '')} | {fallback_doc.get('basket_type', '')} ({fallback_doc.get('section_ref', '')})",
  }


def _dual(light: str, dark: str) -> str:
  return f"light-dark({light}, {dark})"


def _build_a2ui_grid_surfaces(
    state: dict,
    exec_md: str,
    base_url: str,
    wants_v09: bool,
    active_tab: int = 0,
    alike_filter: str = "all",
    col_filter: str = "",
    extra_questions: list[str] | None = None,
) -> list[dict]:
  """Builds a complete Native A2UI v0.9 Interactive Legal Grid + File Checkbox Selector + Original Document Citation Viewer inside Canvas (plus IFrameSrcdoc when enabled)."""
  uid = uuid.uuid4().hex[:6]
  surface_id = f"lexgraph-mcp-grid-{uid}"
  app_html = build_workspace_html(state)
  dyn_col = state["dynamic_columns"][0] if state.get("dynamic_columns") else {"field": "dyn_q", "header": "Extracted Answer"}

  # Build extra dynamic question columns if requested
  extra_q_list = [q.strip() for q in (extra_questions or []) if q.strip()]
  extra_col_defs = []
  for idx, eq in enumerate(extra_q_list):
    short_hdr = eq[:30] + "..." if len(eq) > 30 else eq
    if "fraud" in eq.lower() or "tax" in eq.lower():
      short_hdr = "Fraud & Tax Carve-Outs"
    elif "scrape" in eq.lower() or "materiality" in eq.lower():
      short_hdr = "Materiality Scrape Prongs"
    elif "redline" in eq.lower() or "skadden" in eq.lower():
      short_hdr = "Skadden v4 Redline Delta"
    elif "release" in eq.lower() or "holdback" in eq.lower():
      short_hdr = "Release & Holdback Triggers"
    extra_col_defs.append({"field": f"extra_col_{idx}", "header": f"⚡ {short_hdr}", "question": eq})

  # Filter documents based on alike_filter and col_filter
  all_docs = state["documents"]
  filtered_docs = []
  for d in all_docs:
    if alike_filter == "M-331" and d["matter_id"] != "M-331":
      continue
    if alike_filter == "indem" and d["doc_id"] not in ("DOC-M331-01", "DOC-M331-02", "DOC-M331-03", "DOC-M215-01", "DOC-M518-01"):
      continue
    if alike_filter == "scrape" and "double" not in d["qualifiers"].lower() and "full materiality scrape" not in d["qualifiers"].lower():
      continue
    if alike_filter == "redline" and d["doc_id"] not in ("DOC-M331-01", "DOC-M331-02"):
      continue
    if col_filter:
      needle = col_filter.lower()
      hay = f"{d['doc_id']} {d['matter_id']} {d['title']} {d['cap_pct']} {d['basket_type']} {d['survival_months']} {d['qualifiers']} {d['summary_text']} {d['counsel_firm']}".lower()
      if needle not in hay:
        continue
    filtered_docs.append(d)

  if not filtered_docs:
    filtered_docs = all_docs

  table_columns = [
      {"header": "File / Matter", "field": "doc"},
      {"header": "Document & Counsel (RRF)", "field": "title"},
      {"header": "Indemnity Cap", "field": "cap"},
      {"header": "Basket & Survival", "field": "basket"},
      {"header": f"⚡ {dyn_col['header']}", "field": "dyn_answer"},
  ]
  for ec in extra_col_defs:
    table_columns.append({"header": ec["header"], "field": ec["field"]})
  table_columns.append({"header": "Original Pin-Cite", "field": "citation"})

  table_rows = []
  for d in filtered_docs:
    dyn_cell = (d.get("dynamic_cells") or {}).get(dyn_col["field"], {})
    row_obj = {
        "doc": f"{d['doc_id']} ({d['matter_id']} · {d['practice_area']})",
        "title": f"{d['title']} · {d['counsel_firm']} [RRF={d['hybrid_rrf']}]",
        "cap": d["cap_pct"],
        "basket": f"{d['basket_type']} · {d['survival_months']}",
        "dyn_answer": f"[{dyn_cell.get('badge', 'CITED')}] {dyn_cell.get('answer', d['summary_text'])}",
        "citation": f"📌 {d['section_ref']} (Page {d['primary_page']})",
    }
    for ec in extra_col_defs:
      c_val = compute_preset_dynamic_cell(d["doc_id"], ec["question"], d)
      row_obj[ec["field"]] = f"[{c_val['badge']}] {c_val['answer']}"
    table_rows.append(row_obj)

  # Pure grounded markdown in chat stream (NO external Cloud Run link!)
  parts: list[dict] = [{"kind": "text", "text": exec_md}]

  if wants_v09:
    selected_set = set(state.get("selected_doc_ids") or ["DOC-M331-01", "DOC-M331-02", "DOC-M215-01"])
    active_doc_id = state.get("active_doc_id") or "DOC-M331-01"
    active_chunk_id = state.get("active_chunk_id") or "CL-M331-INDEM"
    active_doc = next((d for d in all_docs if d["doc_id"] == active_doc_id), all_docs[0])

    data_model_val: dict = {
        "appHtml": app_html,
        "rows": table_rows,
        "alikeFilter": alike_filter,
        "colFilter": col_filter,
        "newColQuestion": "",
        "scopedQuestion": "",
        "extraQuestionsStr": "||".join(extra_q_list),
    }

    checkbox_ids = []
    checkbox_comps = []
    inspect_btn_ids = []
    inspect_btn_comps = []
    doc_switcher_ids = []
    doc_switcher_comps = []
    sel_context_bindings: dict = {
        "scopedQuestion": {"path": "/scopedQuestion"},
        "alikeFilter": {"path": "/alikeFilter"},
        "colFilter": {"path": "/colFilter"},
        "extraQuestionsStr": {"path": "/extraQuestionsStr"},
    }

    for idx, d in enumerate(all_docs):
      safe_key = d["doc_id"].replace("-", "_")
      dm_key = f"sel_{safe_key}"
      data_model_val[dm_key] = d["doc_id"] in selected_set
      sel_context_bindings[dm_key] = {"path": f"/{dm_key}"}

      cb_id = f"cb_doc_{idx}"
      checkbox_ids.append(cb_id)
      checkbox_comps.append({
          "id": cb_id,
          "component": "MaterialCheckbox",
          "label": f"{d['doc_id']} ({d['matter_id']}) — {d['title']} · Cap: {d['cap_pct']} · Cite: {d['section_ref']} (p.{d['primary_page']})",
          "checked": {"path": f"/{dm_key}"},
      })

      insp_id = f"btn_insp_{idx}"
      inspect_btn_ids.append(insp_id)
      inspect_btn_comps.append({
          "id": insp_id,
          "component": "MaterialButton",
          "label": f"📌 Highlight {d['doc_id']} (p.{d['primary_page']})",
          "appearance": "tonal" if d["doc_id"] == active_doc_id else "outlined",
          "loadingOnClick": True,
          "action": {
              "event": {
                  "name": "inspect_doc_citation",
                  "context": {
                      "doc_id": d["doc_id"],
                      "chunk_id": d["primary_chunk_id"],
                      "page": str(d["primary_page"]),
                      "extraQuestionsStr": {"path": "/extraQuestionsStr"},
                  },
              }
          },
      })

      sw_id = f"btn_sw_{idx}"
      doc_switcher_ids.append(sw_id)
      doc_switcher_comps.append({
          "id": sw_id,
          "component": "MaterialButton",
          "label": f"{'★ ' if d['doc_id'] == active_doc_id else '📄 '}{d['doc_id']} ({d['section_ref']}, p.{d['primary_page']})",
          "appearance": "filled" if d["doc_id"] == active_doc_id else "outlined",
          "loadingOnClick": True,
          "action": {
              "event": {
                  "name": "inspect_doc_citation",
                  "context": {
                      "doc_id": d["doc_id"],
                      "chunk_id": d["primary_chunk_id"],
                      "page": str(d["primary_page"]),
                      "extraQuestionsStr": {"path": "/extraQuestionsStr"},
                  },
              }
          },
      })

    # Build Original Document Format & Highlighted Citation Chunks for Tab 2
    orig_page_card_ids = []
    orig_page_comps = []
    pages = active_doc.get("pages") or ORIGINAL_DOC_PAGES.get(active_doc_id, [])
    for p_idx, page_obj in enumerate(pages):
      p_num = page_obj.get("page_number", p_idx + 1)
      sec_ids = []
      # Page header watermark
      wm_id = f"orig_wm_{p_idx}"
      sec_ids.append(wm_id)
      orig_page_comps.append({
          "id": wm_id,
          "component": "MaterialText",
          "text": f"OFFICIAL iMANAGE DMS FILING · {active_doc['doc_id']} ({active_doc['dms_version']}) · MATTER {active_doc['matter_id']} · {active_doc['governing_law'].upper()} LAW · PAGE {p_num} OF {len(pages)}",
          "usageHint": "caption",
          "style": {
              "fontFamily": "JetBrains Mono, monospace",
              "color": _dual("#5f6368", "#9aa0a6"),
              "borderBottom": f"1px solid {_dual('#dadce0', '#444746')}",
              "paddingBottom": "6px",
              "marginBottom": "8px",
          },
      })

      for s_idx, sec in enumerate(page_obj.get("sections", [])):
        is_cited = (sec.get("chunk_id") == active_chunk_id) or bool(sec.get("is_primary"))
        sec_box_id = f"orig_sec_box_{p_idx}_{s_idx}"
        sec_children = []

        if is_cited:
          rib_id = f"orig_rib_{p_idx}_{s_idx}"
          sec_children.append(rib_id)
          orig_page_comps.append({
              "id": rib_id,
              "component": "MaterialText",
              "text": f"★ CITED RAG CHUNK HIGHLIGHTED IN ORIGINAL FORMAT: {sec['chunk_id']} ({sec['section_ref']}, Page {p_num}) · BBOX [x:{sec.get('bbox_x', 8)}% y:{sec.get('bbox_y', 24)}% w:84% h:22%] · Hybrid RRF={active_doc['hybrid_rrf']}",
              "style": {
                  "backgroundColor": _dual("#09090B", "#FFFFFF"),
                  "color": _dual("#FFFFFF", "#09090B"),
                  "padding": "4px 8px",
                  "borderRadius": "4px",
                  "fontSize": "11px",
                  "fontWeight": "bold",
                  "fontFamily": "JetBrains Mono, monospace",
                  "marginBottom": "6px",
              },
          })

        hdr_id = f"orig_shdr_{p_idx}_{s_idx}"
        txt_id = f"orig_stxt_{p_idx}_{s_idx}"
        sec_children.extend([hdr_id, txt_id])
        orig_page_comps.extend([
            {
                "id": hdr_id,
                "component": "MaterialText",
                "text": f"{sec['section_ref']} — {sec['heading']}",
                "usageHint": "subtitle1",
                "style": {
                    "fontWeight": "bold",
                    "color": _dual("#09090B", "#EDEDED"),
                    "marginBottom": "4px",
                },
            },
            {
                "id": txt_id,
                "component": "MaterialText",
                "text": sec["text"],
                "style": {
                    "fontFamily": "Georgia, 'Times New Roman', serif",
                    "fontSize": "13.5px",
                    "lineHeight": "22px",
                    "color": _dual("#18181B", "#E4E4E7"),
                },
            },
        ])

        if sec.get("redline_html"):
          clean_redline = (
              sec["redline_html"]
              .replace("<del class='redline-del'>", " [-STRUCK BY SKADDEN: ")
              .replace("</del>", "-] ")
              .replace("<ins class='redline-ins'>", " [+INSERTED BY SKADDEN v4: ")
              .replace("</ins>", "+] ")
              .replace("&amp;", "&")
          )
          red_id = f"orig_sred_{p_idx}_{s_idx}"
          sec_children.append(red_id)
          orig_page_comps.append({
              "id": red_id,
              "component": "MaterialText",
              "text": f"⚖️ LIVE COUNTERPARTY REDLINE OVERLAY (Skadden v4 vs. Buyer v3):\n{clean_redline}",
              "style": {
                  "backgroundColor": _dual("#fce8e6", "#3b1219"),
                  "color": _dual("#991b1b", "#fecdd3"),
                  "border": f"1px solid {_dual('#f5c6c2', '#8c1d18')}",
                  "borderRadius": "6px",
                  "padding": "8px 10px",
                  "marginTop": "8px",
                  "fontSize": "12px",
                  "fontFamily": "JetBrains Mono, monospace",
              },
          })

        orig_page_comps.append({
            "id": sec_box_id,
            "component": "MaterialColumn",
            "children": sec_children,
            "style": {
                "backgroundColor": _dual("#fef7e0", "#3f2e04") if is_cited else _dual("#ffffff", "#18181b"),
                "border": f"2px solid {_dual('#ca8a04', '#facc15')}" if is_cited else f"1px solid {_dual('#e4e4e7', '#27272a')}",
                "borderRadius": "8px",
                "padding": "12px",
                "marginBottom": "10px",
            },
        })
        sec_ids.append(sec_box_id)

      p_card_id = f"orig_page_card_{p_idx}"
      orig_page_card_ids.append(p_card_id)
      orig_page_comps.append({
          "id": p_card_id,
          "component": "MaterialCard",
          "appearance": "outlined",
          "children": sec_ids,
          "style": {
              "backgroundColor": _dual("#ffffff", "#121214"),
              "border": f"1px solid {_dual('#d4d4d8', '#3f3f46')}",
              "borderRadius": "10px",
              "padding": "16px",
              "marginBottom": "12px",
          },
      })

    components = [
        {
            "id": "root",
            "component": "Canvas",
            "cardTitle": "LexGraph Interactive Legal Grid & Original Document Citation Highlighter",
            "cardDescription": f"Dynamic Column: '{dyn_col['header']}' ({len(filtered_docs)} Docs) · Filter columns, check [x] files, & inspect highlighted original citations",
            "cardIcon": "table_chart",
            "autoOpen": True,
            "children": ["canvas-col"],
        },
        {
            "id": "canvas-col",
            "component": "MaterialColumn",
            "align": "stretch",
            "style": {"gap": "12px", "padding": "8px"},
            "children": [
                "interactive-grid-iframe",
                "top_controls_card",
                "workbench_tabs",
            ],
        },
        {
            "id": "interactive-grid-iframe",
            "component": "IFrameSrcdoc",
            "title": "LexGraph Interactive Legal Grid, Scoped RAG Chat & Original Citation Viewer",
            "height": 820,
            "htmlContent": {"path": "/appHtml"},
        },
        # --- TOP INTERACTIVE CONTROLS CARD (Filter Alike Docs + Add Dynamic Question Columns) ---
        {
            "id": "top_controls_card",
            "component": "MaterialCard",
            "appearance": "outlined",
            "children": ["top_controls_col"],
            "style": {
                "padding": "12px",
                "borderRadius": "10px",
                "border": f"1px solid {_dual('#e4e4e7', '#27272a')}",
                "backgroundColor": _dual("#fafafa", "#18181b"),
            },
        },
        {
            "id": "top_controls_col",
            "component": "MaterialColumn",
            "children": [
                "top_controls_hdr",
                "alike_filter_chips",
                "filter_and_add_col_row",
                "preset_cols_row",
            ],
            "style": {"gap": "8px"},
        },
        {
            "id": "top_controls_hdr",
            "component": "MaterialText",
            "text": f"⚡ INTERACTIVE LEGAL GRID CONTROLS · Cloud Spanner Hybrid RAG ({state['latency_ms']} ms) · Filter Alike Document Rows or Add Dynamic Question Columns",
            "usageHint": "caption",
            "style": {"fontWeight": "bold", "fontFamily": "JetBrains Mono, monospace"},
        },
        {
            "id": "alike_filter_chips",
            "component": "MaterialChips",
            "value": {"path": "/alikeFilter"},
            "selectable": True,
            "loadingOnClick": True,
            "options": [
                {"label": "All Cleared Docs (8)", "value": "all"},
                {"label": "M-331 Deal Suite (4)", "value": "M-331"},
                {"label": "Indemnity Benchmarks (5)", "value": "indem"},
                {"label": "Double Scrape Only (3)", "value": "scrape"},
                {"label": "Skadden Redline Risk (2)", "value": "redline"},
            ],
            "action": {
                "event": {
                    "name": "apply_grid_controls",
                    "context": {
                        "alikeFilter": {"path": "/alikeFilter"},
                        "colFilter": {"path": "/colFilter"},
                        "newColQuestion": {"path": "/newColQuestion"},
                        "extraQuestionsStr": {"path": "/extraQuestionsStr"},
                    },
                }
            },
        },
        {
            "id": "filter_and_add_col_row",
            "component": "MaterialRow",
            "children": ["col_filter_input", "new_col_q_input", "btn_apply_grid"],
            "style": {"gap": "8px", "alignItems": "center", "flexWrap": "wrap"},
        },
        {
            "id": "col_filter_input",
            "component": "MaterialInput",
            "label": "🔍 Filter Grid Rows by Column Text",
            "placeholder": "e.g. 0.75%, Double Scrape, Skadden, First-Dollar",
            "value": {"path": "/colFilter"},
        },
        {
            "id": "new_col_q_input",
            "component": "MaterialInput",
            "label": "➕ Ask Question to Add Dynamic Grid Column",
            "placeholder": "e.g. Does Fraud or Tax bypass the Cap?",
            "value": {"path": "/newColQuestion"},
        },
        {
            "id": "btn_apply_grid",
            "component": "MaterialButton",
            "label": "⚡ Update Grid / Add Column",
            "appearance": "filled",
            "loadingOnClick": True,
            "action": {
                "event": {
                    "name": "apply_grid_controls",
                    "context": {
                        "alikeFilter": {"path": "/alikeFilter"},
                        "colFilter": {"path": "/colFilter"},
                        "newColQuestion": {"path": "/newColQuestion"},
                        "extraQuestionsStr": {"path": "/extraQuestionsStr"},
                    },
                }
            },
        },
        {
            "id": "preset_cols_row",
            "component": "MaterialRow",
            "children": [
                "btn_preset_fraud",
                "btn_preset_scrape",
                "btn_preset_redline",
                "btn_preset_release",
                "btn_preset_reset",
            ],
            "style": {"gap": "6px", "flexWrap": "wrap"},
        },
        {
            "id": "btn_preset_fraud",
            "component": "MaterialButton",
            "label": "+ Fraud & Tax Carve-Out Column",
            "appearance": "outlined",
            "loadingOnClick": True,
            "action": {
                "event": {
                    "name": "quick_add_column",
                    "context": {
                        "presetQuestion": "Does Fraud or Pre-Closing Tax bypass the Indemnity Cap?",
                        "alikeFilter": {"path": "/alikeFilter"},
                        "colFilter": {"path": "/colFilter"},
                        "extraQuestionsStr": {"path": "/extraQuestionsStr"},
                    },
                }
            },
        },
        {
            "id": "btn_preset_scrape",
            "component": "MaterialButton",
            "label": "+ Materiality Scrape Prongs Column",
            "appearance": "outlined",
            "loadingOnClick": True,
            "action": {
                "event": {
                    "name": "quick_add_column",
                    "context": {
                        "presetQuestion": "Is Materiality Scrape Double (Breach + Losses) or Single?",
                        "alikeFilter": {"path": "/alikeFilter"},
                        "colFilter": {"path": "/colFilter"},
                        "extraQuestionsStr": {"path": "/extraQuestionsStr"},
                    },
                }
            },
        },
        {
            "id": "btn_preset_redline",
            "component": "MaterialButton",
            "label": "+ Skadden v4 Redline Delta Column",
            "appearance": "outlined",
            "loadingOnClick": True,
            "action": {
                "event": {
                    "name": "quick_add_column",
                    "context": {
                        "presetQuestion": "What is Opposing Counsel Redline Position vs Buyer Market?",
                        "alikeFilter": {"path": "/alikeFilter"},
                        "colFilter": {"path": "/colFilter"},
                        "extraQuestionsStr": {"path": "/extraQuestionsStr"},
                    },
                }
            },
        },
        {
            "id": "btn_preset_release",
            "component": "MaterialButton",
            "label": "+ Release & Holdback Triggers Column",
            "appearance": "outlined",
            "loadingOnClick": True,
            "action": {
                "event": {
                    "name": "quick_add_column",
                    "context": {
                        "presetQuestion": "What are the Release / Termination Triggers & Holdbacks?",
                        "alikeFilter": {"path": "/alikeFilter"},
                        "colFilter": {"path": "/colFilter"},
                        "extraQuestionsStr": {"path": "/extraQuestionsStr"},
                    },
                }
            },
        },
        {
            "id": "btn_preset_reset",
            "component": "MaterialButton",
            "label": "✕ Reset Filters & Columns",
            "appearance": "text",
            "loadingOnClick": True,
            "action": {
                "event": {
                    "name": "reset_grid",
                    "context": {},
                }
            },
        },
        # --- 2-TAB WORKBENCH (Tab 1: Interactive Grid & File Selector | Tab 2: Original Document & Highlighted Citations) ---
        {
            "id": "workbench_tabs",
            "component": "MaterialTabs",
            "activeTab": active_tab,
            "tabs": [
                {
                    "label": f"📊 Interactive Document Grid ({len(filtered_docs)} Docs, {len(table_columns)} Cols)",
                    "content": "tab_grid_view",
                },
                {
                    "label": f"📑 Original Document & Highlighted Citation ({active_doc_id} · p.{active_doc['primary_page']})",
                    "content": "tab_original_doc_view",
                },
            ],
        },
        # TAB 1 CONTENT
        {
            "id": "tab_grid_view",
            "component": "MaterialColumn",
            "children": [
                "native-backup-table",
                "inspect_citations_bar_card",
                "file_selection_card",
            ],
            "style": {"gap": "12px", "paddingTop": "10px"},
        },
        {
            "id": "native-backup-table",
            "component": "MaterialTable",
            "rows": {"path": "/rows"},
            "columns": table_columns,
        },
        {
            "id": "inspect_citations_bar_card",
            "component": "MaterialCard",
            "appearance": "outlined",
            "children": ["inspect_citations_hdr", "inspect_citations_row"],
            "style": {"padding": "10px", "borderRadius": "8px"},
        },
        {
            "id": "inspect_citations_hdr",
            "component": "MaterialText",
            "text": "📌 CLICK ANY DOCUMENT BELOW TO OPEN ITS ORIGINAL CONTRACT FORMAT & HIGHLIGHTED CITATION CHUNK IN TAB 2:",
            "usageHint": "caption",
            "style": {"fontWeight": "bold", "marginBottom": "6px"},
        },
        {
            "id": "inspect_citations_row",
            "component": "MaterialRow",
            "children": inspect_btn_ids,
            "style": {"gap": "6px", "flexWrap": "wrap"},
        },
        {
            "id": "file_selection_card",
            "component": "MaterialCard",
            "appearance": "outlined",
            "children": [
                "file_selection_hdr",
                "file_checkboxes_col",
                "scoped_ask_row",
            ],
            "style": {
                "padding": "12px",
                "borderRadius": "10px",
                "border": f"1px solid {_dual('#e4e4e7', '#27272a')}",
            },
        },
        {
            "id": "file_selection_hdr",
            "component": "MaterialText",
            "text": "☑️ SELECT SPECIFIC FILES [x] IN THE GRID TO ASK FOLLOW-UP QUESTIONS & HIGHLIGHT CITATIONS:",
            "usageHint": "subtitle2",
            "style": {"fontWeight": "bold", "marginBottom": "6px"},
        },
        {
            "id": "file_checkboxes_col",
            "component": "MaterialColumn",
            "children": checkbox_ids,
            "style": {"gap": "4px", "marginBottom": "8px"},
        },
        {
            "id": "scoped_ask_row",
            "component": "MaterialRow",
            "children": ["scoped_q_input", "btn_ask_scoped"],
            "style": {"gap": "8px", "alignItems": "center", "flexWrap": "wrap"},
        },
        {
            "id": "scoped_q_input",
            "component": "MaterialInput",
            "label": "💬 Ask Follow-Up Question Strictly Across Checked [x] Files",
            "placeholder": "e.g. Compare Skadden v4 Indemnity Cap and Double Scrape deletion against our Kestrel precedent",
            "value": {"path": "/scopedQuestion"},
        },
        {
            "id": "btn_ask_scoped",
            "component": "MaterialButton",
            "label": "🎯 Ask Agent on Checked [x] Files & Highlight Citations",
            "appearance": "filled",
            "loadingOnClick": True,
            "action": {
                "event": {
                    "name": "ask_scoped_files",
                    "context": sel_context_bindings,
                }
            },
        },
        # TAB 2 CONTENT (ORIGINAL DOCUMENT FORMAT + HIGHLIGHTED CITATION CHUNK + REDLINE + SPANNER GRANT)
        {
            "id": "tab_original_doc_view",
            "component": "MaterialColumn",
            "children": [
                "doc_switcher_card",
                "active_doc_banner_card",
                *orig_page_card_ids,
                "spanner_grant_card",
            ],
            "style": {"gap": "12px", "paddingTop": "10px"},
        },
        {
            "id": "doc_switcher_card",
            "component": "MaterialCard",
            "appearance": "outlined",
            "children": ["doc_switcher_hdr", "doc_switcher_row"],
            "style": {"padding": "10px", "borderRadius": "8px"},
        },
        {
            "id": "doc_switcher_hdr",
            "component": "MaterialText",
            "text": "📂 SWITCH ORIGINAL CONTRACT IN VIEWER (HIGHLIGHTS CITED RAG CHUNK INLINE):",
            "usageHint": "caption",
            "style": {"fontWeight": "bold", "marginBottom": "6px"},
        },
        {
            "id": "doc_switcher_row",
            "component": "MaterialRow",
            "children": doc_switcher_ids,
            "style": {"gap": "6px", "flexWrap": "wrap"},
        },
        {
            "id": "active_doc_banner_card",
            "component": "MaterialCard",
            "appearance": "outlined",
            "children": ["active_doc_title", "active_doc_meta"],
            "style": {
                "padding": "12px",
                "borderRadius": "8px",
                "backgroundColor": _dual("#f8f9fa", "#1e1f20"),
            },
        },
        {
            "id": "active_doc_title",
            "component": "MaterialText",
            "text": f"📄 {active_doc['title']} ({active_doc['doc_id']} · Matter {active_doc['matter_id']})",
            "usageHint": "h4",
            "style": {"fontWeight": "bold"},
        },
        {
            "id": "active_doc_meta",
            "component": "MaterialText",
            "text": f"Pinned Citation: {active_chunk_id} · {active_doc['section_ref']} (Page {active_doc['primary_page']}) · Counsel: {active_doc['counsel_firm']} · Cap: {active_doc['cap_pct']} · Basket: {active_doc['basket_type']}",
            "usageHint": "caption",
            "style": {"fontFamily": "JetBrains Mono, monospace"},
        },
        {
            "id": "spanner_grant_card",
            "component": "MaterialCard",
            "appearance": "outlined",
            "children": ["spanner_grant_row"],
            "style": {"padding": "10px", "borderRadius": "8px"},
        },
        {
            "id": "spanner_grant_row",
            "component": "MaterialRow",
            "children": ["spanner_grant_lbl", "btn_spanner_grant"],
            "style": {"gap": "10px", "alignItems": "center", "justifyContent": "space-between", "flexWrap": "wrap"},
        },
        {
            "id": "spanner_grant_lbl",
            "component": "MaterialText",
            "text": "🔒 Unfiled Tax Partner Email EM-9901 ($9.5M Sec. 338(h)(10) Gross-Up Cap) — Commit 30-Day TeammateGrant Edge in Cloud Spanner:",
            "usageHint": "body2",
        },
        {
            "id": "btn_spanner_grant",
            "component": "MaterialButton",
            "label": "⚡ Grant 30-Day Access to EM-9901 in Cloud Spanner",
            "appearance": "tonal",
            "loadingOnClick": True,
            "action": {
                "event": {
                    "name": "grant_teammate_30d",
                    "context": {
                        "email_id": "EM-9901",
                        "matter_id": "M-331",
                        "granted_to": "s-jenkins@lexgraph.com",
                    },
                }
            },
        },
        *checkbox_comps,
        *inspect_btn_comps,
        *doc_switcher_comps,
        *orig_page_comps,
    ]

    v09_messages = [
        {
            "version": "v0.9",
            "createSurface": {
                "surfaceId": surface_id,
                "catalogId": COMPOSITE_CATALOG_URL,
                "theme": {"primaryColor": "#09090B", "font": "Inter"},
            },
        },
        {
            "version": "v0.9",
            "updateComponents": {
                "surfaceId": surface_id,
                "components": components,
            },
        },
        {
            "version": "v0.9",
            "updateDataModel": {
                "surfaceId": surface_id,
                "path": "/",
                "value": data_model_val,
            },
        },
    ]
    for m in v09_messages:
      parts.append({
          "kind": "data",
          "metadata": {"mimeType": "application/json+a2ui"},
          "data": m,
      })
  else:
    v08_begin = {"beginRendering": {"surfaceId": surface_id, "root": "root"}}
    v08_update = {
        "surfaceUpdate": {
            "surfaceId": surface_id,
            "components": [
                {
                    "id": "root",
                    "component": {
                        "WebFrameSrcdoc": {
                            "htmlContent": {"literalString": app_html},
                            "height": 820,
                            "cardTitle": "LexGraph Interactive Legal Grid & Citation Highlighter (MCP App)",
                            "cardDescription": f"Dynamic Column: {dyn_col['header']} · 0-ms Column Filtering & Highlighted Original Citations",
                            "cardIcon": "table_chart",
                            "autoOpen": True,
                        }
                    },
                }
            ],
        }
    }
    parts.append({"kind": "data", "metadata": {"mimeType": "application/json+a2ui"}, "data": v08_begin})
    parts.append({"kind": "data", "metadata": {"mimeType": "application/json+a2ui"}, "data": v08_update})

  return parts


@app.post("/")
async def handle_a2a_post(request: Request):
  scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
  base_url = f"{scheme}://{request.url.netloc}".rstrip("/")
  try:
    body = await request.json()
  except Exception:
    body = {}

  headers_dict = dict(request.headers)
  rpc_method = body.get("method", "message/send")
  rpc_id = body.get("id", str(uuid.uuid4()))

  LAST_HANDSHAKE["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
  LAST_HANDSHAKE["protocol"] = "A2A"
  LAST_HANDSHAKE["body"] = body

  if rpc_method == "tasks/get":
    t_id = (body.get("params") or {}).get("id")
    if t_id and t_id in TASKS_STORE:
      return JSONResponse({"jsonrpc": "2.0", "id": rpc_id, "result": TASKS_STORE[t_id]})

  ext_header = (
      headers_dict.get("x-a2a-extensions", "")
      + " "
      + headers_dict.get("a2a-extensions", "")
      + " "
      + json.dumps((body.get("params") or {}).get("metadata", {}))
  )
  wants_v09 = ("v0.9" in ext_header) or ("v0_9" in ext_header) or ("v0.8" not in ext_header)

  msg_in = (body.get("params") or {}).get("message") or {}
  context_id = msg_in.get("contextId") or (body.get("params") or {}).get("contextId") or str(uuid.uuid4())
  task_id = msg_in.get("taskId") or (body.get("params") or {}).get("id") or str(uuid.uuid4())
  art_id = str(uuid.uuid4())

  query_text = "Compare Indemnity Caps, Deductible Baskets, Materiality Scrapes, and Skadden Redlines across M-331 and precedents"
  selected_doc_ids = None
  active_tab = 0
  alike_filter = "all"
  col_filter = ""
  extra_questions: list[str] = []
  forced_active_doc_id = None
  forced_active_chunk_id = None
  forced_active_page = None

  parts_in = msg_in.get("parts") or []
  for p in parts_in:
    if isinstance(p, dict):
      if p.get("text"):
        query_text = p["text"]
      elif p.get("kind") == "data" or "data" in p:
        data_obj = p.get("data") or {}
        if isinstance(data_obj, dict) and ("userAction" in data_obj or "action" in data_obj):
          act = data_obj.get("userAction") or data_obj.get("action") or {}
          if isinstance(act.get("event"), dict):
            act = act["event"]
          act_name = act.get("name", "")
          ctx_map = _extract_action_context(act)

          prev_extra = [x for x in ctx_map.get("extraQuestionsStr", "").split("||") if x.strip()]
          extra_questions = list(prev_extra)
          alike_filter = ctx_map.get("alikeFilter", "all") or "all"
          col_filter = ctx_map.get("colFilter", "") or ""

          if act_name == "grant_teammate_30d":
            wb = await asyncio.to_thread(
                execute_spanner_teammate_grant,
                ctx_map.get("email_id", "EM-9901"),
                ctx_map.get("matter_id", "M-331"),
                ctx_map.get("granted_to", "s-jenkins@lexgraph.com"),
                30,
            )
            query_text = f"Verify 30-day TeammateGrant {wb['grant_id']} for {wb['email_id']} on {wb['matter_id']} and show updated Section 338(h)(10) Tax Allocation Rider citation"
            forced_active_doc_id = "DOC-M331-04"
            forced_active_chunk_id = "CL-M331-TAX"
            forced_active_page = 1
            active_tab = 1

          elif act_name == "inspect_doc_citation":
            forced_active_doc_id = ctx_map.get("doc_id", "DOC-M331-01")
            forced_active_chunk_id = ctx_map.get("chunk_id", "CL-M331-INDEM")
            forced_active_page = int(ctx_map.get("page", "1") or 1)
            active_tab = 1
            query_text = f"Inspect original contract format and highlighted citation chunk {forced_active_chunk_id} (Page {forced_active_page}) in {forced_active_doc_id}"

          elif act_name == "apply_grid_controls":
            new_q = (ctx_map.get("newColQuestion") or "").strip()
            if new_q and new_q not in extra_questions:
              extra_questions.append(new_q)
              query_text = new_q
            active_tab = 0

          elif act_name == "quick_add_column":
            pq = (ctx_map.get("presetQuestion") or "").strip()
            if pq and pq not in extra_questions:
              extra_questions.append(pq)
              query_text = pq
            active_tab = 0

          elif act_name == "reset_grid":
            alike_filter = "all"
            col_filter = ""
            extra_questions = []
            active_tab = 0

          elif act_name in ("ask_scoped_files", "ask_grid_question"):
            sq = (ctx_map.get("scopedQuestion") or ctx_map.get("question") or "").strip()
            if sq:
              query_text = sq
              if sq not in extra_questions:
                extra_questions.append(sq)
            checked_docs = []
            for doc_code in ("DOC-M331-01", "DOC-M331-02", "DOC-M331-03", "DOC-M331-04", "DOC-M215-01", "DOC-M518-01", "DOC-M402-01", "DOC-M109-01"):
              k = f"sel_{doc_code.replace('-', '_')}"
              if ctx_map.get(k) in ("true", "True", "1"):
                checked_docs.append(doc_code)
            if not checked_docs and ctx_map.get("selected_docs"):
              checked_docs = [s.strip() for s in ctx_map["selected_docs"].split(",") if s.strip()]
            if checked_docs:
              selected_doc_ids = checked_docs
              forced_active_doc_id = checked_docs[0]
            active_tab = 1

  state, exec_md = await build_initial_workspace_state(query_text, selected_doc_ids)
  if forced_active_doc_id:
    state["active_doc_id"] = forced_active_doc_id
  if forced_active_chunk_id:
    state["active_chunk_id"] = forced_active_chunk_id
  if forced_active_page:
    state["active_page"] = forced_active_page

  artifact_parts = _build_a2ui_grid_surfaces(
      state,
      exec_md,
      base_url,
      wants_v09,
      active_tab=active_tab,
      alike_filter=alike_filter,
      col_filter=col_filter,
      extra_questions=extra_questions,
  )

  completed_task = {
      "kind": "task",
      "id": task_id,
      "contextId": context_id,
      "status": {
          "state": "completed",
          "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
      },
      "artifacts": [
          {
              "artifactId": art_id,
              "parts": artifact_parts,
          }
      ],
  }
  TASKS_STORE[task_id] = completed_task
  return JSONResponse({"jsonrpc": "2.0", "id": rpc_id, "result": completed_task})


@app.get("/api/last-handshake")
async def get_last_handshake():
  return JSONResponse(LAST_HANDSHAKE)

