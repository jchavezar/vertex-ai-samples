# Motorola Solutions — Gemini Enterprise Agent Workflow Creator Prompts (5 Use Cases)
*Tailored specifically for Gemini Enterprise Agent Workflow Builder Connected Apps: **Google Drive**, **ServiceNow**, **Gmail**, and **Google Calendar**.*

> **Architecture Note**: In Google Cloud Gemini Enterprise, **Salesforce (`sfdc`)** operates as a Federated Search Connector in the **Main Chat UI** (where you can query Opportunities directly), while the **Agent Workflow Builder** supports Action Connectors (**Google Drive**, **ServiceNow**, **Gmail**, **Google Calendar**, and **Google Search**). Because our Master Seeder mirrored all CRM pipeline, contract values, and CDMG records into Google Drive (Sheets & Docs), ServiceNow, and Gmail, every workflow below executes 100% natively!

---

## 🛠️ Step 0: Toggle ON the 4 Connected Apps in Workflow Builder
In the right-hand **Connected apps** panel of your Workflow Builder, toggle ON:
- 🔵 **Calendar**
- 🔵 **Drive**
- 🔵 **Gmail**
- 🔵 **ServiceNow**

---

## 🤖 Agent #1: Public Safety Renewal & Cross-Sell Spotter
- **Spreadsheet Business Owner**: **David Katimi** *(Public Safety Sales & Renewals)*
- **Connected Apps Used**: **Google Drive** + **ServiceNow** + **Google Calendar** + **Gmail**

### Copy-Paste Prompt for Workflow Creator (`What would you like to change?`):
```text
Create an agent workflow named "Public Safety Renewal & Cross-Sell Spotter" using Google Drive, ServiceNow, Gmail, and Google Calendar.

Workflow Steps:
1. Contract & Telemetry Lookup (Google Drive):
   When asked about an expiring municipal contract or account renewal (such as "City of Metro Public Safety" or "State Highway Patrol"), search Google Drive for the spreadsheet "Motorola Solutions - 2026 Public Safety Expiring Contracts & LMR Usage Matrix" and extract the Contract ID (MUN-IL-884), Annual Value ($2,600,000), Days to Expiration (45 Days), 36-Month PTT Call Volume (43.2M calls), and Channel Saturation (94.2%).
   Also read the Google Doc "[Motorola Public Safety] City of Metro & State Patrol - 36-Month ASTRO 25 LMR Telemetry & Cloud Video Cross-Sell Playbook" to identify channel congestion warnings (District 4 Tactical Dispatch at 94.2% capacity) and decision makers (Commissioner Marcus Vance).

2. Technical Incident Check (ServiceNow):
   Query ServiceNow for any active P1/P2 technical incidents impacting the customer—specifically Incident INC0010002 (INC0010942: Trunked RF Channel 4 Audio Packet Loss)—and flag that this P1 incident must be resolved prior to renewal signature.

3. War Room Alignment & Proposal Generation (Google Calendar & Gmail):
   Check Google Calendar for the scheduled review session ("[RENEWAL WAR ROOM] City of Metro Public Safety ($3.85M)").
   Generate an Executive Renewal & Upsell Brief that:
   - Summarizes the 36-month ASTRO 25 telemetry and ServiceNow P1 incident INC0010002 mitigation plan.
   - Recommends bundling the ASTRO 25 LMR Core Renewal ($2.6M) with Avigilon Alta Cloud Video Security + License Plate Recognition (LPR) + CommandCentral Aware ($1.25M upsell).
   - Applies the pre-approved 12% Public Sector Parent Bundle Discount.
```

### 🧪 Test Prompt for Agent #1:
> *"Analyze the renewal risk for City of Metro Public Safety. What does their 36-month ASTRO 25 telemetry show in Drive, are there any open P1 ServiceNow incidents blocking the deal, and what cross-sell bundle should David Katimi pitch in the upcoming War Room?"*

---

## 🤖 Agent #2: CDMG Master Data Stewardship & Hierarchy Agent
- **Spreadsheet Business Owners**: **Erica Boklewski & Magdalena Zurakowska** *(CDMG / Master Data)*
- **Connected Apps Used**: **Gmail** + **Google Drive** + **ServiceNow** + **Google Calendar**

