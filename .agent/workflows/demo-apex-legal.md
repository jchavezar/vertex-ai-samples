---
name: demo-apex-legal
description: Sets the agent into complete cognitive context for the Apex Global Law LLP Portal Modernization Demo and presents the 5 progressive demonstration options (Baseline Synthetic Portal, UX/UI Deal Cockpit, Intelligent Precedent Navigator with Gemini 3.8 Flash, 24/7 Apex Deal Advisor, and Multimodal Term Sheet Pre-Clearance with Vision AI) without blindly auto-executing them as a script. Scaffolds files directly into the active workspace directory. Activate whenever the user mentions "demo apex", "demo apex legal", "apex legal demo", or asks about modernizing the Apex Global Law portal.
---

# Apex Global Law LLP Demo: Cognitive Protocol and 5-Act Presentation

This workflow equips the agent with complete architectural, technical, and business context for modernizing **Apex Global Law LLP** (`https://apexgloballaw.example.com/`), ensuring that **all demo files are generated and executed directly inside the user's active workspace directory (`cwd`)** so they appear in the file tree (*Explorer*).

---

## 🎯 Core Operating Principle: Active User Directory (`cwd`)

> [!IMPORTANT]
> **ACTIVE DIRECTORY RULE**:
> If the user opens a new workspace or folder (e.g., `/tmp`, `~/demo`, or any clean directory), demo files **MUST NOT remain hidden in an external path**.
>
> The agent must:
> 1. Detect the current working directory (`cwd`).
> 2. If the current directory does not contain demo files (`site/`, `serve_portal.py`), execute the scaffolding script (`scaffold_workspace.py .`) so the portal and files immediately appear in the left Explorer tree.
> 3. Run the server and modular feature injections directly against the currently active open directory.

---

## 🧠 Complete Knowledge Base

1. **Master Repository Source**:
   - Master Source Path: `semiautonomous-agents/apex-legal-portal-modernization/`
   - Automation Recipe Scripts: `agy-recipes/apex-legal-modernization/scripts/`

2. **Infrastructure & Dual-Port Architecture**:
   - **Website Modernization (Port 8089)**:
     - Server: `serve_portal.py` running on Python multi-threaded (`ThreadingHTTPServer`) on port **`8089`**.
     - `/api/suggest`: Sub-10ms Search-As-You-Type autocomplete over Apex Global Law practices, precedents, and deal structures.
     - `/api/search`: Grounded precedent retrieval and synthesis powered by `gemini-3.8-flash` (`location="global"`).
     - `/api/advisor`: Live 24/7 financial and regulatory deal advisor powered by `gemini-3.8-flash` (sub-1.5s responses and zero token truncation).
     - `/api/multimodal-deal`: Multimodal covenant extraction on Term Sheets and Ethical Wall clearance token issuance (`APEX-NY-2026-CLEARANCE-PASS`).
     - Local Synthetic Deep-Link Resolution: Serves self-contained practice and precedent authority views (`200 OK`, zero external redirects, 100% offline/standalone).
     - **Zero Browser Caching Mandate (`end_headers`)**: Disables localhost caching (`Cache-Control: no-cache, no-store, must-revalidate`).
   - **Executive Legal-Tech Showcase (Ports 8000 & 5173)**:
     - Location: `semiautonomous-agents/apex-legal-agentic-showcase`
     - Backend (Port 8000): FastAPI + Google Agent Development Kit (ADK) + Model Context Protocol (MCP) + Dynamic Clause Harmonizer.
     - Frontend (Port 5173): Vite + React 18 + Tailwind CSS.
     - **100" Big Screen Mode**: Header toggle for high-contrast, scaled typography for boardroom displays.
     - **Inspect Code Overlay Modal**: In-app syntax-highlighted code drawer explaining ADK and Gemini architecture.
     - **Zero-Overlap Container Mandate**: Explicit spacing (`gap-4 lg:gap-6`), `shrink-0` branding, and vertical dividers to guarantee boxes never collide or overlap.
     - **ClauseGuard AI Engine**: 3-tier Autonomous Negotiation Stance Bar (*Apex Pro-Client*, *Balanced Market*, *Fast-Close*), real-time clause recalibration (dynamic notice windows 72h / 30d / annual), and Opposing Counsel Radar (Vanguard LLP / Sterling & Partners).

3. **Artificial Intelligence (Google Cloud 2026 Standard)**:
   - Permitted Models ONLY: **`gemini-3.8-flash`**, **`gemini-4-argon`**, **`gemini-3.1-flash-lite`** (via Vertex AI `location="global"`). NEVER legacy 1.x or 2.x models.

4. **Zero Microsoft "Copilot" Protocol**:
   - **NEVER** use the term "copilot" under any circumstances in code, UI, comments, scripts, or presentation materials.
   - Approved branding: **"Apex Deal & Regulatory AI Advisor"**, **"Apex Deal Advisor 24/7"**, **"Autonomous Legal Agent"**, or **"Deal Advisor"**.

5. **Presenter & Leadership Alignment**:
   - Google Lead / Speaker: **Jesus Chavez** (CE, AI).
   - Synthetic Executive Personas: **Marcus Vance** (Chief Innovation Officer), **Elena Rostova** (Tech Architecture Lead), and Practice Partners.

6. **Modular Feature Injection (`inject_feature.py`)**:
   - Manages live changes on `./site/index.html` within the current directory.
   - Available Modes:
     - `reset`: Restores the pristine synthetic corporate portal baseline (`site/index.pristine.html`).
     - `inject modern_header_ux`: Glassmorphic mega-menu + live deal ticker.
     - `inject modern_header_ai`: Complete UX + Intelligent Precedent Navigator dock (480px -> 760px) with `gemini-3.8-flash` synthesis.
     - `inject ai_advisor`: Floating 24/7 Apex Deal AI Advisor in the bottom-right corner.
     - `inject ai_multimodal_deal`: Multimodal term sheet analyzer modal with laser scan and ethical wall verification token (`APEX-NY-2026-CLEARANCE-PASS`).

