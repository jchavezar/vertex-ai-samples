#!/usr/bin/env python3
"""
Generates all synthetic legal agreements, opposing counsel redlines, escrow schedules,
credit agreements, NDAs, and unfiled tax emails used across the LexGraph Spanner Hybrid
GraphRAG & MCP App (SEP-1865) Demo.

Outputs:
- demo-documents/pdf/*.pdf  (Compiled via Headless Chrome)
- demo-documents/text/*.txt (Plain text with section headers & clause IDs)
"""

import os
import re
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "pdf")
TXT_DIR = os.path.join(BASE_DIR, "text")
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(TXT_DIR, exist_ok=True)

DOCUMENTS = [
    {
        "doc_id": "DOC-M331-01",
        "filename": "DOC-M331-01_M331_Brightwater_Merger_Agreement_Executed",
        "title": "AGREEMENT AND PLAN OF MERGER — Project Helios / Brightwater Corp. ($2.4B Enterprise Value)",
        "matter": "M-331",
        "date": "2026-09-28",
        "category": "Executed Merger Agreement (iManage v14.2)",
        "html_body": """
        <div class="legal-doc">
          <div class="title-block">
            <h2>AGREEMENT AND PLAN OF MERGER</h2>
            <p><strong>DOCUMENT ID: DOC-M331-01 | MATTER: M-331 (PROJECT HELIOS) | iManage-v14.2</strong></p>
            <p>DATED AS OF SEPTEMBER 28, 2026</p>
            <p>BY AND AMONG <strong>APEX GLOBAL HOLDINGS INC.</strong> ("Buyer"), <strong>BRIGHTWATER MERGER SUB INC.</strong> ("Merger Sub"), AND <strong>BRIGHTWATER CORP.</strong> ("Company")</p>
          </div>

          <h3>PREAMBLE & RECITALS [CHUNK: CHK-M331-RECITALS]</h3>
          <p>THIS AGREEMENT AND PLAN OF MERGER (this "Agreement"), dated as of September 28, 2026, is entered into by and among APEX GLOBAL HOLDINGS INC., a Delaware corporation ("Buyer"), BRIGHTWATER MERGER SUB INC. ("Merger Sub"), and BRIGHTWATER CORP., a Delaware semiconductor corporation (the "Company"). Aggregate Enterprise Value is fixed at Two Billion Four Hundred Million Dollars ($2,400,000,000.00), subject to Section 2.04 Escrow Deposit and Working Capital adjustments.</p>

          <h3>ARTICLE I: DEFINITIONS & MATERIAL ADVERSE EFFECT [CHUNK: CL-M331-MAE]</h3>
          <p><strong>Section 1.01 & 7.02(c). Company Material Adverse Effect.</strong> "Company Material Adverse Effect" means any change, event, or occurrence that has a material adverse effect on the business, results of operations, or financial condition of the Company and its Subsidiaries, taken as a whole; provided, however, that none of the following shall constitute a Company Material Adverse Effect: (i) changes in GAAP or Delaware law, (ii) industry-wide semiconductor supply constraints, except to the extent such changes disproportionately impact the Company by more than 15% of Consolidated Adjusted EBITDA compared to peer companies.</p>

          <h3>ARTICLE VIII: SURVIVAL AND INDEMNIFICATION [CHUNK: CL-M331-INDEM]</h3>
          <p class="highlight-target"><strong>Section 8.02(b) & 8.04. Cap, True Deductible Basket & Double Materiality Scrape.</strong> Notwithstanding anything to the contrary set forth herein, Seller shall have no liability under Section 8.02(a) until the aggregate amount of all Losses exceeds $12,000,000 (0.50% of Enterprise Value) (the "Deductible Basket"), after which Seller shall be liable only for Losses in excess of the Deductible Basket up to an aggregate Indemnity Cap equal to $18,000,000 (0.75% of Enterprise Value). For purposes of both determining breach and calculating Losses, all "Material Adverse Effect" and "material" qualifications shall be disregarded (Full Double Materiality Scrape).</p>

          <h3>SECTION 8.01: SURVIVAL PERIODS [CHUNK: CHK-M331-SURVIVAL]</h3>
          <p><strong>Section 8.01. Survival.</strong> Non-Fundamental Representations shall survive the Closing for eighteen (18) months. Fundamental Representations (Organization, Authority, Capitalization, Taxes) shall survive for seventy-two (72) months. Claims grounded in Intentional Fraud bypass both the Deductible Basket and the General Indemnity Cap up to 100% of Enterprise Value ($2,400,000,000).</p>

          <h3>ARTICLE XI: GOVERNING LAW & CHANGE OF CONTROL [CHUNK: CHK-M331-GOVLAW]</h3>
          <p><strong>Section 11.06 & 11.08. Change of Control Assignment & Delaware Chancery Forum.</strong> Neither party may assign this Agreement or undergo a Change of Control prior to Closing without prior written consent of the other party. This Agreement shall be governed by the internal laws of the State of Delaware, with exclusive jurisdiction in the Court of Chancery of the State of Delaware.</p>
        </div>
        """
    },
    {
        "doc_id": "DOC-M331-02",
        "filename": "DOC-M331-02_M331_Opposing_Counsel_Redline_Summary",
        "title": "OPPOSING COUNSEL REDLINE MARKUP — Skadden Draft v4 vs. Buyer Draft v3 (Matter M-331)",
        "matter": "M-331",
        "date": "2026-09-29",
        "category": "Opposing Counsel Redline (iManage v14.4)",
        "html_body": """
        <div class="legal-doc">
          <div class="title-block">
            <h2>SKADDEN, ARPS, SLATE, MEAGHER & FLOM LLP — REDLINE COMPARISON</h2>
            <p><strong>DOCUMENT ID: DOC-M331-02 | MATTER: M-331 (PROJECT HELIOS) | Skadden v4 vs. Buyer v3</strong></p>
            <p>DATE: SEPTEMBER 29, 2026</p>
          </div>

          <h3>1. INDEMNIFICATION CAP & MATERIALITY SCRAPE [CHUNK: CL-M331-REDLINE]</h3>
          <p class="highlight-target"><strong>Redline Section 8.02(b) (Skadden v4 vs. Buyer v3):</strong> Opposing Counsel (Skadden) struck the $18,000,000 (0.75% EV) Indemnity Cap and inserted $6,000,000 (0.25% R&W Policy Retention Split), while increasing the Deductible Basket from 0.50% ($12.0M) to 0.85% ($20.4M), cutting general survival from 18 months to 12 months, and deleting the first prong (breach determination) of the Double Materiality Scrape (converting to Single Scrape — Damages Only).</p>

          <h3>2. TAX INDEMNITY & SECTION 338(h)(10) ELECTION [CHUNK: CHK-M331-REDLINE-TAX]</h3>
          <p><strong>Redline Section 6.09(d) Tax Covenant:</strong> Opposing Counsel inserted a Seller Walk-Right if the Section 338(h)(10) Incremental Tax Gross-Up exceeds $9,500,000. Cross-reference unfiled Deal Tax Partner email <code>EM-9901</code> (Marcus Thorne) regarding the $14.2M step-up valuation model.</p>
        </div>
        """
    },
    {
        "doc_id": "DOC-M331-03",
        "filename": "DOC-M331-03_M331_Indemnity_Escrow_Agreement_Citibank",
        "title": "CITIBANK INDEMNITY ESCROW AGREEMENT — Matter M-331 (Account CIT-ESC-48902-M331)",
        "matter": "M-331",
        "date": "2026-09-18",
        "category": "Escrow Agreement",
        "html_body": """
        <div class="legal-doc">
          <div class="title-block">
            <h2>INDEMNITY ESCROW AGREEMENT</h2>
            <p><strong>DOCUMENT ID: DOC-M331-03 | ACCOUNT NUMBER: CIT-ESC-48902-M331</strong></p>
            <p>BY AND AMONG APEX GLOBAL HOLDINGS INC., SHAREHOLDER REPRESENTATIVE, AND CITIBANK, N.A.</p>
          </div>
          <h3>SECTION 3: ESCROW DEPOSIT & MONTHLY COMPOUNDING [CHUNK: CL-M331-ESCROW]</h3>
          <p class="highlight-target"><strong>Section 3. Escrow Deposit & Compounding Interest.</strong> Escrow Agent confirms receipt of the initial deposit of $3,600,000.00 (7.5% holdback tranche). The Escrow Fund shall be invested in an interest-bearing institutional money market account earning fixed annual interest of 5.25%, with interest credited and compounded on the last Business Day of each calendar month.</p>
          <h3>SECTION 4: PROJECTED RELEASE SCHEDULE</h3>
          <ul>
            <li>Month 0 (Closing Deposit): $3,600,000.00</li>
            <li>Month 6 Projected Balance: $3,695,471.12</li>
            <li>Month 12 Projected Balance: $3,793,466.85</li>
            <li>Month 18 Release Date Balance: <strong>$3,894,292.78</strong></li>
          </ul>
        </div>
        """
    },
    {
        "doc_id": "DOC-M331-04",
        "filename": "DOC-M331-04_M331_Tax_Allocation_Rider_Draft",
        "title": "SECTION 1060 & 338(h)(10) TAX ALLOCATION RIDER — Matter M-331",
        "matter": "M-331",
        "date": "2026-09-22",
        "category": "Tax Allocation Rider & Teammate Grant Channel",
        "html_body": """
        <div class="legal-doc">
          <div class="title-block">
            <h2>CONFIDENTIAL TAX ALLOCATION RIDER & TEAMMATE CORRESPONDENCE</h2>
            <p><strong>DOCUMENT ID: DOC-M331-04 / EM-9901 | MATTER: M-331 (PROJECT HELIOS)</strong></p>
            <p>Owner: Marcus Thorne (Tax Partner, L-003) | Grantee: Sarah Jenkins (M&A Partner, L-001)</p>
          </div>
          <p class="highlight-target"><strong>[GOVERNED BY CLOUD SPANNER TEAMMATEGRANTS GRAPH EDGE — 30-DAY TEMPORAL ACCESS]</strong></p>
          <p><strong>Section 6.09(d) & Rider Schedule A:</strong> Buyer and Seller shall jointly make a timely and irrevocable election under Section 338(h)(10) of the Internal Revenue Code. Seller shall bear 100% of state and local transfer taxes arising from the Pennsylvania semiconductor packaging subsidiary carve-out, while Buyer's incremental tax gross-up obligation is capped at $14,200,000 based on Class V equipment appraisal.</p>
        </div>
        """
    },
    {
        "doc_id": "DOC-M215-01",
        "filename": "DOC-M215-01_M215_Project_Titan_Merger_Agreement_Executed",
        "title": "EXECUTED MERGER AGREEMENT — Project Titan ($1.85B Enterprise Value, Latham Precedent)",
        "matter": "M-215",
        "date": "2026-06-14",
        "category": "Precedent Merger Agreement (iManage v11.0)",
        "html_body": """
        <div class="legal-doc">
          <div class="title-block">
            <h2>AGREEMENT AND PLAN OF MERGER — PROJECT TITAN</h2>
            <p><strong>DOCUMENT ID: DOC-M215-01 | MATTER: M-215 | COUNSEL: LATHAM & WATKINS LLP</strong></p>
            <p>EXECUTED JUNE 14, 2026 | ENTERPRISE VALUE: $1,850,000,000.00</p>
          </div>
          <h3>ARTICLE VIII: INDEMNIFICATION & R&W INSURANCE RETENTION [CHUNK: CL-M215-INDEM]</h3>
          <p class="highlight-target"><strong>Section 8.04(a) Indemnity Cap & Tipping Basket:</strong> Seller's aggregate liability for breaches of Non-Fundamental Representations shall not exceed 0.50% of Enterprise Value ($9,250,000.00), structured as a 50/50 retention split under the Euclid Transactional R&W Insurance Policy. Buyer shall not recover until aggregate Losses exceed a Tipping Basket of 0.35% of Enterprise Value ($6,475,000.00), upon which recovery relates back to the first dollar. Survival period is fixed at 15 months. Includes full Double Materiality Scrape.</p>
          <h3>ARTICLE X: CHANGE OF CONTROL & ASSIGNMENT [CHUNK: CHK-M215-COC]</h3>
          <p><strong>Section 10.04 Change of Control:</strong> Direct or indirect acquisition of >50% voting power of Company requires written consent of Counterparty under Material Customer Contracts listed in Schedule 3.16, except for affiliate restructurings.</p>
        </div>
        """
    },
    {
        "doc_id": "DOC-M518-01",
        "filename": "DOC-M518-01_M518_Project_Vanguard_SPA_Executed",
        "title": "STOCK PURCHASE AGREEMENT — Project Vanguard ($3.10B Enterprise Value, Kirkland Precedent)",
        "matter": "M-518",
        "date": "2026-04-09",
        "category": "Precedent Stock Purchase Agreement (iManage v9.8)",
        "html_body": """
        <div class="legal-doc">
          <div class="title-block">
            <h2>STOCK PURCHASE AGREEMENT — PROJECT VANGUARD</h2>
            <p><strong>DOCUMENT ID: DOC-M518-01 | MATTER: M-518 | COUNSEL: KIRKLAND & ELLIS LLP</strong></p>
            <p>EXECUTED APRIL 9, 2026 | ENTERPRISE VALUE: $3,100,000,000.00</p>
          </div>
          <h3>ARTICLE IX: INDEMNIFICATION & DEDUCTIBLE BASKET [CHUNK: CL-M518-INDEM]</h3>
          <p class="highlight-target"><strong>Section 9.01(c) Cap & True Deductible:</strong> Aggregate Seller liability for General Representations is capped at 1.00% of Enterprise Value ($31,000,000.00) above a True Deductible Basket of 0.50% of Enterprise Value ($15,500,000.00). General Representations survive for 24 months; Fundamental and Tax Representations survive for 72 months. Includes Double Materiality Scrape and IP Special Escrow ($12,000,000).</p>
        </div>
        """
    },
    {
        "doc_id": "DOC-M402-01",
        "filename": "DOC-M402-01_M402_Apollo_Credit_Agreement_vFinal",
        "title": "SENIOR SECURED CREDIT AGREEMENT — Apollo $250M Revolving Facility (J.Crew Blocker)",
        "matter": "M-402",
        "date": "2026-08-14",
        "category": "Executed Credit Agreement (iManage v12.1)",
        "html_body": """
        <div class="legal-doc">
          <div class="title-block">
            <h2>SENIOR SECURED CREDIT AGREEMENT</h2>
            <p><strong>DOCUMENT ID: DOC-M402-01 | MATTER: M-402 | COUNSEL: DAVIS POLK & WARDWELL LLP</strong></p>
            <p>DATED AUGUST 14, 2026 | $250,000,000 REVOLVING CREDIT FACILITY</p>
          </div>
          <h3>ARTICLE VII: NEGATIVE COVENANTS & J.CREW BLOCKER [CHUNK: CL-M402-JCREW]</h3>
          <p class="highlight-target"><strong>Section 7.08(c) Covenant Against Asset Drops (J.Crew / Envision Blocker):</strong> No Material Intellectual Property owned by the Borrower or any Restricted Subsidiary may be transferred, assigned, or exclusively licensed to an Unrestricted Subsidiary. Any Basket investment in Unrestricted Subsidiaries is strictly capped at 0.40% of Consolidated Total Assets ($10,000,000.00) with a 0.20% threshold and 36-month covenant survival.</p>
        </div>
        """
    },
    {
        "doc_id": "DOC-M109-01",
        "filename": "DOC-M109-01_M109_Mutual_Non_Disclosure_Agreement_FormSpec_v06",
        "title": "MUTUAL NON-DISCLOSURE AGREEMENT — LexGraph FormSpec v0.0.6 Baseline",
        "matter": "M-109",
        "date": "2026-09-29",
        "category": "NDA FormSpec Baseline (iManage v6.0)",
        "html_body": """
        <div class="legal-doc">
          <div class="title-block">
            <h2>MUTUAL NON-DISCLOSURE AGREEMENT (NDA)</h2>
            <p><strong>DOCUMENT ID: DOC-M109-01 | MATTER: M-109 | LEXGRAPH FORMSPEC v0.0.6 BASELINE</strong></p>
            <p>EFFECTIVE DATE: SEPTEMBER 29, 2026 | GOVERNING LAW: NEW YORK</p>
          </div>
          <h3>SECTION 4 & 7: STANDARD OF CARE, RESIDUALS & 24-MONTH STANDSTILL [CHUNK: CL-M109-NDA]</h3>
          <p class="highlight-target"><strong>Section 4 & Section 7.</strong> Confidentiality obligations survive for 36 months from the Effective Date, coupled with a 24-month Fall-Away Standstill provision and a Narrow Residuals Clause limited to unaided memory of non-source-code business concepts. Liability is uncapped (100% Direct Losses) with $0.00 deductible basket.</p>
        </div>
        """
    },
]