### Copy-Paste Prompt for Workflow Creator:
```text
Create an agent workflow named "CDMG Master Data Stewardship Agent" using Gmail, Google Drive, ServiceNow, and Google Calendar.

Workflow Steps:
1. Unverified Record Ingestion (Gmail):
   Search Gmail for "[CDMG DATA GOVERNANCE ALERT - ERICA BOKLEWSKI]" to retrieve the list of unverified municipal and commercial entities requiring remediation (Apex Global Communications [UNVERIFIED CDMG RECORD], Pacific Rim Tactical Radios Ltd, and City of Metro Public Safety District 4 Sub-Agency).

2. Policy Standard Verification (Google Drive):
   Read the Google Doc "[Motorola CDMG Policy] Master Data Stewardship, Address Validation & Public Sector Hierarchy Grouping Standard (2026)" in Google Drive to verify:
   - Street address validation and County derivation rules (e.g., 1200 N. State Parkway, Chicago IL -> Cook County).
   - Public Sector parent-child hierarchy grouping rules (linking municipal sub-departments like Police, Fire, and District 4 under the parent entity "City of Metro Public Safety").

3. Governance Exception & Board Review (ServiceNow & Google Calendar):
   Query ServiceNow for governance ticket INC0010003 (REQ0010904: Hierarchy Override for Apex Global Communications) and check Google Calendar for "[CDMG GOVERNANCE BOARD] Master Data Hierarchy Remediation".
   Output a structured Data Stewardship Remediation Table with validated addresses, derived counties, parent hierarchy mappings, and recommended ServiceNow approval actions.
```

### 🧪 Test Prompt for Agent #2:
> *"Check Erica Boklewski's CDMG governance alert in Gmail and ServiceNow ticket INC0010003. How should we remediate Apex Global Communications and the City of Metro District 4 sub-agency based on our 2026 CDMG Policy Doc in Drive?"*

---

## 🤖 Agent #3: Procurement RFQ Redliner & Trade Compliance Auditor
- **Spreadsheet Business Owners**: **Yoke Pheng Wong** *(Procurement)*, **Ken Bradshaw** *(Trade Compliance)*, **Ryan Christensen** *(Legal)*
- **Connected Apps Used**: **Gmail** + **Google Drive** + **ServiceNow** + **Google Calendar**

### Copy-Paste Prompt for Workflow Creator:
```text
Create an agent workflow named "Procurement RFQ Redliner & Trade Compliance Auditor" using Gmail, Google Drive, ServiceNow, and Google Calendar.

Workflow Steps:
1. RFQ & Trade Hold Lookup (Gmail & ServiceNow):
   Search Gmail for supplier RFQ submissions ("[RFQ SUBMISSION #2026-884] Shenzhen RF Components Ltd") and query ServiceNow for active Trade Compliance holds (INC0010004 / INC0010819).

2. Tariff Classification Audit (Google Drive):
   Read the Google Doc "[Motorola Procurement & Trade Compliance] Global RFQ Terms, Approved Redlines & HTS Tariff Classification Matrix" in Google Drive.
   Compare the supplier's declared Harmonized Tariff Schedule (HTS) code against Motorola's compliance standard, flagging misclassifications between HTS 8525.60.1020 (Encrypted Public Safety Transceivers w/ AES-256/FIPS 140-3 -> 0.0% Duty Free) and HTS 8525.60.1050 (Commercial Unencrypted Radios -> 7.5% Section 301 tariff).

3. Contract Redlining & Legal Review (Google Drive & Calendar):
   Check Google Calendar for "[TRADE COMPLIANCE & LEGAL REVIEW] Supplier RFQ #2026-884" and generate a redlined legal response enforcing:
   - Payment Terms: Redline Net-60/Net-90 demands back to Motorola standard Net-45 days (or Net-60 with a 3% early payment discount).
   - Limitation of Liability: Redline any 0.5x PO liability cap to the mandatory minimum 2.0x PO value.
```

### 🧪 Test Prompt for Agent #3:
> *"Audit supplier RFQ #2026-884 in Gmail and ServiceNow Trade Hold INC0010004. What HTS tariff classification error did the supplier make, and what contract redlines must Ryan Christensen enforce based on our Procurement Playbook in Drive?"*

---

