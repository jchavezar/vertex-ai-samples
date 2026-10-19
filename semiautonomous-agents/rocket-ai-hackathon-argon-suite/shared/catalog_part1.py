# -*- coding: utf-8 -*-
"""Part 1 of the Rocket AI Hackathon Catalog: Domains 1 (Origination), 2 (Underwriting), 3 (Servicing)."""

CLOUD_RUN_URLS = {
    "portal": "https://rocket-hackathon-portal-254356041555.us-central1.run.app",
    "sales": "https://rocket-demo-origination-254356041555.us-central1.run.app",
    "ops": "https://rocket-demo-underwriting-254356041555.us-central1.run.app",
    "servicing": "https://rocket-demo-servicing-254356041555.us-central1.run.app",
    "marketing": "https://rocket-demo-marketing-254356041555.us-central1.run.app",
    "risk": "https://rocket-demo-compliance-254356041555.us-central1.run.app",
    "sdlc": "https://rocket-demo-sdlc-254356041555.us-central1.run.app",
    "moonshots": "https://rocket-demo-moonshots-254356041555.us-central1.run.app",
}

DOMAINS_PART1 = [
    {
        "id": "sales",
        "service_name": "rocket-demo-origination",
        "demo_url": CLOUD_RUN_URLS["sales"],
        "shortTitle": "1. Loan Origination & Sales",
        "fullTitle": "1. Loan Origination & Mortgage Banking (Rocket Mortgage Production & Pro TPO)",
        "themeName": "Rocket Pro TPO & Banker Velocity Terminal (Bloomberg FinTech Dark UI)",
        "mission": "Maximize banker conversion, accelerate speed-to-quote under 1.5s, automate Salesforce/LOS logging, and convert Redfin & Rocket Money leads with Gemini 4 Argon.",
        "awsWinback": "Replaces high-latency AWS Bedrock Claude 3.7 prompt chains with Gemini 4 Argon native Function Calling, Context Caching (75% lower TCO), and Gemini Enterprise M365/Outlook connectors.",
        "projects": [
            {
                "code": "1.1",
                "level": "L100",
                "tags": ["L100"],
                "tool": "Gemini 4 Argon + Prompt Framework",
                "project": "The ABCDQ Post-Call Structured Debriefer",
                "focus": "Persona-Task-Context-Format prompting to turn messy banker intake notes into DTI/LTV calculations, CRM JSON, and Outlook follow-ups.",
                "desc": "Paste messy intake call shorthand from a first-time Detroit/Oakland County homebuyer into Gemini 4 Argon. Instantly outputs a structured 1003 pre-qualification summary (DTI, LTV, qualifying income, reserve check), a Salesforce CRM payload, and an empathetic borrower action checklist.",
                "url": "https://www.skills.google/collections/ai-boost-bites",
                "serviceText": "Vertex AI Gemini 4 Argon & Gemini Enterprise",
                "serviceUrl": "https://cloud.google.com/vertex-ai",
                "gcpStack": ["Gemini 4 Argon (gemini-4-argon)", "Gemini Enterprise Prompt Canvas", "Cloud Run"],
                "competeEdge": "Beats ChatGPT Enterprise & Bedrock Claude by combining deterministic mortgage math verification with zero-retention GCP data governance.",
                "sampleInput": """Caller: Marcus & Elena Vance (First-time buyers, currently renting in Royal Oak MI for $2,350/mo).
Target property found on Redfin: 1420Vinsetta Blvd, Royal Oak, MI 48067 — List Price $460,000.
Income: Marcus is Sr. Mechanical Eng at Ford ($118,000 base + $14k annual bonus last 2 yrs). Elena is RN at Corewell Health ($86,000 base + ~$9,500 overtime).
Assets: $52,000 in Rocket Money Down Payment Vault + $18,000 in Fidelity 401k.
Debts: $410/mo auto loan (Ford F-150), $280/mo student loans, $95/mo min credit card.
Credit: Middle FICO scores 748 (Marcus) / 762 (Elena). Looking to put 10% down ($46k) and keep closing reserves. Concerned about monthly payment staying under $3,400/mo.""",
                "sandboxAction": "calc_1003_dti",
                "sandboxParams": {"price": 460000, "down_pct": 10, "base_income_annual": 204000, "bonus_ot_annual": 23500, "monthly_debts": 785, "rate": 6.125, "fico": 748},
                "systemPrompt": "You are the Rocket Mortgage ABCDQ Post-Call Structured Debriefer powered by Gemini 4 Argon. Analyze the banker's raw intake notes and produce: (1) Executive 1003 Pre-Qualification Summary (Qualifying Monthly Income separating Base vs. 24-month averaged Bonus/Overtime, Front-End & Back-End DTI, LTV, Reserve Cushion), (2) Ready-to-log Salesforce/LOS JSON block, and (3) A warm, reassuring Outlook email draft to the borrowers with their exact next-step document checklist.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│           1.1 ABCDQ POST-CALL STRUCTURED DEBRIEFER (L100)              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Banker Intake Notes / Rocket Logic Synopsis Transcript]              │
│  • Raw shorthand: Income, FICO, Redfin Address, Rocket Money Vault     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini Enterprise / Vertex AI: gemini-4-argon (Global Endpoint)]     │
│  • Persona-Task-Context-Format System Guardrail                        │
│  • Sandboxed DTI / LTV / PITI + PMI Verification Engine                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [3 Standardized Deliverables]                                         │
│  ├─► 1. 1003 Pre-Qual Summary (Front/Back DTI, Reserve Sufficiency)    │
│  ├─► 2. Salesforce / Encompass LOS Structured JSON Payload             │
│  └─► 3. O365 Outlook Ready-to-Send Borrower Follow-Up & Checklist      │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Enable Vertex AI API in your GCP project: `gcloud services enable aiplatform.googleapis.com run.googleapis.com --project=vtxdemos`",
                    "Call the global `gemini-4-argon` endpoint using `google-genai` SDK with the Persona-Task-Context-Format system instruction.",
                    "Attach the Python DTI/LTV calculation verifier tool so all dollar figures (P&I, PMI, Taxes, Front/Back DTI) are 100% mathematically verified before rendering the Outlook draft.",
                    "Deploy the banker frontend to Cloud Run with `--no-allow-unauthenticated` or basic auth middleware."
                ],
                "codeSnippet": """from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project="vtxdemos", location="global")
response = client.models.generate_content(
    model="gemini-4-argon",
    contents=raw_banker_notes,
    config=types.GenerateContentConfig(
        system_instruction="You are a Senior Rocket Mortgage Executive Banker Co-Pilot...",
        temperature=0.2,
    ),
)
print(response.text)"""
            },
            {
                "code": "1.2",
                "level": "L100–L200",
                "tags": ["L100", "L200"],
                "tool": "Gemini Code Assist & O365 Add-In",
                "project": "Outlook Hyper-Personalized Rate-Lock & Pre-Approval Agent",
                "focus": "Compile personalized Rocket Verified Approval letters & Excel closing-cost tables directly inside an O365 Outlook compose workflow.",
                "desc": "Generate a tailored Rocket Mortgage Verified Approval Letter and 3-option Rate-Lock comparison table inside an Outlook-style compose window referencing the exact Redfin property address, seller agent, and local Oakland County millage taxes.",
                "url": "https://cloud.google.com/products/gemini/code-assist",
                "serviceText": "Gemini Code Assist & Vertex AI Argon",
                "serviceUrl": "https://cloud.google.com/products/gemini/code-assist",
                "gcpStack": ["Gemini 4 Argon", "Gemini Code Assist", "Microsoft Graph / Outlook MCP"],
                "competeEdge": "Outperforms Microsoft 365 Copilot in Outlook by pulling live Rocket pricing engine tiers and computing exact county transfer taxes without hallucinating fee buckets.",
                "sampleInput": """Property: 892 Puritan Ave, Birmingham, MI 48009 (Listing Agent: Sarah Jenkins, @properties).
Offer Price: $625,000 | Down Payment: 20% ($125,000) | Loan Amount: $500,000 | 30-Yr Fixed Conventional.
Borrowers: Dr. Priya Nair &ohan Nair | Middle FICO: 785.
Options to Compare:
- Option A: Par Rate 6.125% (0.00 pts)
- Option B: Rate-Lock w/ 0.75 pt Buydown -> 5.875% ($3,750 cost)
- Option C: Rocket 2-1 Temporary Buydown (Year 1: 4.125%, Year 2: 5.125%, Year 3-30: 6.125%, Seller Concession funded)
Closing Date Target: November 24, 2026 (21-day Rocket Fast Track Close).""",
                "sandboxAction": "calc_rate_lock_options",
                "sandboxParams": {"loan_amount": 500000, "price": 625000, "base_rate": 6.125, "buydown_rate": 5.875, "buydown_pts": 0.75},
                "systemPrompt": "You are the Rocket Mortgage O365 Outlook Rate-Lock & Verified Approval Drafter powered by Gemini 4 Argon. Generate: (1) A formal, seller-winning 'Rocket Verified Approval Letter' addressed to the listing agent highlighting Rocket's 21-day closing guarantee, and (2) A borrower-facing Outlook email with a clean Markdown/Excel table comparing Options A (Par), B (Permanent Buydown with breakeven month calculation), and C (2-1 Seller-Paid Buydown).",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│      1.2 OUTLOOK RATE-LOCK & PRE-APPROVAL AGENT (L100-L200)            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [O365 Outlook Add-In / Compose Pane]                                  │
│  • Property Address, Listing Agent, Loan Amount, 3 Rate Options        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Sandboxed Breakeven & PITI Engine + Gemini 4 Argon]                  │
│  • Computes exact P&I, Buydown Cost, Monthly Savings, Breakeven Month  │
│  • Generates Seller-Facing Verified Approval + Buyer Comparison Grid   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Outlook Rich HTML Email + Copy-Paste Excel Table]                    │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Use Gemini Code Assist in VS Code or Antigravity IDE to scaffold the O365 Outlook Web Add-in manifest (`manifest.xml`) and FastAPI backend.",
                    "Connect the backend to `gemini-4-argon` on Vertex AI to synthesize both the Listing Agent Verified Approval certificate and the Borrower 3-Scenario Comparison Table.",
                    "Run the sandboxed amortization calculator so breakeven months (Upfront Points Cost / Monthly P&I Savings) are exact."
                ],
                "codeSnippet": """# Breakeven + Outlook Pre-Approval Generator with Gemini 4 Argon
def calc_payment(principal, annual_rate):
    r = (annual_rate / 100) / 12
    return principal * (r * (1 + r)**360) / ((1 + r)**360 - 1)

p_par = calc_payment(500000, 6.125)
p_buy = calc_payment(500000, 5.875)
breakeven_months = round(3750 / (p_par - p_buy), 1)"""
            },
            {
                "code": "1.3",
                "level": "L100–L200",
                "tags": ["L100", "L200"],
                "tool": "Gemini Enterprise (Sobi Spark) Workplace Agent",
                "project": "No-Code Mortgage Guideline & Competitor Battlecard Agent",
                "focus": "Grounded Gemini Enterprise workplace agent integrated with Microsoft Teams to answer FHA/VA/Conventional guidelines & UWM/Pennymac battlecards.",
                "desc": "Answer complex banker eligibility scenarios (e.g., 640 FICO with 5% down, non-occupant co-borrower, recent student loan IBR) in seconds with exact credit matrix overlays, reserve rules, and live competitive counter-points.",
                "url": "https://cloud.google.com/products/gemini-enterprise",
                "serviceText": "Gemini Enterprise (Sobi / Spark) & Agent Registry",
                "serviceUrl": "https://cloud.google.com/products/gemini-enterprise",
                "gcpStack": ["Gemini Enterprise (global-gemini-enterprise)", "SharePoint / OneDrive 3LO Connector", "Gemini 4 Argon"],
                "competeEdge": "Queries Rocket's SharePoint & Fannie/Freddie PDFs in-place via Sobi 3-object MCP Registry (`McpServer`, `AuthProvider`, `AuthBinding`) with full ACL inheritance—zero AWS S3 data duplication.",
                "sampleInput": """Banker Question in Microsoft Teams:
"I have a borrower in Macomb County buying a $380,000 single-family home with 5% down ($19,000). Middle FICO is 642. Debt-to-income is 46.5%. Part of the down payment ($8,000) is a gift from an aunt, and they are comparing our quote against a local wholesale broker pitching UWM Conventional 95%.
1) Should we structure this as Fannie Mae HomeReady (620+ FICO, <80% AMI) or FHA 3.5% down?
2) How does MI (Mortgage Insurance) compare between Conventional at 642 FICO vs FHA MIP (0.55% annual)?
3) Give me 3 crisp battlecard talking points to win this deal today over the competing broker." """,
                "sandboxAction": "calc_fha_vs_conv",
                "sandboxParams": {"price": 380000, "fico": 642, "dti": 46.5, "down_pct_conv": 5.0, "down_pct_fha": 3.5},
                "systemPrompt": "You are the Gemini Enterprise (Sobi Spark) Mortgage Guideline & Battlecard Agent for Rocket Mortgage. Ground your answer in Fannie Mae Selling Guide (B3-5.1-01, HomeReady B5-6-01), HUD 4000.1 FHA Handbook, and Rocket's Competitive Battlecard vs. Wholesale Brokers. Provide: (1) Exact Side-by-Side Eligibility & Monthly Payment/MI comparison (Fannie HomeReady vs. Standard Conv vs. FHA), (2) Gift Fund documentation rules (Donor ability + Wire transfer trail), and (3) 3 High-Impact Banker Battlecard talking points (Rocket Money integration, Mr. Cooper/Rocket retained servicing vs. broker servicing flip, and Rocket Close certainty).",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│       1.3 GEMINI ENTERPRISE GUIDELINE & BATTLECARD AGENT (L100-200)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Microsoft Teams / Gemini Enterprise Web (/work/cid/<CID>)]           │
