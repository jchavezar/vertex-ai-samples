---
name: demo-weil
description: Sets the agent into complete cognitive context for the Weil, Gotshal & Manges LLP Modernization Demo and presents the 5 progressive demonstration options (Baseline Clone, UX/UI Deal Cockpit, Intelligent Precedent Navigator with Gemini 3.7 Flash, 24/7 Weil Deal Advisor, and Multimodal Term Sheet Pre-Clearance with Vision AI) without blindly auto-executing them as a script. Scaffolds files directly into the active workspace directory. Activate whenever the user mentions "demo weil", "demo weil finance", "weil demo", or asks about modernizing Weil.
---

# Weil, Gotshal & Manges LLP Demo: Cognitive Protocol and 5-Act Presentation

This skill equips the agent with instant, complete architectural, technical, and business context for modernizing **Weil, Gotshal & Manges LLP** (`https://www.weil.com/`), ensuring that **all demo files are generated and executed directly inside the user's active workspace directory (`cwd`)** so they appear in the file tree (*Explorer*).

---

## 🎯 Core Operating Principle: Active User Directory (`cwd`)

> [!IMPORTANT]
> **ACTIVE DIRECTORY RULE**:
> If the user opens a new workspace or folder (e.g., `tmp`, `~/demo`, or any clean directory), demo files **MUST NOT remain hidden in an external path**.
> 
> The agent must:
> 1. Detect the current working directory (`cwd`).
> 2. If the current directory does not contain demo files (`site/`, `serve_weil.py`), execute the scaffolding script (`scaffold_workspace.py .`) so the clone and files immediately appear in the left Explorer tree.
> 3. Run the server and modular feature injections directly against the currently active open directory.

---

## 🧠 Complete Knowledge Base

1. **Master Repository Source**:
   - Master Source Path: `/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/weil-modernization/`
   - Automation Recipe Scripts: `/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/weil-modernization/scripts/`

2. **Infrastructure & Dual-Port Architecture**:
   - **Website Modernization (Port 8089)**:
     - Server: `serve_weil.py` running on Python multi-threaded (`ThreadingHTTPServer`) on port **`8089`**.
     - `/api/suggest`: Sub-10ms Search-As-You-Type autocomplete over Weil practices, precedents, and deal structures.
     - `/api/search`: Grounded precedent retrieval and synthesis powered by `gemini-3.7-flash`.
     - `/api/advisor`: Live 24/7 financial and regulatory deal advisor powered by `gemini-3.7-flash` (configured with `thinking_budget=0` and 1000 tokens for instant sub-1.5s responses and zero token truncation).
     - `/api/multimodal-deal`: Multimodal covenant extraction on Term Sheets and Ethical Wall clearance token issuance.
     - Smart 302 Redirection: Intercepts un-cloned deep links (`/people/...`, `/experience/...`) and redirects to `https://www.weil.com/...` with zero 404 errors.
     - **Zero Browser Caching Mandate (`end_headers`)**: Disables localhost caching (`Cache-Control: no-cache, no-store, must-revalidate`).
   - **Executive Legal-Tech Showcase (Ports 8000 & 5173)**:
     - Location: `/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/weil-legal-agentic-showcase`
     - Backend (Port 8000): FastAPI + Google Agent Development Kit (ADK) + Model Context Protocol (MCP) + Dynamic Clause Harmonizer.
     - Frontend (Port 5173): Vite + React 18 + Tailwind CSS.
     - **100" Big Screen Mode**: Header toggle for high-contrast, scaled typography for boardroom displays.
     - **Inspect Code Overlay Modal**: In-app syntax-highlighted code drawer explaining ADK and Gemini architecture.
     - **Zero-Overlap Container Mandate**: Explicit spacing (`gap-4 lg:gap-6`), `shrink-0` branding, and vertical dividers to guarantee boxes never collide or overlap.
     - **Privacy Pro Legos AI Engine**: 3-tier Autonomous Negotiation Stance Bar (*Weil Pro-Client*, *Balanced Market*, *Fast-Close*), real-time clause recalibration (dynamic notice windows 72h / 30d / annual), and Opposing Counsel Radar (Skadden/Latham).

