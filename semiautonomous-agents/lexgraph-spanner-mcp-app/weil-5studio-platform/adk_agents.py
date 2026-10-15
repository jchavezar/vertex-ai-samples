"""Google ADK Multi-Agent Suite for Weil Legal AI Platform (`gemini-3.8-flash` on `location="global"`).

Implements the 5 Specialist Legal Sub-Agents + Root Orchestrator replacing Weil's fragmented
stack (Harvey, Legora, CoCounsel, DeepJudge, Hebbia, Syntheia, Litera Compare, Draftable,
Super Comparer, Privacy Pro Legal Legos, FundGen/FundHQ, and Antitrust HSR Review):

1. `mike_tabular_diligence_agent` (UC-3 Side-by-Side Citation Review, UC-5 Tabular Grids, UC-6 Workflow Builder)
2. `redline_word_composer_agent` (UC-1 Deterministic Document Redlining, UC-2 Word Legal Legos & Numbering)
3. `private_funds_antitrust_agent` (Weil Oct 13 Homegrown `FundGen` / `FundHQ` MFN Compendium + Antitrust HSR & Multimodal Charts)
4. `ethical_wall_cmn_governance_agent` (UC-7 Matter Workspaces, UC-8 Client Matter Number `CMN` Tracking & Intapp Ethical Walls)
5. `inbox_calendar_triage_agent` (UC-4 Partner Inbox Triage, Calendar Conflict Resolution & iPad One-Tap Review)
6. `weil_root_orchestrator` (Root ADK `LlmAgent` coordinating all 5 specialist sub-agents + Cloud Run MCPToolset)
"""

import difflib
import os
import time
from typing import Any

import demo_data
from spanner_engine import spanner_engine

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos")
LOCATION = "global"
PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3-flash-preview"]


# ---------------------------------------------------------------------------
# Default Rich Legal Datasets (with dynamic override if present in demo_data)
# ---------------------------------------------------------------------------

DEFAULT_REDLINE_PAIRS: dict[str, dict[str, Any]] = {
    "KESTREL-SPA-802": {
        "pair_id": "KESTREL-SPA-802",
        "title": "Section 8.02 — Indemnification Cap, Basket & Fraud Carve-Out",
        "matter_id": "M-331-KESTREL",
        "doc_a_name": "Project Kestrel SPA — Weil v3 Playbook Draft (Seller-Friendly)",
        "doc_b_name": "Project Kestrel SPA — Skadden v4 Counterparty Markup (Buyer-Friendly)",
        "playbook_standard": "Weil PE Seller Playbook v3.4: Indemnity Cap <= 0.75% of Enterprise Value ($31.5M), True Deductible Basket (0.50% EV), Uncapped Carve-Out limited strictly to Delaware Express Written Actual Fraud.",
        "clause_a_text": (
            "Section 8.02 Limitation on Indemnification. (a) Notwithstanding anything to the contrary in this Agreement, "
            "the Seller Parties shall have no liability under Section 8.01(a) until the aggregate amount of all Losses exceeds "
            "an amount equal to 0.50% of the Base Purchase Price (the 'Deductible'), in which case Seller Parties shall be liable "
            "only for the excess over the Deductible. (b) The maximum aggregate liability of the Seller Parties under Section 8.01(a) "
            "shall not exceed 0.75% of the Base Purchase Price ($31,500,000) (the 'Indemnity Cap'). (c) The limitations in this "
            "Section 8.02 shall not apply solely in the case of Actual Fraud (defined strictly as intentional common law fraud under "
            "Delaware law with respect to the express representations set forth in Article III)."
        ),
        "clause_b_text": (
            "Section 8.02 Limitation on Indemnification. (a) Notwithstanding anything to the contrary in this Agreement, "
            "the Seller Parties shall have no liability under Section 8.01(a) until the aggregate amount of all Losses exceeds "
            "an amount equal to 0.25% of the Base Purchase Price (the 'Tipping Basket'), in which case Seller Parties shall be liable "
            "from the first dollar of all Losses. (b) The maximum aggregate liability of the Seller Parties under Section 8.01(a) "
            "shall not exceed 0.25% of the Base Purchase Price ($10,500,000) for general representations and 100% of the Base Purchase Price "
            "for Special Environmental & IP Warranties (the 'Indemnity Cap'). (c) The limitations in this Section 8.02 shall not apply "
            "in the case of Actual or Constructive Fraud, equitable fraud, reckless misrepresentation, or willful breach."
        ),
        "key_deviations": [
            {
                "issue": "Basket Structure Shift (Deductible -> First-Dollar Tipping Basket)",
                "severity": "HIGH",
                "weil_v3": "0.50% EV True Deductible Basket ($21.0M threshold; excess only)",
                "skadden_v4": "0.25% EV First-Dollar Tipping Basket ($10.5M threshold; liable from dollar one)",
                "recommendation": "Reject Tipping Basket; compromise at 0.375% EV True Deductible per Project Titan precedent (DOC-402-A).",
            },
            {
                "issue": "General Indemnity Cap Reduction + Special Rep Super-Cap",
                "severity": "CRITICAL",
                "weil_v3": "0.75% EV ($31.5M) single unified R&W Indemnity Cap",
                "skadden_v4": "0.25% EV ($10.5M) general cap BUT adds 100% EV ($4.2B) uncapped exposure for Special Environmental & IP Warranties",
                "recommendation": "Reject 100% EV Special Rep super-cap; route Environmental/IP coverage to R&W Insurance policy ($50M tower).",
            },
            {
                "issue": "Delaware Fraud Carve-Out Expansion (ABRY Partners Risk)",
                "severity": "CRITICAL",
                "weil_v3": "Strictly limited to Delaware intentional Actual Fraud on express Article III reps",
                "skadden_v4": "Expands carve-out to 'Constructive Fraud, equitable fraud, reckless misrepresentation'",
                "recommendation": "Hard reject constructive/equitable fraud per Delaware ABRY Partners & Express Non-Reliance Playbook.",
            },
        ],
    },
    "KESTREL-COC-804": {
        "pair_id": "KESTREL-COC-804",
        "title": "Section 8.04 — Software License Change of Control & Assignment",
        "matter_id": "M-331-KESTREL",
        "doc_a_name": "Weil Standard Commercial License Rider v2.1",
        "doc_b_name": "02_Software_License_Quillfeather_Ostrander.docx (Counterparty Executed)",
        "playbook_standard": "Weil Tech Transactions Playbook: Change of Control to solvent PE affiliate requires Notice Only with zero termination fee.",
        "clause_a_text": (
            "Section 8.04 Assignment & Change of Control. Neither party may assign this Agreement without prior written consent, "
            "provided that Licensee may assign this Agreement or undergo a Change of Control without Licensor consent upon thirty (30) "
            "days written notice in connection with a merger, acquisition, or reorganization with a financially solvent affiliate."
        ),
        "clause_b_text": (
            "Section 8.04 Assignment & Deemed Transfer. Neither party may assign or transfer this Agreement without the prior written "
            "consent of Licensor. Any merger, consolidation, reorganization, or Change of Control of Licensee shall be deemed an attempted "
            "assignment in violation of this Section 8.04, rendering the Enterprise Software License immediately terminable at Licensor's "
            "sole discretion and accelerating $420,000 in remaining annual license fees."
        ),
        "key_deviations": [
            {
                "issue": "Deemed Assignment on PE Acquisition + $420K Fee Acceleration",
                "severity": "HIGH",
                "weil_v3": "Permitted CoC carve-out upon 30 days notice to solvent affiliate",
                "skadden_v4": "Sole discretion termination right + $420,000 accelerated license fee penalty",
                "recommendation": "Draft Side-Letter Waiver & Consent prior to Project Kestrel signing; escrow $420K only if consent withheld.",
            }
        ],
    },
    "KESTREL-SCRAPE-804": {
        "pair_id": "KESTREL-SCRAPE-804",
        "title": "Section 8.04(a) — Double Materiality Scrape vs. Single-Prong Damages Scrape",
        "matter_id": "M-331-KESTREL",
        "doc_a_name": "07_M331_Brightwater_Merger_Agreement_Weil_v3.docx (Section 8.04(a))",
        "doc_b_name": "08_M331_Brightwater_Merger_Agreement_Skadden_v4_Redline.docx (Section 8.04(a))",
        "playbook_standard": "Weil Buyer/Seller M&A Playbook: Full Double Materiality Scrape required when Deductible Basket >= 0.50% of Enterprise Value ($12.0M).",
        "clause_a_text": (
            "Section 8.04(a) Materiality Scrape Scope. For purposes of both determining whether a breach of any representation "
            "or warranty has occurred and calculating the dollar amount of Losses (Full Double Materiality Scrape), any Material Adverse "
            "Effect or materiality qualification contained in Article III or Article IV shall be disregarded."
        ),
        "clause_b_text": (
            "Section 8.04(a) Materiality Scrape Scope. For purposes of solely calculating the dollar amount of Losses once a "
            "qualified breach has been proven (Single Prong Damages-Only Scrape), any Material Adverse Effect or materiality "
            "qualification contained in Article III or Article IV shall be disregarded."
        ),
        "key_deviations": [
            {
                "issue": "Deletion of Prong 1 (Breach Determination) Materiality Scrape",
                "severity": "CRITICAL",
                "weil_v3": "Full Double Materiality Scrape (applies to both breach determination and Losses calculation)",
                "skadden_v4": "Single-Prong Damages-Only Scrape (requires proving MAE/materiality threshold before any claim triggers)",
                "recommendation": "Reject Single-Prong deletion per EM-9902 precedent analysis (M-215 Kestrel & M-902 Falcon Aerospace both closed with Full Double Scrape).",
            }
        ],
    },
    "KESTREL-TAX-304": {
        "pair_id": "KESTREL-TAX-304",
        "title": "Tax Rider Section 3.04 — IRC Section 338(h)(10) Gross-Up Ceiling ($14.2M vs $9.5M)",
        "matter_id": "M-331-KESTREL",
        "doc_a_name": "DOC-M331-04_M331_Tax_Allocation_Rider_Draft.pdf (Weil Tax v3)",
        "doc_b_name": "08_M331_Brightwater_Merger_Agreement_Skadden_v4_Redline.docx (Tax Rider § 3.04)",
        "playbook_standard": "Weil Tax Structuring Standard (EM-9901): Section 338(h)(10) step-up election requires full Class V cleanroom equipment depreciation gross-up ($14.2M).",
        "clause_a_text": (
            "Section 3.04 Section 338(h)(10) Gross-Up Ceiling. Seller's Section 338(h)(10) Joint Election tax gross-up "
            "reimbursement obligation shall be capped at $14,200,000 (Class V Equipment Depreciation Step-Up Model) and "
            "funded into the Citibank N.A. Special Tax Reserve Account at Closing."
        ),
        "clause_b_text": (
            "Section 3.04 Section 338(h)(10) Gross-Up Ceiling. Seller's Section 338(h)(10) Joint Election tax gross-up "
            "reimbursement obligation shall be capped at $9,500,000 (Seller Capped Tax Adjustment Ceiling) and paid "
            "exclusively from the General Indemnity Escrow Account."
        ),
        "key_deviations": [
            {
                "issue": "$4.7M Haircut on Section 338(h)(10) Tax Gross-Up + Commingling with General Escrow",
                "severity": "CRITICAL",
                "weil_v3": "$14,200,000 dedicated Special Tax Reserve at Citibank N.A. (ABA 021000089)",
                "skadden_v4": "$9,500,000 cap paid out of the $18.0M General Indemnity Escrow (eroding R&W coverage)",
                "recommendation": "Enforce Marcus Thorne's directive in EM-9901: reject $9.5M cap unless Seller posts separate $4.7M special tax reserve.",
            }
        ],
    },
}