CSS = """
<style>
  body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 11pt;
    line-height: 1.55;
    color: #111;
    margin: 42px;
  }
  .title-block {
    text-align: center;
    margin-bottom: 28px;
    border-bottom: 2px solid #222;
    padding-bottom: 16px;
  }
  h2 { font-size: 15pt; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.02em; }
  h3 { font-size: 11.5pt; margin-top: 22px; margin-bottom: 8px; border-bottom: 1px solid #ccc; text-transform: uppercase; }
  p { margin-bottom: 12px; text-align: justify; }
  .highlight-target {
    background-color: #fef08a;
    border-left: 3px solid #ca8a04;
    padding: 8px 12px;
    margin: 12px 0;
  }
</style>
"""

if __name__ == "__main__":
  print("=== Generating LexGraph Demo Legal Corpus (PDF + TXT) ===")
  for doc in DOCUMENTS:
    base_name = doc["filename"]
    txt_path = os.path.join(TXT_DIR, f"{base_name}.txt")
    html_path = os.path.join("/tmp", f"{base_name}.html")
    pdf_path = os.path.join(PDF_DIR, f"{base_name}.pdf")

    clean_txt = re.sub(r"<[^>]+>", " ", doc["html_body"])
    clean_txt = re.sub(r"\s+", " ", clean_txt).strip()
    with open(txt_path, "w", encoding="utf-8") as f:
      f.write(
          f"# {doc['title']}\n"
          f"Document ID: {doc['doc_id']} | Matter: {doc['matter']} | Date: {doc['date']} | Category: {doc['category']}\n\n"
          f"{clean_txt}\n"
      )
    print(f"  [TXT] {os.path.basename(txt_path)} ({len(clean_txt):,} chars)")

    full_html = (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{doc['title']}</title>{CSS}</head><body>{doc['html_body']}</body></html>"
    )
    with open(html_path, "w", encoding="utf-8") as f:
      f.write(full_html)

    r = subprocess.run(
        ["google-chrome", "--headless", "--disable-gpu", f"--print-to-pdf={pdf_path}", html_path],
        capture_output=True,
        text=True,
    )
    if r.returncode == 0 and os.path.exists(pdf_path):
      print(f"  [PDF] {os.path.basename(pdf_path)} ({os.path.getsize(pdf_path):,} bytes)")
    else:
      print(f"  [WARN] Could not compile PDF for {base_name}: {r.stderr}")

  # Also write standalone EM-9901 Unfiled Tax Email text file
  em_path = os.path.join(TXT_DIR, "EM-9901_Unfiled_Tax_Email_Section_338h10_Election.txt")
  with open(em_path, "w", encoding="utf-8") as f:
    f.write(
        "EMAIL ID: EM-9901\n"
        "MATTER: M-331 (Project Helios — Brightwater Corp. $2.4B Merger)\n"
        "FROM: Marcus Thorne <m-thorne@lexgraph.com> (Tax Partner, L-003)\n"
        "TO: Sarah Jenkins <s-jenkins@lexgraph.com> (M&A Partner, L-001)\n"
        "SUBJECT: URGENT — Unfiled Section 338(h)(10) Election Gross-Up Cap ($14.2M vs Skadden $9.5M Walk-Right)\n"
        "ACCESS POLICY: Governed by Cloud Spanner TeammateGrants Graph Edge (30-Day Temporal Grant)\n\n"
        "Sarah,\n"
        "Per our working call on the Brightwater semiconductor packaging subsidiary carve-out, "
        "do NOT accept Skadden's v4 markup capping the Section 338(h)(10) incremental tax gross-up at $9.5M. "
        "Our Class V equipment depreciation model shows $14.2M in step-up exposure. Keep the $14.2M gross-up cap "
        "tied to the $18.0M (0.75% EV) Indemnity Cap in Section 8.02(b).\n"
    )
  print(f"  [TXT] {os.path.basename(em_path)}")
  print("=== Done! ===")
