# Verity Nexus Engine - Tools & Data Generation

> **Role:** Senior Forensic Data Engineer
> **Purpose:** Generate high-stakes grounding files for AI-powered audit and compliance workflows

---

## Overview

The Verity Nexus platform implements a **Smart Audit Architecture**, mirroring enterprise-grade audit platforms used by global professional services firms. This toolkit generates the **Grounding Data** (knowledge) that ensures AI agents provide accurate, audit-ready evidence rather than hallucinated responses.

### Why Grounding Matters

Without grounding documents, AI agents would just be guessing. Grounding ensures:
- **Accuracy:** Agents cite specific policies and regulations
- **Auditability:** Every finding can be traced to source documentation
- **Compliance:** Decisions align with legal and regulatory frameworks
- **Explainability:** Agents can justify their reasoning to audit partners

---

## Quick Start

```bash
# Navigate to the project root
cd verity-nexus-engine

# Generate all governance files
uv run python scripts/generate_governance.py

# Generate regulatory knowledge base (with Google Search)
uv run python tools/generate_regulatory_kb.py

# Generate synthetic transaction data (with Google Search)
uv run python tools/generate_synthetic_data.py
```

---

## Generated Documents

### The Grounding Data Stack

| Document | Category | Purpose |
|----------|----------|---------|
| `ledger_2026.csv` | **Raw Data** | Complete transaction dataset - the "crime scene" where the Audit Agent searches for anomalies |
| `regulatory_kb_2026.md` | **Knowledge Base** | 2026 tax/audit regulations (OECD Pillar Two, SBIE, QDMTT) ensuring legally valid findings |
| `materiality_policy.yaml` | **Governance** | "Rules of Engagement" defining material vs. de minimis thresholds |
| `smart_audit_workflow.json` | **Logic** | Step-by-step agent workflow following enterprise audit methodology |
| `erp_mapping_schema.json` | **Integration** | Field mappings between Verity Nexus and enterprise ERPs (SAP/Oracle) |
| `approved_vendors.json` | **Master Data** | Authorized vendor list for unapproved vendor detection |

---

## Document Details

### 1. `ledger_2026.csv` - Transaction Ledger

**Purpose:** The primary dataset for anomaly detection and forensic analysis.

**Structure:**
```
Trans_ID | Date | Account_Code | Entity | Vendor_Name | Amount_USD | Approval_Status | Description
```

**Key Features:**
- **500 rows** of realistic financial transactions
- **495 legitimate transactions** across 8 categories (Software, Consulting, Travel, etc.)
- **5 embedded signals** for K-Consulting LLC with high-risk attributes:
  - Amounts exceeding $100,000
  - Timestamps after 11:00 PM
  - "Urgent" in descriptions
  - `AUTO-APPROVE` status (bypassing normal workflow)

**Regenerate:**
```bash
uv run python scripts/generate_governance.py
```

---

### 2. `regulatory_kb_2026.md` - Regulatory Knowledge Base

**Purpose:** The "brain" for the Tax Agent, providing ground truth on international tax regulations.

**Contents:**
- OECD Pillar Two 2026 Side-by-Side Safe Harbour amendments
- Substance-based Income Exclusion (SBIE) calculations
- Qualified Domestic Minimum Top-up Tax (QDMTT) implementation
- **Critical compliance flag:**
  > "Any unverified service fees exceeding $100,000 to non-treaty jurisdictions must be flagged for manual forensic review to prevent Top-up Tax evasion."

**Regenerate:**
```bash
uv run python tools/generate_regulatory_kb.py
```

---

### 3. `materiality_policy.yaml` - Audit Materiality Policy

**Purpose:** Defines thresholds that determine which findings are significant enough to report.

**Key Thresholds:**
```yaml
thresholds:
  overall_materiality: 1,500,000    # Maximum tolerable misstatement
  performance_materiality: 1,125,000 # 75% of overall (working threshold)
  de_minimis: 75,000                # Below this = trivial, no action
  trivial_threshold: 7,500          # Clearly immaterial
```

**Risk Triggers:**
| Trigger | Risk Level | Threshold | Action |
|---------|------------|-----------|--------|
| Unapproved Vendors | HIGH | $50,000 | Flag for immediate review |
| Non-Treaty Jurisdiction Transfers | CRITICAL | $100,000 | Mandatory forensic review |
| Unusual Timing (after 9 PM) | MEDIUM | N/A | Log for pattern analysis |
| Approval Bypass (AUTO-APPROVE) | HIGH | Any | Senior auditor review |

**Regenerate:**
```bash
uv run python scripts/generate_governance.py
```

---

### 4. `smart_audit_workflow.json` - Audit Workflow

**Purpose:** A 4-step sequential workflow that orchestrates agent collaboration.

```
┌─────────────┐    ┌─────────────────────┐    ┌────────────────┐    ┌──────────────┐
│  INGESTION  │───▶│ TRANSACTION_SCORING │───▶│ A2A_VALIDATION │───▶│ FINAL_REVIEW │
│             │    │                     │    │                │    │              │
│ DataAgent   │    │    AuditAgent       │    │   TaxAgent     │    │ ReportAgent  │
└─────────────┘    └─────────────────────┘    └────────────────┘    └──────────────┘
```