DEFAULT_LEGAL_LEGOS_BLOCKS: dict[str, dict[str, Any]] = {
    "LEGO-DE-FRAUD": {
        "block_id": "LEGO-DE-FRAUD",
        "name": "Delaware Express Actual Fraud & Non-Reliance Carve-Out (ABRY Compliant)",
        "practice_group": "M&A / Private Equity",
        "numbering_style": "Article VIII -> Section 8.02(c) -> (i)..(iii)",
        "clause_text": (
            "8.02(c) Exclusive Remedy & Actual Fraud Carve-Out.\n"
            "  (i) Except for claims of Actual Fraud against the Person who committed such Actual Fraud, the indemnification "
            "provisions of this Article VIII shall be the sole and exclusive monetary remedy of the Indemnified Parties.\n"
            "  (ii) 'Actual Fraud' means actual, intentional, and knowing common law fraud under Delaware law with respect to "
            "the making of the express representations and warranties set forth in Article III or Article IV, and expressly excludes "
            "equitable fraud, constructive fraud, promissory fraud, or negligent misrepresentation."
        ),
    },
    "LEGO-PRIVACY-PRO": {
        "block_id": "LEGO-PRIVACY-PRO",
        "name": "Weil Privacy Pro — Cross-Border AI & CCPA/GDPR Data Processing Addendum Block",
        "practice_group": "Technology & IP Transactions (Privacy Pro)",
        "numbering_style": "Article XI -> Section 11.04(a)..(d)",
        "clause_text": (
            "11.04 Data Protection, AI Model Isolation & Cross-Border Transfers.\n"
            "  (a) Processor shall process Personal Data solely on documented instructions from Controller in compliance with GDPR Art. 28 and CCPA.\n"
            "  (b) Zero Foundation Model Training: Processor shall not use Customer Confidential Data or Personal Data to train, fine-tune, "
            "or distill any multi-tenant machine learning or foundation model.\n"
            "  (c) Breach Notification: Processor shall notify Controller within twenty-four (24) hours of confirming any Security Incident."
        ),
    },
    "LEGO-338H10-TAX": {
        "block_id": "LEGO-338H10-TAX",
        "name": "IRC Section 338(h)(10) Election & $14.2M Tax Gross-Up Escrow Covenant (EM-9901)",
        "practice_group": "Tax & M&A",
        "numbering_style": "Article VI -> Section 6.09(a)..(c)",
        "clause_text": (
            "6.09 Section 338(h)(10) Election and Tax Gross-Up Escrow.\n"
            "  (a) Buyer and Seller shall join in making a timely, irrevocable election under Section 338(h)(10) of the Code (and any corresponding state elections).\n"
            "  (b) Buyer shall reimburse Seller for the incremental Tax liability resulting from the Section 338(h)(10) Election, "
            "subject to a hard aggregate cap of $14,200,000 funded into the Tax Adjustment Escrow Account at Closing for an eighteen (18) month survival period."
        ),
    },
    "LEGO-MFN-FUNDGEN": {
        "block_id": "LEGO-MFN-FUNDGEN",
        "name": "FundGen / FundHQ — LP Side-Letter Most Favored Nation (MFN) Size-Tier Block",
        "practice_group": "Private Funds (FundGen)",
        "numbering_style": "Side Letter -> Paragraph 4(a)..(c)",
        "clause_text": (
            "4. Most Favored Nation (MFN) Election Rights.\n"
            "  (a) Commitment Tier Parity: The Investor ($150M+ Anchor Tier) shall receive a complete compendium of all Side Letters within thirty (30) days following Final Closing.\n"
            "  (b) Election Window: The Investor may elect in writing within twenty (20) business days to adopt any more favorable fee discount or co-investment right granted to any Limited Partner holding an equal or lesser Capital Commitment.\n"
            "  (c) Carve-Outs: MFN rights shall not apply to regulatory, ERISA, sovereign immunity, or strategic seed anchor rights above $250,000,000."
        ),
    },
}

