# Weil Legal-Tech Innovation: Demo Runbook & Teaching Guide
## Complete Script, Step-by-Step Instructions & Executive Talking Points

> **Session**: Weil, Gotshal & Manges LLP Workshop & Executive Briefing  
> **Speaker / Presenter**: Jesus Chavez (Google Cloud AI Customer Engineer)  
> **Application URL**: `http://localhost:5173` (Frontend) | `http://localhost:8000` (Backend API)  
> **Target Audience**: Andrew Simon (Chief Innovation Officer), Ian Miller (Architecture Lead), Practice Partners

---

## 🎯 Executive Setup & Presentation Flow

This runbook gives you a turn-by-turn script so you can effortlessly present the slides, transition directly into the live demos, teach each architectural component, and handle any tough question from Weil leadership.

### Recommended Timing Breakdown (45 Minutes Total):
1. **Introduction & Slide Walkthrough (8 Mins)**: Present the 3 topics (ADK Orchestration, Antigravity Sandbox, Single-Pane Cockpit).
2. **Demo A: Google ADK Multi-Agent Team (12 Mins)**: Run Scenario 1 (Privacy Pro) & Scenario 2 (Ethical Wall Breach).
3. **Demo B: Antigravity Managed Agent Sandbox (12 Mins)**: Run Scenario 4 (Python Monte Carlo Damage Settlement & File Disk).
4. **Demo C: Privacy Pro Lego Studio & MCP Vault (8 Mins)**: Drag-and-drop clause assembly and iManage live search.
5. **Q&A & Transition to Executive Session with Ravi (5 Mins)**.

---

## 🎬 Act 1: The Slide Intro & Transition to Demo

### Script:
> *"Good morning Andrew, Ian, and the Weil team. In our previous session with Roberto, we explored how Vertex AI Vector Search and BM25 hybrid retrieval form the data foundation for high-precision legal discovery.*
>
> *Now, we address the critical question Andrew posed in our planning session: **how do we take those legal building blocks and orchestrate them safely, autonomously, and deterministically without human error?***
>
> *Today, we are going to explore two cutting-edge architectural choices available to you on Google Cloud:*
> 1. *First: **Google Agent Development Kit (ADK)** for deterministic multi-agent teams with strict ethical wall guardrails.*
> 2. *Second: **Antigravity Managed Agents**, where frontier Gemini models run inside an isolated Linux microVM to perform quantitative computations, air-gapped code execution, and contract file generation.*
>
> *Let's step directly inside the live Weil Legal-Tech Cockpit."*

---

## 🚀 Act 2: Demo A — Google ADK Multi-Agent Team

### Step 1: Navigate to the `🤖 Google ADK Team` Tab
1. In the top navigation bar, ensure **"🤖 Google ADK Team"** is selected.
2. Point out the **4 parallel deliberation lanes** on the screen:
   - 📄 **Assembly Agent ("Privacy Pro")**: Focuses strictly on contract clause composition.
   - 🔍 **Citation Agent**: Focuses strictly on legal authority verification (*Delaware Court of Chancery*, *SDNY*).
   - 🛡️ **Ethical Wall Agent**: Enforces General Counsel Chinese-wall boundaries between adverse clients.
   - ✍️ **Redline Agent**: Analyzes deviation risks against standard Weil market terms.

### Step 2: Click Preset 1 — `🇪🇺 Assemble EU-US AI Data Transfer (Privacy Pro)`
1. Click the button: **"🇪🇺 Assemble EU-US AI Data Transfer"**.
2. **What happens live**:
   - The query *"Assemble GDPR + Schrems II compliant AI governance addendum with zero data retention and 30-day audit rights"* is submitted.
   - Watch the **Coordinator Agent** decompose the request and dispatch tasks concurrently.
   - Watch the **Assembly Agent** snap together Clauses 1, 2, 4 (Zero-Retention AI Training Prohibition), and Clause 3 (Sub-processor Audit Right).
   - Watch the **Citation Agent** run an MCP call to `verify_case_citation("Case C-311/18", "CJEU")` and confirm the *Schrems II* standard is grounded.
   - Watch the **Ethical Wall Agent** clear the matter (no client conflicts on TechCorp matter).
   - The completed, verified agreement appears in the unified right-hand work product drawer with 100% compliance pass!

### Teaching Point to Explain to Andrew:
> *"Andrew, notice what just happened in under 3 seconds. The Assembly Agent didn't guess the legal standard—it pulled the approved 'Lego' clause from the repository. Meanwhile, the Citation Agent independently verified that the Schrems II cross-border transfer citation was authentic. If an associate made a typo in the citation or cited a non-existent authority, the Citation Agent would have flagged an ungrounded assertion before any partner saw the draft."*

---

### Step 3: Click Preset 2 — `🛡️ Ethical Wall Breach Challenge (Adverse Client Test)`
1. Click the button: **"🛡️ Ethical Wall Breach Challenge"**.
2. **What happens live**:
   - Query: *"Retrieve merger indemnification precedent from the BioGen acquisition to use in drafting for Apex Pharma."*
   - Watch the **Ethical Wall Agent** lane immediately flash **AMBER / RED**:
     - `CONFLICT DETECTED: EW-7809-BIO`
     - `Adverse Party: BioGen Corp is in active litigation against Apex Pharma.`
   - Watch the agent sanitize the retrieval: it intercepts the confidential pricing schedule, blocks cross-client contamination, and injects the standardized anonymized Weil benchmark clause instead.
   - An immutable audit log entry is written to the deterministic harness.

