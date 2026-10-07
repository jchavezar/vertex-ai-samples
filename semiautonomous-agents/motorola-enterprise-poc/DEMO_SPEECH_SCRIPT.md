# 🎙️ Motorola Solutions — Gemini Enterprise Master Demo Script (All 4 Progressive Agents)

**Direct IDE File Link:** `file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/motorola-enterprise-poc/DEMO_SPEECH_SCRIPT.md`

---

## 1️⃣ Level 1 — Basic Agent (Single Connector, No-Code)
### 🤖 Agent Name in Gemini Enterprise:
**`Motorola Contract Renewals & Pipeline Advisor`** *(Agent ID: `8517176328388284078`)*

### 📌 What It Does:
Single-connector Basic Agent built in Gemini Enterprise Agent Designer using **Salesforce Hosted MCP (`soqlQuery`)**. Translates plain English directly into live Salesforce queries to audit contract values, renewal stages, close dates, and territory pipeline exposure in seconds without building manual CRM reports.

### 💬 Questions to Ask:
1. **Single Deal Lookup (`Miami-Dade $1.95M`):**
   ```text
   What is the current renewal status, stage, close date, and exact contract dollar amount for the Miami-Dade Dispatch deal in Salesforce?
   ```
2. **Territory Pipeline Rollup (`>$1.5M Public Safety Deals`):**
   ```text
   List all active public safety renewal opportunities in Salesforce over $1.5M with their Opportunity IDs, contract values, stages, and target close dates.
   ```
3. **CRO Forecast & Expiration Risk Summary:**
   ```text
   Which of these public safety contracts are closing within the next 60 days or sitting in Negotiation/Review where executive sponsorship is required?
   ```

---

## 2️⃣ Level 2 — Workflow Agent (Multi-Connector Cross-Silo Orchestration)
### 🤖 Agent Name in Gemini Enterprise:
**`Customer 360 & Cross-Sell Executive Review`** *(Agent ID: `4266057264553488023`)*  
*(Companion Multi-Connector Event Agent: **`Territory Event Catalyst & Competitive Advisor`**)*

### 📌 What It Does:
Multi-step Workflow Agent orchestrating **Salesforce CRM (`soqlQuery`) + ServiceNow ITSM (`incident`) + Google Drive Playbooks & Telemetry + Google Calendar**. Automatically correlates upcoming multi-million-dollar renewals against active Priority-1 radio outages, 36-month ASTRO 25 usage saturation logs, and pre-approved discount rules.

### 💬 Questions to Ask:
1. **Cross-Silo Renewal & P1 Outage Audit (`Salesforce + ServiceNow`):**
   ```text
   Give me a full Customer 360 executive review for Miami-Dade Dispatch and City of Metro Public Safety. What are their upcoming renewal amounts in Salesforce, and are there any active Priority-1 ServiceNow incidents threatening these renewals?
   ```
2. **Engineering Root Cause & Playbook Bundle Match (`Google Drive Docs & Sheets`):**
   ```text
   Drill into the 36-month ASTRO 25 usage telemetry and cross-sell playbooks in Google Drive for these accounts. What exact hardware/SaaS expansion bundles solve these RF congestion and dead-zone issues, and what discount thresholds are pre-approved?
   ```
3. **Executive War Room Action Plan (`Google Calendar + Turnaround Brief`):**
   ```text
   Check Google Calendar for our upcoming Renewal War Room session, and generate an executive turnaround action plan for David Katimi sequencing the ServiceNow P1 fix, discount override, and pitch to Commissioner Marcus Vance.
   ```

---

## 3️⃣ Level 3 — Custom A2A Deep-Reasoning Agent (Pro-Code + Full-Screen Cockpit)
### 🤖 Agent Name in Gemini Enterprise:
**`Motorola Unified Enterprise AI & A2UI Agent`** *(Agent ID: `12736444551981854880`)*

### 📌 What It Does:
Custom Cloud Run A2A agent powered by **`gemini-3.8-flash`** performing deep cross-silo reasoning across **Salesforce (`006jV000001CIWrQAO`)**, **ServiceNow (`INC0010007`, `INC0010006`, `INC0010004`)**, and **Google Drive Governance Policies**. Generates comprehensive boardroom memos, full legal/tariff clause analyses (`HTS 8517.62.00`), clickable citations, native A2UI action cards, and the full-screen interactive **Executive Deal Cockpit**.

### 💬 Questions to Ask:
1. **Deep Cross-Silo Renewal & Outage Investigation:**
   ```text
   Analyze the Miami-Dade Dispatch $1.95M renewal in Salesforce, correlate any active P1 ServiceNow outages, and recommend a compliant restructuring playbook based on our Google Drive governance policies.
   ```
2. **Supply Chain Customs Hold & Procurement Liability Escalation Audit:**
   ```text
   Audit ServiceNow escalations INC0010004 (Customs Section 301 Tariff Hold) and INC0010006 (Vendor Liability Redline) against Motorola's binding HTS customs rulings and procurement policy.
   ```

---

## 4️⃣ Level 4 — Native Interactive Visual Command Deck Agent (GA A2UI `v0.9` War Room)
### 🤖 Agent Name in Gemini Enterprise:
**`Motorola Visual Command Deck`** *(Agent ID: `13129996171629815464`)*

### 📌 What It Does:
Executive Visual Intelligence & War Room agent built on **native GA A2UI (`v0.9`)**. Renders an ultra-crisp **5-line Executive Flash Brief** above a **43-component native interactive visual dashboard** directly inside the Gemini Enterprise chat window—featuring 3 side-by-side KPI cards, high-DPI multi-series & SLA charts, live cross-silo MCP audit trail, interactive scenario switcher buttons, and **1-click live OAuth 2.0 write-back to ServiceNow (`dev271596.service-now.com`)**.

### 💬 Questions to Ask:
1. **Scenario A — Commercial Deal Restructuring & P1 RF Outage Recovery (`$1.95M → $1.98M`):**
   ```text
   Show the visual executive command deck for Miami-Dade Dispatch ($1.95M renewal)
   ```
   *(Click **`⚡ Authorize 20% Override & Patch ServiceNow Live (INC0010007)`** right inside the card to execute live ServiceNow OAuth 2.0 write-back!)*

2. **Scenario B — National Public Safety Portfolio War Room (`$9.75M → $10.42M`):**
   ```text
   Launch the National Public Safety Portfolio War Room across all accounts
   ```
   *(Or click **`📊 Switch to National Portfolio War Room ($9.75M)`** directly inside the card.)*

3. **Scenario C — Global Trade Tariff (`INC0010004`) & Legal Redline (`INC0010006`) Simulator (`$1.90M Saved`):**
   ```text
   Run the Global Supply Chain Tariff and Legal Redline visual simulator
   ```
   *(Or click **`🛡️ Switch to Tariff & Legal Redline Simulator`** directly inside the card.)*




-- Maps ---

```text
Show the live geospatial RF outage and field dispatch map for Miami-Dade Dispatch
```