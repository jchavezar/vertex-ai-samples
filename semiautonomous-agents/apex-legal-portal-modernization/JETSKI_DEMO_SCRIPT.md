# Antigravity Demonstration Runbook: Modernizing Apex Global Law LLP

> **Target Audience**: Marcus Vance (Chief Innovation Officer), Elena Rostova (Tech Architecture Lead), and Practice Partners  
> **Presenter / Lead Engineer**: Jesus Chavez (Google Cloud AI Customer Engineer)  
> **Environment**: Antigravity Linux Sandbox / Local Terminal & Port `8089`  
> **Repository Root**: `semiautonomous-agents/apex-legal-portal-modernization`

---

## 1. Executive Modernization Analysis

### 1.1 Legacy Architecture Diagnostics (Monolithic Corporate Portal)
* **Current State Challenges on `apexgloballaw.example.com`**:
  - Rigid monolithic CMS layout paired with legacy static stylesheets and compartmentalized practice silos.
  - Traditional search interface relying on a basic input field (`#txtGlobalSearch`) requiring full-page reloads, with zero direct access to precedent transactions, covenants, or deal structures.
  - Disjointed navigation disconnected from high-stakes workflows across Private Equity, Banking & Debt Finance, and Restructuring.
* **Modernization Strategy via Antigravity**:
  - **Single-Pane-of-Glass Deal Cockpit**: Unifying fragmented research and precedent discovery into an ultra-responsive, context-aware interface.
  - **High-End Corporate Branding**: Preserving Apex Global Law's institutional aesthetic (Navy `#0a192f`, Gold `#d4af37`, Slate `#8892b0`) with modern glassmorphism (`backdrop-filter: blur(16px)`), smooth micro-interactions, and crisp typography.

---

### 1.2 Enterprise AI Capabilities for Apex Global Law's Core Practices
Transforming the portal from a static brochure into an autonomous engine for transactional intelligence:

1. **Intelligent Precedent Navigator (Vertex AI & Gemini 3.8 Flash)**:
   - Dynamic self-expanding dock (480px &rarr; 760px) delivering parallel *Search-As-You-Type*:
     - **Track A (<10ms)**: Instant sub-10ms autocomplete over Apex Global Law's core practice groups and representative transactions.
     - **Track B (<1.5s)**: Grounded executive synthesis generated in real time by **Gemini 3.8 Flash** (`gemini-3.8-flash`), referencing synthetic mandates and regulatory clearances with self-contained local authority pages (zero 404s).
2. **24/7 Apex Deal & Regulatory AI Advisor**:
   - Floating, conversational drawer docked in the bottom-right corner.
   - Grounded in corporate transactional jurisprudence: Delaware Court of Chancery Material Adverse Effect (MAE) benchmarks, cross-border data transfer addenda (*Schrems II*), and cov-lite debt protections.
3. **Multimodal Term Sheet Pre-Clearance (Vision AI)**:
   - Visual parsing of complex legal-financial instruments via **Gemini 3.8 Flash Vision**.
   - Automated extraction of critical covenants: *Total Net Leverage Ratio*, interest coverage benchmarks, and *Negative Pledge* debt baskets.
   - Deterministic *Ethical Wall* conflict verification checking adverse party registries and issuing an immutable clearance token (`APEX-NY-2026-CLEARANCE-PASS`) before partner redlining.

---

## 2. 5-Act Demonstration Architecture

```text
┌──────────────────────────────────────────────────────────────────────────┐
│            APEX GLOBAL LAW PORTAL: 5-ACT MODERNIZATION FLOW              │
├─────────┬──────────────────────────────────┬─────────────────────────────┤
│ ACT 1   │ Baseline Corporate Portal        │ http://localhost:8089       │
├─────────┼──────────────────────────────────┼─────────────────────────────┤
│ ACT 2   │ UX/UI Modernization (Cockpit)    │ Glassmorphic Mega-Menu      │
├─────────┼──────────────────────────────────┼─────────────────────────────┤
│ ACT 3   │ AI Feature 1: Precedent Search   │ <10ms Suggest + Gemini 3.8  │
├─────────┼──────────────────────────────────┼─────────────────────────────┤
│ ACT 4   │ AI Feature 2: 24/7 Deal Advisor  │ Floating Transactional AI   │
├─────────┼──────────────────────────────────┼─────────────────────────────┤
│ ACT 5   │ AI Feature 3: Term Sheet Vision  │ Covenant Scan & Ethical Wall│
└─────────┴──────────────────────────────────┴─────────────────────────────┘
```

---

## 3. Step-by-Step Script & Executive Talking Points

### 🎬 ACT 1: Baseline Corporate Portal (Legacy Monolith)

> **Presenter Talking Points (to Marcus Vance & Elena Rostova)**:
> *"Good morning Marcus and Elena. To start, let's launch the baseline corporate portal of Apex Global Law LLP (`apexgloballaw.example.com`) inside our isolated local sandbox on port 8089, completely self-contained with zero external network dependencies."*

#### 💬 Command Prompt for Antigravity:
```text
Antigravity, execute step 1 of the Apex Legal demo: deploy the baseline portal on the local server.
```
*(Or execute directly: `python3 agy-recipes/apex-legal-modernization/scripts/demo_step1_clone.py`)*