### Teaching Point to Explain to Ian:
> *"Ian, remember in our prep call when we debated where ethical wall filtering should occur? You mentioned that client B data must be scrubbed before it ever finds its way into client A's work product. Here you see it happening deterministically at the agent harness boundary. The LLM is never allowed to leak the adverse party's confidential pricing because the Ethical Wall Agent intercepts the tool call at the MCP layer."*

---

## ⚡ Act 3: Demo B — Antigravity Managed Agent Sandbox

### Step 1: Navigate to the `⚡ Antigravity Sandbox` Tab
1. In the top navigation bar, click **"⚡ Antigravity Sandbox"**.
2. Point out the interface elements:
   - Left side: **Dedicated Linux MicroVM Terminal (`/workspace`) & Forensic Wire-Tap**.
   - Top right: **Virtual Disk Drawer** showing files persisted on the MicroVM disk (`/workspace/settlement_model.py`, `/workspace/contract_v2.docx`, `/workspace/risk_matrix.csv`).
   - Bottom right: **Dynamic Artifact Viewer** for rendered charts and formatted documents.

### Step 2: Click Preset 4 — `💻 Run Python Damage & Settlement Simulation`
1. Click the button: **"💻 Run Python Damage & Settlement Simulation"**.
2. **What happens live**:
   - The prompt asks: *"Calculate a 10,000-iteration Monte Carlo settlement risk distribution for the pending Delaware patent infringement dispute."*
   - Watch the Antigravity Agent write a complete Python script (`/workspace/dispute_sim.py`) using `numpy` and `scipy`.
   - Watch the agent execute the command inside the Linux microVM:
     ```bash
     python3 /workspace/dispute_sim.py
     ```
   - Watch stdout stream the percentile outcomes:
     - `P10 (Best Case): $14.2M`
     - `P50 (Expected Median): $28.5M`
     - `P90 (Worst Case Exposure): $44.1M`
     - `Recommended Settlement Range: $25.0M – $29.5M`
   - An interactive SVG probability distribution chart renders directly in the artifact panel!
   - A newly generated file `settlement_summary.csv` appears in the Virtual Disk Drawer.

### Teaching Point to Explain to Weil Leadership:
> *"Why does an elite corporate law firm need Antigravity Managed Agents with a sandboxed Linux VM? Because legal practice is increasingly computational. When negotiating a $500M buyout or settling complex multi-district litigation, you cannot rely on an LLM's natural language estimation for financial damages or liquidation waterfalls. You want the agent to write a deterministic mathematical model, run it inside a secure air-gapped Google Cloud sandbox, and produce defensible, auditable figures."*

---

## 🧩 Act 4: Demo C — Privacy Pro Lego Studio & Legal MCP Vault

### Step 1: Navigate to `🧩 Privacy Pro Lego Studio` Tab
1. In the navigation bar, click **"🧩 Privacy Pro Studio"**.
2. Show the modular clause repository:
   - Clause cards for *Definitions*, *Schrems II SCCs*, *Sub-processor Audit Right*, *AI Training Prohibition*, *Indemnification Cap*, and *Governing Law*.
3. Click on individual clauses to toggle them into the active contract draft.
4. Demonstrate the **Automated Dependency Engine**:
   - Turn on *AI Training Prohibition (Clause 4)* without *Audit Right (Clause 3)*.
   - The system immediately displays a warning banner:
     `⚠️ Dependency Warning: Clause 4 requires Clause 3 (Sub-processor Audit Rights) to be legally enforceable under EU AI Act Article 28.`
   - Click **"Auto-Resolve Dependencies"** and watch the system automatically snap the required companion clause into place!

### Step 2: Navigate to `🛡️ Legal Knowledge & MCP Vault` Tab
1. In the navigation bar, click **"🛡️ Legal Vault & MCP"**.
2. Demonstrate how open **Model Context Protocol (MCP)** connects to Weil's data:
   - Type a query into the iManage Search box: `"Software license indemnification cap"`
   - Watch it return exact matter documents from iManage with matter IDs, practice groups, and ethical wall clearance tags.
   - Click on the **Citation Grounding Tester**: Enter `698 A.2d 959` and watch it instantly verify the citation against the *Caremark* landmark decision.

---

## 🧠 Handling Likely Questions from Weil Leadership

### Q1 (From Andrew Simon): *"Can we use open-weight models like Gemma for routine tasks and reserve Gemini for high-level reasoning?"*
**Answer**:
> *"Yes, absolutely! The Google ADK architecture is model-agnostic. In fact, you can configure routine subagents—like the initial intake form parser or German power of attorney generator—to run on Gemma 2 / 4 hosted on Vertex AI to guarantee 100% frozen parameter stability (your 'tissue paper' applications). Meanwhile, you direct the Coordinator and Redline agents to Gemini 3.8 Flash for deep multi-clause legal synthesis."*

### Q2 (From Ian Miller): *"How does this integrate with our existing iManage document management system and Relativity without creating a new silo?"*
**Answer**:
> *"Through the open Model Context Protocol (MCP). Rather than rebuilding your repositories on Google Cloud, we deploy lightweight, secure MCP gateways that sit alongside your iManage or Azure repositories. The agents invoke standard MCP tool schemas (`search_precedents`, `get_clause_text`) over secure RPC. You retain your authoritative document source of truth while Google Cloud provides the cognitive orchestration fabric."*

### Q3 (From General Counsel / Risk): *"How can we be sure client confidential data won't be used to train Google's models or leak to another client?"*
**Answer**:
> *"Google Cloud operates under an enterprise Zero-Data-Retention and Zero-Model-Training guarantee. Your prompts, inputs, and retrieved data are NEVER used to train Google foundation models. Furthermore, with VPC Service Controls, all agent compute and sandbox execution occur strictly within your firm's isolated tenant perimeter."*
