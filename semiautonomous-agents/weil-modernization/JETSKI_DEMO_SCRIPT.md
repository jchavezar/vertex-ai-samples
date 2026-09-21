# Antigravity Demonstration Runbook: Modernizing Weil, Gotshal & Manges LLP

> **Target Audience**: Andrew Simon (Chief Innovation Officer), Ian Miller (Tech Architecture Lead), and Practice Partners  
> **Presenter / Lead Engineer**: Jesus Chavez (Google Cloud AI Customer Engineer)  
> **Target Date**: September 9, 2026 (GCP Legal-Tech & AI Innovation Workshop)  
> **Environment**: Antigravity Linux Sandbox / Local Terminal & Port `8089`  
> **Repository Root**: `~/IdeaProjects/vertex-ai-samples/semiautonomous-agents/weil-modernization`

---

## 1. Executive Modernization Analysis

### 1.1 Legacy Architecture Diagnostics (Sitecore & jQuery)
* **Current State Challenges on `weil.com`**:
  - Heavy Sitecore monolithic infrastructure paired with legacy jQuery 3.6 and oversized stylesheets exceeding 300,000 characters (`redesign.v-*.css`).
  - Traditional search interface relying on a basic input field (`#txtGlobalSearch`) requiring full-page reloads, with zero direct access to precedent transactions, covenants, or deal structures.
  - Rigid, siloed navigation disconnected from high-stakes workflows across Private Equity, Banking & Debt Finance, and Restructuring.
* **Modernization Strategy via Antigravity**:
  - **Single-Pane-of-Glass Deal Cockpit**: Unifying fragmented research and precedent discovery into an ultra-responsive, context-aware interface.
  - **High-End Corporate Branding**: Preserving Weil's corporate elegance (Navy `#0a192f`, Gold `#d4af37`, Slate `#8892b0`) with modern glassmorphism (`backdrop-filter: blur(16px)`), smooth micro-interactions, and crisp typography.

---

### 1.2 Enterprise AI Capabilities for Weil's Core Practices
Transforming the portal from a static catalog into an autonomous engine for transactional intelligence:

1. **Intelligent Precedent Navigator (Vertex AI & Gemini 3.7 Flash)**:
   - Dynamic self-expanding dock (480px &rarr; 760px) delivering parallel *Search-As-You-Type*:
     - **Track A (<10ms)**: Instant sub-10ms autocomplete over Weil's core practice groups and representative transactions.
     - **Track B (<1.5s)**: Grounded executive synthesis generated in real time by **Gemini 3.7 Flash**, referencing landmark deals and regulatory clearances with zero broken links (Smart 302 Redirection).
2. **24/7 Weil Deal & Regulatory AI Advisor**:
   - Floating, conversational drawer docked in the bottom-right corner.
   - Grounded in high-level corporate transactional knowledge: Delaware Court of Chancery Material Adverse Effect (MAE) benchmarks, cross-border data transfer addenda (*Schrems II*), and cov-lite debt protections.
3. **Multimodal Term Sheet Pre-Clearance (Vision AI)**:
   - Visual parsing of complex legal-financial instruments via **Gemini 3.7 Flash Vision**.
   - Automated extraction of critical covenants: *Total Net Leverage Ratio*, interest coverage benchmarks, and *Negative Pledge* debt baskets.
   - Deterministic *Ethical Wall* conflict verification checking adverse client databases and issuing an immutable clearance token before partner redlining.

---

## 2. 5-Act Demonstration Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      WEIL MODERNIZATION: 5-ACT DEMONSTRATION                           │
├─────────┬───────────────────────────────────────┬──────────────────────────────────────┤
│ ACT 1   │ Faithful Baseline Clone               │ Sitecore/jQuery at http://localhost:8089 │
├─────────┼───────────────────────────────────────┼──────────────────────────────────────┤
│ ACT 2   │ UX/UI Modernization (Deal Cockpit)    │ Glassmorphic Mega-Menu & Live Ticker │
├─────────┼───────────────────────────────────────┼──────────────────────────────────────┤
│ ACT 3   │ AI Feature 1: Precedent Navigator     │ Autocomplete <10ms + Gemini 3.7      │
├─────────┼───────────────────────────────────────┼──────────────────────────────────────┤
│ ACT 4   │ AI Feature 2: 24/7 Deal AI Advisor    │ Floating Transactional Intelligence  │
├─────────┼───────────────────────────────────────┼──────────────────────────────────────┤
│ ACT 5   │ AI Feature 3: Multimodal Term Sheet   │ Laser Covenant Extraction & Ethical Wall │
└─────────┴───────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 3. Step-by-Step Script & Executive Talking Points

### 🎬 ACT 1: Faithful Baseline Clone (Legacy Monolith)

> **Presenter Talking Points (to Andrew Simon & Ian Miller)**:
> *"Good morning Andrew and Ian. To start, let's have Antigravity autonomously inspect and reverse-engineer the official production website of Weil (weil.com), replicating 100% of its visual structure, typography, and assets in our local sandbox without touching external servers."*

#### 💬 Command Prompt for Antigravity:
```text
Antigravity, execute step 1 of the Weil demo: deploy the baseline clone on the local server.
```
*(Or execute directly: `python3 agy-recipes/weil-modernization/scripts/demo_step1_clone.py`)*

