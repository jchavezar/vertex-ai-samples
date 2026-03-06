# 🎙️ Verity Nexus: Live Demo Script

This script is designed for a human presenter to follow during a live demonstration of the Verity Nexus Forensic Swarm.

---

## 🏗️ Pre-Flight Check (The "Setup")
Before starting the presentation, ensure both engines are running in separate terminal tabs:

**Tab 1: Backend Engine**
```bash
cd verity-nexus-engine && uv run python server.py
```

**Tab 2: Frontend UI**
```bash
cd verity-nexus-ui && npm run dev -- -p 5174
```
*Open your browser to `http://localhost:5174`*

---

## 🎬 Narrative Act 1: The First Contact
**Presenter Voice:** *"Imagine we are forensic auditors at a Tier-1 firm. We've just been handed the 2026 ledgers for a multi-billion dollar entity. We need to find the 'needle in the haystack' immediately."*

**Action:** Paste the following query into the **"Instruct the Swarm"** box.

> **Query 1:** "Perform a forensic audit on the 2026 ledger. Focus on high-value transactions and materiality concerns based on the corporate policy."

**What to explain while it runs:**
- *"Observe the **Agent Graph** on the left. The Orchestrator (Gemini 3 Pro) is now briefing the specialized **Audit Agent**."*
- *"In the **Reasoning Stream**, you can see the agent actually invoking the `TransactionScorer` tool, which is scanning the raw CSV ledger in real-time."*

**Expected Answer:**
The system should return a list of material transactions (e.g., those over $1.5M) and highlight outliers.

---

## 🕵️ Narrative Act 2: Deep Forensic Patterns
**Presenter Voice:** *"Basic materiality is easy. Let's look for suspicious patterns—specifically 'Auto-Approved' transactions that bypassed human eyes."*

**Action:** Paste the following query.

> **Query 2:** "Search for all transactions marked as 'AUTO-APPROVE'. Filter for those involving unapproved vendors or round-number amounts. Why does the 'TransactionScorer' consider these high-risk?"

**What to explain while it runs:**
- *"The agent isn't just searching; it's **scoring**. It uses fuzzy matching against approved vendor lists and looks for 'Round Number' patterns common in fraudulent entries."*
- *"Look at the **Audit Cards** appearing. Each one has a risk score (0.0 to 1.0) and a set of 'Risk Factors'."*

**Expected Answer:**
A list of transactions with risk scores > 0.7, citing "Round number" or "Unapproved vendor" as factors.

---

## 🤝 Narrative Act 3: The Multi-Agent Swarm (The "Wow" Moment)
**Presenter Voice:** *"Now, forensic auditing is one thing, but international tax compliance is a different beast. Let's see how the swarm handles a cross-domain escalation."*

**Action:** Paste the following query.

> **Query 3:** "Run a comprehensive audit for high-risk payments. If you encounter transactions involving non-treaty jurisdictions or known tax havens, escalate to the Tax Agent for a regulatory impact study."

**What to watch for (The Handoff):**
- **VISUAL:** The Agent Graph should suddenly sprout a new node: **tax_agent**.
- **LOGIC:** The Orchestrator realizes its Audit sub-agent found an international payment and automatically "transfers" to the Tax expert.

**Expected Answer:**
A dual-section report.
1. **Audit Agent**: Scored transactions and materiality.
2. **Tax Agent**: Citations from the regulatory markdown files (e.g., Pillar Two compliance) and a "Total Tax Exposure" calculation.

---

## 📊 Narrative Act 4: The Executive Briefing
**Presenter Voice:** *"Finally, we need something for the CFO. We don't want spreadsheets; we want a synthesis of risk."*

**Action:** Paste the following query.

> **Query 4:** "Synthesize all findings from the Audit and Tax sessions. What is our total financial exposure, and what's your recommendation for the Q4 closing?"

**What to explain while it runs:**
- *"The Orchestrator is now acting as a Senior Partner, summarizing the work of its expert associates into a final recommendation."*

**Expected Answer:**
A professional executive summary covering total material risk (e.g., $2.8M) and an actionable closing recommendation.

---

## 🔬 Narrative Act 5: The Multi-Modal Investigation (SQL & MCP)
**Presenter Voice:** *"Our natural language Orchestrator found anomalies. But in forensics, trust requires verification. Let's prove where this data comes from."*

**Action 1:** Open the **SQL Terminal** from the top right button. 
Execute the following exact query:
```sql
SELECT * FROM `vtxdemos.verity_nexus_ledger.ledger_transactions` WHERE jurisdiction = 'Cayman Islands' LIMIT 5;
```

**What to explain while it runs:**
- *"We are switching to a deterministic approach by executing raw SQL against the BigQuery ledger."*
- *"Notice that the results—like the $1.55M transaction—match the AI's findings exactly. This proves our agent is structurally grounded in the actual enterprise data warehouse, not just generating plausible text."*

**Action 2:** Open the **MCP Toolbox** (wrench icon on the far left or top menu).
1. Expand the `query_transactions_by_jurisdiction` tool.
2. Click the Send to Chat icon to load this JSON payload, or type it manually into the Toolbox Chat:
```json
{ "jurisdiction_name": "Cayman Islands" }
```
3. Click Send.

**What to explain while it runs:**
- *"Here we peel back the curtain. This is the Model Context Protocol (MCP) Server, deployed statelessly on Cloud Run."*
- *"By sending the exact JSON payload the agent used, we can see the raw tool output. This is the structured data feed the LLM receives *before* it synthesizes its human-readable answer."*
- *"The results match perfectly across all three domains: AI natural language, raw SQL, and direct tool protocol."*

---

## 🛑 Clean Up
To end the demo, just `Ctrl+C` both terminal tabs.
