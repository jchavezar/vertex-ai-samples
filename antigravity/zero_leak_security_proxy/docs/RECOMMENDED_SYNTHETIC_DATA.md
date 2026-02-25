# Recommended Synthetic Data for Deep Consulting Use Cases

To create a powerful demonstration of the LLM Security Proxy that WOWs PwC clients, we need synthetic documents that trigger complex analytical reasoning, cross-document synthesis, and showcase the proxy's capability to generalize highly sensitive strategic data.

By expanding the repository with the following 5 document types, we can demonstrate "Deep Consulting Use Cases" (like cross-referencing HR data with Financial data to find ROI on talent retention).

---

## 1. Board of Directors Meeting Minutes (Highly Confidential)
**Purpose:** Demonstrates masking of top-level strategic decisions, exact dividend numbers, and named executive actions.
**Content to Gather/Create:**
- **Context:** A Q3 2024 board meeting discussing an upcoming unnamed acquisition target.
- **Sensitive Data to Include:** Specific board member names (e.g., "Chairperson Sarah Jenkins"), exact dividend proposals ("$1.25 per share"), target company names ("Project Phoenix / AlphaCorp"), and specific vote tallies.
- **Strategic Value:** Enables queries like: *"How do boards typically evaluate the strategic rationale for mid-market acquisitions?"* The proxy will extract the evaluation framework but redact AlphaCorp and the exact dividend effects.

## 2. Global Supply Chain Disruption Report
**Purpose:** Demonstrates geopolitical risk masking and vendor-specific issue generalization.
**Content to Gather/Create:**
- **Context:** An internal audit of supply chain failures following a regional crisis or tariff change.
- **Sensitive Data to Include:** Exact manufacturer names (e.g., "Shenzhen TechWorks"), exact lost revenue figures ("$14.2M Q2 loss"), and specific shipping routes or port names used by the company.
- **Strategic Value:** Enables queries like: *"What supply chain diversification strategies are companies using to mitigate single-region manufacturing risks?"* The proxy will abstract the strategies (e.g., dual-sourcing, nearshoring) without leaking the specific vendors or the exact financial impact.

## 3. Employee Engagement & Compensation Analysis (Internal HR)
**Purpose:** To be merged dynamically with Financial documents to show complex synthesis (e.g., the cost of turnover).
**Content to Gather/Create:**
- **Context:** A cross-departmental HR review showing turnover rates tied to specific manager names and compensation bands.
- **Sensitive Data to Include:** Specific manager names ("Sales Dir. Mark Volton - 45% turnover"), exact salary bands ("$140k-$160k for Senior Account Execs"), and internal employee survey quotes complaining about management.
- **Strategic Value:** Enables cross-document queries when paired with financial reports: *"How does high turnover in mid-management affect overall quarterly sales performance, and what retention strategies work?"* Needs to mask salaries and named managers to provide a generalized retention framework.

## 4. Unreleased Internal R&D Strategy (Product Roadmap)
**Purpose:** Demonstrates protection of intellectual property and future product lines while extracting innovation methodologies.
**Content to Gather/Create:**
- **Context:** A highly confidential 3-year roadmap for an AI-powered SaaS product.
- **Sensitive Data to Include:** Codenames ("Project Quantum"), exact release dates ("April 15, 2025"), proprietary algorithm names, and projected R&D budgets ("$4.5M allocated").
- **Strategic Value:** Enables queries like: *"How should SaaS companies structure their R&D investments for long-term AI feature rollouts?"* The proxy extracts the agile framework and investment phasing without leaking the actual product names or exact dates.

## 5. M&A Post-Mortem Integration Report
**Purpose:** Shows learning from failures, which is highly sought-after consulting intelligence, masked safely.
**Content to Gather/Create:**
- **Context:** A brutally honest review of a failed or difficult integration of an acquired company.
- **Sensitive Data to Include:** Real names of systems that failed to integrate ("Oracle ERP to custom legacy AS400"), exact culture clashes involving named executives, and budget overruns ("$2.1M over budget on IT integration").
- **Strategic Value:** Enables queries like: *"What are the most common pitfalls when integrating legacy ERP systems during acquisitions?"* The proxy generalizes the technical debt challenges and executive alignment strategies without shaming the specific client or executives.

---

### How to use this list:
Create these as PDF files and upload them to the SharePoint site. The application's `SAMPLE-QUERIES` list can then be expanded to showcase multi-document insights and advanced "Zero-Leak" capabilities on highly unstructured, risky data.