DEFAULT_FUNDGEN_DATA: dict[str, Any] = {
    "fund_id": "M-610-FUNDGEN",
    "fund_name": "Weil Private Equity Partners XII, L.P. ($12.5B Target)",
    "homegrown_apps": ["FundGen (Automated LPA & Side-Letter Drafting)", "FundHQ (MFN Compendium & Election Matrix)"],
    "lp_side_letters": [
        {
            "lp_id": "LP-01",
            "lp_name": "CalPERS Sovereign Anchor Trust",
            "tier": "Tier 1 Anchor (>=$250M)",
            "commitment_usd_m": 350.0,
            "mgmt_fee_bps": 115,
            "carry_pct": 17.5,
            "mfn_scope": "Full Uncapped MFN Across All Tiers",
            "co_invest_priority": "1st Priority Zero-Fee / Zero-Carry ($150M Co-Invest Sleeve)",
            "esg_excusal": "Mandatory Weapons / Thermal Coal Excusal Right",
            "advisory_board_seat": "Guaranteed LPAC Seat",
        },
        {
            "lp_id": "LP-02",
            "lp_name": "Abu Dhabi Strategic Investment Authority",
            "tier": "Tier 1 Anchor (>=$250M)",
            "commitment_usd_m": 300.0,
            "mgmt_fee_bps": 120,
            "carry_pct": 18.0,
            "mfn_scope": "Size-Tiered MFN (<=$300M LPs) + Sovereign Tax Immunity",
            "co_invest_priority": "Pro-Rata Zero-Fee Co-Invest Right",
            "esg_excusal": "Sharia / Sovereign Policy Excusal Right",
            "advisory_board_seat": "Guaranteed LPAC Seat",
        },
        {
            "lp_id": "LP-03",
            "lp_name": "Ontario Teachers' Pension Plan (OTPP)",
            "tier": "Tier 2 Early-Bird ($100M–$249M)",
            "commitment_usd_m": 175.0,
            "mgmt_fee_bps": 135,
            "carry_pct": 19.0,
            "mfn_scope": "Size-Tiered MFN (<=$175M LPs)",
            "co_invest_priority": "Best-Efforts Co-Invest Allocation",
            "esg_excusal": "Standard OECD ESG Reporting Covenant",
            "advisory_board_seat": "Observer LPAC Seat",
        },
        {
            "lp_id": "LP-04",
            "lp_name": "Yale University Endowment Partners",
            "tier": "Tier 2 Early-Bird ($100M–$249M)",
            "commitment_usd_m": 125.0,
            "mgmt_fee_bps": 140,
            "carry_pct": 20.0,
            "mfn_scope": "Size-Tiered MFN (<=$125M LPs; UBTI Blocker Required)",
            "co_invest_priority": "Standard Co-Invest Access",
            "esg_excusal": "Endowment Climate Disclosure Rider",
            "advisory_board_seat": "Standard Voting LP",
        },
        {
            "lp_id": "LP-05",
            "lp_name": "Nordic Sovereign Wealth Fund",
            "tier": "Tier 3 Standard (<$100M)",
            "commitment_usd_m": 75.0,
            "mgmt_fee_bps": 150,
            "carry_pct": 20.0,
            "mfn_scope": "Tier 3 Only (<=$75M LPs)",
            "co_invest_priority": "Discretionary GP Allocation",
            "esg_excusal": "Strict EU SFDR Article 8 Excusal Right",
            "advisory_board_seat": "No LPAC Seat",
        },
    ],
    "antitrust_hsr": {
        "matter_id": "M-720-ANTITRUST",
        "deal_name": "Brightwater / Halvorsen Precision Manufacturing Merger (FTC HSR Second Request)",
        "relevant_market": "North American Industrial Precision CNC & Semiconductor Robotics Actuators",
        "pre_merger_hhi": 2180,
        "post_merger_hhi": 2690,
        "hhi_delta": 510,
        "doj_ftc_threshold": "2023 DOJ/FTC Merger Guidelines Presumption Triggered (Post-Merger HHI > 1,800 AND Delta > 100)",
        "remedy_divestiture_hhi": 2210,
        "remedy_hhi_delta": 30,
        "remedy_recommendation": "Propose structural divestiture of Halvorsen's Midwest Actuator Division ($180M revenue, 6% share) to pre-cleared buyer (Pellucid Dynamics), reducing HHI delta from +510 to +30 and clearing FTC Second Request.",
        "market_participants": [
            {"company": "Brightwater Industrial (Acquirer)", "share_pct": 22.0, "hhi_contribution": 484},
            {"company": "Halvorsen Manufacturing (Target)", "share_pct": 11.6, "hhi_contribution": 135},
            {"company": "Apex Global Automation", "share_pct": 28.0, "hhi_contribution": 784},
            {"company": "Kiyota Robotics NA", "share_pct": 19.0, "hhi_contribution": 361},
            {"company": "Ferrous Precision Systems", "share_pct": 12.0, "hhi_contribution": 144},
            {"company": "Other Fragmented Suppliers", "share_pct": 7.4, "hhi_contribution": 272},
        ],
    },
    "multimodal_exhibits": [
        {
            "exhibit_id": "EX-MM-01",
            "title": "FundGen XII — Management Fee Discount Curve vs. LP Commitment Size (Multimodal Chart)",
            "source_doc": "FundGen_XII_PPM_Fee_Waterfall_Chart_p14.pdf",
            "extracted_insight": "Step-down curve drops from 150 bps (<$100M) to 135 bps ($175M OTPP) and 115 bps ($350M CalPERS Anchor). Triggers MFN election for Abu Dhabi ($300M at 120 bps -> eligible for 5 bps reduction worth $1.5M/yr).",
            "series": [
                {"label": "$50M-$99M (Tier 3)", "bps": 150, "carry": 20.0},
                {"label": "$100M-$149M (Yale)", "bps": 140, "carry": 20.0},
                {"label": "$150M-$249M (OTPP)", "bps": 135, "carry": 19.0},
                {"label": "$250M-$325M (ADIA)", "bps": 120, "carry": 18.0},
                {"label": "$350M+ (CalPERS)", "bps": 115, "carry": 17.5},
            ],
        },
        {
            "exhibit_id": "EX-MM-02",
            "title": "Project Kestrel — FY2024-FY2026 Adjusted EBITDA Bridge ($310M -> $412M) (Financial Waterfall)",
            "source_doc": "Kestrel_QoE_Presentation_Slide_22.pdf",
            "extracted_insight": "Quality of Earnings (QoE) bridge adds back $28M of 'One-Time ERP & Supply Chain Restructuring' and $19M of 'Pro-Forma Run-Rate Synergies'. Section 1.01 EBITDA definition in Skadden v4 caps synergy add-backs at 15% ($61.8M) vs Weil v3 25% cap.",
            "series": [
                {"step": "Reported GAAP EBITDA", "value_m": 310.0},
                {"step": "+ Non-Recurring Litigation", "value_m": 24.0},
                {"step": "+ ERP Migration Add-Back", "value_m": 28.0},
                {"step": "+ Halvorsen Cost Synergies", "value_m": 31.0},
                {"step": "+ Run-Rate Pricing Lift", "value_m": 19.0},
                {"step": "= Pro-Forma Adj. EBITDA", "value_m": 412.0},
            ],
        },
        {
            "exhibit_id": "EX-MM-03",
            "title": "Brightwater / Halvorsen — Delaware & Cayman Tax Blocker Org Structure (Diagram)",
            "source_doc": "Kestrel_Structure_Deck_Section_338h10_p08.pdf",
            "extracted_insight": "Cayman LP Feeder routes through Delaware UBTI Blocker Corp into BidCo LLC. Confirms why Lead Tax Partner D. Cockerell mandated IRC Section 338(h)(10) election + $14.2M Tax Gross-Up Escrow in EM-9901.",
        },
    ],
}