| Step | Agent Role | Description |
|------|------------|-------------|
| **Ingestion** | DataIngestionAgent | ERP data acquisition, validation, normalization |
| **Transaction_Scoring** | AuditAgent | AI-powered risk scoring using materiality thresholds |
| **A2A_Validation** | TaxAgent | Cross-agent verification for high-risk transactions |
| **Final_Review** | ReportingAgent | Human oversight and regulatory report generation |

**Regenerate:**
```bash
uv run python scripts/generate_governance.py
```

---

### 5. `erp_mapping_schema.json` - ERP Field Mappings

**Purpose:** Enables integration with enterprise ERP systems (SAP S/4HANA, Oracle Financials).

**Example Mappings:**
| Ledger Field | SAP Field | Oracle Field |
|--------------|-----------|--------------|
| `Trans_ID` | `SAP_BSEG_BELNR` | `ORA_GL_JE_LINE_NUM` |
| `Date` | `SAP_BKPF_BUDAT` | `ORA_GL_EFFECTIVE_DATE` |
| `Vendor_Name` | `SAP_LFA1_NAME1` | `ORA_AP_VENDOR_NAME` |
| `Amount_USD` | `SAP_BSEG_DMBTR` | `ORA_GL_ENTERED_DR` |
| `Approval_Status` | `SAP_BKPF_BSTAT` | `ORA_GL_STATUS` |

**Includes:**
- Full field mapping dictionary
- SAP and Oracle extraction queries
- Data type specifications
- Join key relationships

**Regenerate:**
```bash
uv run python scripts/generate_governance.py
```

---

## Technology Stack

### 1. Google ADK (Agent Development Kit)

**Role:** The "Brain" of individual agents

**What it does:**
- Build specialized AI workers (Audit Agent, Tax Agent)
- Agents have memory and tool-use capabilities
- Structured output via Pydantic schemas
- Built-in Google Search for real-time grounding

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

audit_agent = Agent(
    name="audit_agent",
    model="gemini-2.5-flash",
    tools=[google_search],
    instruction="Analyze transactions for anomalies..."
)
```

### 2. A2A (Agent-to-Agent Protocol)

**Role:** The "Diplomatic Hotline"

**What it does:**
- Standardized protocol for agent communication
- Agents discover each other via Agent Cards (digital resumes)
- Enables Audit Agent ↔ Tax Agent collaboration
- Consensus voting on high-risk findings

### 3. MCP (Model Context Protocol)

**Role:** The "Data Bridge"

**What it does:**
- Connects agents to external systems (databases, cloud storage)
- Secure tool authentication
- Enables ERP data extraction

---

## Why This Creates a "Next-Gen" Demo

By combining these technologies, Verity Nexus demonstrates an **Orchestrated AI Workforce**:

| Traditional Audit | Verity Nexus (Smart Audit) |
|-------------------|----------------------------|
| Sample 5% of transactions | Analyze 100% of transactions |
| Manual anomaly detection | AI-powered pattern recognition |
| Siloed specialists | Collaborative multi-agent system |
| "Trust me" findings | Grounded, explainable evidence |

### Audit-Ready Explainability

Because agents are grounded in policy files, they can explain their reasoning:

> "I flagged transaction TXN-2026-9001 because:
> 1. Amount ($127,000) exceeds the $100,000 threshold in Section 4.2 of your Materiality Policy
> 2. Vendor 'K-Consulting LLC' is not in the approved_vendors.json master list
> 3. Timestamp (23:21:52) violates the unusual_timing_patterns rule
> 4. Per regulatory_kb_2026.md, service fees to non-treaty jurisdictions require forensic review"

---

## Scripts Reference

| Script | Purpose | Output |
|--------|---------|--------|
| `scripts/generate_governance.py` | Generate all governance files | `materiality_policy.yaml`, `smart_audit_workflow.json`, `erp_mapping_schema.json`, `ledger_2026.csv` |
| `tools/generate_regulatory_kb.py` | Generate regulatory knowledge base | `regulatory_kb_2026.md` |
| `tools/generate_synthetic_data.py` | Generate transaction data with Google Search | `ledger_2026.csv`, `approved_vendors.json` |

### Regenerate Everything

```bash
cd verity-nexus-engine

# All governance files
uv run python scripts/generate_governance.py

# Regulatory knowledge base
uv run python tools/generate_regulatory_kb.py
```

---

## Environment Setup

### Prerequisites

- Python 3.10+
- Google Cloud authentication (`gcloud auth application-default login`)
- uv package manager

### Configuration

The `.env` file contains required environment variables:

```env
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=vtxdemos
GOOGLE_CLOUD_LOCATION=global
```

### Dependencies

Managed via `pyproject.toml`:

```toml
dependencies = [
    "google-adk>=1.0.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
]
```

---

## References

- [OECD Pillar Two GloBE Rules](https://www.oecd.org/tax/beps/pillar-two-globe-rules.htm)
- [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- [Agent-to-Agent (A2A) Protocol](https://github.com/google/A2A)

---

*© 2026 Verity Nexus Engine - Forensic Data Engineering Team*