3. **Artificial Intelligence (Google Cloud)**:
   - Permitted Models ONLY: **`gemini-3.7-flash`**, **`gemini-3.8-flash`**, **`gemini-3-flash-preview`**, **`gemini-3-pro-preview`** (via Vertex AI). NEVER obsolete models (no 2.x, 1.x, or 3.5).

4. **Zero Microsoft "Copilot" Protocol**:
   - **NEVER** use the term "copilot" under any circumstances in code, UI, comments, scripts, or presentation materials.
   - Approved branding: **"Weil Deal & Regulatory AI Advisor"**, **"Weil Deal Advisor 24/7"**, **"Autonomous Legal Agent"**, or **"Deal Advisor"**.

5. **Presenter & Leadership Alignment**:
   - Google Lead / Speaker: **Jesus Chavez** (CE, AI).
   - Audience: Andrew Simon (CIO), Ian Miller (Architecture Lead), Steve Kedem, Daulton Cockerell.

6. **Modular Feature Injection (`inject_feature.py`)**:
   - Manages live changes on `./site/index.html` within the current directory.
   - Available Modes:
     - `reset`: Restores the pristine clone baseline (legacy Sitecore/jQuery).
     - `inject modern_header_ux`: Glassmorphic mega-menu + live deal ticker.
     - `inject modern_header_ai`: Complete UX + Intelligent Precedent Navigator dock (480px ──► 760px) with Gemini 3.7 Flash synthesis.
     - `inject ai_advisor`: Floating 24/7 Weil Deal AI Advisor in the bottom-right corner.
     - `inject ai_multimodal_deal`: Multimodal term sheet analyzer modal with laser scan and ethical wall verification token.

---

## 🚫 Strict Activation Rule: ZERO TOOLS / ZERO COMMANDS in Turn 1

> [!CAUTION]
> **ABSOLUTE NO-AUTOEXECUTION RULE**:
> When the user types *"demo weil"*, *"demo weil finance"*, or similar, the agent **MUST NOT EXECUTE ANY COMMAND OR MODIFY ANY FILE**.
> 
> 1. **ZERO TOOLS**: Calling `run_command`, `write_to_file`, `replace_file_content`, or any other tool in the initial turn is strictly prohibited.
> 2. **DIALOGUE ONLY**: The agent must reply SOLELY with the formatted 5-option menu in plain text and await explicit instructions.
> 3. **NO DIFFS IN USER EDITOR**: NEVER open files in diff mode; delegate injections to recipe scripts.
> 4. **ON-DEMAND SCAFFOLDING**: Files are copied to the active directory (`scaffold_workspace.py`) **ONLY** after the user explicitly selects an option.

---

## 📋 Response Protocol for "demo weil"

When the user triggers *"demo weil"* or *"demo weil finance"*, immediately respond in plain text (without tools) displaying:

### 1. The 5-Option Executive Menu

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                  DEMO WEIL FINANCE: 5-OPTION MENU                           │
 ├─────────────────────────────────────────────────────────────────────────────┤
 │                                                                             │
 │ [1] FAITHFUL CLONE BASELINE (Sitecore / jQuery Monolith)                    │
 │     • 100% faithful replication of production portal (weil.com).            │
 │     • Assets and files scaffolded into this directory (visible in Explorer).│
 │     • Corporate styling, branding, and assets running on http://localhost:8089/ │
 │     • Diagnosis: traditional monolith, rigid navigation, and static search. │
 │                                                                             │
 │ [2] UX/UI MODERNIZATION (Deal Cockpit & Glassmorphic Mega-Menu)             │
 │     • Injects interactive dropdown Mega-Menu with modern glassmorphism.     │
 │     • Organized into Banking & Finance, M&A / Private Equity, Restructuring.│
 │     • Real-time ticker of landmark closed transactions ($12.4B Carve-Out).  │
 │     • Instant 1-click reversibility to contrast before vs. after.           │
 │                                                                             │
 │ [3] AI FEATURE 1: PRECEDENT NAVIGATOR (Search-As-You-Type & Gemini 3.7)     │
 │     • Dual-track Search-As-You-Type: instant autocomplete (<10ms).          │
 │     • Dynamic self-expanding dock (480px ──► 760px) with live synthesis.   │
 │     • Deeply grounded in Weil deal history and legal authorities.           │
 │     • Zero broken links (Smart 302 Redirection to weil.com).                │
 │                                                                             │
 │ [4] AI FEATURE 2: 24/7 WEIL DEAL ADVISOR (Gemini 3.7 Flash)                 │
 │     • Floating conversational drawer acting as senior deal advisor.         │
 │     • Instant chips for frequent inquiries (Delaware MAE, Schrems II, Debt).│
 │     • Rigorous legal & financial reasoning tailored for General Counsels.   │
 │                                                                             │
 │ [5] AI FEATURE 3: MULTIMODAL TERM SHEET PRE-CLEARANCE (Vision AI)           │
 │     • Interactive laser scan over a 14-page $850M Syndicated Facility.      │
 │     • Structured covenant extraction via Gemini 3.7 Flash Vision.           │
 │     • Deterministic Ethical Wall conflict verification check.               │
 │     • Immutable audit token: WEIL-NY-2026-APEX-CLEARANCE-PASS.              │
 │                                                                             │
 └─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Prompting the User
Ask: **"Which of the 5 options would you like to prepare or execute in this directory?"**

---

## 🛠️ Execution per Option (Only Upon User Request)

When the user specifies an option (e.g., *"execute step 1"*, *"let's do step 3"*, *"run multimodal pre-clearance"*), invoke the corresponding script via `run_command`:

> 💡 **RECOMMENDED DIRECT METHOD**:
> Each script automatically detects the active directory (`pwd`), scaffolds local files if not yet present, applies changes, starts the server on port 8089, and opens the browser:
> - **Step 1**: `python3 /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/weil-modernization/scripts/demo_step1_clone.py`
> - **Step 2**: `python3 /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/weil-modernization/scripts/demo_step2_ux.py`
> - **Step 3**: `python3 /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/weil-modernization/scripts/demo_step3_ai.py`
> - **Step 4**: `python3 /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/weil-modernization/scripts/demo_step4_advisor.py`
> - **Step 5**: `python3 /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/weil-modernization/scripts/demo_step5_multimodal.py`
> - **Teardown**: `python3 /Users/jesusarguelles/IdeaProjects/vertex-ai-samples/agy-recipes/weil-modernization/scripts/teardown.py`

---

## 🎭 Presentation Takeaways per Step

### Step 1: Faithful Baseline Clone (Legacy Sitecore Monolith)
- 100% visual fidelity to `weil.com`.
- Highlights traditional architecture, rigid navigation, and slow discovery.

### Step 2: UX/UI Modernization (Glassmorphic Deal Cockpit)
- Executive layout prioritizing high-yield practices (Banking, M&A, Restructuring).
- Live deal ticker. 100% reversible in one command.

### Step 3: AI Feature 1 (Precedent Navigator)
- Sub-10ms autocomplete in compact 480px dock.
- Fluid expansion to 760px and executive synthesis generated by Gemini 3.7 Flash.

### Step 4: AI Feature 2 (24/7 Weil Deal Advisor)
- Premium navy/gold floating button with live green status indicator.
- Conversational strategic deal advisory grounded in Delaware law.

### Step 5: AI Feature 3 (Multimodal Term Sheet Pre-Clearance)
- Visual scan with Gemini 3.7 Flash Vision on financing credit agreements.
- Deterministic Ethical Wall boundary validation with cryptographic audit token.