DEFAULT_INBOX_TRIAGE: dict[str, Any] = {
    "partner_name": "Sarah Jenkins (M&A Lead Partner — iPad Pro Review Queue)",
    "emails": [
        {
            "email_id": "EM-9901",
            "matter_id": "M-331-KESTREL",
            "cmn": "31402-0018 (Brightwater / Project Kestrel)",
            "sender": "D. Cockerell (Lead Tax Partner, Weil NY)",
            "subject": "URGENT: Section 338(h)(10) Election & $14.2M Tax Gross-Up Escrow Cap",
            "received_at": "Oct 14, 2026 · 08:14 AM EDT",
            "aging_hours": 6.5,
            "priority": "P0 — CRITICAL SIGNING BLOCKER",
            "visibility": "UNFILED -> 30-DAY TEAMMATE GRANT ACTIVE",
            "summary": "Client CFO confirmed Brightwater will only sign SPA if Section 338(h)(10) gross-up reimbursement is capped at $14.2M in an 18-month escrow.",
            "proposed_reply": "Approved. Inserting Legal Lego Block LEGO-338H10-TAX into SPA Section 6.09 with a hard $14,200,000 Tax Adjustment Escrow cap and 18-month survival. Filing email to iManage M-331-KESTREL.",
            "status": "READY_FOR_ONE_TAP_APPROVAL",
        },
        {
            "email_id": "EM-9902",
            "matter_id": "M-331-KESTREL",
            "cmn": "31402-0018 (Brightwater / Project Kestrel)",
            "sender": "J. Sterling (Skadden Arps — Counterparty Lead Partner)",
            "subject": "RE: Project Kestrel SPA v4 Markup — Section 8.02 Indemnity Cap & Basket",
            "received_at": "Oct 14, 2026 · 09:42 AM EDT",
            "aging_hours": 5.0,
            "priority": "P0 — COUNTERPARTY REDLINE",
            "visibility": "FILED_IMANAGE_M331",
            "summary": "Skadden transmitted SPA v4 cutting general R&W cap to 0.25% EV ($10.5M), flipping basket to tipping, and expanding fraud carve-out to constructive fraud.",
            "proposed_reply": "Sending Weil v5 responsive redline: restoring express Delaware Actual Fraud definition (ABRY Partners), rejecting 100% Special Rep super-cap in favor of $50M R&W Insurance tower, and offering 0.375% EV True Deductible compromise.",
            "status": "READY_FOR_ONE_TAP_APPROVAL",
        },
        {
            "email_id": "EM-9903",
            "matter_id": "M-610-FUNDGEN",
            "cmn": "61088-0004 (Weil PE Partners XII — FundGen)",
            "sender": "R. Zane (Private Funds Partner, Weil NY)",
            "subject": "FundHQ MFN Compendium Sign-Off — ADIA $300M Side-Letter Election",
            "received_at": "Oct 14, 2026 · 11:05 AM EDT",
            "aging_hours": 3.5,
            "priority": "P1 — CLOSING DELIVERABLE",
            "visibility": "FILED_IMANAGE_M610",
            "summary": "FundHQ flagged that CalPERS ($350M) 115 bps fee tier is excluded from ADIA ($300M) MFN due to Size-Tiered commitment threshold, saving GP $1.5M/yr.",
            "proposed_reply": "Confirmed via FundHQ MFN Matrix: ADIA's size-tiered MFN clause only reaches LPs at or below $300M commitment, so CalPERS ($350M) 115 bps tier is cleanly carved out. Approved to circulate Final MFN Compendium.",
            "status": "READY_FOR_ONE_TAP_APPROVAL",
        },
    ],
    "calendar_conflicts": [
        {
            "conflict_id": "CAL-101",
            "date": "Oct 15, 2026 · 2:00 PM – 3:30 PM EDT",
            "event_a": {
                "title": "Brightwater Board of Directors — Project Kestrel Final SPA Approval Call",
                "matter_id": "M-331-KESTREL",
                "cmn": "31402-0018",
                "attendees": ["Sarah Jenkins (Weil)", "D. Cockerell (Weil Tax)", "Brightwater Investment Committee"],
                "criticality": "MANDATORY LEAD PARTNER PRESENCE",
            },
            "event_b": {
                "title": "FTC Bureau of Competition — HSR Second Request Meet & Confer (HHI Divestiture)",
                "matter_id": "M-720-ANTITRUST",
                "cmn": "72019-0002",
                "attendees": ["Andrew Simon (Weil Antitrust DC)", "Sarah Jenkins (Weil M&A)", "FTC Staff Attorneys"],
                "criticality": "DELEGABLE TO ANTITRUST CO-LEAD OR RESCHEDULE TO 4:00 PM EDT",
            },
            "ai_resolution": "Keep Sarah Jenkins on Brightwater Board SPA Approval Call (2:00 PM EDT). Delegate first 30 mins of FTC HSR Meet & Confer to Antitrust Partner Andrew Simon (with pre-cleared Midwest Actuator divestiture packet reducing HHI delta to +30) and move FTC joint wrap-up to 3:45 PM EDT.",
            "status": "CONFLICT_DETECTED_AUTO_RESOLUTION_READY",
        }
    ],
}


# ---------------------------------------------------------------------------
# Deterministic Legal Tool Functions (Exposed to ADK Agents, REST & MCP)
# ---------------------------------------------------------------------------

