# 🎙️ Motorola Solutions — Gemini Enterprise Executive Demo Speech & 4-Turn Question Playbook

**Local File URI:** `file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/motorola-enterprise-poc/MOTOROLA_DEMO_SPEECH_AND_QUESTIONS.md`  
**Gemini Enterprise Engine:** `projects/254356041555/locations/global/collections/default_collection/engines/gemini-enterprise-17877637_1787763712023`

---

## 📊 Verified Live Gemini Enterprise Agents Inventory

| Use Case / Row | Live Display Name in Gemini Enterprise | Agent ID | Type | Connected Data Silos |
| :--- | :--- | :--- | :--- | :--- |
| **Row 19 (Primary)** | `Customer 360 & Cross-Sell Executive Review` | `4266057264553488023` | Workflow Agent | Salesforce + ServiceNow + Google Drive |
| **Row 19 (Companion)** | `Account Contract Reconciliation Advisor` | `17675123094112187464` | Workflow Agent | Salesforce + ServiceNow + Google Drive |
| **Row 19 (A2UI Unified)** | `Motorola Unified Enterprise AI & A2UI Agent` | `12736444551981854880` | ADK / A2UI v0.9 | Salesforce + ServiceNow + Google Drive |
| **Row 3 (Event & VIP)** | `Territory Event Catalyst & Competitive Advisor` | Main Chat / Workflow | Multi-Connector | Gmail + Google Calendar + Google Drive + Salesforce |
| **Row 5 (Basic Agent)** | `Motorola Contract Renewals & Pipeline Advisor` | `8517176328388284078` | Basic Agent | Salesforce Hosted MCP (`soqlQuery`) |

---

## 🎯 1. Row 19 — Customer 360 & Cross-Sell / Renewal Risk Agent
* **Business Owner:** David Katimi *(Public Safety Sales & Account Operations)*
* **Active Agent IDs:** `4266057264553488023` (`Customer 360 & Cross-Sell Executive Review`) | `17675123094112187464` (`Account Contract Reconciliation Advisor`)
* **Connected Systems:** **Salesforce CRM** (`soqlQuery`) + **ServiceNow ITSM** (`incident`) + **Google Drive** *(36-Month ASTRO 25 Telemetry & Cross-Sell Playbooks)* + **Google Calendar**

### 🗣️ Why This Agent Matters (Executive Business Value Speech — 25 Seconds)
> *"At Motorola Solutions, our biggest threat to multi-million-dollar public safety renewals isn’t competitor pricing—it’s siloed enterprise data. Today, an Account Executive preparing for a renewal meeting has to manually check Salesforce for contract terms, ServiceNow for open dispatch outages, and Google Drive for approved cross-sell playbooks. If an AE walks into a renewal review blind to an active Priority-1 radio outage, we risk losing the account. This Customer 360 Agent unifies all three silos in seconds—turning technical outage risk into a pre-approved, data-grounded expansion proposal."*

---

### 💬 4 Progressive Demo Questions (Multi-Turn Conversation Flow)