---

## 🚫 Strict Activation Rule: ZERO TOOLS / ZERO COMMANDS in Turn 1

> [!CAUTION]
> **ABSOLUTE NO-AUTOEXECUTION RULE**:
> When the user types *"demo apex"*, *"demo apex legal"*, or similar, the agent **MUST NOT EXECUTE ANY COMMAND OR MODIFY ANY FILE**.
>
> 1. **ZERO TOOLS**: Calling `run_command`, `write_file`, `edit_file`, or any other tool in the initial turn is strictly prohibited.
> 2. **DIALOGUE ONLY**: The agent must reply SOLELY with the formatted 5-option menu in plain text and await explicit instructions.
> 3. **NO DIFFS IN USER EDITOR**: NEVER open files in diff mode; delegate injections to recipe scripts.
> 4. **ON-DEMAND SCAFFOLDING**: Files are copied to the active directory (`scaffold_workspace.py`) **ONLY** after the user explicitly selects an option.

---

## 📋 Response Protocol for "demo apex legal"

When the user triggers *"demo apex"* or *"demo apex legal"*, immediately respond in plain text (without tools) displaying:

### 1. The 5-Option Executive Menu

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                 APEX GLOBAL LAW LLP: 5-ACT MODERNIZATION                 │
├──────────────────────────────────────────────────────────────────────────┤
│ [1] BASELINE CORPORATE PORTAL (Legacy Monolith)                          │
│     • Self-contained corporate baseline (apexgloballaw.example.com).     │
│     • Assets & files scaffolded into active directory (Explorer tree).   │
│     • Served locally at http://localhost:8089/ with zero external deps.  │
│                                                                          │
│ [2] UX/UI MODERNIZATION (Deal Cockpit & Glassmorphic Mega-Menu)          │
│     • Injects interactive dropdown Mega-Menu with modern glassmorphism.  │
│     • Banking & Finance, M&A / Private Equity, and Restructuring lanes.  │
│     • Real-time ticker of closed mandates ($12.4B Carve-Out) + rollback. │
│                                                                          │
│ [3] AI FEATURE 1: PRECEDENT NAVIGATOR (Autocomplete & Gemini 3.8 Flash)  │
│     • Dual-track Search-As-You-Type: instant autocomplete (<10ms).       │
│     • Dynamic self-expanding dock (480px -> 760px) with live synthesis.  │
│     • Grounded in synthetic Apex deal history with zero broken links.    │
│                                                                          │
│ [4] AI FEATURE 2: 24/7 APEX DEAL ADVISOR (Gemini 3.8 Flash)              │
│     • Floating conversational drawer acting as senior deal advisor.      │
│     • Instant chips for Delaware MAE, Schrems II, and Cov-Lite Debt.     │
│     • Structured legal & financial reasoning for General Counsels.       │
│                                                                          │
│ [5] AI FEATURE 3: MULTIMODAL TERM SHEET PRE-CLEARANCE (Vision AI)        │
│     • Interactive laser scan over a 14-page $850M Syndicated Facility.   │
│     • Structured covenant extraction via Gemini 3.8 Flash Vision.        │
│     • Ethical Wall check + audit token: APEX-NY-2026-CLEARANCE-PASS.     │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2. Prompting the User
Ask: **"Which of the 5 options would you like to prepare or execute in this directory?"**

---

## 🛠️ Execution per Option (Only Upon User Request)

When the user specifies an option (e.g., *"execute step 1"*, *"let's do step 3"*, *"run multimodal pre-clearance"*), invoke the corresponding script via `run_command` from the repository root:

- **Step 1**: `python3 agy-recipes/apex-legal-modernization/scripts/demo_step1_clone.py`
- **Step 2**: `python3 agy-recipes/apex-legal-modernization/scripts/demo_step2_ux.py`
- **Step 3**: `python3 agy-recipes/apex-legal-modernization/scripts/demo_step3_ai.py`
- **Step 4**: `python3 agy-recipes/apex-legal-modernization/scripts/demo_step4_advisor.py`
- **Step 5**: `python3 agy-recipes/apex-legal-modernization/scripts/demo_step5_multimodal.py`
- **Teardown**: `python3 agy-recipes/apex-legal-modernization/scripts/teardown.py`

---

## 🎭 Presentation Takeaways per Step

### Step 1: Baseline Corporate Portal (Legacy Monolith)
- Self-contained synthetic baseline for `apexgloballaw.example.com`.
- Highlights traditional architecture, rigid navigation, and static `#txtGlobalSearch` discovery.

### Step 2: UX/UI Modernization (Glassmorphic Deal Cockpit)
- Executive layout prioritizing high-yield practices (Banking & Finance, M&A, Restructuring).
- Live deal ticker. 100% reversible in one command.

### Step 3: AI Feature 1 (Precedent Navigator)
- Sub-10ms autocomplete in compact 480px dock.
- Fluid expansion to 760px and executive synthesis generated by `gemini-3.8-flash`.

### Step 4: AI Feature 2 (24/7 Apex Deal Advisor)
- Premium navy/gold floating button with live green status indicator.
- Conversational strategic deal advisory grounded in Delaware corporate law.

### Step 5: AI Feature 3 (Multimodal Term Sheet Pre-Clearance)
- Visual scan with `gemini-3.8-flash` Vision on financing credit agreements.
- Deterministic Ethical Wall boundary validation with cryptographic audit token `APEX-NY-2026-CLEARANCE-PASS`.