#### ⚙️ Live System Behavior:
1. Antigravity detects the current workspace directory, scaffolds files if running in a clean folder (`scaffold_workspace.py`), resets `site/index.html` to its baseline, launches `serve_weil.py` on port **8089**, and opens the browser.
2. **Key Teaching Takeaways**:
   - Highlight 100% fidelity to `weil.com`.
   - Point out Antigravity's non-destructive local workspace management.
   - Demonstrate Smart 302 Redirection on secondary links to guarantee zero 404 broken pages.

---

### 🎨 ACT 2: UX/UI Modernization (Deal Cockpit & Glassmorphic Mega-Menu)

> **Presenter Talking Points**:
> *"Now let's watch Antigravity restructure the traditional navigation into a sleek Glassmorphic Mega-Menu tailored specifically to Weil's premier transactional practices: Banking & Finance, M&A / Private Equity, and Restructuring."*

#### 💬 Command Prompt for Antigravity:
```text
Antigravity, execute step 2: modernize the portal's UI/UX by injecting the executive Mega-Menu and live deal ticker.
```
*(Or execute: `python3 agy-recipes/weil-modernization/scripts/demo_step2_ux.py`)*

#### ⚙️ Live System Behavior:
1. The sticky glassmorphic navigation bar (`backdrop-filter: blur(16px)`) is injected, alongside structured practice dropdowns and the live transaction ticker ($12.4B Carve-Out, $8.5B Syndicated Facility, Schrems II AI Standard).
2. **Key Teaching Takeaways**:
   - Surgical modularity: Code injections are clean and 100% reversible.
   - User experience reoriented around transactional partners and institutional clients.

---

### ⚡ ACT 3: AI Feature 1 — Intelligent Precedent Navigator

> **Presenter Talking Points**:
> *"Andrew, in our preparatory session you emphasized consolidating fragmented discovery across 45,000 internal surfaces. Here Antigravity introduces an Intelligent Precedent Navigator running directly inside the header."*

#### 💬 Command Prompt for Antigravity:
```text
Antigravity, execute step 3: activate the Intelligent Precedent Navigator with Search-As-You-Type and Gemini 3.5 Flash Lite synthesis.
```
*(Or execute: `python3 agy-recipes/weil-modernization/scripts/demo_step3_ai.py`)*

#### ⚙️ Live System Behavior:
1. A floating search dock appears at the top center (480px).
2. The presenter types *"carve-out"* or *"Schrems II"*:
   - In **<10ms**, instant autocomplete surfaces matching Weil practice groups and landmark precedents.
   - The dock smoothly expands to **760px** while **Gemini 3.5 Flash Lite** produces a grounded two-paragraph executive brief detailing structuring options.
3. Precedent cards open verified destination pages without 404 errors.

---

### 🤖 ACT 4: AI Feature 2 — 24/7 Weil Deal AI Advisor

> **Presenter Talking Points**:
> *"For institutional sponsors and general counsels requiring instantaneous strategic clarity, Antigravity deploys a floating 24/7 conversational deal advisor."*

#### 💬 Command Prompt for Antigravity:
```text
Antigravity, execute step 4: inject the 24/7 Weil Deal AI Advisor in the bottom-right corner.
```
*(Or execute: `python3 agy-recipes/weil-modernization/scripts/demo_step4_advisor.py`)*

#### ⚙️ Live System Behavior:
1. A gold and navy floating badge with a live green status dot appears in the bottom right.
2. Clicking the advisor opens the conversational drawer equipped with rapid query chips:
   - *"Analyze Delaware MAE standards for pending buyout"*
   - *"Check Schrems II cross-border data transfer clause"*
   - *"Summarize cov-lite syndicated debt protections"*
3. **Gemini 3.7 Flash** responds with partner-level reasoning, rigorous legal citations, and zero hallucinations.

---

### 📑 ACT 5: AI Feature 3 — Multimodal Term Sheet Pre-Clearance

> **Presenter Talking Points**:
> *"Finally, let's explore how Antigravity connects Vision AI to parse complex financing term sheets and verify deterministic Ethical Wall boundaries before partner redlining."*

#### 💬 Command Prompt for Antigravity:
```text
Antigravity, execute step 5: deploy the multimodal credit agreement analyzer and ethical wall pre-clearance modal.
```
*(Or execute: `python3 agy-recipes/weil-modernization/scripts/demo_step5_multimodal.py`)*

#### ⚙️ Live System Behavior:
1. Click the top-right button **"Pre-Clear Term Sheet"**.
2. An interactive modal opens featuring an animated laser-scan analysis across 14 pages of an $850M Senior Secured Facility term sheet.
3. Key financial covenants are extracted (leverage caps, interest coverage, negative pledge baskets) and checked against adverse-party registries, issuing the clearance token: `WEIL-NY-2026-APEX-CLEARANCE-PASS`.

---

## 4. Rapid Teardown & Workspace Reset

To cleanly conclude the demonstration or restore the workspace for a fresh run:

```bash
python3 agy-recipes/weil-modernization/scripts/teardown.py
```
Or instruct Antigravity directly:
```text
Antigravity, clean up and restore this workspace to start over from scratch.
```