## 🤖 Agent #4: Territory Event Catalyst & Competitive Intelligence Advisor
- **Spreadsheet Business Owners**: **Sahil Taank** *(Sales Territory Catalyst)* & **Jacky Chui** *(Marketing / Competitive Intelligence)*
- **Connected Apps Used**: **Gmail** + **Google Drive** + **Google Calendar**

### Copy-Paste Prompt for Workflow Creator:
```text
Create an agent workflow named "Territory Event Catalyst & Competitive Advisor" using Gmail, Google Drive, and Google Calendar.

Workflow Steps:
1. VIP Attendance & Event Lookup (Gmail & Google Calendar):
   Search Gmail for "[PARTNER TERRITORY ALERT] APCO 2026 Public Safety Summit" and check Google Calendar for "[APCO 2026] Motorola Territory Partner & VIP Customer Hospitality Reception" to identify attending VIP executives (Commissioner Marcus Vance, Colonel Elena Rostova, Director Henrik Lindqvist, Sheriff Dietrich Keller) and their active deal values ($3.85M, $5.2M, $1.95M).

2. Competitive Counter-Strategy Synthesis (Gmail & Google Drive):
   Search Gmail for "[COMPETITIVE INTELLIGENCE BRIEF - JACKY CHUI]" and read the Google Doc "[Motorola Competitive Intelligence] 2026 Deep Research Dossier" in Google Drive.
   Extract counter-positioning against:
   - Competitor A (Axon Enterprise): Counter Fleet 3 + body-worn camera SaaS discounting by highlighting Motorola's unified mission-critical ASTRO 25 voice + Avigilon Alta cloud video + CommandCentral Aware interoperability.
   - Competitor B (L3Harris): Counter 15% P25 radio hardware discounts by highlighting their FIPS 140-3 encryption chip supply chain delays.

3. Executive Briefing Generation:
   Produce a 1-page VIP Executive Dossier & Competitive Battlecard for Sahil Taank's team ahead of the Orlando APCO hospitality reception.
```

### 🧪 Test Prompt for Agent #4:
> *"Who are the VIP customers attending the APCO 2026 summit from Sahil Taank's Gmail alert, and how should we position Motorola against Axon and L3Harris during our Calendar hospitality reception based on Jacky Chui's Deep Research dossier in Drive?"*

---

## 🤖 Agent #5: HR/IT Service Delivery & High-Value Approval Orchestrator
- **Spreadsheet Business Owners**: **Apoorva** *(HR/IT Support)* & **Priyanka B** *(IT Ticket Analytics)*
- **Connected Apps Used**: **ServiceNow** + **Google Drive** + **Gmail** + **Google Calendar**

### Copy-Paste Prompt for Workflow Creator:
```text
Create an agent workflow named "HR & IT Service Delivery Approval Orchestrator" using ServiceNow, Google Drive, Gmail, and Google Calendar.

Workflow Steps:
1. Ticket & Cost Inspection (ServiceNow):
   When asked about an employee hardware/software request or approval (such as REQ0010881 or INC0010001), query ServiceNow to retrieve the requester (David Katimi), cost center (CC-4402), itemization ($3,200 Ruggedized Field RF Laptop w/ ASTRO 25 CPS interface + $1,650 CommandCentral AES-256 Key Loader license), and total cost ($4,850.00).

2. Escalation Policy Verification (Google Drive):
   Read the Google Doc "[Motorola HR & IT Service Delivery] Global Employee Support, Hardware/Software Escalation & ServiceNow Approval Policy" in Google Drive. Verify that requests exceeding the $2,500 auto-approval threshold require Engineering Manager approval and valid mission-critical deployment justification.

3. Approval Notification & Sync (Gmail & Google Calendar):
   Search Gmail for "[ACTION REQUIRED: ServiceNow Approval REQ0010881]" and check Google Calendar for "[HR/IT SERVICE DELIVERY SYNC]".
   Generate a compliance verification summary confirming that David Katimi's City of Metro District 4 emergency deployment justification satisfies HR/IT policy, and draft the manager approval confirmation to transition ServiceNow ticket INC0010001 to "Approved / In Progress".
```

### 🧪 Test Prompt for Agent #5:
> *"Review ServiceNow request REQ0010881 (INC0010001) for David Katimi's $4,850 ruggedized RF laptop. Does it comply with our HR/IT escalation policy in Drive, and what action is needed on the Gmail approval thread?"*
