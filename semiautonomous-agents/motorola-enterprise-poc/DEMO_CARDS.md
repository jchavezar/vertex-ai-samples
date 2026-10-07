# 🚀 Motorola Solutions — Gemini Enterprise POC Demo Script & Cards

**Local File URI:** `file:///Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/motorola-enterprise-poc/DEMO_CARDS.md`

---

## 📋 1. Customer 360 & Cross-Sell Agent (Workflow Agent — Row 19)
* **Agent Names in Gemini Enterprise:**
  * Workflow 1: `MSI Cross-Silo Account 360 & Renewal Risk` (ID: `9292006299939784738`)
  * Workflow 2: `Customer 360 and cross-sell agent` (ID: `4266057264553488023`)
* **Business Owner:** David Katimi (Sales Ops / Account Management)
* **Connectors:** Salesforce CRM (`soqlQuery`) + ServiceNow ITSM (`incident`) + Google Drive (`ASTRO 25 Playbook`)

### 🎙️ Full Business Speech (45 Seconds — Executive Pitch)
> *"At Motorola Solutions, our biggest threat to contract renewals isn’t competitor pricing—it’s siloed data. Today, an Account Executive preparing for a $2M public safety renewal meeting has to manually check three disconnected systems: Salesforce for the contract stage, ServiceNow to see if the dispatch center has open support tickets, and Google Drive to find approved product cross-sell playbooks. If an AE walks into that renewal meeting unaware that the customer is suffering a Priority-1 radio outage right now, we lose the deal.*
>
> *This Customer 360 & Cross-Sell Workflow Agent eliminates that blind spot in under 10 seconds. When I enter an account like **Miami-Dade**, Gemini Enterprise simultaneously queries all three silos in parallel:*
> 1. *First, it pulls the live **$1.95M ASTRO 25 renewal** from Salesforce CRM (`006jV000001CIWrQAO`).*
> 2. *Second, it audits ServiceNow ITSM and immediately flags active **Priority-1 Incident `INC0010007`**—trunked RF packet loss on Repeater Site 4.*
> 3. *Third, instead of just warning the AE, it cross-references our Google Drive product playbooks to turn that technical outage into a strategic upsell: recommending **APX NEXT Smart Radios** with automatic LTE broadband failover to solve the RF dead zone, paired with a pre-approved **20% executive retention discount**.*
>
> *In one click, we turn a high-risk churn event into a proactive, data-grounded cross-sell proposal."*

### ⚡ Short 1-Paragraph Business Speech (20 Seconds)
> *"Account Executives lose renewals when they walk into customer meetings blind to active support outages. This Customer 360 & Cross-Sell Agent connects Salesforce, ServiceNow, and Google Drive in parallel: when we type **Miami-Dade**, it pulls the $1.95M renewal from Salesforce (`006jV000001CIWrQAO`), detects a live P1 radio packet-loss incident in ServiceNow (`INC0010007`), and automatically matches it to our Google Drive playbooks to pitch APX NEXT LTE-failover radios with a 20% retention override discount—turning churn risk into immediate expansion revenue."*

---

### 💬 Live Test Inputs to Run

#### **Option A: Primary Test Input (`Miami-Dade`)**
* **Type in Test / Chat:**
  ```text
  Miami-Dade
  ```
  *(or in Main Chat: `Start the workflow: Miami-Dade`)*
* **What to Point Out on Screen:**
  * **Salesforce Citation:** Opportunity ID **`006jV000001CIWrQAO`** | Value: **`$1,950,000.00`** | Stage: `Negotiation/Review` | Close Date: `2026-10-15`
  * **ServiceNow Citation:** Incident **`INC0010007`** | Priority: **`1 - Critical`** | `[INC0010999] P1 Critical: Miami-Dade ASTRO 25 Repeater Site 4 RF Packet Loss`
  * **Google Drive Citation:** `ASTRO 25 Telemetry & Video Cross-Sell Playbook` | Upsell: **APX NEXT Smart Radios (LTE/Wi-Fi failover)** + **CommandCentral Aware** | Incentive: **20% Executive Override Discount**

#### **Option B: Secondary Test Input (`City of Metro`)**
* **Type in Test / Chat:**
  ```text
  City of Metro
  ```
* **What to Point Out on Screen:**
  * **Salesforce Citation:** Opportunity ID **`001jV000009Im4DQAS`** (`$3.85M` / `$2.6M`)
  * **ServiceNow Citation:** Incident **`INC0010002`** | Priority: **`1 - Critical`** | `[INC0010942] P1 Critical: City of Metro ASTRO 25 Packet Loss`

---

## 📋 2. Contract Management & Renewals (Basic Agent — Row 5)
* **Agent Name:** `Motorola Contract Renewals & Pipeline Advisor` (ID: `8517176328388284078`)
* **Business Owner:** David Katimi (Sales / Operations)
* **Integration / Connector:** Salesforce Hosted MCP (`soqlQuery`)

### 🎙️ Business Speech (15–20 Seconds)
> *"For our Account Executives and Renewal Managers, finding contract expiration dates, deal amounts, and renewal stages across CRM silos usually requires multiple custom reports. With Gemini Enterprise, we've connected Salesforce directly to this conversational agent so reps can audit high-value public safety renewals in seconds."*

### 💬 Test Prompts to Copy-Paste
1. **Specific Account Deep Dive:**
   ```text
   What is the current renewal status and contract size for the Miami-Dade Dispatch deal in Salesforce?
   ```
2. **Portfolio Pipeline Overview:**
   ```text
   List all our active public safety renewal opportunities in Salesforce over $1.5M with their amounts and target close dates.
   ```
