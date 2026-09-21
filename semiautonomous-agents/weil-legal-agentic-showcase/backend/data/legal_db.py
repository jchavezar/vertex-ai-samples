"""Weil Legal Database — Precedents, Modular 'Lego' Clauses, Case Law & Ethical Walls.

Provides authentic corporate, M&A, and regulatory data structures for:
- "Privacy Pro" modular clause assembly
- iManage DMS precedent search simulation
- Case law citation verification (Delaware, SDNY, CJEU)
- Ethical wall conflict boundary enforcement
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional

# ---------------------------------------------------------------------------
# 1. "Privacy Pro" Modular Lego Clauses
# ---------------------------------------------------------------------------
LEGO_CLAUSES: List[Dict[str, Any]] = [
    {
        "id": "CLAUSE-01",
        "title": "Definitions & Scope of Protected Data",
        "category": "Foundations",
        "jurisdiction": "Global / Multi-Jurisdictional",
        "risk_level": "Low",
        "dependencies": [],
        "summary": "Establishes strict definitions of Personal Data, Confidential Materials, and Proprietary Intellectual Property.",
        "text": (
            "1. DEFINITIONS AND INTERPRETATION. For the purposes of this Agreement: "
            "(a) 'Protected Data' means any personal, proprietary, or confidential data provided by or on behalf of "
            "Client to Service Provider in connection with the Services; (b) 'Applicable Privacy Law' includes Regulation "
            "(EU) 2016/679 (GDPR), the California Consumer Privacy Act as amended (CCPA/CPRA), and the EU AI Act (Regulation (EU) 2024/1689)."
        )
    },
    {
        "id": "CLAUSE-02",
        "title": "Schrems II Standard Contractual Clauses (Module 2)",
        "category": "Cross-Border Transfer",
        "jurisdiction": "EU / EEA / United States",
        "risk_level": "High",
        "dependencies": ["CLAUSE-01"],
        "summary": "Mandatory EU-US cross-border transfer mechanism incorporating European Commission Implementing Decision (EU) 2021/914.",
        "text": (
            "2. INTERNATIONAL DATA TRANSFERS. To the extent that the processing of Protected Data involves transfers from the EEA "
            "to countries not deemed to provide an adequate level of data protection, the Parties hereby enter into and incorporate by reference "
            "the Standard Contractual Clauses (Module 2: Controller-to-Processor) pursuant to CJEU Decision Case C-311/18 (Schrems II). "
            "The Parties agree that the technical and organizational measures set forth in Schedule B satisfy supplementary safeguard obligations."
        )
    },
    {
        "id": "CLAUSE-03",
        "title": "Sub-processor Notification & 30-Day Audit Right",
        "category": "Sub-processing & Security",
        "jurisdiction": "EU / Global",
        "risk_level": "Medium",
        "dependencies": ["CLAUSE-01"],
        "summary": "Restricts sub-processor onboarding, requiring 30 days prior written notice and independent SOC 2 / ISO audit rights.",
        "text": (
            "3. SUB-PROCESSORS AND AUDIT RIGHTS. Service Provider shall not engage any third-party sub-processor without providing at least "
            "thirty (30) days prior written notice to Client. Client shall have the right to object to any proposed sub-processor on reasonable data protection grounds. "
            "Client or an accredited independent auditor may, upon thirty (30) days notice, inspect and audit Service Provider's processing facilities, security controls, and adherence to this Addendum."
        )
    },
    {
        "id": "CLAUSE-04",
        "title": "Generative AI Training Prohibition & Zero Data Retention",
        "category": "AI Governance",
        "jurisdiction": "Global / Enterprise Standard",
        "risk_level": "Critical",
        "dependencies": ["CLAUSE-01", "CLAUSE-03"],
        "summary": "Ironclad prohibition on utilizing Client data or work product to train, retrain, fine-tune, or calibrate public or shared AI models.",
        "text": (
            "4. ARTIFICIAL INTELLIGENCE GOVERNANCE & PROHIBITION ON MODEL TRAINING. Service Provider expressly covenants and warrants that "
            "neither Client Protected Data, prompts, embeddings, outputs, nor any derivatives thereof shall be utilized to train, retrain, fine-tune, validate, "
            "or calibrate any machine learning, large language model, foundation model, or algorithmic scoring system. All customer inferences shall execute under "
            "strict Zero-Data-Retention (ZDR) memory controls, with all intermediate vector buffers purged immediately upon token stream completion."
        )
    },
    {
        "id": "CLAUSE-05",
        "title": "Transfer Impact Assessment (TIA) Compliance",
        "category": "Regulatory Compliance",
        "jurisdiction": "EU / EEA",
        "risk_level": "High",
        "dependencies": ["CLAUSE-02"],
        "summary": "Documents government surveillance risk evaluation under FISA Section 702 and Executive Order 14086.",
        "text": (
            "5. TRANSFER IMPACT ASSESSMENT AND GOVERNMENT ACCESS REQUESTS. The Parties acknowledge that a documented Transfer Impact Assessment (TIA) "
            "has evaluated legal remedies under US Executive Order 14086 and the EU-U.S. Data Privacy Framework. Service Provider covenants to notify Client within "
            "forty-eight (48) hours of any compulsory disclosure order or warrant received from state intelligence agencies, unless explicitly prohibited by a court of competent jurisdiction."
        )
    },
    {
        "id": "CLAUSE-06",
        "title": "Mutual Indemnification for Data Breaches & Regulatory Fines",
        "category": "Liability & Indemnity",
        "jurisdiction": "Delaware / New York",
        "risk_level": "Critical",
        "dependencies": ["CLAUSE-01"],
        "summary": "Full defense and indemnification for third-party claims, legal fees, forensic costs, and GDPR administrative penalties.",
        "text": (
            "6. INDEMNIFICATION FOR SECURITY INCIDENTS. Service Provider shall defend, indemnify, and hold harmless Client, its affiliates, and their respective "
            "partners, attorneys, and employees from and against any third-party claims, regulatory enforcement actions, regulatory fines (including GDPR Article 83 penalties), "
            "forensic investigative expenses, and reasonable attorneys' fees arising out of or resulting from a Security Incident or material breach of this Addendum by Service Provider."
        )
    },
    {
        "id": "CLAUSE-07",
        "title": "Ethical Wall & Information Barrier Protocol",
        "category": "Ethics & Conflicts",
        "jurisdiction": "State Bar Association / Global",
        "risk_level": "Critical",
        "dependencies": ["CLAUSE-01"],
        "summary": "Mandatory technical and operational screening to segregate adverse client matters and maintain attorney-client privilege.",
        "text": (
            "7. ETHICAL WALLS AND CONFLICT ISOLATION. In accordance with ABA Model Rule 1.10 and applicable state rules of professional conduct, "
            "Service Provider and Weil shall maintain cryptographically enforced, role-based information barriers ('Ethical Walls') around all matter files. "
            "No personnel or computational agent assigned to Matter Alpha shall access, index, cross-reference, or synthesize data from any designated adverse or conflicting client matter."
        )
    },
    {
        "id": "CLAUSE-08",
        "title": "Governing Law & Delaware Chancery Arbitration",
        "category": "Dispute Resolution",
        "jurisdiction": "Delaware, USA",
        "risk_level": "Low",
        "dependencies": [],
        "summary": "Exclusive Delaware Court of Chancery venue and AAA commercial expedited arbitration.",
        "text": (
            "8. GOVERNING LAW AND JURISDICTION. This Agreement shall be governed by, and construed in accordance with, the internal laws of the State of Delaware, "
            "without regard to conflicts of law principles. Any dispute arising hereunder shall be submitted to the exclusive jurisdiction of the Delaware Court of Chancery, "
            "or if such court lacks subject-matter jurisdiction, the United States District Court for the District of Delaware."
        )
    }
]

# ---------------------------------------------------------------------------
# 2. Case Law & Landmark Precedent Database
# ---------------------------------------------------------------------------
CASE_LAW_DATABASE: List[Dict[str, Any]] = [
    {
        "citation": "698 A.2d 959",
        "case_name": "In re Caremark Int'l Inc. Derivative Litig.",
        "court": "Delaware Court of Chancery",
        "year": 1996,
        "holding": "Directors have an affirmative fiduciary duty to ensure an adequate corporate information and compliance reporting system exists.",
        "key_terms": ["Caremark duty", "fiduciary oversight", "compliance monitoring", "director liability"],
        "verified": True
    },
    {
        "citation": "88 A.3d 635",
        "case_name": "Kahn v. M&F Worldwide Corp. (MFW)",
        "court": "Delaware Supreme Court",
        "year": 2014,
        "holding": "The business judgment standard of review applies to controlling stockholder buyouts conditioned ab initio on special committee approval and majority-of-the-minority vote.",
        "key_terms": ["MFW framework", "controlling stockholder", "special committee", "majority of the minority"],
        "verified": True
    },
    {
        "citation": "Case C-311/18",
        "case_name": "Data Protection Commissioner v. Facebook Ireland & Schrems (Schrems II)",
        "court": "Court of Justice of the European Union (CJEU)",
        "year": 2020,
        "holding": "Invalidated the EU-US Privacy Shield and held that Standard Contractual Clauses require supplementary measures where third-country surveillance laws exceed necessity.",
        "key_terms": ["Schrems II", "FISA 702", "cross-border transfer", "supplementary measures", "SCCs"],
        "verified": True
    },
    {
        "citation": "488 A.2d 858",
        "case_name": "Smith v. Van Gorkom",
        "court": "Delaware Supreme Court",
        "year": 1985,
        "holding": "Directors breached their fiduciary duty of care by approving a cash-out merger upon two hours' consideration without informed valuation analysis.",
        "key_terms": ["duty of care", "gross negligence", "board diligence", "cash-out merger"],
        "verified": True
    },
    {
        "citation": "637 A.2d 34",
        "case_name": "Paramount Communications Inc. v. QVC Network Inc.",
        "court": "Delaware Supreme Court",
        "year": 1994,
        "holding": "Sale of control imposes an enhanced scrutiny duty (Revlon) upon directors to secure the transaction offering the best value reasonably available to stockholders.",
        "key_terms": ["Revlon duties", "change of control", "enhanced scrutiny", "defensive deal protections"],
        "verified": True
    }
]

# ---------------------------------------------------------------------------
# 3. Ethical Wall & Client Conflict Registry
# ---------------------------------------------------------------------------
ETHICAL_WALLS: List[Dict[str, Any]] = [
    {
        "wall_id": "EW-7809-BIO",
        "client_matter_a": "MATTER-9042 (Apex Pharma Inc. — Target Acquisition)",
        "client_matter_b": "MATTER-4103 (BioGen Corp. — Patent Dispute & Licensing)",
        "nature_of_conflict": "Adverse parties in pending Delaware Chancery litigation (Civil Action No. 2024-0412-JTL).",
        "firewalled_attorneys": ["daulton.c@weil.com", "steve.k@weil.com"],
        "sanitization_rule": "BLOCK_AND_SCRUB_PRICING_SCHEDULES",
        "status": "ACTIVE_BARRIER"
    },
    {
        "wall_id": "EW-9214-TECH",
        "client_matter_a": "MATTER-8820 (CloudScale SaaS Buyout)",
        "client_matter_b": "MATTER-7719 (HyperScale Inc. Enterprise Antitrust)",
        "nature_of_conflict": "Direct market competitors; non-disclosure covenants require technical ring-fencing.",
        "firewalled_attorneys": ["ian.m@weil.com"],
        "sanitization_rule": "ANONYMIZE_METADATA_AND_CAPS",
        "status": "ACTIVE_BARRIER"
    }
]

# ---------------------------------------------------------------------------
# 4. iManage Simulated Precedent Documents
# ---------------------------------------------------------------------------
IMANAGE_PRECEDENTS: List[Dict[str, Any]] = [
    {
        "doc_id": "IMANAGE-9042-AGMT",
        "title": "Agreement and Plan of Merger — Apex Acquisition of HelixBio",
        "matter_id": "MATTER-9042",
        "client": "Apex Pharma Inc.",
        "practice_group": "M&A / Corporate",
        "year": 2025,
        "indemnity_cap_percent": 12.5,
        "survival_months": 18,
        "governing_law": "Delaware",
        "confidentiality_tier": "Strict Ethical Wall",
        "content": (
            "AGREEMENT AND PLAN OF MERGER. Article VIII: Indemnification. "
            "Seller aggregate liability for Fundamental Representations shall not exceed 100% of Purchase Price ($320,000,000). "
            "General representations shall survive for eighteen (18) months and be capped at twelve and one-half percent (12.5%) of the Enterprise Value. "
            "Governing Law: Delaware Court of Chancery pursuant to Kahn v. M&F Worldwide Corp."
        )
    },
    {
        "doc_id": "IMANAGE-4103-LIC",
        "title": "BioGen Master Technology Licensing & Cross-Border Transfer Addendum",
        "matter_id": "MATTER-4103",
        "client": "BioGen Corp.",
        "practice_group": "IP Litigation / Antitrust",
        "year": 2024,
        "indemnity_cap_percent": 5.0,
        "survival_months": 6,
        "governing_law": "New York",
        "confidentiality_tier": "CONFIDENTIAL CONFLICT BARRIER",
        "content": (
            "CONFIDENTIAL SETTLEMENT & LICENSE AGREEMENT. BioGen reserves exclusive proprietary patent rights for RNA vectors. "
            "Indemnification is strictly capped at five percent (5.0%) with a six (6) month survival period. "
            "All pricing formulas, royalty tiers, and milestone rebates ($45M) are subject to strict confidential information barriers under EW-7809-BIO."
        )
    },
    {
        "doc_id": "IMANAGE-8820-PRIV",
        "title": "Privacy Pro — Global AI Data Governance Addendum (Gold Standard)",
        "matter_id": "MATTER-8820",
        "client": "CloudScale Enterprises",
        "practice_group": "Tech Transactions & Data Privacy",
        "year": 2026,
        "indemnity_cap_percent": 25.0,
        "survival_months": 36,
        "governing_law": "Delaware",
        "confidentiality_tier": "Weil Firm-Wide Precedent",
        "content": (
            "WEIL GOLD STANDARD AI GOVERNANCE ADDENDUM. "
            "Module 2 Standard Contractual Clauses (Schrems II) incorporated. "
            "Zero Data Retention (ZDR) enforced across all AI inference endpoints. "
            "Sub-processor onboarding requires thirty (30) days prior written notice and client objection rights. "
            "Unlimited mutual indemnification for data breaches and regulatory fines."
        )
    }
]
