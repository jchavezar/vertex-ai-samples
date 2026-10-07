import subprocess
import urllib.request
import urllib.error
import json
import time

PROJECT_ID = "vtxdemos"
INSTANCE_ID = "lexgraph-legal-spanner"
DB_ID = "lexgraph-legal-context"
SPANNER_DB_URI = f"projects/{PROJECT_ID}/instances/{INSTANCE_ID}/databases/{DB_ID}"

def get_token():
    return subprocess.check_output(["gcloud", "auth", "print-access-token"]).decode().strip()

def get_headers(token=None):
    if not token:
        token = get_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_ID
    }

def embed_text_gemini_2(text, token, task_type="RETRIEVAL_DOCUMENT"):
    url = f"https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us/publishers/google/models/gemini-embedding-2:embedContent"
    body = {
        "content": {
            "parts": [{"text": text}]
        },
        "taskType": task_type,
        "outputDimensionality": 3072
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=get_headers(token), method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        return data["embedding"]["values"]

def create_session(token):
    url = f"https://spanner.googleapis.com/v1/{SPANNER_DB_URI}/sessions"
    req = urllib.request.Request(url, data=b"{}", headers=get_headers(token), method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())["name"]

def commit_mutations(session_name, mutations, token):
    url = f"https://spanner.googleapis.com/v1/{session_name}:commit"
    body = {
        "singleUseTransaction": {"readWrite": {}},
        "mutations": mutations
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=get_headers(token), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print("SPANNER COMMIT ERROR:", e.code, e.read().decode())
        raise

def main():
    token = get_token()
    session = create_session(token)
    print("Created Spanner Session:", session)

    lawyers = [
        ["L-001", "Sarah Jenkins", "sarah.jenkins@lexgraph.com", "Managing Partner", "M&A / Private Equity", "New York"],
        ["L-002", "David Vance", "david.vance@lexgraph.com", "Senior Partner", "Mergers & Acquisitions", "New York"],
        ["L-003", "Marcus Thorne", "marcus.thorne@lexgraph.com", "Tax Partner", "Tax & Structuring", "New York"],
        ["L-004", "Elena Rostova", "elena.rostova@lexgraph.com", "Banking Partner", "Banking & Finance", "London"],
        ["L-005", "Rachel Zane", "rachel.zane@lexgraph.com", "Senior Associate", "M&A / Private Equity", "New York"],
        ["L-006", "Chief Legal Architect", "andrew.simon@lexgraph.com", "Counsel / Legal Tech", "Restructuring", "Boston"]
    ]

    clients = [
        ["C-100", "Apex Global Holdings Inc.", "Enterprise Software & Semiconductor", "Platinum"],
        ["C-200", "Apollo Strategic Credit Fund LP", "Private Credit & Direct Lending", "Platinum"],
        ["C-300", "Vanguard Sovereign Infrastructure", "Energy & Infrastructure", "Gold"],
        ["C-400", "Project Omega Special Situations", "Distressed Debt / Restructuring", "Platinum"]
    ]

    matters = [
        ["M-331", "Brightwater Corp. Acquisition ($2.4B)", "C-100", "M&A / Private Equity", "ACTIVE_CLOSING", "L-001", 2400000000.0],
        ["M-402", "Apollo $850M Senior Secured Credit Facility", "C-200", "Banking & Finance", "ACTIVE", "L-004", 850000000.0],
        ["M-109", "Apex / SilverLake Mutual NDA & Clean Team", "C-100", "M&A / Private Equity", "EXECUTED", "L-002", 0.0],
        ["M-215", "Kestrel Semiconductor Carve-Out ($1.65B)", "C-100", "M&A / Private Equity", "CLOSED_PRECEDENT", "L-001", 1650000000.0],
        ["M-518", "Vanguard / Brookfield Infrastructure JV ($3.1B)", "C-300", "M&A / Private Equity", "CLOSED_PRECEDENT", "L-002", 3100000000.0],
        ["M-999", "Project Omega Hostile Takeover Defense (Restricted)", "C-400", "Restructuring / Hostile M&A", "WALL_RESTRICTED", "L-006", 4200000000.0]
    ]

    documents = [
        ["DOC-M331-01", "M-331", "Agreement and Plan of Merger (Apex / Brightwater Corp.)", "Merger Agreement", "Wachtell, Lipton, Rosen & Katz", "Delaware", "2026-09-28", "M331_Brightwater_Merger_Agreement_Executed.pdf", 3, "iManage-v14.2"],
        ["DOC-M331-02", "M-331", "Opposing Counsel Redline Summary (Skadden Draft v4 vs Buyer v3)", "Redline Markup", "Skadden, Arps, Slate, Meagher & Flom", "Delaware", "2026-09-29", "M331_Opposing_Counsel_Redline_Summary.pdf", 2, "iManage-v4.0"],
        ["DOC-M331-03", "M-331", "Indemnity Escrow Agreement (Citibank N.A. $18,000,000)", "Escrow Agreement", "Cravath, Swaine & Moore LLP", "New York", "2026-09-29", "M331_Indemnity_Escrow_Agreement_Citibank.pdf", 2, "iManage-v7.1"],
        ["DOC-M331-04", "M-331", "Section 338(h)(10) Tax Allocation Rider & Gross-Up", "Tax Rider", "Kirkland & Ellis LLP", "Delaware", "2026-09-30", "M331_Tax_Allocation_Rider_Draft.pdf", 2, "iManage-v3.4"],
        ["DOC-M402-01", "M-402", "Senior Secured First-Lien Credit Agreement ($850M)", "Credit Agreement", "Latham & Watkins LLP", "New York", "2026-08-14", "M402_Apollo_Credit_Agreement_vFinal.pdf", 2, "iManage-v11.0"],
        ["DOC-M109-01", "M-109", "Mutual Non-Disclosure & Standstill Agreement (FormSpec v06)", "Mutual NDA", "Sullivan & Cromwell LLP", "Delaware", "2026-07-19", "M109_Mutual_Non_Disclosure_Agreement_FormSpec_v06.pdf", 2, "iManage-v6.0"],
        ["DOC-M215-01", "M-215", "Kestrel Semiconductor Stock Purchase Agreement ($1.65B)", "Purchase Agreement", "Kirkland & Ellis LLP", "Delaware", "2025-11-12", "M331_Brightwater_Merger_Agreement_Executed.pdf", 3, "iManage-v19.0"],
        ["DOC-M518-01", "M-518", "Vanguard Infrastructure Membership Interest Purchase Agreement", "Purchase Agreement", "Simpson Thacher & Bartlett LLP", "Delaware", "2026-03-04", "M331_Brightwater_Merger_Agreement_Executed.pdf", 3, "iManage-v12.1"],
        ["DOC-M999-01", "M-999", "Project Omega Confidential Poison Pill & White Knight Term Sheet", "Restructuring Term Sheet", "Davis Polk & Wardwell LLP", "Delaware", "2026-09-25", "M331_Brightwater_Merger_Agreement_Executed.pdf", 3, "iManage-v2.0"]
    ]

    clauses_raw = [
        {
            "clause_id": "CL-M331-INDEM",
            "doc_id": "DOC-M331-01",
            "matter_id": "M-331",
            "clause_type": "Indemnification & Survival Cap",
            "section_ref": "Section 8.02(b) & 8.04",
            "page_number": 2,
            "cap_pct": "0.75% ($18.0M Escrow Cap)",
            "basket_type": "0.50% ($12.0M) True Deductible Basket",
            "survival_months": "18 Months (General) / 72 Months (Fundamental)",
            "qualifiers": "Full Materiality Scrape (Determinations & Losses)",
            "summary_text": "General representation survival of 18 months; Seller aggregate liability capped at $18,000,000 (0.75% of Enterprise Value) subject to a $12,000,000 (0.50%) true deductible basket with full double materiality scrape.",
            "verbatim_quote": "Section 8.02(b) Cap and Deductible Basket: Notwithstanding anything to the contrary set forth herein, Seller shall have no liability under Section 8.02(a) until the aggregate amount of all Losses exceeds $12,000,000 (0.50% of Enterprise Value) (the 'Deductible Basket'), after which Seller shall be liable only for Losses in excess of the Deductible Basket up to an aggregate Indemnity Cap equal to $18,000,000 (0.75% of Enterprise Value). For purposes of both determining breach and calculating Losses, all 'Material Adverse Effect' and 'material' qualifications shall be disregarded (Full Materiality Scrape).",
            "counsel_firm": "Wachtell, Lipton, Rosen & Katz",
            "governing_law": "Delaware",
            "bbox_json": json.dumps({"page": 2, "x": 8, "y": 24, "w": 84, "h": 22, "label": "Sec. 8.02(b) — 0.75% Cap / 0.50% Deductible Basket"})
        },
        {
            "clause_id": "CL-M331-MAE",
            "doc_id": "DOC-M331-01",
            "matter_id": "M-331",
            "clause_type": "Material Adverse Effect (MAE) & Disproportionate Impact",
            "section_ref": "Section 1.01 & 7.02(c)",
            "page_number": 1,
            "cap_pct": "N/A (Walk Right / Closing Condition)",
            "basket_type": "Quantitative 15% EBITDA Disproportionate Carve-Out",
            "survival_months": "Pre-Closing Period",
            "qualifiers": "Excludes macro/industry shifts unless >15% peer divergence",
            "summary_text": "Customary Delaware MAE definition excluding general economic, tariff, or semiconductor supply chain disruptions unless disproportionately affecting Brightwater Corp. by >15% EBITDA relative to peer index.",
            "verbatim_quote": "Section 1.01 'Company Material Adverse Effect' means any change, event, or occurrence that has a material adverse effect on the business, results of operations, or financial condition of the Company and its Subsidiaries, taken as a whole; provided, however, that none of the following shall constitute a Company Material Adverse Effect: (i) changes in GAAP or Delaware law, (ii) industry-wide semiconductor supply constraints, except to the extent such changes disproportionately impact the Company by more than 15% of Consolidated Adjusted EBITDA compared to peer companies.",
            "counsel_firm": "Wachtell, Lipton, Rosen & Katz",
            "governing_law": "Delaware",
            "bbox_json": json.dumps({"page": 1, "x": 8, "y": 52, "w": 84, "h": 20, "label": "Sec. 1.01 — Material Adverse Effect (15% Peer Threshold)"})
        },
        {
            "clause_id": "CL-M331-REDLINE",
            "doc_id": "DOC-M331-02",
            "matter_id": "M-331",
            "clause_type": "Opposing Counsel Redline — Basket & R&W Recourse",
            "section_ref": "Redline Sec. 8.02(b) (Skadden v4 vs Buyer v3)",
            "page_number": 1,
            "cap_pct": "Skadden proposed 0.25% ($6.0M) vs LexGraph 0.75% ($18.0M)",
            "basket_type": "Skadden Tipping Basket Rejection -> 0.85% Deductible",
            "survival_months": "12 Months (Skadden Counter) vs 18 Months (LexGraph)",
            "qualifiers": "Partial Scrape Only (Damages Only, Not Breach)",
            "summary_text": "Skadden v4 redline attempts to slash Seller Indemnity Escrow from 0.75% ($18.0M) down to 0.25% ($6.0M), shift survival from 18 to 12 months, and eliminate the breach prong of the Materiality Scrape.",
            "verbatim_quote": "REDLINE COMPARISON [Skadden Draft v4 vs. Buyer Draft v3]: In Section 8.02(b), Opposing Counsel (Skadden) struck the $18,000,000 (0.75%) Indemnity Cap and inserted $6,000,000 (0.25% R&W Policy Retention Split), while increasing the Deductible Basket from 0.50% ($12.0M) to 0.85% ($20.4M) and deleting the first prong of the Double Materiality Scrape.",
            "counsel_firm": "Skadden, Arps, Slate, Meagher & Flom",
            "governing_law": "Delaware",
            "bbox_json": json.dumps({"page": 1, "x": 8, "y": 30, "w": 84, "h": 26, "label": "Skadden Redline v4 — Sec. 8.02(b) Cap Cut to 0.25%"})
        },
        {
            "clause_id": "CL-M331-ESCROW",
            "doc_id": "DOC-M331-03",
            "matter_id": "M-331",
            "clause_type": "Indemnity Escrow Release & Joint Instruction",
            "section_ref": "Section 4(a)-(c)",
            "page_number": 1,
            "cap_pct": "$18,000,000 Funded Escrow Account",
            "basket_type": "10 Business Day Objection Window",
            "survival_months": "18 Months + Pending Claim Holdback",
            "qualifiers": "Citibank N.A. Joint Written Direction or Final Delaware Order",
            "summary_text": "Citibank N.A. holds $18.0M Indemnity Escrow Fund in Treasury Money Market account; automatic release at 18-month anniversary minus Unresolved Claim Reserve unless Seller delivers Claim Objection Notice within 10 Business Days.",
            "verbatim_quote": "Section 4(b) Release of Escrow Fund: On the first Business Day following the eighteen (18) month anniversary of the Closing Date (the 'Escrow Termination Date'), Escrow Agent (Citibank, N.A.) shall disburse to Seller Representative the remaining balance of the $18,000,000 Indemnity Escrow Fund, less the aggregate amount of all Pending Claim Reserves specified in Buyer Claim Notices delivered prior to 5:00 p.m. Eastern Time on the Escrow Termination Date.",
            "counsel_firm": "Cravath, Swaine & Moore LLP",
            "governing_law": "New York",
            "bbox_json": json.dumps({"page": 1, "x": 8, "y": 44, "w": 84, "h": 22, "label": "Sec. 4(b) — Citibank $18.0M Escrow Holdback & Release"})
        },
        {
            "clause_id": "CL-M331-TAX",
            "doc_id": "DOC-M331-04",
            "matter_id": "M-331",
            "clause_type": "Section 338(h)(10) Election & Tax Gross-Up Cap",
            "section_ref": "Section 2.01 & 3.04 (Tax Rider)",
            "page_number": 1,
            "cap_pct": "100% Pre-Closing Tax / $9.5M Gross-Up Ceiling",
            "basket_type": "First-Dollar Indemnity (Exempt from Deductible Basket)",
            "survival_months": "Statute of Limitations + 60 Days",
            "qualifiers": "Uncapped Pre-Closing Income Tax Indemnity",
            "summary_text": "First-dollar indemnity for all Pre-Closing Tax Liabilities bypassing the Section 8.02 Deductible Basket, paired with a capped $9,500,000 Section 338(h)(10) ordinary-to-capital-gains Tax Gross-Up.",
            "verbatim_quote": "Section 3.04 Tax Indemnification Carve-Out: Seller's obligation to indemnify Buyer for Pre-Closing Taxes and Section 338(h)(10) Election adjustments shall be on a first-dollar basis, shall not be subject to the Deductible Basket or the General Indemnity Cap in Section 8.02(b), and shall survive until sixty (60) days following the expiration of the applicable federal or state statute of limitations.",
            "counsel_firm": "Kirkland & Ellis LLP",
            "governing_law": "Delaware",
            "bbox_json": json.dumps({"page": 1, "x": 8, "y": 38, "w": 84, "h": 24, "label": "Sec. 3.04 — First-Dollar Tax Indemnity & 338(h)(10) Gross-Up"})
        },
        {
            "clause_id": "CL-M402-COV",
            "doc_id": "DOC-M402-01",
            "matter_id": "M-402",
            "clause_type": "Financial Covenants & J.Crew / Chewy Blocker",
            "section_ref": "Section 6.08 & 7.11",
            "page_number": 1,
            "cap_pct": "4.50x Max Total Net Leverage / 20% EBITDA Cap",
            "basket_type": "5-Quarter Equity Cure Right (Max 2 Consecutive)",
            "survival_months": "60 Months (5-Year Term Loan B)",
            "qualifiers": "Strict Material IP Unrestricted Subsidiary Blocker",
            "summary_text": "Total Net Leverage Ratio capped at 4.50x stepping down to 3.75x; EBITDA add-backs for restructuring capped at 20% LTM EBITDA; strict J.Crew/Chewy blocker prohibiting transfer of Material IP to Unrestricted Subsidiaries.",
            "verbatim_quote": "Section 6.08(d) Material Intellectual Property Blocker: Notwithstanding anything to the contrary in this Agreement, neither the Borrower nor any Restricted Subsidiary may transfer, assign, or exclusively license any Material Intellectual Property to any Unrestricted Subsidiary, nor may any Subsidiary holding Material Intellectual Property be designated as an Unrestricted Subsidiary (Strict J.Crew / Serta / Chewy Protection).",
            "counsel_firm": "Latham & Watkins LLP",
            "governing_law": "New York",
            "bbox_json": json.dumps({"page": 1, "x": 8, "y": 46, "w": 84, "h": 22, "label": "Sec. 6.08(d) — J.Crew / Material IP Blocker & 4.50x Leverage"})
        },
        {
            "clause_id": "CL-M109-NDA",
            "doc_id": "DOC-M109-01",
            "matter_id": "M-109",
            "clause_type": "Standstill, Fall-Away & Non-Solicitation",
            "section_ref": "Section 5 & Section 7",
            "page_number": 1,
            "cap_pct": "Uncapped Equitable / Specific Performance Recourse",
            "basket_type": "Automatic Fall-Away on 3rd-Party >50% Tender Offer",
            "survival_months": "24 Months Confidentiality / 18 Months Standstill",
            "qualifiers": "Residuals Clause Excluded; Clean Team Protocol Required",
            "summary_text": "18-month Standstill with automatic fall-away if target enters into a definitive third-party sale agreement; 18-month non-solicitation of VP+ executives with general advertising carve-out.",
            "verbatim_quote": "Section 7 Standstill & Fall-Away: For a period of eighteen (18) months from the Effective Date, Recipient shall not acquire beneficial ownership of more than 2.0% of the Company's voting securities; provided that the restrictions of this Section 7 shall automatically terminate ('Fall-Away') upon the Company entering into a definitive agreement with a third party providing for a merger or sale of 50% or more of its consolidated assets.",
            "counsel_firm": "Sullivan & Cromwell LLP",
            "governing_law": "Delaware",
            "bbox_json": json.dumps({"page": 1, "x": 8, "y": 40, "w": 84, "h": 22, "label": "Sec. 7 — 18-Month Standstill with Automatic Fall-Away"})
        },
        {
            "clause_id": "CL-M215-INDEM",
            "doc_id": "DOC-M215-01",
            "matter_id": "M-215",
            "clause_type": "Indemnification & Survival Cap",
            "section_ref": "Section 9.01(c) (Kestrel Carve-Out Precedent)",
            "page_number": 2,
            "cap_pct": "0.50% ($8.25M R&W Retention Cap)",
            "basket_type": "0.50% ($8.25M) True Deductible Basket",
            "survival_months": "15 Months (General) / 60 Months (Fundamental)",
            "qualifiers": "Double Materiality Scrape; Synthetic R&W Policy Primary",
            "summary_text": "Prior Apex semiconductor precedent (Kestrel $1.65B carve-out) negotiated against Kirkland & Ellis: 0.50% Seller Indemnity Cap ($8.25M), 15-month general survival, full double materiality scrape.",
            "verbatim_quote": "Section 9.01(c) Kestrel Semiconductor Precedent Cap: Seller's aggregate liability for breaches of Non-Fundamental Representations shall not exceed $8,250,000 (0.50% of Base Purchase Price) and shall survive for fifteen (15) months following Closing.",
            "counsel_firm": "Kirkland & Ellis LLP",
            "governing_law": "Delaware",
            "bbox_json": json.dumps({"page": 2, "x": 8, "y": 24, "w": 84, "h": 20, "label": "Kestrel Precedent Sec. 9.01(c) — 0.50% Cap / 15-Mo Survival"})
        },
        {
            "clause_id": "CL-M518-INDEM",
            "doc_id": "DOC-M518-01",
            "matter_id": "M-518",
            "clause_type": "Indemnification & Survival Cap",
            "section_ref": "Section 10.03(a) (Vanguard Infrastructure JV)",
            "page_number": 2,
            "cap_pct": "1.00% ($31.0M Indemnity Cap)",
            "basket_type": "0.35% ($10.85M) Tipping Basket (Dollar-One Once Tipped)",
            "survival_months": "24 Months (General) / 72 Months (Environmental)",
            "qualifiers": "Breach-Only Materiality Scrape",
            "summary_text": "Vanguard $3.1B Infrastructure JV precedent negotiated with Simpson Thacher: 1.00% Indemnity Cap ($31.0M), 0.35% Tipping Basket, 24-month survival for operational & infrastructure representations.",
            "verbatim_quote": "Section 10.03(a) Vanguard JV Indemnity: Once aggregate Losses exceed the 0.35% Tipping Threshold ($10,850,000), Seller shall indemnify Buyer from dollar one up to the 1.00% Aggregate Cap ($31,000,000) for a survival period of twenty-four (24) months.",
            "counsel_firm": "Simpson Thacher & Bartlett LLP",
            "governing_law": "Delaware",
            "bbox_json": json.dumps({"page": 2, "x": 8, "y": 24, "w": 84, "h": 20, "label": "Vanguard JV Sec. 10.03(a) — 1.00% Cap / 0.35% Tipping Basket"})
        },
        {
            "clause_id": "CL-M999-RESTRICTED",
            "doc_id": "DOC-M999-01",
            "matter_id": "M-999",
            "clause_type": "Hostile Defense Poison Pill & Break-Up Fee (Intapp Walled)",
            "section_ref": "Section 4.02 (Project Omega Restricted)",
            "page_number": 2,
            "cap_pct": "4.25% ($178.5M) Reverse Termination Fee",
            "basket_type": "12.5% Beneficial Ownership Flip-In Trigger",
            "survival_months": "12 Months Stockholder Rights Plan",
            "qualifiers": "INTAPP ETHICAL WALL: Restricted to Restructuring Group",
            "summary_text": "ETHICAL WALL PROTECTED: Project Omega hostile defense 12.5% flip-in poison pill trigger and 4.25% ($178.5M) reverse break-up fee. Excluded from M&A team queries via Intapp Screen-Before-Rank.",
            "verbatim_quote": "CONFIDENTIAL / ETHICAL WALL M-999: Upon any Acquiring Person obtaining 12.5% or more of Company Common Stock without Board approval, Flip-In Rights shall trigger immediately; Reverse Termination Fee fixed at 4.25% ($178,500,000).",
            "counsel_firm": "Davis Polk & Wardwell LLP",
            "governing_law": "Delaware",
            "bbox_json": json.dumps({"page": 2, "x": 8, "y": 24, "w": 84, "h": 20, "label": "Restricted M-999 Poison Pill (Intapp Walled)"})
        }
    ]

    emails = [
        [
            "EM-9901", "M-331", "L-003", "L-002",
            "RE: M-331 Brightwater — Section 338(h)(10) Tax Allocation Rider & Skadden Indemnity Cap Pushback",
            "David / Sarah — On the 3:00 PM call with Kirkland & Skadden Tax Counsel, they conceded that the Section 338(h)(10) tax gross-up will remain uncapped for pre-closing federal consolidated return liabilities up to $9.5M, provided we hold firm at the 0.75% ($18.0M) General Indemnity Escrow Cap in Section 8.02(b) and reject Skadden's 0.25% ($6.0M) counter-proposal. Attached is v3.4 of the Tax Rider.",
            "2026-09-30T16:42:00Z",
            "METADATA_ONLY",
            True,
            "DOC-M331-04"
        ],
        [
            "EM-9902", "M-331", "L-002", "L-001",
            "FW: Skadden v4 Redline Markup on Section 8.02(b) Deductible Basket & Materiality Scrape",
            "Sarah — Skadden just sent over Draft v4 of the Brightwater Merger Agreement. They tried to cut the Indemnity Escrow from 0.75% ($18M) to 0.25% ($6M) and strip the breach prong of the Double Materiality Scrape. Based on our Kestrel Semiconductor (M-215, 0.50% cap) and Vanguard (M-518, 1.00% cap) precedents in Spanner Graph, 0.75% is squarely market for a $2.4B Delaware semiconductor acquisition.",
            "2026-09-29T21:15:00Z",
            "FULL",
            True,
            "DOC-M331-02"
        ],
        [
            "EM-9903", "M-402", "L-004", "L-001",
            "Apollo $850M Credit Facility — J.Crew / Chewy IP Blocker Final Language (Sec. 6.08(d))",
            "Sarah — Latham agreed to include the strict Material IP Unrestricted Subsidiary blocker in Section 6.08(d) of the Apollo Credit Agreement alongside the 4.50x Total Net Leverage covenant and 20% EBITDA restructuring add-back cap.",
            "2026-08-14T14:05:00Z",
            "FULL",
            True,
            "DOC-M402-01"
        ]
    ]

    worked_on = [
        ["L-001", "M-331", "Lead M&A Partner", 142.5],
        ["L-002", "M-331", "Co-Lead M&A Partner", 118.0],
        ["L-003", "M-331", "Tax Structuring Partner", 64.5],
        ["L-005", "M-331", "Senior M&A Associate", 210.0],
        ["L-001", "M-402", "Relationship Partner", 28.0],
        ["L-004", "M-402", "Lead Banking Partner", 95.0],
        ["L-001", "M-109", "Supervising Partner", 12.0],
        ["L-002", "M-109", "Negotiating Partner", 19.5],
        ["L-001", "M-215", "Lead Partner (Precedent)", 185.0],
        ["L-002", "M-518", "Lead Partner (Precedent)", 160.0],
        ["L-006", "M-999", "Restructuring Lead (Walled)", 130.0]
    ]

    belongs_to_matter = [[d[0], d[1], "Official iManage DMS Filing"] for d in documents]
    contains_clause = [[c["doc_id"], c["clause_id"], c["section_ref"]] for c in clauses_raw]

    cites_precedent = [
        ["DOC-M331-01", "DOC-M215-01", "Market benchmark for Delaware semiconductor Indemnity Cap (0.75% vs 0.50% Kestrel precedent)", 0.94],
        ["DOC-M331-01", "DOC-M518-01", "Comparison of True Deductible Basket (0.50%) vs Vanguard Tipping Basket (0.35%)", 0.89],
        ["DOC-M331-02", "DOC-M331-01", "Opposing counsel Skadden v4 redline against Buyer v3 execution draft", 0.98],
        ["DOC-M331-03", "DOC-M331-01", "Escrow holdback mechanics implementing Section 8.02(b) $18M Indemnity Cap", 0.95],
        ["DOC-M331-04", "DOC-M331-01", "Section 338(h)(10) first-dollar tax carve-out from Section 8.02(b) Deductible Basket", 0.92]
    ]

    intapp_walls = [
        ["WALL-001", "L-001", "M-331", "INCLUDE", "Authorized Deal Team — Apex / Brightwater Acquisition", "2026-08-01T00:00:00Z"],
        ["WALL-002", "L-001", "M-402", "INCLUDE", "Authorized Relationship Partner — Apollo Credit Facility", "2026-07-15T00:00:00Z"],
        ["WALL-003", "L-001", "M-109", "INCLUDE", "Authorized Deal Team — Apex Mutual NDA", "2026-07-01T00:00:00Z"],
        ["WALL-004", "L-001", "M-215", "INCLUDE", "Authorized Firm Precedent — Kestrel Carve-Out", "2025-11-12T00:00:00Z"],
        ["WALL-005", "L-001", "M-518", "INCLUDE", "Authorized Firm Precedent — Vanguard JV", "2026-03-04T00:00:00Z"],
        ["WALL-999", "L-001", "M-999", "EXCLUDE", "INTAPP ETHICAL WALL: Sarah Jenkins screened from Project Omega Hostile Defense due to prior Apex representation", "2026-09-01T00:00:00Z"]
    ]

    for d in documents:
        d[8] = str(d[8])

    print("Generating 3,072-dim gemini-embedding-2 vectors for Clauses & DocumentChunks...")
    clause_rows = []
    chunk_rows = []
    for idx, c in enumerate(clauses_raw):
        embed_input = f"{c['clause_type']} | {c['matter_id']} | {c['counsel_firm']} | {c['governing_law']} | {c['summary_text']} | {c['verbatim_quote']}"
        vec = embed_text_gemini_2(embed_input, token)
        print(f"  Embedded {c['clause_id']} -> {len(vec)} dims")
        clause_rows.append([
            c["clause_id"], c["doc_id"], c["matter_id"], c["clause_type"],
            c["section_ref"], str(c["page_number"]), c["cap_pct"], c["basket_type"],
            c["survival_months"], c["qualifiers"], c["summary_text"], c["verbatim_quote"],
            c["counsel_firm"], c["governing_law"], c["bbox_json"], vec
        ])
        chunk_rows.append([
            f"CHK-{idx+1:03d}", c["doc_id"], c["matter_id"], c["section_ref"],
            str(c["page_number"]), f"{c['summary_text']}\n\n{c['verbatim_quote']}",
            c["bbox_json"], vec
        ])

    mutations = [
        {"insertOrUpdate": {"table": "Lawyers", "columns": ["lawyer_id", "full_name", "email", "title", "practice_group", "office"], "values": lawyers}},
        {"insertOrUpdate": {"table": "Clients", "columns": ["client_id", "client_name", "industry", "tier"], "values": clients}},
        {"insertOrUpdate": {"table": "Matters", "columns": ["matter_id", "matter_name", "client_id", "practice_area", "status", "lead_partner_id", "deal_value_usd"], "values": matters}},
        {"insertOrUpdate": {"table": "Documents", "columns": ["doc_id", "matter_id", "title", "doc_type", "counsel_firm", "governing_law", "execution_date", "pdf_filename", "page_count", "dms_version"], "values": documents}},
        {"insertOrUpdate": {"table": "Clauses", "columns": ["clause_id", "doc_id", "matter_id", "clause_type", "section_ref", "page_number", "cap_pct", "basket_type", "survival_months", "qualifiers", "summary_text", "verbatim_quote", "counsel_firm", "governing_law", "bbox_json", "embedding"], "values": clause_rows}},
        {"insertOrUpdate": {"table": "DocumentChunks", "columns": ["chunk_id", "doc_id", "matter_id", "section_ref", "page_number", "chunk_text", "bbox_json", "embedding"], "values": chunk_rows}},
        {"insertOrUpdate": {"table": "Emails", "columns": ["email_id", "matter_id", "sender_lawyer_id", "recipient_lawyer_id", "subject_line", "body_text", "sent_timestamp", "visibility_state", "has_attachment", "attachment_doc_id"], "values": emails}},
        {"insertOrUpdate": {"table": "WorkedOn", "columns": ["lawyer_id", "matter_id", "role", "hours_logged"], "values": worked_on}},
        {"insertOrUpdate": {"table": "BelongsToMatter", "columns": ["doc_id", "matter_id", "filing_type"], "values": belongs_to_matter}},
        {"insertOrUpdate": {"table": "ContainsClause", "columns": ["doc_id", "clause_id", "section_ref"], "values": contains_clause}},
        {"insertOrUpdate": {"table": "CitesPrecedent", "columns": ["source_doc_id", "target_doc_id", "citation_reason", "similarity_score"], "values": cites_precedent}},
        {"insertOrUpdate": {"table": "IntappWalls", "columns": ["wall_id", "lawyer_id", "matter_id", "rule_type", "reason", "enforced_at"], "values": intapp_walls}}
    ]

    res = commit_mutations(session, mutations, token)
    print("COMMITTED ALL SPANNER GRAPH NODES, EDGES & GEMINI-EMBEDDING-2 VECTORS:", json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