#### ⚙️ Live System Behavior:
1. Antigravity detects the current workspace directory, scaffolds files if running in a clean folder (`scaffold_workspace.py`), resets `site/index.html` to `site/index.pristine.html`, launches `serve_portal.py` on port **8089**, and opens the browser.
2. **Key Teaching Takeaways**:
   - Highlight 100% standalone offline operation for `apexgloballaw.example.com`.
   - Point out Antigravity's non-destructive local workspace management.
   - Demonstrate built-in local authority pages on secondary links to guarantee zero 404 broken pages.

---

### 🎨 ACT 2: UX/UI Modernization (Deal Cockpit & Glassmorphic Mega-Menu)

> **Presenter Talking Points**:
> *"Now let's watch Antigravity restructure the traditional navigation into a sleek Glassmorphic Mega-Menu tailored specifically to Apex Global Law's premier transactional practices: Banking & Finance, M&A / Private Equity, and Restructuring."*

#### 💬 Command Prompt for Antigravity:
```text
Antigravity, execute step 2: modernize the portal's UI/UX by injecting the executive Mega-Menu and live deal ticker.
```
*(Or execute: `python3 agy-recipes/apex-legal-modernization/scripts/demo_step2_ux.py`)*

#### ⚙️ Live System Behavior:
1. The sticky glassmorphic navigation bar (`backdrop-filter: blur(16px)`) is injected, alongside structured practice dropdowns and the live transaction ticker ($12.4B Carve-Out, $8.5B Syndicated Facility, Schrems II AI Standard).
2. **Key Teaching Takeaways**:
   - Surgical modularity: Code injections are clean and 100% reversible (`inject_feature.py reset`).
   - User experience reoriented around transactional partners and institutional clients.

---

### ⚡ ACT 3: AI Feature 1 — Intelligent Precedent Navigator

> **Presenter Talking Points**:
> *"Marcus, in our architecture review we discussed consolidating fragmented discovery across internal knowledge surfaces. Here Antigravity introduces an Intelligent Precedent Navigator running directly inside the header."*

#### 💬 Command Prompt for Antigravity:
```text
Antigravity, execute step 3: activate the Intelligent Precedent Navigator with Search-As-You-Type and Gemini 3.8 Flash synthesis.
```
*(Or execute: `python3 agy-recipes/apex-legal-modernization/scripts/demo_step3_ai.py`)*

#### ⚙️ Live System Behavior:
1. A floating search dock appears at the top center (480px).
2. The presenter types *"carve-out"* or *"Schrems II"*:
   - In **<10ms**, instant autocomplete surfaces matching Apex practice groups and representative precedents.
   - The dock smoothly expands to **760px** while **Gemini 3.8 Flash** produces a grounded executive brief detailing structuring options.
3. Precedent cards open verified local authority briefs without 404 errors.

---

### 🤖 ACT 4: AI Feature 2 — 24/7 Apex Deal AI Advisor

> **Presenter Talking Points**:
> *"For institutional sponsors and general counsels requiring instantaneous strategic clarity, Antigravity deploys a floating 24/7 conversational deal advisor."*

#### 💬 Command Prompt for Antigravity:
```text
Antigravity, execute step 4: inject the 24/7 Apex Deal AI Advisor in the bottom-right corner.
```
*(Or execute: `python3 agy-recipes/apex-legal-modernization/scripts/demo_step4_advisor.py`)*

#### ⚙️ Live System Behavior:
1. A gold and navy floating badge with a live green status dot appears in the bottom right.
2. Clicking the advisor opens the conversational drawer equipped with rapid query chips:
   - *"Analyze Delaware MAE standards for pending buyout"*
   - *"Check Schrems II cross-border data transfer clause"*
   - *"Summarize cov-lite syndicated debt protections"*
3. **Gemini 3.8 Flash** responds with partner-level reasoning, rigorous legal citations, and zero hallucinations.

---

### 📑 ACT 5: AI Feature 3 — Multimodal Term Sheet Pre-Clearance

> **Presenter Talking Points**:
> *"Finally, let's explore how Antigravity connects Vision AI to parse complex financing term sheets and verify deterministic Ethical Wall boundaries before partner redlining."*

#### 💬 Command Prompt for Antigravity:
```text
Antigravity, execute step 5: deploy the multimodal credit agreement analyzer and ethical wall pre-clearance modal.
```
*(Or execute: `python3 agy-recipes/apex-legal-modernization/scripts/demo_step5_multimodal.py`)*

#### ⚙️ Live System Behavior:
1. Click the top-right button **"Pre-Clear Term Sheet"**.
2. An interactive modal opens featuring an animated laser-scan analysis across 14 pages of an $850M Senior Secured Facility term sheet.
3. Key financial covenants are extracted (leverage caps, interest coverage, negative pledge baskets) and checked against adverse-party registries, issuing the clearance token: `APEX-NY-2026-CLEARANCE-PASS`.

---

## 4. Rapid Teardown & Workspace Reset

To cleanly conclude the demonstration or restore the workspace for a fresh run:

```bash
python3 agy-recipes/apex-legal-modernization/scripts/teardown.py
```
Or instruct Antigravity directly:
```text
Antigravity, clean up and restore this workspace to start over from scratch.
```