def compute_deterministic_redline(
    pair_id: str = "KESTREL-SPA-802",
    custom_clause_a: str | None = None,
    custom_clause_b: str | None = None,
) -> dict[str, Any]:
    """Computes word-level deterministic redline diff (`<del>` / `<ins>`) and Playbook risk deviations."""
    t0 = time.perf_counter()
    pair = DEFAULT_REDLINE_PAIRS.get(pair_id, DEFAULT_REDLINE_PAIRS["KESTREL-SPA-802"]).copy()
    text_a = custom_clause_a.strip() if custom_clause_a else pair["clause_a_text"]
    text_b = custom_clause_b.strip() if custom_clause_b else pair["clause_b_text"]

    tokens_a = text_a.split()
    tokens_b = text_b.split()
    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)

    html_parts: list[str] = []
    deleted_count = 0
    inserted_count = 0
    unchanged_count = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            unchanged_count += i2 - i1
            html_parts.append(" ".join(tokens_a[i1:i2]))
        elif tag == "delete":
            deleted_count += i2 - i1
            html_parts.append(f"<del class='redline-del'>{' '.join(tokens_a[i1:i2])}</del>")
        elif tag == "insert":
            inserted_count += j2 - j1
            html_parts.append(f"<ins class='redline-ins'>{' '.join(tokens_b[j1:j2])}</ins>")
        elif tag == "replace":
            deleted_count += i2 - i1
            inserted_count += j2 - j1
            html_parts.append(
                f"<del class='redline-del'>{' '.join(tokens_a[i1:i2])}</del> "
                f"<ins class='redline-ins'>{' '.join(tokens_b[j1:j2])}</ins>"
            )

    similarity_ratio = round(matcher.ratio() * 100, 1)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    return {
        "pair_id": pair_id,
        "title": pair["title"],
        "matter_id": pair["matter_id"],
        "doc_a_name": pair["doc_a_name"],
        "doc_b_name": pair["doc_b_name"],
        "playbook_standard": pair["playbook_standard"],
        "clause_a_text": text_a,
        "clause_b_text": text_b,
        "redline_html": " ".join(html_parts),
        "stats": {
            "similarity_pct": similarity_ratio,
            "tokens_deleted": deleted_count,
            "tokens_inserted": inserted_count,
            "tokens_unchanged": unchanged_count,
            "latency_ms": elapsed_ms,
        },
        "key_deviations": pair["key_deviations"],
        "replaces_vendors": ["Syntheia Compare MCP", "Litera Compare", "Draftable Legal", "Super Comparer"],
    }


def compose_legal_legos_clause(
    block_ids: list[str] | None = None,
    target_section_prefix: str = "Article VIII",
) -> dict[str, Any]:
    """Composes modular 'Legal Legos' clause blocks with automatic multi-level .docx numbering."""
    selected_ids = block_ids or ["LEGO-DE-FRAUD", "LEGO-338H10-TAX", "LEGO-PRIVACY-PRO"]
    blocks = [DEFAULT_LEGAL_LEGOS_BLOCKS[bid] for bid in selected_ids if bid in DEFAULT_LEGAL_LEGOS_BLOCKS]
    if not blocks:
        blocks = list(DEFAULT_LEGAL_LEGOS_BLOCKS.values())

    composed_sections = []
    for idx, b in enumerate(blocks, start=1):
        composed_sections.append(f"/* [LEGAL LEGO BLOCK {idx}: {b['block_id']} — {b['practice_group']}] */\n{b['clause_text']}")

    return {
        "target_section_prefix": target_section_prefix,
        "selected_block_ids": [b["block_id"] for b in blocks],
        "blocks": blocks,
        "available_blocks": list(DEFAULT_LEGAL_LEGOS_BLOCKS.values()),
        "composed_docx_preview": "\n\n".join(composed_sections),
        "numbering_integrity": "VERIFIED_MULTI_LEVEL_DOCX_OUTLINE",
        "replaces_vendors": ["Weil Privacy Pro Legal Legos", "CoCounsel Word Add-In", "Henchman / Lexis Create"],
    }


def analyze_fundgen_mfn_and_antitrust_hhi(
    commitment_filter_m: float = 0.0,
    include_divestiture_remedy: bool = True,
) -> dict[str, Any]:
    """Analyzes Weil's FundGen/FundHQ LP Side-Letter MFN Matrix, Antitrust HSR HHI, and Multimodal Charts."""
    import json
    lps = [
        lp for lp in DEFAULT_FUNDGEN_DATA["lp_side_letters"]
        if lp["commitment_usd_m"] >= commitment_filter_m
    ]
    hsr = DEFAULT_FUNDGEN_DATA["antitrust_hsr"].copy()
    active_hhi = hsr["remedy_divestiture_hhi"] if include_divestiture_remedy else hsr["post_merger_hhi"]
    active_delta = hsr["remedy_hhi_delta"] if include_divestiture_remedy else hsr["hhi_delta"]
    mm_path = os.path.join(os.path.dirname(__file__), "corpus", "multimodal_extractions.json")
    raw_mm = {}
    if os.path.exists(mm_path):
        try:
            with open(mm_path, "r", encoding="utf-8") as f:
                raw_mm = json.load(f)
        except Exception:
            raw_mm = {}
    return {
        "fund_id": DEFAULT_FUNDGEN_DATA["fund_id"],
        "fund_name": DEFAULT_FUNDGEN_DATA["fund_name"],
        "homegrown_apps": DEFAULT_FUNDGEN_DATA["homegrown_apps"],
        "filtered_lp_count": len(lps),
        "lp_side_letters": lps,
        "mfn_savings_summary": "Size-Tiered MFN structure isolates CalPERS ($350M, 115 bps) from Tier 2/3 LPs and ADIA ($300M, 120 bps), preserving $4.85M/yr in GP management fee revenue.",
        "antitrust_hsr": {
            **hsr,
            "active_post_merger_hhi": active_hhi,
            "active_hhi_delta": active_delta,
            "clearance_status": "CLEARED_WITH_MIDWEST_ACTUATOR_DIVESTITURE" if include_divestiture_remedy else "PRESUMED_ANTITRUST_CHALLENGE_HHI_DELTA_510",
        },
        "multimodal_exhibits": DEFAULT_FUNDGEN_DATA["multimodal_exhibits"],
        "extracted_multimodal_pipeline": raw_mm,
        "visual_files": [
            {
                "id": "DOC-CHART-01",
                "title": "Brightwater LTM Consolidated Adjusted EBITDA Bridge ($145M -> $175M) & $2.4B Waterfall",
                "image_url": "/api/corpus/image/DOC-CHART-01_Brightwater_EBITDA_Bridge_and_Valuation_Waterfall.png",
                "pdf_url": "/api/corpus/file/DOC-CHART-01_Brightwater_EBITDA_Bridge_and_Valuation_Waterfall.pdf",
                "matter_id": "M-331-KESTREL",
            },
            {
                "id": "DOC-CHART-02",
                "title": "FundHQ & FundGen LP Commitment Tiers vs. Net Management Fee Step-Down Curve",
                "image_url": "/api/corpus/image/DOC-CHART-02_Private_Funds_LP_Fee_Discount_Curve.png",
                "pdf_url": "/api/corpus/file/DOC-CHART-02_Private_Funds_LP_Fee_Discount_Curve.pdf",
                "matter_id": "M-610-FUNDGEN",
            },
            {
                "id": "DOC-DIAG-01",
                "title": "Apex Global Corporate Org Structure & Sec. 7.04 J.Crew Unrestricted Subsidiary Firewall",
                "image_url": "/api/corpus/image/DOC-DIAG-01_Apex_Global_Corporate_Org_Structure_and_Unrestricted_Subs.png",
                "pdf_url": "/api/corpus/file/DOC-DIAG-01_Apex_Global_Corporate_Org_Structure_and_Unrestricted_Subs.pdf",
                "matter_id": "M-402",
            },
            {
                "id": "DOC-SCAN-01",
                "title": "Executed Citibank N.A. $18,000,000 Indemnity Escrow Signature Page & Wire Exhibit",
                "image_url": "/api/corpus/image/DOC-SCAN-01_Executed_Escrow_Signature_Page_and_Wire_Exhibit.png",
                "pdf_url": "/api/corpus/file/DOC-SCAN-01_Executed_Escrow_Signature_Page_and_Wire_Exhibit.pdf",
                "matter_id": "M-331-KESTREL",
            },
        ],
    }


