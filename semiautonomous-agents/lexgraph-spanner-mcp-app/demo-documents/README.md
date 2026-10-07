# 📄 LexGraph Demo Legal Corpus (`demo-documents/`)

This directory contains all synthetic M&A, Private Equity, Credit, NDA, and Tax correspondence documents seeded into **Cloud Spanner Graph (`LexGraphLegalGraph`)** and rendered inside the **MCP App (SEP-1865) Original Document Citation Viewer**.

## Folder Structure

```text
demo-documents/
├── README.md                    # Complete index of documents, chunks, and test prompts
├── generate_demo_pdfs.py        # Script to deterministically compile all PDFs & TXT files
├── pdf/                         # Multi-page print-ready PDF agreements
│   ├── DOC-M331-01_M331_Brightwater_Merger_Agreement_Executed.pdf
│   ├── DOC-M331-02_M331_Opposing_Counsel_Redline_Summary.pdf
│   ├── DOC-M331-03_M331_Indemnity_Escrow_Agreement_Citibank.pdf
│   ├── DOC-M331-04_M331_Tax_Allocation_Rider_Draft.pdf
│   ├── DOC-M215-01_M215_Project_Titan_Merger_Agreement_Executed.pdf
│   ├── DOC-M518-01_M518_Project_Vanguard_SPA_Executed.pdf
│   ├── DOC-M402-01_M402_Apollo_Credit_Agreement_vFinal.pdf
│   └── DOC-M109-01_M109_Mutual_Non_Disclosure_Agreement_FormSpec_v06.pdf
└── text/                        # Plain-text contract corpus with chunk markers
    ├── DOC-M331-01_M331_Brightwater_Merger_Agreement_Executed.txt
    ├── DOC-M331-02_M331_Opposing_Counsel_Redline_Summary.txt
    ├── DOC-M331-03_M331_Indemnity_Escrow_Agreement_Citibank.txt
    ├── DOC-M331-04_M331_Tax_Allocation_Rider_Draft.txt
    ├── DOC-M215-01_M215_Project_Titan_Merger_Agreement_Executed.txt
    ├── DOC-M518-01_M518_Project_Vanguard_SPA_Executed.txt
    ├── DOC-M402-01_M402_Apollo_Credit_Agreement_vFinal.txt
    ├── DOC-M109-01_M109_Mutual_Non_Disclosure_Agreement_FormSpec_v06.txt
    └── EM-9901_Unfiled_Tax_Email_Section_338h10_Election.txt
```

---

## Document & Clause Matrix (Cloud Spanner `Documents` + `Clauses`)

| Document ID | Matter ID | Deal / Matter Name | Practice Area | Primary Chunk ID | Section Ref | Indemnity Cap | Basket Type | Survival | Materiality & Key Qualifiers | Intapp Access (`L-001` Sarah Jenkins) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`DOC-M331-01`** | `M-331` | Project Helios — Brightwater $2.4B Merger | M&A / Private Equity | `CL-M331-INDEM` | `Sec. 8.02(b) & 8.04` (p.2) | **0.75% ($18.0M)** | True Deductible (0.50% / $12M) | 18 Months (72m Fund.) | Full Double Materiality Scrape; Fraud Carve-Out | ✅ Authorized (`CLEARED_INTAPP`) |
| **`DOC-M331-02`** | `M-331` | Project Helios — Skadden Opposing Redline v4 | M&A / Private Equity | `CL-M331-REDLINE` | `Redline Sec. 8.02(b)` (p.1) | **0.25% ($6.0M)** | True Deductible (0.85% / $20.4M) | 12 Months | Single Scrape (Damages Only); $9.5M 338(h)(10) Walk-Right | ✅ Authorized (`CLEARED_INTAPP`) |
| **`DOC-M331-03`** | `M-331` | Project Helios — Citibank Indemnity Escrow | M&A / Private Equity | `CL-M331-ESCROW` | `Sec. 3 & Sec. 4` (p.1) | **7.50% ($3.6M Tranche)** | Escrow Holdback (5.25% Compounded) | 18 Months | Releases $3,894,292.78 at Month 18 | ✅ Authorized (`CLEARED_INTAPP`) |
| **`DOC-M215-01`** | `M-215` | Project Titan — $1.85B Semiconductor Acquisition | M&A / Private Equity | `CL-M215-INDEM` | `Sec. 8.04(a)` (p.1) | **0.50% ($9.25M)** | Tipping Basket (0.35% / $6.47M) | 15 Months | Double Scrape + R&W Policy Retention Split | ✅ Authorized (`CLEARED_INTAPP`) |
| **`DOC-M518-01`** | `M-518` | Project Vanguard — $3.1B Healthcare Buyout | Private Equity | `CL-M518-INDEM` | `Sec. 9.01(c)` (p.1) | **1.00% ($31.0M)** | True Deductible (0.50% / $15.5M) | 24 Months | Double Scrape + IP Special Escrow ($12M) | ✅ Authorized (`CLEARED_INTAPP`) |
| **`DOC-M402-01`** | `M-402` | Apollo $250M Senior Secured Credit Facility | Banking & Finance | `CL-M402-JCREW` | `Sec. 7.08(c)` (p.1) | **0.40% ($10.0M)** | Asset Drop Blocker (0.20%) | 36 Months | Strict J.Crew / Envision IP Transfer Blocker | ✅ Authorized (`CLEARED_INTAPP`) |
| **`DOC-M109-01`** | `M-109` | LexGraph FormSpec v0.0.6 Mutual NDA Baseline | Corporate Governance | `CL-M109-NDA` | `Sec. 4 & Sec. 7` (p.1) | **Uncapped (100%)** | N/A ($0 Deductible) | 36 Months | 24-Month Standstill Fall-Away; Narrow Residuals | ✅ Authorized (`CLEARED_INTAPP`) |
| **`DOC-M999-WALL`** | `M-999` | Restricted Competitor Hostile Bid (Quarantined) | M&A Hostile | `CL-M999-WALL` | `Sec. 8.01` | *Quarantined* | *Quarantined* | *Quarantined* | Automatically pruned at 0ms in Spanner GQL by `ETHICAL_WALL_BLOCK` | 🚫 **Blocked by Intapp Wall** |
| **`EM-9901`** | `M-331` | Unfiled Tax Email — Sec. 338(h)(10) Gross-Up | Tax Practice Group | `EM-9901` | `Sec. 6.09(d) Rider` | **$14.2M Tax Cap** | Section 338(h)(10) Election | 30-Day Grant | Unlocked via ACID `TeammateGrants` Graph Edge commit | 🔓 **Teammate 30-Day Grant** |

---

## Regenerating the PDF & Text Corpus

```bash
python3 demo-documents/generate_demo_pdfs.py
```