│  • Banker asks eligibility + competitor battlecard question            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini Enterprise Sobi Runtime + Agent Registry]                     │
│  ├─► McpServer: SharePoint Product Matrix & Selling Guides             │
│  ├─► AuthProvider & AuthBinding: 3LO Entra ID / O365 ACL Enforcement   │
│  └─► Model: gemini-4-argon with Paragraph-Level Grounding Citations    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Grounded Matrix Comparison + FHA vs Conv Math + Winning Battlecard]  │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "In Google Cloud Console -> Gemini Enterprise (`collections/default_collection/engines/global-gemini-enterprise`), connect your SharePoint Online or Cloud Storage datastore containing Rocket Product Matrices & Fannie/Freddie Guides.",
                    "Create a No-Code Custom Agent in Gemini Enterprise Agent Studio with system instructions enforcing citation tags and FHA vs. Conventional payment comparisons.",
                    "Publish the agent to Microsoft Teams via the Gemini Enterprise M365 extension binding."
                ],
                "codeSnippet": """# Querying Gemini Enterprise StreamAssist / Sobi Agent via Discovery Engine API
import requests, google.auth
from google.auth.transport.requests import Request

creds, _ = google.auth.default()
creds.refresh(Request())
url = "https://discoveryengine.googleapis.com/v1alpha/projects/vtxdemos/locations/global/collections/default_collection/engines/global-gemini-enterprise/assistants/default_assistant:streamAssist"
payload = {"query": {"text": banker_question}}
resp = requests.post(url, headers={"Authorization": f"Bearer {creds.token}"}, json=payload)"""
            },
            {
                "code": "1.4",
                "level": "L200–L300",
                "tags": ["L200", "L300"],
                "tool": "Gemini 4 Argon: Native Function Calling",
                "project": "Dynamic Loan Pricing & Amortization Co-Pilot",
                "focus": "Connect Gemini 4 Argon to live pricing engine APIs, LLPAs, county tax tables, and amortization tools in <1.5 seconds.",
                "desc": "Invoke `fetch_live_rates(zip_code, ltv, fico, loan_amount, loan_purpose)` and `compute_amortization_schedule()` dynamically. Computes Fannie Mae LLPAs, monthly P&I, county property tax, PMI, and 5-year equity buildup in a single turn.",
                "url": "https://ai.google.dev/gemini-api/docs/function-calling",
                "serviceText": "Vertex AI Gemini 4 Argon Function Calling",
                "serviceUrl": "https://cloud.google.com/vertex-ai",
                "gcpStack": ["Gemini 4 Argon", "Gemini 3.8 Flash", "Vertex AI Function Calling", "Cloud Run Pricing Microservice"],
                "competeEdge": "Gemini 4 Argon + 3.8 Flash parallel tool-calling executes multi-tool pricing + LLPA + tax lookups 2.4x faster than AWS Bedrock Claude 3.7 Sonnet.",
                "sampleInput": """Quote a client purchasing a $540,000 single-family home in Oakland County, MI (ZIP 48009) with 10% down ($486,000 loan amount, 90% LTV) and a 742 middle FICO score.
Also compare what happens if they use $27,000 more from their Rocket Money savings to reach 85% LTV ($459,000 loan amount) — show the exact LLPA adjustment, PMI drop, monthly PITI difference, and 5-year cumulative interest saved.""",
                "sandboxAction": "calc_dynamic_pricing",
                "sandboxParams": {"price": 540000, "zip": "48009", "fico": 742, "ltv_1": 90.0, "ltv_2": 85.0},
                "systemPrompt": "You are the Rocket Dynamic Loan Pricing & Amortization Co-Pilot powered by Gemini 4 Argon Function Calling. Use the live pricing & amortization tool results to present: (1) Live Rate Sheet & Fannie Mae LLPA breakdown for 90% LTV vs. 85% LTV at 742 FICO in Oakland County (48009), (2) Complete Monthly PITI + PMI breakdown table, and (3) 60-Month (5-Year) Equity & Interest Savings recommendation.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│       1.4 DYNAMIC LOAN PRICING & AMORTIZATION CO-PILOT (L200-L300)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Banker Natural Language Query]                                       │
│  "Quote $540k purchase in 48009 at 90% vs 85% LTV, 742 FICO"           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini 4 Argon Parallel Function Calling Router]                     │
│  ├─► Tool 1: fetch_live_rates(zip="48009", ltv=90, fico=742)           │
│  ├─► Tool 2: fetch_live_rates(zip="48009", ltv=85, fico=742)           │
│  └─► Tool 3: compute_amortization_60m(loan_a, loan_b)                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Verified PITI + PMI + LLPA Breakdown Table & 5-Yr Equity Chart]      │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Define Python functions `fetch_live_rates(zip_code: str, ltv: float, fico: int, loan_amount: float)` and `compute_amortization_60m(...)` with docstrings and type annotations.",
                    "Pass the Python functions directly into `types.GenerateContentConfig(tools=[fetch_live_rates, compute_amortization_60m])` with `model='gemini-4-argon'`.",
                    "Gemini 4 Argon automatically emits parallel `FunctionCall` parts, executes the deterministic pricing formulas, and synthesizes the side-by-side comparison."
                ],
                "codeSnippet": """def fetch_live_rates(zip_code: str, ltv: float, fico: int, loan_amount: float) -> dict:
    \"\"\"Fetches Rocket live rate sheet, Fannie Mae LLPA, PMI, and local millage tax.\"\"\"
    base_rate = 5.990 if fico >= 740 else 6.250
    llpa_pts = 0.250 if ltv == 90 else 0.125
    pmi_factor = 0.0041 if ltv == 90 else 0.0024
    return {"rate": base_rate, "llpa_points": llpa_pts, "monthly_pmi": round(loan_amount * pmi_factor / 12, 2)}

response = client.models.generate_content(
    model="gemini-4-argon",
    contents=prompt,
    config=types.GenerateContentConfig(tools=[fetch_live_rates])
)"""
            },
            {
                "code": "1.5",
                "level": "L300",
                "tags": ["L300"],
                "tool": "Google Antigravity IDE + Sandbox + MCP",
                "project": "Autonomous Banker Inbound Triage & Calendar Booking Suite",
                "focus": "Multi-agent Antigravity workflow that ingests Redfin/RocketMortgage.com webhooks, queries O365 Calendar MCP, scores lead urgency, and provisions a 1003 sandbox draft.",
                "desc": "Ingest live webhook events when a homebuyer books a Redfin tour or completes a Rocket Money readiness check, verify NMLS state licensing & banker availability via Outlook Calendar MCP, and auto-provision the complete borrower profile.",
                "url": "https://antigravity.google",
                "serviceText": "Google Antigravity 2.0 & MCP Server Registry",
                "serviceUrl": "https://antigravity.google",
                "gcpStack": ["Google Antigravity 2.0", "Antigravity gVisor Sandbox", "MCP Server (O365 Calendar + Redfin Lead Webhook)", "Gemini 4 Argon"],
                "competeEdge": "Directly replaces Anthropic Claude Code + custom glue scripts with Antigravity's enterprise-governed Managed Agents API, native MCP harness, and VPC-SC sandboxed execution.",
                "sampleInput": """{
  "event_type": "REDFIN_TOUR_BOOKED_HIGH_INTENT",
  "timestamp": "2026-10-13T17:35:00Z",
  "borrower": {
    "name": "Devon & Chloe Brooks",
    "email": "dbrooks@gmail.com",
    "state": "MI",
    "fico_soft_pull": 774,
    "rocket_money_linked_liquid_assets": 94500,
    "verified_annual_income": 215000
  },
  "redfin_property": {
    "mls_id": "MI-202609841",
    "address": "315 S Main St #402, Ann Arbor, MI 48104",
    "list_price": 585000,
    "scheduled_tour_utc": "2026-10-15T21:00:00Z",
    "pre_approval_status": "NONE_YET"
  }
}""",
                "sandboxAction": "triage_inbound_webhook",
                "sandboxParams": {"fico": 774, "assets": 94500, "income": 215000, "list_price": 585000, "state": "MI"},
                "systemPrompt": "You are the Google Antigravity Autonomous Inbound Triage & Banker Routing Orchestrator powered by Gemini 4 Argon. Process the incoming Redfin/Rocket Money webhook payload and output: (1) Lead Conversion Urgency Score (0-100) & Pre-Approval Readiness Audit (must book banker BEFORE their Oct 15 Redfin tour!), (2) MCP Tool Execution Log matching the highest-converting Michigan NMLS-licensed Senior Banker with an open O365 Calendar slot, and (3) The provisioned 1003 Sandbox Profile JSON + SMS/Calendar Invite dispatched to the borrower.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│     1.5 ANTIGRAVITY INBOUND TRIAGE & CALENDAR BOOKING SUITE (L300)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Inbound Webhook: Redfin Tour Booked + Rocket Money Asset Link]       │
│  • Buyer touring $585k Ann Arbor home in 48 hrs with NO pre-approval   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Google Antigravity Multi-Agent Harness (Gemini 4 Argon)]             │
│  ├─► Subagent 1: Lead Scorer & Sandbox DTI/Asset Pre-Check             │
│  ├─► Subagent 2: MCP Call -> nmls_roster_lookup(state="MI")            │
│  └─► Subagent 3: MCP Call -> o365_calendar_book_slot(banker_id)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Provisioned 1003 Draft + Booked O365 Meeting + SMS Pre-Tour Alert]   │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Register the O365 Calendar & NMLS Roster MCP server in `~/.gemini/antigravity/mcp_config.json` (or Gemini Enterprise Agent Registry).",
                    "Use the Antigravity CLI (`agy`) or ADK orchestrator with `gemini-4-argon` to wire the 3-step pipeline: Webhook Validator -> NMLS/Calendar MCP Lookup -> 1003 Sandbox Provisioner.",
                    "Deploy the webhook triage service to Cloud Run."
                ],
                "codeSnippet": """// ~/.gemini/antigravity/mcp_config.json
{
  "mcpServers": {
    "rocket-o365-calendar": {
      "command": "python3",
      "args": ["/app/mcp_servers/o365_calendar_mcp.py"],
      "env": {"ROCKET_TENANT_ID": "rocket-ms365-prod"}
    }
  }
}"""
            }
        ]
    },
    {
        "id": "ops",
        "service_name": "rocket-demo-underwriting",
        "demo_url": CLOUD_RUN_URLS["ops"],
        "shortTitle": "2. Ops, Underwriting & Closing",
        "fullTitle": "2. Operations, Underwriting & Closing (Rocket Logic Fulfillment & Rocket Close Title)",
        "themeName": "Rocket Logic Underwriting Workbench & Document AI Lightbox (Executive Slate Paper-Audit UI)",
        "mission": "Ingest and validate unstructured borrower documents (W-2s, Paystubs, 1040 Schedule C, Bank Statements, Title Commitments), compute Fannie Mae Form 1084 income, and clear conditions 10x faster.",
        "awsWinback": "Replaces fragile AWS Textract + Bedrock post-processing scripts with Google Cloud Document AI specialized mortgage processors + Gemini 4 Argon 2M-token strict Pydantic JSON schemas and Vertex AI Policy Grounding.",
        "projects": [
            {
                "code": "2.1",
                "level": "L100–L200",
                "tags": ["L100", "L200"],
                "tool": "NotebookLM Enterprise & Vertex Grounding",
                "project": "Fannie Mae / Freddie Mac Selling Guide Citation Assistant",
                "focus": "Ingest Fannie Mae B3-3.1 & Freddie Mac Chapter 5300 manuals to verify complex RSU, seasonal bonus, and overtime income with exact paragraph citations.",
                "desc": "Query Fannie Mae and Freddie Mac guidelines in natural language when underwriting complex variable income (RSUs, variable overtime, 1099 transitions) and receive exact calculation formulas with clickable paragraph-level citations.",
                "url": "https://notebooklm.google/",
                "serviceText": "NotebookLM Enterprise & Vertex AI Grounding",
                "serviceUrl": "https://cloud.google.com/agentspace/notebooklm-enterprise",
                "gcpStack": ["NotebookLM Enterprise", "Vertex AI Search & Grounding", "Gemini 4 Argon"],
                "competeEdge": "Delivers zero-hallucination inline paragraph citations and Audio Overviews for underwriter training, beating Claude Projects' context window limits on 1,400-page GSE selling guides.",
                "sampleInput": """Underwriter Scenario #UW-88412:
Borrower is a Principal Software Engineer at a publicly traded tech company (NYSE: NOW) applying for a Conventional Conforming loan.
1) Base Salary: $165,000/yr.
2) Restricted Stock Units (RSUs): Vested $48,000 in 2024 and $62,000 in 2025. Employer stock is publicly traded; borrower has 180 unvested shares vesting quarterly over the next 24 months.
3) Annual Performance Bonus: Received $22,000 in 2024, but drop to $14,000 in 2025 (>20% year-over-year decline).
Question: Under Fannie Mae Selling Guide B3-3.1-01 and B3-3.1-09, how must the underwriter calculate the monthly qualifying RSU income and the declining annual bonus income, and what exact documentation is required?""",
                "sandboxAction": "calc_gse_variable_income",
                "sandboxParams": {"base_annual": 165000, "rsu_yr1": 48000, "rsu_yr2": 62000, "bonus_2024": 22000, "bonus_2025": 14000},
                "systemPrompt": "You are the Rocket Underwriting Fannie Mae / Freddie Mac Selling Guide Citation Assistant powered by Gemini 4 Argon. Answer the underwriter's question with: (1) Exact Paragraph-Level Citations (`[Fannie Mae B3-3.1-01]`, `[Fannie Mae B3-3.1-09]`, `[Freddie Mac Section 5303.4]`), (2) Step-by-step Qualifying Monthly Income calculation table (highlighting why the declining 2025 bonus of $14,000 cannot be averaged up with 2024 unless documented as a one-time anomaly), and (3) Underwriting Condition Checklist required to clear.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│      2.1 FANNIE MAE / FREDDIE MAC SELLING GUIDE ASSISTANT (L100-200)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Underwriter Complex Income Query: RSUs + Declining YoY Bonus]        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Vertex AI Grounding Datastore / NotebookLM Enterprise Corpus]        │
│  ├─► Fannie Mae Selling Guide (Part B3-3: Income Assessment)           │
│  ├─► Freddie Mac Single-Family Seller/Servicer Guide (Ch. 5300)        │
│  └─► Rocket Logic Internal Underwriting Overlay Bulletins              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Cited Underwriting Memo + Verified Monthly Qualifying Income Math]   │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Upload the Fannie Mae Selling Guide PDF and Freddie Mac Seller/Servicer Guide into a NotebookLM Enterprise notebook or Vertex AI Search unstructured datastore.",
                    "Configure `gemini-4-argon` with Vertex AI Grounding (`types.Tool(retrieval=...)`) so every response includes grounded `grounding_chunks` and paragraph citations.",
                    "Pair with the deterministic GSE income calculator to flag YoY declining variable income (`>10%` drop uses lower most-recent year)."
                ],
                "codeSnippet": """# Grounded Fannie/Freddie Underwriting Query with Vertex AI Search + Gemini 4 Argon
datastore_path = "projects/vtxdemos/locations/global/collections/default_collection/dataStores/gse-selling-guides"
response = client.models.generate_content(
    model="gemini-4-argon",
    contents=underwriter_query,
    config=types.GenerateContentConfig(
        tools=[types.Tool(retrieval=types.Retrieval(vertex_ai_search=types.VertexAISearch(datastore=datastore_path)))]
    )
)"""
            },
            {
                "code": "2.2",
                "level": "L200",
                "tags": ["L200"],
                "tool": "Gemini Enterprise Agent Platform (GEAP): Agent Studio",
                "project": "Low-Code Underwriting Condition Clearing & Large-Deposit Agent",
                "focus": "Cross-check borrower bank statements against the 1003 loan application, flag unverified deposits >50% of qualifying income, and stage LOE conditions.",
                "desc": "Visually orchestrate an underwriting agent that scans 60 days of bank statements against Fannie Mae B3-4.2-02 Large Deposit rules (50% of total monthly qualifying income threshold) and stages a one-click Letter of Explanation (LOE) request.",
                "url": "https://cloud.google.com/products/gemini-enterprise-agent-platform",
                "serviceText": "Gemini Enterprise Agent Platform (GEAP)",
                "serviceUrl": "https://cloud.google.com/products/gemini-enterprise-agent-platform",
                "gcpStack": ["GEAP Agent Studio", "Gemini 4 Argon", "Cloud Run Condition Engine"],
                "competeEdge": "Gives Rocket Operations business analysts a low-code visual canvas with built-in HITL (Human-in-the-Loop) CEL policy gates (`RUNTIME_STAGE_BLOCKING`), which AWS Bedrock Flows lacks.",
                "sampleInput": """Loan Application #RKT-992041 (Conventional Purchase — Qualifying Monthly Income: $11,400/mo -> 50% Large Deposit Threshold = $5,700.00):
Chase Checking Account #...4491 (Statement Period: Aug 15 – Oct 14, 2026):
- 09/01/2026: ACH Payroll Direct Deposit - General Motors Corp: +$3,850.00
- 09/08/2026: Wire Transfer In - "COINBASE INC WITHDRAWAL": +$18,500.00
- 09/15/2026: ACH Payroll Direct Deposit - General Motors Corp: +$3,850.00
- 09/22/2026: Counter Deposit - Check #1042 (No memo): +$7,200.00
- 10/01/2026: ACH Payroll Direct Deposit - General Motors Corp: +$3,850.00
- 10/04/2026: Zelle Transfer From "M. Thompson": +$1,200.00
Funds required for closing + reserves: $44,000. Current Ending Balance: $51,200.""",
                "sandboxAction": "audit_large_deposits",
                "sandboxParams": {"qualifying_monthly_income": 11400, "ending_balance": 51200, "funds_needed": 44000, "deposits": [
                    {"date": "2026-09-01", "desc": "ACH Payroll - General Motors", "amount": 3850, "type": "PAYROLL"},
                    {"date": "2026-09-08", "desc": "Wire In - COINBASE INC WITHDRAWAL", "amount": 18500, "type": "CRYPTO_WIRE"},
                    {"date": "2026-09-22", "desc": "Counter Deposit - Check #1042", "amount": 7200, "type": "UNVERIFIED_CHECK"},
                    {"date": "2026-10-04", "desc": "Zelle Transfer - M. Thompson", "amount": 1200, "type": "ZELLE"}
                ]},
                "systemPrompt": "You are the GEAP Underwriting Condition Clearing Agent powered by Gemini 4 Argon. Audit the borrower's 60-day bank ledger against Fannie Mae B3-4.2-02 (Large Deposits > 50% of qualifying monthly income = $5,700). Output: (1) Transaction-by-Transaction Audit Table flagging the $18,500 Coinbase Crypto Wire and $7,200 Check #1042, (2) Back-Out Sufficiency Calculation showing whether the borrower still has $44,000 if unverified deposits are backed out ($51,200 - $25,700 = $25,500 -> SHORTFALL of $18,500, meaning sourcing is MANDATORY), and (3) Auto-staged Underwriting Condition PTDF (Prior-to-Docs) + Borrower Letter of Explanation (LOE) template.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│     2.2 GEAP LOW-CODE UNDERWRITING CONDITION CLEARING AGENT (L200)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [60-Day Bank Statement Ledger + 1003 Qualifying Income ($11,400/mo)]  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [GEAP Agent Studio Workflow + Fannie Mae B3-4.2-02 Rule Engine]       │
│  ├─► Step 1: Compute 50% Threshold ($5,700.00)                         │
│  ├─► Step 2: Flag Non-Payroll Deposits > $5,700 (Crypto + Check)       │
│  └─► Step 3: Run Asset Back-Out Test & Stage PTDF Condition + LOE      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Processor Condition Queue + Pre-Filled Borrower LOE Request]         │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Open Gemini Enterprise Agent Studio (`collections/default_collection/engines/global-gemini-enterprise`) and create a workflow agent.",
                    "Add the `audit_large_deposits` Python sandbox tool to calculate the exact 50% Fannie Mae B3-4.2-02 threshold and asset back-out math.",
                    "Configure a HITL `RUNTIME_STAGE_BLOCKING` approval policy before dispatching the LOE request to the borrower's Rocket Mortgage portal."
                ],
                "codeSnippet": """# Fannie Mae B3-4.2-02 Large Deposit Auditor
threshold = qualifying_monthly_income * 0.50
flagged = [d for d in deposits if d["type"] != "PAYROLL" and d["amount"] > threshold]
unverified_total = sum(d["amount"] for d in flagged)
backed_out_balance = ending_balance - unverified_total
must_source = backed_out_balance < funds_needed_to_close"""
            },
            {
                "code": "2.3",
                "level": "L200–L300",
                "tags": ["L200", "L300"],
                "tool": "Google Cloud Document AI + Gemini 4 Argon",
                "project": "Automated W-2 & Paystub Entity Extraction & Variance Pipeline",
                "focus": "OCR & key-value extraction from scanned paystubs and W-2s, cross-checking stated 1003 income and flagging >5% discrepancies.",
                "desc": "Extract employer name, FEIN, pay frequency, YTD gross earnings, base hourly/salary rate, and overtime lines into normalized key-value pairs with confidence scores and bounding-box coordinates, flagging any variance >5% against the 1003 application.",
                "url": "https://cloud.google.com/document-ai/docs",
                "serviceText": "Google Cloud Document AI Lending Suite",
                "serviceUrl": "https://cloud.google.com/document-ai",
                "gcpStack": ["Document AI W-2 & Paystub Parsers", "Gemini 4 Argon Cross-Document Reconciliation", "Cloud Run"],
                "competeEdge": "Pre-trained Lending Document AI processors achieve 99.2% field accuracy on noisy mobile phone photos of W-2s/Paystubs without custom AWS Textract template tuning.",
                "sampleInput": """Document AI OCR Payload (2 Uploaded Documents vs. Form 1003 Application):
- Form 1003 Stated Income: $10,500.00 / month ($126,000/yr) at "Stellantis NV - Auburn Hills MI".
- Paystub Extracted Entities (Pay Period Ending 09/30/2026 — 9.0 Months Elapsed in 2026):
  * Employer: FCA US LLC / Stellantis North America (FEIN: 38-2678910)
  * Pay Rate: $4,583.33 Semi-Monthly ($110,000.00 annualized base)
  * YTD Base Earnings (9.0 mos): $82,500.00 (matches $9,166.67/mo)
  * YTD Overtime Earnings (9.0 mos): $4,950.00 ($550.00/mo pace)
  * Total Documented Monthly Pace: $9,716.67 / month.
- 2025 W-2 Extracted Entities:
  * Box 1 Wages: $114,200.00 | Box 5 Medicare Wages: $119,600.00.""",
                "sandboxAction": "reconcile_paystub_w2",
                "sandboxParams": {"stated_monthly": 10500.0, "semi_monthly_base": 4583.33, "ytd_base_9m": 82500.0, "ytd_ot_9m": 4950.0, "w2_2025_box5": 119600.0},
                "systemPrompt": "You are the Rocket Document AI W-2 & Paystub Entity Reconciliation Engine powered by Gemini 4 Argon. Analyze the extracted Document AI entities and the sandbox reconciliation math. Produce: (1) Extracted Entity & Confidence Table (showing FEIN/Corporate DBA match between 'Stellantis NV' and 'FCA US LLC'), (2) Income Variance Alert flagging that Stated 1003 Income ($10,500/mo) exceeds Documented Paystub Pace ($9,716.67/mo) by +8.06% (breaching the 5.0% tolerance rule!), and (3) Exact Corrected 1003 Qualifying Income entry.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│     2.3 DOCUMENT AI W-2 & PAYSTUB EXTRACTION PIPELINE (L200-L300)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Borrower Uploaded PDF / Mobile Photo: Paystub + 2025 W-2]            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Google Cloud Document AI Lending Processors]                         │
│  ├─► Paystub Parser: Pay Rate, YTD Base, YTD Overtime, Pay Period      │
│  └─► W-2 Parser: FEIN, Box 1, Box 3, Box 5 Wages + Confidence Scores   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini 4 Argon + Variance Verifier]                                  │
│  • Resolves DBA ("Stellantis" == "FCA US LLC")                         │
│  • Flags +8.06% Stated vs Documented Variance (>5% threshold)          │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Create a Paystub Processor (`PAY_STUB_PROCESSOR`) and W-2 Processor (`US_W2_PROCESSOR`) in Google Cloud Document AI.",
                    "Send the Document AI `document.entities` JSON to `gemini-4-argon` alongside the borrower's Form 1003 stated income.",
                    "Run the automated 5% variance check and output the Encompass/Rocket Logic income adjustment payload."
                ],
                "codeSnippet": """from google.cloud import documentai_v1 as documentai

docai_client = documentai.DocumentProcessorServiceClient()
name = docai_client.processor_path("vtxdemos", "us", "PAYSTUB_PROCESSOR_ID")
result = docai_client.process_document(request={"name": name, "raw_document": {"content": pdf_bytes, "mime_type": "application/pdf"}})
entities = {e.type_: e.mention_text for e in result.document.entities}"""
            },
            {
                "code": "2.4",
                "level": "L300",
                "tags": ["L300"],
                "tool": "Gemini 4 Argon: Strict JSON Schema (Pydantic)",
                "project": "Self-Employed Schedule C / 1040 Cash-Flow Extractor (Form 1084)",
                "focus": "Enforce strict Pydantic JSON schemas (`response_schema`) on multi-page 1040 tax returns to compute Fannie Mae Form 1084 self-employed cash flow.",
                "desc": "Parse 2024 and 2025 IRS Form 1040 + Schedule C tax returns into a guaranteed Pydantic JSON schema, automatically adding back non-cash depreciation, depletion, and business use of home while deducting meals/entertainment and non-recurring income.",
                "url": "https://ai.google.dev/gemini-api/docs/structured-output",
                "serviceText": "Vertex AI Gemini 4 Argon Structured Outputs",
                "serviceUrl": "https://cloud.google.com/vertex-ai",
                "gcpStack": ["Gemini 4 Argon (response_schema)", "Pydantic v2", "Fannie Mae Form 1084 Engine"],
                "competeEdge": "Gemini 4 Argon's constrained decoding guarantees 100% schema adherence on nested 2-year tax schedules with zero malformed JSON retries.",
                "sampleInput": """Borrower: Motor City Precision Tooling LLC (Sole Proprietorship — IRS Form 1040 Schedule C, NAICS 332710).
2024 Schedule C:
- Line 1 Gross Receipts: $485,000 | Line 4 COGS: $162,000 | Line 7 Gross Income: $323,000
- Line 13 Depreciation (Form 4562 non-cash): $28,400
- Line 24b Deductible Meals: $6,200
- Line 30 Business Use of Home (Form 8829): $4,800
- Line 31 Net Profit: $142,000
- Form 4562 Business Miles: 14,000 miles (@ $0.30/mi IRS depreciation factor = $4,200 add-back)
2025 Schedule C:
- Line 1 Gross Receipts: $530,000 | Line 4 COGS: $175,000 | Line 7 Gross Income: $355,000
- Line 13 Depreciation (Form 4562 non-cash): $31,600
- Line 24b Deductible Meals: $7,400
- Line 30 Business Use of Home (Form 8829): $5,100
- Line 31 Net Profit: $158,000
- Form 4562 Business Miles: 15,500 miles (@ $0.33/mi IRS depreciation factor = $5,115 add-back)""",
                "sandboxAction": "calc_form_1084",
                "sandboxParams": {
                    "yr2024": {"net_profit": 142000, "depreciation": 28400, "meals_deduction": 6200, "home_office": 4800, "mileage_addback": 4200},
                    "yr2025": {"net_profit": 158000, "depreciation": 31600, "meals_deduction": 7400, "home_office": 5100, "mileage_addback": 5115}
                },
                "systemPrompt": "You are the Rocket Logic Self-Employed Form 1084 Cash Flow Extractor powered by Gemini 4 Argon Structured JSON Outputs. Using the verified Form 1084 sandbox calculation, return: (1) Complete Fannie Mae Form 1084 Line-by-Line Worksheet (2024 Adjusted Cash Flow vs. 2025 Adjusted Cash Flow, showing why increasing YoY trend allows 24-month averaging), (2) The exact strict Pydantic JSON payload ready for direct LOS database ingestion, and (3) Underwriter sign-off notes.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│       2.4 SCHEDULE C / 1040 FORM 1084 EXTRACTOR (L300 JSON SCHEMA)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Multi-Page IRS Form 1040 + Schedule C + Form 4562 (2024 & 2025)]     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Gemini 4 Argon Constrained Decoding (response_schema=Form1084)]      │
│  • Extracts Line 31 Net Profit, Line 13 Depreciation, Line 30 Home     │
│  • Deducts Line 24b Meals, Adds Back Business Mileage Depreciation     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Strict Pydantic JSON Object + 24-Month Qualifying Income ($15,442)]  │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Define a Pydantic model `FannieMaeForm1084ScheduleC` representing 2024 and 2025 Schedule C lines (`line_31_net_profit`, `line_13_depreciation_addback`, `line_24b_meals_deduction`, `line_30_home_office_addback`, `mileage_depreciation_addback`, `monthly_qualifying_income`).",
                    "Pass `response_mime_type='application/json'` and `response_schema=FannieMaeForm1084ScheduleC` to `gemini-4-argon`.",
                    "Ingest the validated JSON directly into Rocket's underwriting database."
                ],
                "codeSnippet": """from pydantic import BaseModel

class ScheduleCYear(BaseModel):
    tax_year: int
    line_31_net_profit: float
    line_13_depreciation_addback: float
    line_30_home_office_addback: float
    line_24b_meals_deduction: float
    mileage_depreciation_addback: float
    adjusted_annual_cash_flow: float

class Form1084Output(BaseModel):
    business_name: str
    year_1: ScheduleCYear
    year_2: ScheduleCYear
    trend_status: str
    qualifying_monthly_income: float"""
            },
            {
                "code": "2.5",
                "level": "L300",
                "tags": ["L300"],
                "tool": "Vertex AI Grounding & Search",
                "project": "Rocket Close (Amrock) Title Exception & Municipal Lien Matcher",
                "focus": "Ground title clearance decisions against Rocket Close precedent repositories and ALTA endorsement rules to eliminate curative bottlenecks.",
                "desc": "When a Schedule B-II Title Commitment reveals an unreleased prior mortgage, solar UCC-1 fixture filing, or Detroit utility easement, cross-reference Rocket Close curative precedents and ALTA endorsement standards automatically.",
                "url": "https://cloud.google.com/vertex-ai/docs/generative-ai/grounding/overview",
                "serviceText": "Vertex AI Grounding & Search",
                "serviceUrl": "https://cloud.google.com/vertex-ai",
                "gcpStack": ["Vertex AI Search & Grounding", "Gemini 4 Argon", "BigQuery Title Precedent Store"],
                "competeEdge": "Matches title exceptions against 10M+ historical Amrock / Rocket Close curative files in BigQuery + Vertex AI Search in <800ms.",
                "sampleInput": """Rocket Close Title Commitment File #RC-2026-77190 (Wayne County, MI — Property: 19450 Livernois Ave, Detroit, MI 48221):
Schedule B - Section II Exceptions Flagged:
1) Exception #8: Unreleased Prior Mortgage dated May 14, 2018 in favor of Fifth Third Bank in original principal amount of $145,000 (Liber 54412, Page 882). Payoff receipt from 2021 refinancing exists in prior title file, but Discharge of Mortgage was never recorded by Wayne County Register of Deeds.
2) Exception #11: Recorded Detroit Edison (DTE Energy) 6-foot rear lot line utility easement recorded in Liber 21094, Page 112. Survey shows detached garage eaves overhang 0.4 feet (4.8 inches) into easement air space.
3) Exception #14: UCC-1 Financing Statement filed by Sunrun Inc. (Solar Lease) recorded Oct 2023.""",
                "sandboxAction": "evaluate_title_exceptions",
                "sandboxParams": {"exceptions_count": 3, "unreleased_mortgage_age_yrs": 8, "has_prior_payoff_indemnity": True, "easement_encroachment_ft": 0.4, "has_solar_ucc1": True},
                "systemPrompt": "You are the Rocket Close (Amrock) Title Exception & Curative Clearance Engine powered by Vertex AI Grounding and Gemini 4 Argon. Evaluate each Schedule B-II exception against Michigan Master Indemnity treaties, Fannie Mae B7-2-05 Title Exceptions, and ALTA 9 / ALTA 28.1 Endorsement standards. Output: (1) Curative Resolution Matrix for Exceptions #8, #11, and #14, (2) Whether closing is BLOCKED or CLEARED TO CLOSE (highlighting why Exception #8 clears via Michigan Mutual Indemnity Agreement, Exception #11 clears via ALTA 28.1 Encroachment Endorsement, and Exception #14 requires a standard Sunrun UCC-3 Termination/Subordination before funding), and (3) Automated Curative Action Dispatch.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│     2.5 ROCKET CLOSE TITLE EXCEPTION & LIEN MATCHER (L300 GROUNDING)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Schedule B-II Title Commitment: Unreleased Lien, Easement, UCC-1]    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Vertex AI Grounding: Rocket Close / Amrock Curative Knowledge Base]  │
│  ├─► Michigan Mutual Indemnity Treaty Database                         │
│  ├─► Fannie Mae B7-2-05 Acceptable Title Exceptions                    │
│  └─► ALTA Endorsement Manual (ALTA 9, ALTA 28.1, UCC-3 Solar Rules)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Curative Clearance Memo + Auto-Dispatched Sunrun UCC-3 Subordination]│
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Index Rocket Close (Amrock) curative underwriting bulletins, state mutual indemnity treaties, and ALTA endorsement guides into a Vertex AI Search datastore.",
                    "Pass Schedule B-II exceptions from the title commitment into `gemini-4-argon` with Vertex AI Grounding enabled.",
                    "Output structured clearance status (`AUTO_CLEARED_INDEMNITY`, `CLEARED_WITH_ALTA_ENDORSEMENT`, or `REQUIRES_SUBORDINATION`) directly to the Rocket Close portal."
                ],
                "codeSnippet": """# Grounded Title Curative Verification
response = client.models.generate_content(
    model="gemini-4-argon",
    contents=schedule_b2_exceptions,
    config=types.GenerateContentConfig(
        system_instruction="Verify Schedule B-II exceptions against Amrock Indemnity Treaties & Fannie Mae B7-2-05...",
        tools=[vertex_search_tool]
    )
)"""
            }
        ]
    },
    {
        "id": "servicing",
        "service_name": "rocket-demo-servicing",
        "demo_url": CLOUD_RUN_URLS["servicing"],
        "shortTitle": "3. CX & Mr. Cooper Servicing",
        "fullTitle": "3. Client Experience & Servicing (Mr. Cooper Portfolio, Escrow, Synopsis & Recapture)",
        "themeName": "Mr. Cooper x Rocket Servicing Omnichannel CX & Voice Studio (The Sierra AI Killer)",
        "mission": "Drive 85%+ first-contact resolution across Rocket & Mr. Cooper's multi-million-loan servicing portfolio (escrow shortages, payoffs, Form 1098s, CFPB hardship) and recapture refinances with Gemini Live API.",
        "awsWinback": "Replaces expensive third-party Sierra AI per-resolution fees and AWS Connect + Bedrock wrappers with native Gemini Enterprise for CX (GECX), CCAI Agent Assist (upgrading Rocket Logic Synopsis), and sub-200ms Gemini Multimodal Live API.",
        "projects": [
            {
                "code": "3.1",
                "level": "L100–L200",
                "tags": ["L100", "L200"],
                "tool": "Gemini Enterprise for CX (GECX)",
                "project": "Annual Escrow Shortage Resolution Journey",
                "focus": "Self-service omnichannel GECX journey that explains county property tax/insurance increases in plain language and executes 1-click payment plan updates.",
                "desc": "Deflect the #1 post-closing servicing call volume driver across Rocket & Mr. Cooper: annual escrow analysis shortages. Visualizes exact county tax + hazard insurance changes and lets borrowers pick Lump-Sum vs. 12-Month Spread or 24-Month Hardship Spread.",
                "url": "https://cloud.google.com/solutions/contact-center",
                "serviceText": "Gemini Enterprise for CX (GECX)",
                "serviceUrl": "https://cloud.google.com/solutions/contact-center",
                "gcpStack": ["Gemini Enterprise for CX (GECX)", "Gemini 4 Argon", "Mr. Cooper / MSP Servicing Ledger API"],
                "competeEdge": "Beats Sierra AI by combining deterministic RESPA 2-month cushion escrow math with native GCP omnichannel state persistence across mobile app, web, and voice.",
                "sampleInput": """Servicing Loan #MRC-4409182 (Mr. Cooper / Rocket Servicing Portfolio — Property: 2410 Dorchester Rd, Troy, MI 48084):
Borrower asks: "Why did my monthly mortgage payment suddenly jump from $2,480 to $2,765 starting November 1st?! Did my fixed interest rate change?"
Escrow Analysis Ledger Data:
- Loan Type: 30-Yr Fixed at 5.25% (Principal & Interest is UNCHANGED at $1,840.00/mo).
- 2025 Troy / Oakland County Property Tax Disbursed: $4,920/yr ($410/mo).
- 2026 Troy / Oakland County Property Tax Assessed (Uncapped after purchase): $6,000/yr ($500/mo -> +$90/mo tax increase).
- Homeowners Hazard Insurance (State Farm): Increased from $1,680/yr ($140/mo) to $2,280/yr ($190/mo -> +$50/mo insurance increase).
- Required New Base Escrow Deposit: $690/mo (up from $550/mo = +$140/mo ongoing increase).
- Retroactive Escrow Shortage (plus RESPA 2-month cushion): $1,740.00 total shortage ($145.00/mo if spread over 12 months).""",
                "sandboxAction": "calc_escrow_shortage",
                "sandboxParams": {"pi_monthly": 1840.0, "old_tax_yr": 4920.0, "new_tax_yr": 6000.0, "old_ins_yr": 1680.0, "new_ins_yr": 2280.0, "shortage_total": 1740.0},
                "systemPrompt": "You are the Rocket & Mr. Cooper GECX Annual Escrow Shortage Concierge powered by Gemini 4 Argon. Reassure the borrower immediately that their 5.25% Fixed Interest Rate and $1,840/mo Principal & Interest NEVER changed. Then present: (1) Plain-Language Breakdown of why their Oakland County uncapped property tax (+$90/mo) and State Farm insurance (+$50/mo) caused both an ongoing $140/mo base escrow increase and a one-time $1,740 retroactive shortage, and (2) Three Interactive Resolution Options (Option A: Pay $1,740 Lump Sum -> New Payment $2,620/mo; Option B: 12-Month Shortage Spread -> New Payment $2,765/mo; Option C: Request Oakland County Principal Residence Exemption (PRE) Audit + Insurance Shop).",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│       3.1 GECX ANNUAL ESCROW SHORTAGE RESOLUTION JOURNEY (L100-200)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Borrower Inquiry: "Why did my fixed mortgage jump $285/mo?!"]        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [GECX Conversational Agent + RESPA Escrow Analysis Sandbox]           │
│  ├─► Verifies P&I ($1,840/mo) is 100% locked                           │
│  ├─► Separates Ongoing Tax/Ins Delta (+$140/mo) vs Shortage (+$145/mo) │
│  └─► Computes Lump-Sum ($2,620/mo) vs 12-Mo Spread ($2,765/mo)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [1-Click Self-Service Billing Update + Michigan PRE Tax Check]        │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "In Gemini Enterprise for CX (GECX) Agent Studio, create a hybrid Playbook + Deterministic Flow for `Escrow_Shortage_Resolution`.",
                    "Bind the `calc_escrow_shortage` OpenAPI/Cloud Run tool to fetch the borrower's RESPA annual escrow statement from MSP/Servicing.",
                    "Render the 3 interactive payment election cards in the Rocket Mobile App / Web widget."
                ],
                "codeSnippet": """# RESPA Escrow Shortage Calculator Tool for GECX
ongoing_delta = ((new_tax_yr - old_tax_yr) + (new_ins_yr - old_ins_yr)) / 12
option_lump_sum_monthly = pi_monthly + (new_tax_yr + new_ins_yr) / 12
option_12mo_spread_monthly = option_lump_sum_monthly + (shortage_total / 12)"""
            },
            {
                "code": "3.2",
                "level": "L200",
                "tags": ["L200"],
                "tool": "Dialogflow CX Deterministic Flows",
                "project": "Self-Service Payoff Quote & IRS Form 1098 Voice/Chat Bot",
                "focus": "Deterministic state-machine bot with MFA/SSN verification for official payoff quotes (with per-diem interest) and instant Form 1098 delivery.",
                "desc": "Automate the two highest-volume transactional servicing requests across Mr. Cooper & Rocket Servicing with strict state-machine authentication gates, computing exact per-diem interest through a good-through closing date.",
                "url": "https://cloud.google.com/dialogflow/cx/docs",
                "serviceText": "Google Cloud Dialogflow CX",
                "serviceUrl": "https://cloud.google.com/dialogflow",
                "gcpStack": ["Dialogflow CX State Machine", "Gemini 3.8 Flash", "Cloud Run Payoff Per-Diem Calculator"],
                "competeEdge": "Combines rock-solid deterministic state transitions (mandatory for PII/SSN authentication and payoff wire instructions) with generative natural language slot-filling.",
                "sampleInput": """Authenticated Borrower: Jordan Taylor | Loan #RKT-7712098 | SSN Last 4: 8821 (Verified) | Property ZIP: 48226 (Verified).
Request: "I'm selling my condo and closing on November 12, 2026. Please generate my official Payoff Quote good through 11/12/2026 and also email my prior-year IRS Form 1098 Mortgage Interest Statement to my CPA."
Loan Ledger:
- Unpaid Principal Balance (UPB as of Oct 1, 2026): $284,500.00
- Note Interest Rate: 6.000% (365-day per diem basis -> $46.77/day)
- Accrued Interest (Oct 1 to Nov 12 = 42 days): $1,964.34
- Recording / Discharge Fee (Wayne County MI): $30.00
- Escrow Credit Balance to Net / Refund: $1,120.00""",
                "sandboxAction": "calc_payoff_quote",
                "sandboxParams": {"upb": 284500.0, "rate": 6.0, "days_accrued": 42, "recording_fee": 30.0, "escrow_balance": 1120.0},
                "systemPrompt": "You are the Dialogflow CX Official Payoff Quote & Form 1098 Fulfillment Bot. Confirm the state-machine authentication path (`START -> AUTH_SSN_ZIP -> INTENT_PAYOFF_AND_1098 -> FULFILLMENT_COMPLETE`), present the exact official Payoff Statement table (UPB, 42-day Accrued Interest at $46.77/day Per Diem, Wayne County $30 Discharge Fee, Total Payoff Wire Amount, and Escrow Refund notice), and confirm encrypted dispatch of IRS Form 1098.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│       3.2 DIALOGFLOW CX PAYOFF QUOTE & FORM 1098 BOT (L200)            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [State 1: Identity Verification Gate (SSN4 + Property ZIP + OTP)]     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [State 2: Deterministic Fulfillment Webhook (Cloud Run)]              │
│  ├─► Per-Diem Interest: ($284,500 * 6.00%) / 365 = $46.77/day          │
│  ├─► 42-Day Good-Through Payoff Total: $286,494.34                     │
│  └─► Generates Official Payoff PDF + Dispatches IRS Form 1098          │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Define a Dialogflow CX flow with deterministic pages: `Authenticate_Borrower` -> `Collect_Good_Through_Date` -> `Execute_Payoff_Webhook`.",
                    "Configure route guards requiring session parameters `$session.params.auth_verified = true` before exposing payoff wire numbers.",
                    "Connect the Cloud Run fulfillment webhook to compute exact per-diem interest."
                ],
                "codeSnippet": """# Official Mortgage Payoff Per-Diem Calculator
daily_per_diem = round((upb * (rate / 100.0)) / 365.0, 2)
accrued_interest = round(daily_per_diem * days_accrued, 2)
total_payoff_due = round(upb + accrued_interest + recording_fee, 2)"""
            },
            {
                "code": "3.3",
                "level": "L200–L300",
                "tags": ["L200", "L300"],
                "tool": "Contact Center AI: Agent Assist (Synopsis Next-Gen)",
                "project": "Hardship & Forbearance Live Servicing Assistant (CFPB Reg X)",
                "focus": "Real-time call transcription, distress keyword detection, CFPB loss mitigation waterfall cards, and 1-click post-call wrap-up replacing manual Synopsis work.",
                "desc": "Supercharge Rocket Logic Synopsis: detect borrower financial distress in real time, surface compliant Fannie/Freddie/FHA loss mitigation waterfall options (Forbearance vs. Payment Deferral vs. Flex Modification), and generate a zero-edit wrap-up log.",
                "url": "https://cloud.google.com/agent-assist/docs",
                "serviceText": "Google Cloud CCAI Agent Assist & Gemini 4 Argon",
                "serviceUrl": "https://cloud.google.com/agent-assist",
                "gcpStack": ["CCAI Agent Assist", "Chirp 3 Streaming STT", "Gemini 4 Argon", "Vertex AI Policy Grounding"],
                "competeEdge": "Upgrades Rocket Logic Synopsis (currently batch/AWS Bedrock) into a real-time in-call co-pilot that prevents CFPB Regulation X dual-tracking violations while cutting wrap-up time by 82%.",
                "sampleInput": """Live Servicing Call Transcript Stream (Loan #MRC-901244 — Fannie Mae Conforming, Current UPB $312,000, PITI $2,180/mo, 30 Days Delinquent):
[00:12] Borrower (David Miller): "Hi, I'm calling because I missed October's payment and I'm really panicking. My plant in Sterling Heights just had a 60-day retooling layoff, and my wife had emergency gallbladder surgery last month."
[00:28] Borrower: "I'm going back to work full-time on December 1st with my recall letter in hand, so I can afford my normal $2,180 payment starting December, but I can't pay October and November right now. Are you guys going to foreclose on my house?"
[00:44] Servicing Specialist: "Mr. Miller, take a deep breath—you are safe, and we are here to help you keep your home. Let me pull up your Fannie Mae relief options right now..." """,
                "sandboxAction": "eval_loss_mitigation",
                "sandboxParams": {"investor": "Fannie Mae", "delinquent_months": 2, "piti": 2180.0, "hardship_type": "Temporary Layoff + Medical (Resolved by Dec 1)", "can_resume_full_payment": True},
                "systemPrompt": "You are the CCAI Agent Assist Live Hardship & Loss Mitigation Co-Pilot for Rocket / Mr. Cooper Servicing powered by Gemini 4 Argon. Analyze the live call transcript and output: (1) Real-Time Distress & Sentiment Alert + Mandatory CFPB Regulation X Anti-Dual-Tracking Guardrail (12 CFR § 1024.41 — Foreclosure referral strictly prohibited under 120 days), (2) Fannie Mae Loss Mitigation Waterfall Recommendation Card (Temporary 2-Month Forbearance transitioning into a Fannie Mae Payment Deferral putting the $4,360 missed payments into a non-interest-bearing balance due at maturity/refi, keeping his Dec 1 payment at $2,180/mo!), and (3) One-Click Rocket Logic Synopsis Post-Call CRM Wrap-Up Note.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│     3.3 CCAI AGENT ASSIST HARDSHIP & FORBEARANCE CO-PILOT (L200-300)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Live Audio Stream -> Chirp 3 Real-Time STT Transcript]               │
│  • Detects "layoff", "medical surgery", "recall letter Dec 1"          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [CCAI Agent Assist + Gemini 4 Argon Loss Mitigation Waterfall]        │
│  ├─► CFPB Reg X Guardrail: Zero Foreclosure Risk (<120 days)           │
│  ├─► Fannie Mae Waterfall: 2-Mo Forbearance -> Payment Deferral        │
│  └─► Defers $4,360 to non-interest tail; Dec 1 PITI stays $2,180/mo    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Live Specialist Suggestion Cards + 1-Click Synopsis Wrap-Up Log]     │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Create a Conversation Profile in Google Cloud CCAI Agent Assist with Knowledge Assist (grounded in CFPB Reg X & Fannie Mae Servicing Guide D2-3.2) and Summarization enabled.",
                    "Stream live call audio via gRPC `StreamingAnalyzeContent`.",
                    "Render the real-time Agent Assist suggestion cards and 1-click Synopsis wrap-up payload in the servicing desktop."
                ],
                "codeSnippet": """# Fannie Mae Payment Deferral Eligibility & Agent Assist Card Generator
deferred_arrears = delinquent_months * piti  # $4,360.00 moved to non-interest tail
new_monthly_piti = piti  # Unchanged ($2,180.00/mo) upon hardship resolution"""
            },
            {
                "code": "3.4",
                "level": "L300",
                "tags": ["L300"],
                "tool": "Gemini Multimodal Live API (WebSockets)",
                "project": "Conversational Rocket Recapture Voice Concierge",
                "focus": "Ultra-low-latency bidirectional WebSocket voice agent that proactively contacts Mr. Cooper servicing clients when rates drop to recapture refis.",
                "desc": "Unlock the #1 revenue synergy of the Mr. Cooper acquisition: Portfolio Recapture. When rates drop 75+ bps below a borrower's note rate, the Gemini Live API voice agent engages them in a natural, interruptible conversation, computes exact monthly savings & breakeven, and warm-transfers to a licensed Rocket banker.",
                "url": "https://ai.google.dev/gemini-api/docs/live",
                "serviceText": "Gemini Multimodal Live API (Bidi WebSockets)",
                "serviceUrl": "https://ai.google.dev/gemini-api/docs/live",
                "gcpStack": ["Gemini Live API (BidiGenerateContent WebSocket)", "Gemini 4 Argon", "Cloud Run Recapture Math Engine"],
                "competeEdge": "Native multimodal audio-to-audio streaming eliminates the 1,200ms STT -> LLM -> TTS cascade lag of Sierra Voice and AWS Connect Lex bots.",
                "sampleInput": """Mr. Cooper Servicing Recapture Campaign Target #MRC-REFI-55109:
- Borrower: Samantha & Kevin Ortiz (Austin, TX — originated Oct 2023 at 7.375% 30-Yr Fixed).
- Current UPB: $418,000 | Current Monthly P&I: $2,887.02/mo | Remaining Term: 324 months.
- Today's Rocket VIP Streamline Refi Offer: 5.875% 30-Yr Fixed (zero appraisal waiver eligible via Fannie Mae Value Acceptance, $0 out-of-pocket closing costs rolled in = $421,200 new loan).
- Borrower Mid-Call Interruption: "Wait—hold on! If we don't want to reset our loan clock back to 30 years, what would our payment be if we refinance into a 20-year fixed at 5.625% instead?" """,
                "sandboxAction": "calc_refi_recapture",
                "sandboxParams": {"current_upb": 418000.0, "current_rate": 7.375, "current_pi": 2887.02, "new_loan": 421200.0, "rate_30yr": 5.875, "rate_20yr": 5.625},
                "systemPrompt": "You are the Conversational Rocket Recapture Voice Concierge powered by Gemini Multimodal Live API & Gemini 4 Argon. Respond naturally to the borrower's mid-sentence interruption ('What if we do a 20-year fixed instead of resetting to 30 years?'). Present: (1) Spoken Natural Voice Script (warm, conversational, <180ms barge-in style), (2) Exact Side-by-Side Comparison Table (Current 7.375% Loan vs. 30-Yr Fixed at 5.875% saving $395/mo vs. 20-Yr Fixed at 5.625% at $2,927/mo which keeps payment virtually identical (+$40/mo) while shaving 7 FULL YEARS off their mortgage and saving $184,000+ in lifetime interest!), and (3) Warm-Transfer Whisper Packet to the licensed Texas NMLS Banker.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│     3.4 GEMINI LIVE API ROCKET RECAPTURE VOICE CONCIERGE (L300)        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Bidi WebSocket Audio Stream (wss://.../BidiGenerateContent)]         │
│  • Borrower barges in mid-sentence: "What about a 20-yr fixed?"        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Live Tool Call: calc_refi_recapture(30yr=5.875%, 20yr=5.625%)]       │
│  ├─► 30-Yr Refi: $2,492/mo (-$395/mo immediate cash flow savings)      │
│  └─► 20-Yr Refi: $2,927/mo (+$40/mo, cuts 7 yrs & saves $184k interest)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Instant Spoken Response + Warm Context Handoff to Rocket Banker]     │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Open a bidirectional WebSocket connection to `wss://aiplatform.googleapis.com/ws/google.cloud.aiplatform.v1beta1.LlmBidiService/BidiGenerateContent`.",
                    "Register the `calc_refi_recapture` tool in the `setup` frame with `responseModalities: ['AUDIO']`.",
                    "When the borrower interrupts mid-sentence, Gemini Live API automatically halts audio output, invokes the recalculation tool, and speaks the 20-year vs 30-year comparison."
                ],
                "codeSnippet": """setup_msg = {
    "setup": {
        "model": "projects/vtxdemos/locations/us-central1/publishers/google/models/gemini-3.8-live",
        "generationConfig": {"responseModalities": ["AUDIO"]},
        "tools": [{"functionDeclarations": [refi_calculator_schema]}]
    }
}"""
            },
            {
                "code": "3.5",
                "level": "L300",
                "tags": ["L300"],
                "tool": "GEAP Multi-Agent Orchestration & Agent Registry",
                "project": "Autonomous Borrower Retention & Life-Event Orchestrator",
                "focus": "Stateful multi-agent swarm across Redfin listing signals, Mr. Cooper equity ledgers, and Rocket Money to prevent portfolio runoff before a borrower lists their home.",
                "desc": "Coordinate an Ecosystem Listener Agent (detecting when a Mr. Cooper servicing customer favorites homes or requests a Redfin home value estimate), a Financial Benefit Calculator Agent (computing portable equity + bridge/purchase options), and a Communication Dispatch Agent.",
                "url": "https://cloud.google.com/products/gemini-enterprise-agent-platform",
                "serviceText": "Gemini Enterprise Agent Platform & Agent Registry",
                "serviceUrl": "https://cloud.google.com/products/gemini-enterprise-agent-platform",
                "gcpStack": ["GEAP Multi-Agent Orchestrator", "Google Cloud Agent Registry (A2A)", "Gemini 4 Argon", "BigQuery Cross-Brand Event Hub"],
                "competeEdge": "Unifies Rocket's 3 crown-jewel datasets (Mr. Cooper Servicing + Redfin Search + Rocket Money) through Google Cloud Agent Registry & A2A protocol with zero cross-account AWS IAM sprawl.",
                "sampleInput": """Cross-Ecosystem Event Trigger #EVT-99402:
1) [Mr. Cooper Servicing Signal]: Borrower Alex & Rachel Kim (Royal Oak, MI) have $210,000 UPB at 3.25% rate; current automated home valuation (AVM) is $495,000 ($285,000 gross home equity).
2) [Redfin Behavioral Signal]: Same household email just saved 4 Redfin listings in Northville, MI ($725,000–$780,000 4-bed colonials) and clicked "What is my Royal Oak home worth?"
3) [Rocket Money Signal]: Monthly free cash flow surplus is $3,900/mo; child care expenses dropping by $1,600/mo in September.
Goal: Prevent competitor purchase mortgage runoff and structure an irresistible Move-Up Purchase vs. Keep-Current-Home-as-Rental (at 3.25%!) comparison package.""",
                "sandboxAction": "calc_retention_moveup",
                "sandboxParams": {"current_upb": 210000.0, "current_rate": 3.25, "current_home_val": 495000.0, "target_purchase": 750000.0, "rate_new_purchase": 6.125},
                "systemPrompt": "You are the GEAP Autonomous Borrower Retention & Life-Event Orchestrator powered by Gemini 4 Argon. Show the stateful 3-Agent execution trace (`[Agent 1: Ecosystem Listener] -> [Agent 2: Equity & Move-Up Strategist] -> [Agent 3: Omnichannel Dispatcher]`) and output: (1) Cross-Brand Signal Correlation Summary, (2) Two Wealth-Building Move-Up Scenarios (Scenario A: Sell Royal Oak home, net ~$255k equity after Redfin 1% listing fee savings, put 34% down on $750k Northville home; Scenario B: Keep the 3.25% Royal Oak mortgage as a cash-flowing rental yielding +$1,150/mo net rent + use a Rocket Home Equity Loan / Bridge for the Northville down payment), and (3) Coordinated Redfin Premier Agent + Rocket Executive Banker outreach payload.",
                "architectureDiagram": """┌────────────────────────────────────────────────────────────────────────┐
│    3.5 GEAP MULTI-AGENT RETENTION & LIFE-EVENT ORCHESTRATOR (L300)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Agent 1: Ecosystem Listener Agent (BigQuery + Pub/Sub)]              │
│  • Correlates Mr. Cooper ($285k equity) + Redfin (Northville search)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Agent 2: Financial Benefit Calculator Agent (Gemini 4 Argon)]        │
│  ├─► Scenario A: Sell w/ Redfin 1% Listing Fee + 34% Down on $750k     │
│  └─► Scenario B: Retain 3.25% Loan as Rental + Rocket Equity Bridge    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  [Agent 3: Communication Dispatch Agent (Redfin App + Rocket Mobile)]  │
└────────────────────────────────────────────────────────────────────────┘""",
                "reproSteps": [
                    "Register `EcosystemListenerAgent`, `EquityCalculatorAgent`, and `DispatchAgent` in Google Cloud Agent Registry (`apphub` / `agentregistry`).",
                    "Wire the parent `RetentionOrchestrator` using Google ADK (`LlmAgent` with `sub_agents=[...]`) running on `gemini-4-argon`.",
                    "Trigger the multi-agent pipeline via Cloud Run when Redfin search telemetry matches an active Mr. Cooper servicing loan."
                ],
                "codeSnippet": """from google.adk.agents import LlmAgent

listener_agent = LlmAgent(name="EcosystemListener", model="gemini-3.8-flash", instruction="Correlate Redfin + Mr. Cooper signals...")
calculator_agent = LlmAgent(name="EquityCalculator", model="gemini-4-argon", tools=[calc_retention_moveup])
orchestrator = LlmAgent(name="RetentionOrchestrator", model="gemini-4-argon", sub_agents=[listener_agent, calculator_agent])"""
            }
        ]
    }
]