#### **Turn 1 — Opening Prompt (Cross-Silo Account & Renewal Risk Audit)**
```text
Give me a full Customer 360 executive review for Miami-Dade Dispatch and City of Metro Public Safety. What are their upcoming renewal amounts in Salesforce, and are there any active Priority-1 ServiceNow incidents threatening these renewals?
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **Salesforce CRM (`Miami-Dade Dispatch`):** Opportunity ID **`006jV000001CIWrQAO`** | Deal Name: `Miami-Dade Dispatch Center ASTRO 25 Core & APX Renewal` | Amount: **`$1,950,000.00`** | Stage: `Negotiation/Review` | Close Date: `2026-10-15`.
  * **ServiceNow ITSM (`Miami-Dade`):** Incident **`INC0010007`** *(also cross-referenced as `INC0010999`)* | Priority: **`1 - Critical`** | Issue: `P1 Critical: Miami-Dade ASTRO 25 Repeater Site 4 RF Packet Loss`.
  * **Salesforce & Drive Matrix (`City of Metro Public Safety`):** Account ID **`001jV000009Im4DQAS`** | Contract ID: **`MUN-IL-884`** | Total Deal Value: **`$3,850,000.00`** (`$2.60M` Core LMR Renewal + `$1.25M` Cloud Video Expansion) | Expiring in **45 Days**.
  * **ServiceNow ITSM (`City of Metro`):** Incident **`INC0010002`** *(cross-ref `INC0010942`)* | Priority: **`1 - Critical`** | Issue: `Trunked RF Channel 4 Audio Packet Loss`.

---

#### **Turn 2 — Follow-Up Prompt (36-Month RF Telemetry & Technical Root Cause)**
```text
Drill into the 36-month ASTRO 25 usage telemetry and engineering logs in Google Drive for these accounts. What operational bottlenecks are driving these P1 packet-loss incidents, and who is the key municipal decision-maker?
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **Google Drive Sheet Citation:** `Motorola Solutions - 2026 Public Safety Expiring Contracts & LMR Usage Matrix`
    * **36-Month Push-To-Talk (PTT) Call Volume:** **`43.2 Million calls`**.
    * **Peak Channel Saturation:** **`94.2% capacity`** on District 4 Tactical Dispatch *(exceeding the 85% mission-critical congestion threshold)*.
  * **Google Drive Doc Citation:** `[Motorola Public Safety] City of Metro & State Patrol - 36-Month ASTRO 25 LMR Telemetry & Cloud Video Cross-Sell Playbook`
    * Identifies **Commissioner Marcus Vance** as the executive economic buyer requiring zero-downtime SLA assurances prior to signature.

---

#### **Turn 3 — Deep-Dive Follow-Up Prompt (Playbook Cross-Sell Solution & Discount Rules)**
```text
Based on our official Google Drive Cross-Sell Playbooks, what exact hardware/SaaS expansion bundles solve these RF congestion and dead-zone issues, and what discount thresholds are pre-approved?
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **Google Drive Playbook Citation:** `ASTRO 25 Telemetry & Video Cross-Sell Playbook`
  * **Technical Remediation + Upsell Architecture:**
    * **For Miami-Dade (`$1.95M`):** Pitch **APX NEXT Smart Radios** *(automatic LTE/Wi-Fi broadband failover eliminates Repeater Site 4 RF dead zones)* + **CommandCentral Aware** + **Avigilon Unity Video**.
    * **For City of Metro (`$3.85M` total package):** Bundle **ASTRO 25 LMR Core Renewal (`$2.60M`)** with **Avigilon Alta Cloud Video Security + License Plate Recognition (LPR) + CommandCentral Aware (`$1.25M` upsell)**.
  * **Pre-Approved Commercial Discount Governance:**
    * **12% Public Sector Parent Bundle Discount** for municipal multi-agency LMR + Cloud Video bundles (`City of Metro`).
    * **15% Retention Discount** for multi-year SaaS bundle renewals exceeding `$1.5M`.
    * **20% Executive Override Discount** authorized specifically when bundling `CommandCentral Aware` on active LMR accounts experiencing P1/P2 hardware incidents (`Miami-Dade`).

---

#### **Turn 4 — Executive Action Follow-Up Prompt (War Room Alignment & Turnaround Brief)**
```text
Check Google Calendar for our upcoming Renewal War Room session, and generate an executive turnaround action plan for David Katimi that sequences the ServiceNow P1 fix, the executive discount override, and the customer pitch to Commissioner Marcus Vance.
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **Google Calendar Citation:** `[RENEWAL WAR ROOM] City of Metro Public Safety ($3.85M)`
  * **Synthesized 3-Step Executive Turnaround Sequence:**
    1. **Immediate Engineering Escalation:** Dispatch RF Field Engineering to resolve ServiceNow **P1 Incidents `INC0010002` & `INC0010007`** prior to executive review.
    2. **Commercial Concession Structuring:** Apply the **20% Executive Override Discount** (`Miami-Dade`) and **12% Public Sector Parent Bundle Discount** (`City of Metro`).
    3. **Executive Proposal Delivery:** Present the unified ASTRO 25 + APX NEXT LTE failover + CommandCentral Aware roadmap to **Commissioner Marcus Vance** during the scheduled War Room.

---

## 🏆 2. Row 3 — VIP Customer & Partner Event Engagement Agent
* **Business Owners:** Sahil Taank *(Sales Territory Catalyst)* & Jacky Chui *(Marketing / Competitive Intelligence)*
* **Connected Systems:** **Gmail** + **Google Calendar** + **Google Drive** *(Competitive Intelligence Deep Research Dossier)* + **Salesforce Pipeline**