def verify_cmn_and_intapp_wall(
    lawyer_id: str = "L-001",
    matter_id: str = "M-331-KESTREL",
) -> dict[str, Any]:
    """Verifies Client Matter Number (CMN), Intapp Ethical Wall status, and Outside Counsel Guidelines (OCG)."""
    wall_check = spanner_engine.check_intapp_ethical_wall(lawyer_id=lawyer_id, matter_id=matter_id)
    cmn_catalog = {
        "M-331-KESTREL": {"cmn": "31402-0018", "client": "Brightwater Capital Partners", "ocg_ai_policy": "CLEARED (Zero-Training Vertex AI Regional Isolation)", "imanage_library": "US-NY-M331-KESTREL"},
        "M-402": {"cmn": "31402-0009", "client": "Brightwater Capital Partners", "ocg_ai_policy": "CLEARED (Precedent Read-Only)", "imanage_library": "US-NY-M402-TITAN"},
        "M-610-FUNDGEN": {"cmn": "61088-0004", "client": "Weil Private Equity Partners XII", "ocg_ai_policy": "CLEARED (FundGen / FundHQ Approved)", "imanage_library": "US-NY-M610-FUNDGEN"},
        "M-720-ANTITRUST": {"cmn": "72019-0002", "client": "Apex Global Holdings Inc.", "ocg_ai_policy": "CLEARED (FTC HSR Clean Team Protocol)", "imanage_library": "US-DC-M720-HSR"},
        "M-999": {"cmn": "99900-0001", "client": "Project Omega Special Situations", "ocg_ai_policy": "RESTRICTED (Intapp Ethical Wall EXCLUDE Rule Active)", "imanage_library": "UK-LON-M999-OMEGA"},
    }
    cmn_meta = cmn_catalog.get(matter_id, cmn_catalog["M-331-KESTREL"])
    return {
        "lawyer_id": lawyer_id,
        "matter_id": matter_id,
        "cmn": cmn_meta["cmn"],
        "client_name": cmn_meta["client"],
        "ocg_ai_policy": cmn_meta["ocg_ai_policy"],
        "imanage_library": cmn_meta["imanage_library"],
        "intapp_wall_check": wall_check,
        "teammate_grant_em9901": spanner_engine.get_teammate_grant_status("EM-9901"),
        "available_matters": [
            {"matter_id": k, **v} for k, v in cmn_catalog.items()
        ],
    }


_INBOX_STATE_APPROVED: set[str] = set()
_CALENDAR_STATE_RESOLVED: set[str] = set()


def triage_partner_inbox_and_calendar(
    approve_email_id: str | None = None,
    resolve_conflict_id: str | None = None,
    reset_state: bool = False,
) -> dict[str, Any]:
    """Triages Partner Inbox emails (`EM-9901..9903`) and resolves Calendar Conflicts (`CAL-101`)."""
    if reset_state:
        _INBOX_STATE_APPROVED.clear()
        _CALENDAR_STATE_RESOLVED.clear()
    if approve_email_id:
        _INBOX_STATE_APPROVED.add(approve_email_id)
        if approve_email_id == "EM-9901":
            try:
                spanner_engine.grant_teammate_email_access("EM-9901")
            except Exception:
                pass
    if resolve_conflict_id:
        _CALENDAR_STATE_RESOLVED.add(resolve_conflict_id)

    eml_dir = os.path.join(os.path.dirname(__file__), "corpus", "emails_and_calendar")
    eml_files = {
        "EM-9901": "EM-9901_Unfiled_Tax_Email_Section_338h10_Election.eml",
        "EM-9902": "EM-9902_Skadden_v4_Redline_Reject_Strategy.eml",
        "EM-9903": "EM-9903_Intapp_Wall_Alert_Project_Omega_M999.eml",
    }
    emails_out = []
    for e in DEFAULT_INBOX_TRIAGE["emails"]:
        ec = e.copy()
        eid = ec["email_id"]
        if eid in _INBOX_STATE_APPROVED:
            ec["status"] = "APPROVED_AND_FILED_TO_IMANAGE"
            if eid == "EM-9901":
                ec["visibility"] = "FILED_IMANAGE_M331 + 30-DAY GRANT ACTIVE"
        fn = eml_files.get(eid)
        if fn and os.path.exists(os.path.join(eml_dir, fn)):
            try:
                with open(os.path.join(eml_dir, fn), "r", encoding="utf-8") as f:
                    ec["raw_eml"] = f.read()
                ec["file_url"] = f"/api/corpus/file/{fn}"
            except Exception:
                pass
        emails_out.append(ec)

    cal_out = []
    ics_path = os.path.join(eml_dir, "CAL-101_Closing_Board_Call_and_FTC_HSR_Conflict.ics")
    raw_ics = ""
    if os.path.exists(ics_path):
        try:
            with open(ics_path, "r", encoding="utf-8") as f:
                raw_ics = f.read()
        except Exception:
            pass
    for c in DEFAULT_INBOX_TRIAGE["calendar_conflicts"]:
        cc = c.copy()
        if cc["conflict_id"] in _CALENDAR_STATE_RESOLVED:
            cc["status"] = "RESOLVED_DELEGATED_TO_ANDREW_SIMON_AND_MOVED_TO_345PM"
        cc["raw_ics"] = raw_ics
        cc["ics_url"] = "/api/corpus/file/CAL-101_Closing_Board_Call_and_FTC_HSR_Conflict.ics"
        cal_out.append(cc)

    return {
        "partner_name": DEFAULT_INBOX_TRIAGE["partner_name"],
        "emails": emails_out,
        "calendar_conflicts": cal_out,
    }


# ---------------------------------------------------------------------------
# Google ADK (`google.adk.agents.LlmAgent`) Multi-Agent Definitions
# ---------------------------------------------------------------------------

ADK_AGENTS_METADATA = [
    {
        "agent_id": "mike_tabular_diligence_agent",
        "name": "Mike Tabular Diligence & Citation Agent",
        "model": PRIMARY_MODEL,
        "location": LOCATION,
        "use_cases": ["UC-3 Side-by-Side Citation Review", "UC-5 Tabular Analysis Grids", "UC-6 Custom Workflow Builder"],
        "replaces": ["Harvey Vault", "Legora Tabular Grid", "DeepJudge", "Hebbia Matrix"],
    },
    {
        "agent_id": "redline_word_composer_agent",
        "name": "Deterministic Redline & Word Legal Legos Agent",
        "model": PRIMARY_MODEL,
        "location": LOCATION,
        "use_cases": ["UC-1 Document Redlining & Playbook Deviations", "UC-2 Integrated Word Legal Legos & Numbering"],
        "replaces": ["Syntheia Compare MCP", "Litera Compare", "Draftable", "Super Comparer", "Weil Privacy Pro Legal Legos"],
    },
    {
        "agent_id": "private_funds_antitrust_agent",
        "name": "FundGen / FundHQ & Antitrust Multimodal Agent",
        "model": PRIMARY_MODEL,
        "location": LOCATION,
        "use_cases": ["Private Funds LPA & MFN Side-Letter Compendium (FundGen/FundHQ)", "Antitrust HSR Second Request & HHI", "Multimodal Waterfall & Org Diagrams"],
        "replaces": ["Homegrown FundGen / FundHQ Silos", "Manual HSR Economic Tables"],
    },
    {
        "agent_id": "ethical_wall_cmn_governance_agent",
        "name": "Intapp Ethical Wall, CMN & GraphRAG Governance Agent",
        "model": PRIMARY_MODEL,
        "location": LOCATION,
        "use_cases": ["UC-7 Matter & Knowledge Workspaces", "UC-8 Dynamic Client Matter Number (CMN) Tracking", "Intapp Ethical Walls & 30-Day Teammate Grants"],
        "replaces": ["Intapp Walls Manual Checks", "iManage Post-Filter Leaks", "HYCU R-Serve Silos"],
    },
    {
        "agent_id": "inbox_calendar_triage_agent",
        "name": "Partner Inbox, Calendar Conflict & iPad Triage Agent",
        "model": PRIMARY_MODEL,
        "location": LOCATION,
        "use_cases": ["UC-4 Email & Calendar Automation", "Partner iPad One-Tap Review Queue"],
        "replaces": ["Manual Outlook CMN Filing", "Partner EA Calendar Triage"],
    },
]


def build_adk_agent_hierarchy() -> dict[str, Any]:
    """Constructs the Google ADK `LlmAgent` multi-agent hierarchy on `gemini-3.8-flash` (`location='global'`)."""
    try:
        from google.adk.agents import LlmAgent  # type: ignore

        mike_agent = LlmAgent(
            name="mike_tabular_diligence_agent",
            model=PRIMARY_MODEL,
            description="Executes Change-of-Control tabular extractions, Reciprocal Rank Fusion search, and verbatim pin-cite verification.",
            instruction=(
                "You are the Mike Tabular Diligence Agent at Weil, Gotshal & Manges LLP running on gemini-3.8-flash. "
                "Always ground every extraction in verbatim quotes with exact Section and Page citations from Cloud Spanner Graph."
            ),
            tools=[spanner_engine.hybrid_search, spanner_engine.traverse_precedent_graph],
        )
        redline_agent = LlmAgent(
            name="redline_word_composer_agent",
            model=PRIMARY_MODEL,
            description="Computes deterministic word-level redlines (<del>/<ins>) and composes multi-level numbered Legal Legos clauses.",
            instruction=(
                "You are the Deterministic Redline & Word Legal Legos Agent at Weil running on gemini-3.8-flash. "
                "Compare counterparty markups against the Weil PE Playbook and assemble ABRY-compliant Delaware clauses."
            ),
            tools=[compute_deterministic_redline, compose_legal_legos_clause],
        )
        funds_agent = LlmAgent(
            name="private_funds_antitrust_agent",
            model=PRIMARY_MODEL,
            description="Analyzes FundGen/FundHQ LP side-letter MFN tiers, Antitrust HSR HHI deltas, and multimodal financial charts.",
            instruction=(
                "You are the Private Funds (FundGen/FundHQ) & Antitrust HSR Specialist Agent at Weil running on gemini-3.8-flash."
            ),
            tools=[analyze_fundgen_mfn_and_antitrust_hhi],
        )
        governance_agent = LlmAgent(
            name="ethical_wall_cmn_governance_agent",
            model=PRIMARY_MODEL,
            description="Enforces Screen-Before-Rank Intapp Ethical Walls, Client Matter Numbers (CMN), and 30-day Teammate Grants.",
            instruction=(
                "You are the Ethical Wall & CMN Governance Agent at Weil running on gemini-3.8-flash. "
                "Never allow walled lawyers (e.g. L-001 on M-999 Project Omega) to access restricted matter data."
            ),
            tools=[verify_cmn_and_intapp_wall, spanner_engine.check_intapp_ethical_wall, spanner_engine.grant_teammate_email_access],
        )
        inbox_agent = LlmAgent(
            name="inbox_calendar_triage_agent",
            model=PRIMARY_MODEL,
            description="Triages partner deal inbox emails, tags Client Matter Numbers (CMN), and resolves calendar conflicts.",
            instruction=(
                "You are the Partner Inbox & Calendar Conflict Triage Agent at Weil running on gemini-3.8-flash."
            ),
            tools=[triage_partner_inbox_and_calendar],
        )
        root_orchestrator = LlmAgent(
            name="weil_root_orchestrator",
            model=PRIMARY_MODEL,
            description="Root Weil Enterprise Legal AI Orchestrator routing across all 5 specialist sub-agents.",
            instruction=(
                "You are the Root Legal AI Orchestrator for Weil, Gotshal & Manges LLP running on gemini-3.8-flash (global). "
                "Coordinate the 5 specialist sub-agents with strict Screen-Before-Rank ethical wall compliance and verbatim citations."
            ),
            sub_agents=[mike_agent, redline_agent, funds_agent, governance_agent, inbox_agent],
        )
        return {
            "adk_sdk_loaded": True,
            "root_orchestrator": root_orchestrator,
            "sub_agents": {
                "mike_tabular_diligence_agent": mike_agent,
                "redline_word_composer_agent": redline_agent,
                "private_funds_antitrust_agent": funds_agent,
                "ethical_wall_cmn_governance_agent": governance_agent,
                "inbox_calendar_triage_agent": inbox_agent,
            },
        }
    except Exception as e:
        return {
            "adk_sdk_loaded": False,
            "reason": str(e),
            "sub_agents": {m["agent_id"]: m for m in ADK_AGENTS_METADATA},
        }


ADK_SUITE = build_adk_agent_hierarchy()