### 🗣️ Why This Agent Matters (Executive Business Value Speech — 25 Seconds)
> *"Major public safety summits like APCO are where $10M+ territory pipelines are won or lost—yet our field sales and partner teams often walk into VIP hospitality receptions without knowing which municipal decision-makers are attending, what deals are on the line, or how competitors are attacking our accounts. This VIP Event Engagement Agent automatically correlates Gmail territory alerts, Google Calendar hospitality RSVPs, active deal values, and Google Drive competitive dossiers—arming our executives with precision talking points before they shake a single customer's hand."*

---

### 💬 4 Progressive Demo Questions (Multi-Turn Conversation Flow)

#### **Turn 1 — Opening Prompt (VIP Attendance & Pipeline Exposure at APCO 2026)**
```text
Check Sahil Taank's partner territory alert in Gmail and our Google Calendar for the APCO 2026 Public Safety Summit. Which VIP public safety executives are confirmed for our hospitality reception, and what is the active deal value tied to each attendee?
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **Gmail Citation:** `[PARTNER TERRITORY ALERT] APCO 2026 Public Safety Summit`
  * **Google Calendar Citation:** `[APCO 2026] Motorola Territory Partner & VIP Customer Hospitality Reception` *(Orlando, FL)*
  * **Confirmed VIP Executive Attendees & Pipeline at Stake (`$11.0M+` Total):**
    1. **Commissioner Marcus Vance** *(City of Metro Public Safety)* — **`$3,850,000`** ASTRO 25 + Avigilon Cloud Video renewal/expansion.
    2. **Colonel Elena Rostova** *(State Highway Patrol)* — **`$5,200,000`** statewide mission-critical P25 & vehicular video modernization.
    3. **Sheriff Dietrich Keller** *(County Sheriff’s Office / Miami-Dade Corridor)* — **`$1,950,000`** APX NEXT & dispatch console renewal.
    4. **Director Henrik Lindqvist** *(Regional Emergency Management Agency)* — Multi-agency interoperability expansion.

---

#### **Turn 2 — Follow-Up Prompt (Competitive Threat Analysis: Axon & L3Harris)**
```text
Search Gmail for Jacky Chui's competitive intelligence brief and review the 2026 Deep Research Dossier in Google Drive. How are Axon Enterprise and L3Harris aggressively targeting these exact VIP accounts at APCO?
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **Gmail Citation:** `[COMPETITIVE INTELLIGENCE BRIEF - JACKY CHUI]`
  * **Google Drive Citation:** `[Motorola Competitive Intelligence] 2026 Deep Research Dossier`
  * **Identified Competitor Attack Vectors:**
    * **Competitor A — Axon Enterprise:** Pitching aggressive bundled SaaS discounting around **Axon Fleet 3** in-car video + body-worn cameras + Respond cloud software to displace Motorola video expansion.
    * **Competitor B — L3Harris Technologies:** Offering an upfront **15% hardware price discount** on P25 land mobile radios to undercut Motorola ASTRO 25 renewals.

---

#### **Turn 3 — Deep-Dive Follow-Up Prompt (Executive Counter-Positioning Strategy)**
```text
Based on Jacky Chui's Competitive Intelligence Dossier in Google Drive, what hard technical and operational counter-arguments should our executives use to neutralize Axon's SaaS bundle and L3Harris's 15% hardware discount?
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **Google Drive Dossier Counter-Playbook:**
    * **Countering Axon Enterprise:** Emphasize that Axon lacks native mission-critical P25 voice infrastructure. Highlight Motorola’s **end-to-end mission-critical ecosystem**: native integration between **ASTRO 25 P25 voice**, **APX NEXT smart radios**, **Avigilon Alta cloud video**, and **CommandCentral Aware** single-pane-of-glass dispatch (voice-to-video automated triggers that standalone camera vendors cannot match).
    * **Countering L3Harris (`15% Discount Trap`):** Expose L3Harris's documented **FIPS 140-3 cryptographic module supply chain bottlenecks and multi-quarter delivery delays**, which put public safety agencies at severe compliance and operational readiness risk compared to Motorola’s certified, in-stock AES-256 / FIPS 140-3 APX hardware.

---

#### **Turn 4 — Executive Action Follow-Up Prompt (1-Page VIP Reception Battlecard)**
```text
Generate a concise 1-page Executive Reception Battlecard for Sahil Taank and the Motorola leadership team ahead of the Orlando APCO VIP Hospitality Reception, matching each VIP guest to their custom value pitch and competitive trap-setter question.
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **Structured Executive Battlecard Table:**
    * Maps **Commissioner Marcus Vance (`$3.85M`)**, **Colonel Elena Rostova (`$5.2M`)**, **Sheriff Dietrich Keller (`$1.95M`)**, and **Director Henrik Lindqvist** to their exact account pain points, tailored Motorola solution bundles, and sharp trap-setting questions that disqualify Axon and L3Harris on the spot.

---

## ⚡ 3. Bonus / Companion Agent: Row 5 — Contract Management & Renewals Basic Agent
* **Live Agent Display Name:** `Motorola Contract Renewals & Pipeline Advisor`
* **Live Agent ID:** `8517176328388284078`
* **Business Owner:** David Katimi *(Sales / Operations)*
* **Integration Architecture:** Single-Connector Basic Agent powered by **Salesforce Hosted MCP (`soqlQuery`)**

### 🗣️ Why This Agent Matters (Executive Business Value Speech — 20 Seconds)
> *"For Sales Operations and Renewal Managers who need instant visibility into CRM pipeline health without building complex reports, this single-connector Salesforce Agent turns natural language directly into live `soqlQuery` executions. In seconds, leadership can audit contract expiration timelines, stage bottlenecks, and multi-million-dollar public safety renewal exposure across the entire territory."*

---

### 💬 4 Progressive Demo Questions (Multi-Turn Conversation Flow)

#### **Turn 1 — Opening Prompt (Single Account Contract Audit)**
```text
What is the current renewal status, stage, close date, and exact contract dollar amount for the Miami-Dade Dispatch deal in Salesforce?
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **Live Salesforce `soqlQuery` Result:**
    * **Opportunity ID:** **`006jV000001CIWrQAO`**
    * **Opportunity Name:** `Miami-Dade Dispatch Center ASTRO 25 Core & APX Renewal`
    * **Amount:** **`$1,950,000.00`**
    * **StageName:** `Negotiation/Review` | **CloseDate:** `2026-10-15`.

---

#### **Turn 2 — Follow-Up Prompt (High-Value Territory Pipeline Filter)**
```text
List all active public safety renewal opportunities in Salesforce over $1.5M with their Opportunity IDs, contract values, stages, and target close dates.
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **Live Salesforce Pipeline Rollup:**
    * Surfaces top-tier public safety contracts across the territory, highlighting **Miami-Dade Dispatch (`$1.95M`, `006jV000001CIWrQAO`)**, **City of Metro Public Safety (`$3.85M` / `$2.6M`, `001jV000009Im4DQAS`)**, and **State Highway Patrol (`$5.20M`)**.

---

#### **Turn 3 — Deep-Dive Follow-Up Prompt (Quarterly Expiration Risk Ranking)**
```text
Which of these public safety contracts are closing within the next 60 days or currently sitting in Negotiation/Review where executive sponsorship is required to close on time?
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **Time-to-Close Risk Prioritization:**
    * Flags near-term closing deals in `Negotiation/Review` (`Miami-Dade Dispatch` closing `2026-10-15` and `City of Metro Public Safety` with `45 Days to Expiration`), isolating **`$5.80M+`** in immediate Q4 renewal revenue requiring executive deal-desk attention.

---

#### **Turn 4 — Executive Action Follow-Up Prompt (CRO Weekly Forecast Summary)**
```text
Generate an executive pipeline summary table for our Chief Revenue Officer categorizing these renewals by deal size, risk tier, and recommended next commercial action.
```
* **🔍 Live Grounded Citations to Highlight on Screen:**
  * **CRO Executive Pipeline Table:**
    * Clean, board-ready summary table showing Account Name, Salesforce ID, Contract Amount, Renewal Stage, Risk Tier, and Next Commercial Action—ready to paste directly into the weekly executive forecast.