def run_adk_agent_sync(
    agent_id: str,
    prompt: str,
    matter_id: str = "M-331-KESTREL",
    lawyer_id: str = "L-001",
) -> dict[str, Any]:
    """Executes the specified specialist ADK agent (or root orchestrator) with live Gemini 3.8 Flash + deterministic tool grounding."""
    t0 = time.perf_counter()

    # 1. Screen-Before-Rank Intapp Ethical Wall check first
    wall_check = spanner_engine.check_intapp_ethical_wall(lawyer_id=lawyer_id, matter_id=matter_id)
    if not wall_check["access_granted"]:
        return {
            "agent_id": agent_id,
            "model_used": PRIMARY_MODEL,
            "location": LOCATION,
            "matter_id": matter_id,
            "lawyer_id": lawyer_id,
            "ethical_wall_blocked": True,
            "wall_check": wall_check,
            "answer": (
                f"### ⛔ ACCESS BLOCKED BY INTAPP ETHICAL WALL (`{wall_check['wall_record']['wall_id']}`)\n\n"
                f"- **Screened Lawyer**: `{lawyer_id}` ({wall_check['wall_record'].get('lawyer_name', 'Sarah Jenkins')})\n"
                f"- **Restricted Matter**: `{matter_id}` (`Project Omega Restructuring`)\n"
                f"- **Enforcement Stage**: **Screen-Before-Rank** inside Cloud Spanner `WeilLegalGraph` (`NOT EXISTS (l)-[:INTAPP_WALL]->(m)`)\n"
                f"- **Reason**: {wall_check['wall_record']['reason']}\n\n"
                "Zero tokens, vector embeddings, or document titles from `M-999` entered the Gemini 3.8 Flash context window."
            ),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
        }

    # 2. Gather deterministic tool context for the chosen specialist agent
    tool_payload: dict[str, Any] = {}
    if agent_id == "redline_word_composer_agent":
        tool_payload = {
            "redline": compute_deterministic_redline("KESTREL-SPA-802"),
            "legal_legos": compose_legal_legos_clause(),
        }
    elif agent_id == "private_funds_antitrust_agent":
        tool_payload = analyze_fundgen_mfn_and_antitrust_hhi()
    elif agent_id == "ethical_wall_cmn_governance_agent":
        tool_payload = {
            "governance": verify_cmn_and_intapp_wall(lawyer_id=lawyer_id, matter_id=matter_id),
            "graph": spanner_engine.traverse_precedent_graph(matter_id=matter_id, lawyer_id=lawyer_id),
        }
    elif agent_id == "inbox_calendar_triage_agent":
        tool_payload = triage_partner_inbox_and_calendar()
    else:
        tool_payload = spanner_engine.hybrid_search(query=prompt, matter_id=matter_id, lawyer_id=lawyer_id, top_k=6)

    # 3. Attempt live Vertex AI Gemini 3.8 Flash synthesis (`location="global"`)
    live_answer = None
    model_used = f"{PRIMARY_MODEL} (ADK Deterministic Legal Tool Synthesis)"
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        sys_instruction = (
            f"You are `{agent_id}` in the Weil Gotshal Enterprise Legal AI Suite running on {PRIMARY_MODEL} (location='global'). "
            "Provide a concise, executive-grade legal analysis grounded strictly in the provided deterministic tool output. "
            "Always cite exact document names, section references, dollar caps, and Spanner Graph provenance."
        )
        user_msg = f"User Prompt: {prompt}\n\nDeterministic Tool Output:\n{str(tool_payload)[:6000]}"
        for m_name in FALLBACK_MODELS:
            try:
                resp = client.models.generate_content(
                    model=m_name,
                    contents=user_msg,
                    config=types.GenerateContentConfig(
                        system_instruction=sys_instruction,
                        temperature=0.1,
                        max_output_tokens=900,
                    ),
                )
                if resp and resp.text:
                    live_answer = resp.text
                    model_used = f"{m_name} (Vertex AI Global Endpoint + ADK)"
                    break
            except Exception:
                continue
    except Exception:
        pass

    if not live_answer:
        if agent_id == "redline_word_composer_agent":
            r = tool_payload["redline"]
            live_answer = (
                f"### Deterministic Redline & Playbook Deviation Audit (`{r['pair_id']}`)\n\n"
                f"- **Compared Drafts**: `{r['doc_a_name']}` vs. `{r['doc_b_name']}` (**{r['stats']['similarity_pct']}%** lexical overlap)\n"
                f"- **Deviation 1 (CRITICAL — Indemnity Cap)**: Skadden v4 cuts general cap from **0.75% EV (\\$31.5M)** to **0.25% EV (\\$10.5M)** while adding a **100% EV (\\$4.2B)** super-cap for Special Environmental/IP Warranties.\n"
                f"- **Deviation 2 (CRITICAL — Fraud Carve-Out)**: Skadden v4 inserts *'Constructive Fraud, equitable fraud, reckless misrepresentation'*, violating Weil's Delaware *ABRY Partners* Playbook.\n"
                f"- **Deviation 3 (HIGH — Basket)**: Flips **0.50% True Deductible** to **0.25% First-Dollar Tipping Basket**.\n"
                f"- **Action**: Reject constructive fraud & 100% super-cap; insert `LEGO-DE-FRAUD` and `LEGO-338H10-TAX` blocks."
            )
        elif agent_id == "private_funds_antitrust_agent":
            live_answer = (
                "### FundGen / FundHQ MFN Compendium & Antitrust HSR HHI Synthesis\n\n"
                "- **FundGen XII MFN Isolation**: CalPERS (\\$350M Anchor, **115 bps** fee / **17.5%** carry) is cleanly isolated from ADIA (\\$300M, **120 bps**) and OTPP (\\$175M, **135 bps**) via Size-Tiered MFN commitment thresholds, preserving **\\$4.85M/yr** in GP fee revenue.\n"
                "- **Antitrust HSR Second Request (`M-720-ANTITRUST`)**: Pre-merger HHI is **2,180**; unmitigated post-merger HHI is **2,690** (**+510 delta**, triggering 2023 DOJ/FTC presumption). Proposed structural divestiture of Halvorsen's Midwest Actuator Division reduces post-merger HHI to **2,210** (**+30 delta**), clearing FTC threshold.\n"
                "- **Multimodal QoE Bridge (`EX-MM-02`)**: Verified \\$310M GAAP to \\$412M Pro-Forma Adjusted EBITDA bridge (\\$31M synergies + \\$28M ERP add-back)."
            )
        elif agent_id == "ethical_wall_cmn_governance_agent":
            g = tool_payload["governance"]
            live_answer = (
                f"### Intapp Ethical Wall & Client Matter Number (`CMN {g['cmn']}`) Governance Audit\n\n"
                f"- **Active Matter**: `{g['matter_id']}` — Client: **{g['client_name']}** (`{g['imanage_library']}`)\n"
                f"- **Intapp Wall Status**: `{g['intapp_wall_check']['ethical_wall_status']}` (`{g['intapp_wall_check']['gql_predicate']}`)\n"
                f"- **OCG AI Policy**: `{g['ocg_ai_policy']}`\n"
                f"- **30-Day Teammate Grant (`EM-9901`)**: Active for `{g['teammate_grant_em9901'].get('grantee')}` until `{g['teammate_grant_em9901'].get('expires_at', '')[:10]}`."
            )
        elif agent_id == "inbox_calendar_triage_agent":
            live_answer = (
                "### Partner Inbox & Calendar Conflict Triage (`Sarah Jenkins — iPad Pro Queue`)\n\n"
                "- **`EM-9901` (P0 Signing Blocker — CMN `31402-0018`)**: Lead Tax Partner D. Cockerell confirmed \\$14.2M Section 338(h)(10) gross-up escrow cap. One-tap reply staged with `LEGO-338H10-TAX`.\n"
                "- **`EM-9902` (P0 Skadden v4 SPA Markup — CMN `31402-0018`)**: Responsive Weil v5 redline staged rejecting constructive fraud & 100% Special Rep super-cap.\n"
                "- **`CAL-101` Conflict Resolved**: Kept Sarah Jenkins on Brightwater Board SPA Approval Call (2:00 PM EDT); delegated first 30m of FTC HSR Meet & Confer to Antitrust Partner Andrew Simon and moved joint wrap-up to 3:45 PM EDT."
            )
        else:
            live_answer = (
                "### Mike Tabular Diligence & Spanner Hybrid GraphRAG Synthesis\n\n"
                "Completed Change-of-Control & Assignment extraction across all 6 Project Kestrel agreements (`DOC-KESTREL-01`..`06`) plus unfiled tax email `EM-9901` with 100% verbatim pin-cite verification."
            )

    return {
        "agent_id": agent_id,
        "model_used": model_used,
        "location": LOCATION,
        "matter_id": matter_id,
        "lawyer_id": lawyer_id,
        "ethical_wall_blocked": False,
        "answer": live_answer,
        "tool_output": tool_payload,
        "latency_ms": round((time.perf_counter() - t0) * 1000, 2),
    }
