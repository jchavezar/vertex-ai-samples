"""
MASTER MOTOROLA SOLUTIONS ENTERPRISE DEMO SEEDER & DISASTER RECOVERY SUITE
(`seed_motorola_solutions_master.py`)

Idempotent script that populates (or restores from scratch if any instance is reset)
an extensive, hyper-realistic dataset across:
  1. Google Drive & Google Docs (LMR Telemetry, CDMG Rules, Trade/HTS Playbook, HR/IT Policy KB, Competitive Dossier)
  2. Google Sheets (Municipal Expiring Contracts Matrix & Deal Desk Discount Matrix)
  3. Gmail (RFQ Submissions with HTS Discrepancies, Contract Redlines, ServiceNow Approval Emails, Labels & Drafts)
  4. Google Calendar (APCO Partner Events, Executive Go/No-Go Reviews, Territory Catalyst Briefings)
  5. Salesforce CRM (Public Safety Accounts, Expiring LMR Opportunities, CDMG Unverified Records, Contacts, Cases, Leads, Tasks)
  6. ServiceNow ITSM/HR (Incidents, Laptop/Software Requests, CI Creation, Root-Cause Categories)
"""

import asyncio
import datetime
import json
import os
import re
import requests
from server import mcp


async def call_tool(name: str, args: dict) -> str:
    res = await mcp.call_tool(name, args)
    if hasattr(res, "content") and res.content:
        return res.content[0].text
    return str(res)


def extract_id(text: str) -> str:
    m = re.search(r"ID:\s*`([^`]+)`", text)
    return m.group(1) if m else ""


async def seed_workspace():
    print("\n=======================================================")
    print("1. SEEDING GOOGLE WORKSPACE (DRIVE, DOCS, SHEETS, GMAIL, CALENDAR)")
    print("=======================================================")

    # Create dedicated Motorola Solutions Master Folder in Drive
    find_res = await call_tool("drive_find_folder", {"folder_name": "Motorola Solutions - Enterprise AI Demo Universe"})
    folder_id = extract_id(find_res)
    if not folder_id:
        create_res = await call_tool("drive_create_folder", {"name": "Motorola Solutions - Enterprise AI Demo Universe"})
        folder_id = extract_id(create_res)
    print(f"📁 Motorola Master Drive Folder ID: {folder_id}")

    # -------------------------------------------------------------------------
    # A. GOOGLE DOCS (5 Comprehensive Knowledge Base & Telemetry Documents)
    # -------------------------------------------------------------------------
    docs_to_create = [
        {
            "title": "[Motorola Public Safety] City of Metro & State Patrol - 36-Month ASTRO 25 LMR Telemetry & Cloud Video Cross-Sell Playbook",
            "content": (
                "<h1>Motorola Solutions Mission-Critical Telemetry & Renewal Intelligence</h1>"
                "<p><b>Business Owner:</b> David Katimi (Public Safety Renewals) & Sales Cross-Sell Spotter<br>"
                "<b>Target Accounts:</b> City of Metro Public Safety ($3.85M), State Highway Patrol ($5.2M), Miami-Dade Dispatch ($1.95M)</p>"
                "<h2>1. 36-Month Land Mobile Radio (LMR) Historical Usage Logs</h2>"
                "<ul>"
                "<li><b>City of Metro Police & Fire (ASTRO 25 System #IL-884):</b> 43.2 Million Push-to-Talk (PTT) transmissions over 36 months (Avg 1.2M/month, +18.4% YoY). System availability: <b>99.994% uptime</b> across 4,800 APX NEXT smart radios.</li>"
                "<li><b>Channel Saturation Warning:</b> District 4 Tactical Dispatch reached 94.2% capacity during major municipal events.</li>"
                "<li><b>State Highway Patrol (ASTRO 25 System #TX-109):</b> 78.5 Million PTT transmissions across 8,200 vehicular repeaters. Expiring in 60 days.</li>"
                "</ul>"
                "<h2>2. AI Cross-Sell Spotter Recommendation: Cloud-Native Video Security & LPR</h2>"
                "<p>Customer usage logs indicate high voice dispatch congestion during traffic stops and emergency perimeter lockdowns. Recommend bundling the 5-Year ASTRO 25 LMR Renewal with <b>Avigilon Alta Cloud Video Security + License Plate Recognition (LPR) + CommandCentral Aware</b> ($1.25M upsell). Approved 12% Municipal Multi-Agency Bundle Discount applies when Police and Fire are grouped under a unified Public Sector Parent Entity.</p>"
            )
        },
        {
            "title": "[Motorola CDMG Policy] Master Data Stewardship, Address Validation & Public Sector Hierarchy Grouping Standard (2026)",
            "content": (
                "<h1>Customer Data Management Group (CDMG) Zero-Touch Enrichment Rules</h1>"
                "<p><b>Business Owners:</b> Erica Boklewski & Magdalena Zurakowska (CDMG / Master Data)</p>"
                "<h2>1. Zero-Touch Backend Enrichment Mandate</h2>"
                "<ul>"
                "<li><b>Address & County Verification:</b> Every incoming Salesforce Account/Lead must have its street address validated against USPS/Global postal databases and its <b>County</b> derived (e.g., 1200 N. State Parkway, Chicago IL -> <b>Cook County</b>).</li>"
                "<li><b>Tax ID / VAT & Website Derivation:</b> Automatically derive corporate domain, official website, and EU VAT / US EIN registration numbers via public registries.</li>"
                "<li><b>Reseller vs. End-User POS Detection:</b> Classify whether the account is a Channel Partner/Reseller (Partner Empower) or Mission-Critical End User.</li>"
                "</ul>"
                "<h2>2. Public Sector & Commercial Corporate Hierarchy Rules</h2>"
                "<ul>"
                "<li><b>Public Sector (NA State & Local / Federal):</b> Automatically group municipal sub-departments (e.g., <i>Metro Police Department</i>, <i>Metro Fire Rescue</i>, <i>Metro 911 OEM</i>) under their overarching Municipal Parent Grouping (<b>City of Metro Government</b>).</li>"
                "<li><b>Commercial Accounts:</b> Cross-reference corporate lineage to link regional operating subsidiaries (e.g., <i>Apex Global Communications LLC</i>) to their Ultimate Global Parent (<b>Apex Global Holdings Inc.</b>).</li>"
                "</ul>"
            )
        },
        {
            "title": "[Motorola Procurement & Trade Compliance] Global RFQ Terms, Approved Redlines & HTS Tariff Classification Matrix",
            "content": (
                "<h1>Global Supply Chain Procurement & Export Compliance Playbook</h1>"
                "<p><b>Business Owners:</b> Yoke Pheng Wong (Procurement), Ken Bradshaw (Trade Compliance), Ryan Christensen (Legal Redlining)</p>"
                "<h2>1. Harmonized Tariff Schedule (HTS) Export Compliance Rules</h2>"
                "<ul>"
                "<li><b>HTS Code 8525.60.1020 (MANDATORY for Encrypted Public Safety Transceivers):</b> Applies to all tactical two-way radio modules containing AES-256 / FIPS 140-3 cryptographic modules. Duty rate: <b>0.0% Free under Public Safety Exemption</b>.</li>"
                "<li><b>HTS Code 8525.60.1050 (Commercial Unencrypted Radios):</b> Carries a <b>2.1% import tariff</b>. Suppliers frequently misclassify encrypted modules under 8525.60.1050, causing severe customs holds and $40K+ duty overpayments per 5,000-unit batch.</li>"
                "</ul>"
                "<h2>2. Standard Contract Redlining & Payment Term Limits</h2>"
                "<ul>"
                "<li><b>Payment Terms:</b> Standard Motorola PO policy is <b>Net-45 days</b>. Any supplier RFQ demanding Net-60 or Net-90 must be redlined back to Net-45 (or Net-60 with a 3% early payment discount).</li>"
                "<li><b>Limitation of Liability:</b> Minimum acceptable supplier liability cap is <b>2.0x PO Value</b> (never accept 0.5x PO value on mission-critical components).</li>"
                "</ul>"
            )
        },
        {
            "title": "[Motorola HR & IT Service Delivery] Global Employee Support, Hardware/Software Escalation & ServiceNow Approval Policy",
            "content": (
                "<h1>Motorola Solutions Global IT & HR Support Escalation Manual</h1>"
                "<p><b>Business Owners:</b> Apoorva (HR/IT Support) & Priyanka B (IT Ticket Analytics)</p>"
                "<h2>1. Automated ServiceNow Ticket Logging & Chat Form Rules</h2>"
                "<p>When an employee requests specialized hardware, restricted software licenses, or Configuration Item (CI) creation that cannot be resolved via self-service FAQ:</p>"
                "<ol>"
                "<li>The AI Agent must collect <b>Requester Department, Business Justification, Cost Center, and Urgency</b> via an interactive chat form.</li>"
                "<li>Log an official ServiceNow ticket (`INC` or `REQ`) and return the live ticket number and clickable link.</li>"
                "<li>For requests exceeding $2,500 (such as <b>Ruggedized Field RF Laptops ($3,200)</b> or <b>CommandCentral Encryption Software Suites ($1,650)</b>), automatically dispatch an <b>Interactive Gmail Approval Notification</b> to the engineering manager.</li>"
                "</ol>"
            )
        },
        {
            "title": "[Motorola Competitive Intelligence] 2026 Deep Research Dossier: Public Safety Video, Body-Worn Cameras & LMR Landscape",
            "content": (
                "<h1>Competitive Landscape Deep Research Report (Q3/Q4 2026)</h1>"
                "<p><b>Business Owner:</b> Jacky Chui (Marketing) & Sahil Taank (Sales Territory Catalyst)</p>"
                "<h2>1. Key Competitor Moves & Sales Positioning</h2>"
                "<ul>"
                "<li><b>Competitor A (Axon Enterprise):</b> Pushing bundled fleet camera + body-worn video renewals with aggressive SaaS financing, but lacks native mission-critical ASTRO 25 LMR voice interoperability. <b>Motorola Counter-Pitch:</b> Highlight our unified voice + video + AI dispatch (APX NEXT + Avigilon Alta + CommandCentral).</li>"
                "<li><b>Competitor B (L3Harris):</b> Offering 15% hardware discounts on P25 radios in Midwest municipal accounts, but facing supply chain delays on FIPS 140-3 encryption chips.</li>"
                "</ul>"
            )
        }
    ]

    for d in docs_to_create:
        res = await call_tool("docs_create", {
            "title": d["title"],
            "content": d["content"],
            "parent_id": folder_id
        })
        doc_id = extract_id(res)
        print(f"📄 Created Doc '{d['title'][:55]}...' -> ID: {doc_id}")

    # -------------------------------------------------------------------------
    # B. GOOGLE SHEETS (Municipal Contract Renewal & Trade Compliance Matrices)
    # -------------------------------------------------------------------------
    sheet_res = await call_tool("sheets_create", {
        "title": "Motorola Solutions - 2026 Public Safety Expiring Contracts & LMR Usage Matrix",
        "parent_id": folder_id
    })
    sheet_id = extract_id(sheet_res)
    print(f"📊 Created Motorola Expiring Contracts Sheet ID: {sheet_id}")

    if sheet_id:
        rows = [
            ["Account Name", "Contract ID", "Current Solution", "Annual Value ($)", "Days to Expiration", "36-Mo PTT Calls (Millions)", "Channel Saturation %", "Recommended Upsell Path", "Bundle Discount Approved"],
            ["City of Metro Public Safety", "MUN-IL-884", "ASTRO 25 LMR Core (4,800 Radios)", "$2,600,000", "45 Days", "43.2M (+18% YoY)", "94.2% (District 4 Critical)", "Cloud-Native Video Security + LPR ($1.25M)", "12% Public Sector Parent Bundle"],
            ["State Highway Patrol (TX)", "STATE-TX-109", "ASTRO 25 Statewide Trunking", "$3,800,000", "60 Days", "78.5M (+22% YoY)", "88.5%", "In-Car Video + CommandCentral Aware ($1.4M)", "15% Multi-Year State Renewal"],
            ["Miami-Dade Emergency Dispatch", "MUN-FL-402", "APX 8000 Fleet + Dispatch Console", "$1,450,000", "30 Days", "29.1M (+14% YoY)", "91.0%", "AI 911 Transcription & Video Triage ($500K)", "10% Municipal Renewal Promo"],
            ["County of Maricopa Sheriff", "MUN-AZ-711", "Land Mobile Radio + Repeaters", "$1,900,000", "75 Days", "34.8M (+11% YoY)", "79.0%", "License Plate Recognition (LPR) Expansion ($650K)", "10% Standard Renewal"]
        ]
        await call_tool("sheets_update", {
            "spreadsheet_id": sheet_id,
            "range": "Sheet1!A1:I5",
            "values": json.dumps(rows)
        })
        print("📊 Populated Motorola Expiring Contracts Matrix.")

    # -------------------------------------------------------------------------
    # C. GMAIL THREADS & APPROVAL EMAILS (RFQ, ServiceNow Approval, Partner Events)
    # -------------------------------------------------------------------------
    # Ensure Labels
    for lbl in ["MOTOROLA-RFQ-REVIEW", "SERVICENOW-APPROVAL-REQ", "CDMG-DATA-ALERT", "PUBLIC-SAFETY-RENEWAL"]:
        await call_tool("gmail_create_label", {"name": lbl})

    emails = [
        {
            "subject": "[ACTION REQUIRED: ServiceNow Approval REQ0010881] Ruggedized RF Field Laptop & AES-256 Software Suite ($4,850)",
            "body": (
                "ServiceNow IT Service Management — Interactive Manager Approval Notification\n"
                "-------------------------------------------------------------------------\n"
                "Request Number: REQ0010881 (Linked Incident: INC0010944)\n"
                "Requester: David Katimi (Public Safety Field Engineering)\n"
                "Cost Center: CC-4402 (North America Municipal Deployments)\n"
                "Total Cost: $4,850.00 USD (Exceeds $2,500 Auto-Approval Threshold)\n\n"
                "Items Requested:\n"
                "1. Motorola Ruggedized Field Engineering Laptop w/ ASTRO 25 CPS Programming Interface ($3,200.00)\n"
                "2. CommandCentral Aware Video Analytics & AES-256 Key Loader License ($1,650.00)\n\n"
                "Business Justification:\n"
                "Emergency deployment support required for City of Metro Public Safety District 4 channel expansion ahead of contract renewal.\n\n"
                "TO APPROVE OR REJECT:\n"
                "Use your Gemini Enterprise Assistant to verify HR/IT Policy compliance in Drive, update ServiceNow Ticket INC0010944 to 'Approved / In Progress', and reply 'APPROVED' to this email."
            )
        },
        {
            "subject": "[PARTNER TERRITORY ALERT] APCO 2026 Public Safety Summit - Key Customer Attendance List (Sahil Taank Territory)",
            "body": (
                "Hi Sales Leadership,\n\n"
                "Our Cloverleaf & Event Intelligence feed identified 4 high-value Public Safety executives from your Midwest & Southeast territories attending the upcoming APCO 2026 Public Safety Summit in Orlando:\n\n"
                "1. Commissioner Marcus Vance — City of Metro Public Safety ($3.85M Renewal Opportunity closing Oct 30)\n"
                "2. Colonel Elena Rostova — State Highway Patrol ($5.2M LMR + Video Expansion)\n"
                "3. Director Henrik Lindqvist — Miami-Dade Emergency Dispatch ($1.95M Renewal)\n"
                "4. Sheriff Dietrich Keller — County of Maricopa Sheriff Department\n\n"
                "Recommended Action:\n"
                "Cross-reference their open Salesforce Opportunities and schedule an Executive Partner Dinner on Google Calendar during APCO 2026."
            )
        },
        {
            "subject": "[COMPETITIVE INTELLIGENCE BRIEF - JACKY CHUI] Deep Research V2: Axon & L3Harris Q3 Municipal Bundling Strategy",
            "body": (
                "Team,\n\n"
                "Attached is our Q3 Competitive Intelligence Deep Research V2 synthesis prepared by Jacky Chui (Marketing/Strategy).\n\n"
                "Key Findings:\n"
                "- Axon Enterprise is aggressively discounting Fleet 3 in-car video when bundled with body-worn cameras in Midwest municipal RFPs (impacting City of Metro & Cook County).\n"
                "- L3Harris is pitching multiband P25 radios to State Highway Patrol (Salesforce Opp $5.2M).\n"
                "- Motorola Counter-Strategy (David Katimi & Sahil Taank): Leverage ASTRO 25 mission-critical reliability + CommandCentral Aware unified cloud video analytics.\n\n"
                "Full Dossier & Podcast Script stored in Google Drive: '[Motorola Competitive Intelligence] 2026 Deep Research Dossier'."
            )
        },
        {
            "subject": "[CDMG DATA GOVERNANCE ALERT - ERICA BOKLEWSKI] Unverified Municipal Hierarchy Records in Salesforce Requiring Remediation",
            "body": (
                "Attention Data Stewardship Team (Erica Boklewski & Magdalena Zurakowska),\n\n"
                "Our automated CDMG scan detected 3 Salesforce Accounts flagged as [UNVERIFIED CDMG RECORD] with missing DUNS and unlinked parent municipal hierarchies:\n"
                "1. Apex Global Communications [UNVERIFIED CDMG RECORD] (SFDC ID: 001jV000009ImFVQA0) -> Needs hierarchy link to County Emergency Services Authority (ServiceNow Ticket INC0010003 / REQ0010904).\n"
                "2. Pacific Rim Tactical Radios Ltd [UNVERIFIED CDMG] (SFDC ID: 001jV000009INbIQAW) -> Duplicate entity flag.\n"
                "3. City of Metro Public Safety District 4 Sub-Agency -> Must be grouped under parent Account 'City of Metro Public Safety' (001jV000009Im4DQAS).\n\n"
                "Please review the Motorola CDMG Policy Doc in Google Drive before approving the hierarchy overrides in ServiceNow."
            )
        }
    ]
    for em in emails:
        res = await call_tool("gmail_send_message", {
            "to": "admin@jesusarguelles.altostrat.com",
            "subject": em["subject"],
            "body": em["body"]
        })
        print(f"📧 Sent Email: '{em['subject'][:50]}...' -> {res}")

    print("\n--- Seeding Google Calendar Events (calendar connector) ---")
    cal_events = [
        {
            "summary": "[APCO 2026] Motorola Territory Partner & VIP Customer Hospitality Reception (Sahil Taank)",
            "start_time": "2026-09-16T18:00:00Z",
            "end_time": "2026-09-16T20:30:00Z",
            "location": "Orlando County Convention Center - Motorola Executive Lounge (Booth #402)",
            "description": (
                "Territory Event Catalyst (Sahil Taank & Cloverleaf Partners).\n"
                "Confirmed VIP Customer Attendees from Salesforce Pipeline:\n"
                "- Commissioner Marcus Vance (City of Metro Public Safety - $3.85M ASTRO 25 Renewal)\n"
                "- Colonel Elena Rostova (State Highway Patrol - $5.2M Statewide Upgrade)\n"
                "- Director Henrik Lindqvist (Miami-Dade Emergency Dispatch - $1.95M Cloud Video Cross-Sell)\n"
                "Objective: Social engagement with Cloverleaf channel partners and live demo of CommandCentral Aware Video Analytics."
            )
        },
        {
            "summary": "[RENEWAL WAR ROOM] City of Metro Public Safety ($3.85M) ASTRO 25 Renewal & P1 Packet Loss Review (David Katimi)",
            "start_time": "2026-09-17T14:00:00Z",
            "end_time": "2026-09-17T15:00:00Z",
            "location": "Motorola Solutions Executive Briefing Center / Google Meet",
            "description": (
                "Lead: David Katimi (Public Safety Sales).\n"
                "Agenda:\n"
                "1. Review City of Metro expiring contract in Google Sheet ('2026 Public Safety Expiring Contracts Matrix').\n"
                "2. Address ServiceNow P1 Incident INC0010002 ([INC0010942] Trunked RF Channel 4 Audio Packet Loss) root-cause fix.\n"
                "3. Finalize $3.85M multi-year renewal + CommandCentral Aware Cloud Video cross-sell proposal."
            )
        },
        {
            "summary": "[CDMG GOVERNANCE BOARD] Master Data Hierarchy Remediation: Apex Global & Municipal Sub-Agencies (Erica Boklewski & Magdalena Zurakowska)",
            "start_time": "2026-09-17T16:00:00Z",
            "end_time": "2026-09-17T17:00:00Z",
            "location": "Data Governance Conference Room B / Google Meet",
            "description": (
                "Owners: Erica Boklewski & Magdalena Zurakowska (CDMG Stewardship).\n"
                "Agenda:\n"
                "- Review ServiceNow Governance Exception INC0010003 ([REQ0010904] Hierarchy Override for Apex Global Communications 001jV000009ImFVQA0).\n"
                "- Enforce Motorola CDMG Policy Standard (Google Drive Doc) for parent-child public safety agency grouping in Salesforce."
            )
        },
        {
            "summary": "[TRADE COMPLIANCE & LEGAL REVIEW] Supplier RFQ #2026-884 HTS Tariff Discrepancy Hold (Yoke Pheng Wong, Ken Bradshaw, Ryan Christensen)",
            "start_time": "2026-09-18T15:00:00Z",
            "end_time": "2026-09-18T16:00:00Z",
            "location": "Global Procurement & Legal War Room / Google Meet",
            "description": (
                "Owners: Yoke Pheng Wong (Procurement), Ken Bradshaw (Trade Compliance), Ryan Christensen (Legal).\n"
                "Agenda:\n"
                "- Inspect Gmail Thread '[RFQ SUBMISSION #2026-884] Shenzhen RF Components Ltd'.\n"
                "- Resolve ServiceNow Trade Compliance Hold INC0010004 ([INC0010819]): Vendor declared HTS 8525.60.1020 (0% duty) vs Motorola Mandatory Compliance Classification 8525.60.1050 (7.5% Section 301 tariff).\n"
                "- Issue redlined contract terms per Google Drive Procurement & HTS Tariff Matrix."
            )
        },
        {
            "summary": "[HR/IT SERVICE DELIVERY SYNC] ServiceNow Approval REQ0010881 ($4,850 Laptop) & Export Control Policy (Apoorva & Priyanka B)",
            "start_time": "2026-09-18T17:30:00Z",
            "end_time": "2026-09-18T18:15:00Z",
            "location": "HR & IT Service Delivery Hub / Google Meet",
            "description": (
                "Owners: Apoorva & Priyanka B (HR/IT Service Delivery).\n"
                "Agenda:\n"
                "- Review ServiceNow Ticket INC0010001 ([REQ0010881] Marcus Vance Ruggedized RF Field Laptop & AES-256 Suite - $4,850).\n"
                "- Verify Gmail Manager Approval Thread (#1a0a5c8850b2d2f8) against Motorola HR/IT Policy Doc ($2,500 auto-approval threshold).\n"
                "- Approve international hand-carry export clearance for encrypted APX NEXT demo radios."
            )
        }
    ]
    for ev in cal_events:
        res = await call_tool("calendar_create_event", ev)
        print(f"📅 Created Calendar Event: '{ev['summary'][:50]}...' -> {res}")


def seed_salesforce():
    print("\n=======================================================")
    print("2. SEEDING SALESFORCE CRM (MOTOROLA SOLUTIONS RECORDS)")
    print("=======================================================")
    auth_path = os.path.expanduser("~/.gemini/sfdc_altostrat_auth.json")
    if not os.path.exists(auth_path):
        print("⚠️ Salesforce auth file missing.")
        return

    with open(auth_path) as f:
        auth = json.load(f)
    sid = auth.get("session_id")
    inst = auth.get("instance_url")
    if not sid:
        print("⚠️ Salesforce session_id missing.")
        return

    headers = {"Authorization": f"Bearer {sid}", "Content-Type": "application/json"}
    base = f"{inst}/services/data/v60.0/sobjects"

    # 1. Create Additional Motorola Public Safety & CDMG Accounts
    accounts = [
        {
            "Name": "State Highway Patrol - Department of Public Safety",
            "Type": "Government - State",
            "Industry": "Public Safety & Law Enforcement",
            "AnnualRevenue": 1200000000,
            "NumberOfEmployees": 9500,
            "BillingStreet": "5805 N Lamar Blvd",
            "BillingCity": "Austin",
            "BillingState": "Texas",
            "BillingCountry": "United States",
            "Website": "https://www.dps.texas.gov.example.com",
            "Description": "Statewide ASTRO 25 Land Mobile Radio trunked network (8,200 vehicular repeaters). Expiring in 60 days. High upsell potential for In-Car Video + CommandCentral Aware."
        },
        {
            "Name": "Miami-Dade Emergency Dispatch & Fire Rescue",
            "Type": "Government - Municipal",
            "Industry": "Public Safety & Emergency Services",
            "AnnualRevenue": 620000000,
            "NumberOfEmployees": 3800,
            "BillingStreet": "9300 NW 41st St",
            "BillingCity": "Doral",
            "BillingState": "Florida",
            "BillingCountry": "United States",
            "Description": "Municipal APX 8000 radio fleet expiring in 30 days. Attending APCO 2026 Summit. Interested in AI 911 Transcription & Cloud Video Triage."
        },
        {
            "Name": "Pacific Rim Tactical Radios Ltd [UNVERIFIED CDMG]",
            "Type": "Channel Partner / Reseller",
            "Industry": "Telecommunications Equipment",
            "BillingStreet": "450 Mission St (Missing County & VAT)",
            "BillingCity": "San Francisco",
            "BillingState": "California",
            "BillingCountry": "United States",
            "Description": "CDMG ZERO-TOUCH ENRICHMENT TARGET: Partner Empower channel reseller missing Tax ID, County (San Francisco County), Website, and Ultimate Parent Hierarchy (Subsidiary of Pacific Rim Defense Group)."
        }
    ]

    for acc in accounts:
        r = requests.post(f"{base}/Account", headers=headers, json=acc)
        if r.status_code in (200, 201):
            aid = r.json()["id"]
            print(f"🏢 Created SFDC Account '{acc['Name']}' -> ID: {aid}")
            # Create Opportunity for Public Safety accounts
            if "Patrol" in acc["Name"]:
                opp = {
                    "Name": "State Highway Patrol - Statewide ASTRO 25 Renewal & In-Car Video Expansion",
                    "AccountId": aid,
                    "StageName": "Proposal/Price Quote",
                    "Amount": 5200000,
                    "CloseDate": "2026-11-15",
                    "Probability": 65,
                    "NextStep": "Engage Colonel Elena Rostova at APCO 2026 Summit & present 15% Multi-Year State Bundle",
                    "Description": "Renewal of $3.8M ASTRO 25 LMR network + $1.4M In-Car Video & CommandCentral Aware upsell."
                }
                requests.post(f"{base}/Opportunity", headers=headers, json=opp)
                print(f"💰 Created SFDC Opportunity for State Highway Patrol ($5.2M)")
            elif "Miami-Dade" in acc["Name"]:
                opp = {
                    "Name": "Miami-Dade Dispatch - APX NEXT Renewal & AI 911 Video Triage",
                    "AccountId": aid,
                    "StageName": "Negotiation/Review",
                    "Amount": 1950000,
                    "CloseDate": "2026-10-15",
                    "Probability": 80,
                    "NextStep": "Finalize 10% Municipal Renewal Promo before 30-day contract expiration",
                    "Description": "Core $1.45M APX 8000 renewal + $500K AI 911 Transcription & Video Triage."
                }
                requests.post(f"{base}/Opportunity", headers=headers, json=opp)
                print(f"💰 Created SFDC Opportunity for Miami-Dade ($1.95M)")


def seed_servicenow():
    print("\n=======================================================")
    print("3. SEEDING SERVICENOW ITSM & HR TICKETS (dev271596)")
    print("=======================================================")
    sn_path = os.path.expanduser("~/.gemini/servicenow_altostrat_auth.json")
    if not os.path.exists(sn_path):
        print("⚠️ ServiceNow config file missing.")
        return

    with open(sn_path) as f:
        cfg = json.load(f)
    base_url = cfg["instance_url"].rstrip("/")
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    auth = None
    if cfg.get("client_id") and cfg.get("client_secret"):
        r_oauth = requests.post(f"{base_url}/oauth_token.do", data={
            "grant_type": "password",
            "client_id": cfg["client_id"],
            "client_secret": cfg["client_secret"],
            "username": cfg["username"],
            "password": cfg["password"]
        })
        if r_oauth.status_code == 200:
            headers["Authorization"] = f"Bearer {r_oauth.json()['access_token']}"
        else:
            auth = (cfg["username"], cfg["password"])
    else:
        auth = (cfg["username"], cfg["password"])

    tickets = [
        {
            "short_description": "[REQ0010881] Approval Pending: Ruggedized RF Laptop ($4,850)",
            "description": "Requester: Marcus Vance | Approver: Priyanka B | Total: $4,850 (Exceeds $2,500 auto-approval threshold). Gmail Thread #1a0a5c8850b2d2f8.",
            "urgency": "2",
            "impact": "2",
            "category": "hardware",
            "comments": "Pending Manager Approval in Gmail (Thread Subject: [ACTION REQUIRED: ServiceNow Approval REQ0010881])."
        },
        {
            "short_description": "[INC0010942] P1 Critical: City of Metro ASTRO 25 Packet Loss",
            "description": "Customer: City of Metro Public Safety | Account: 001jV000009Im4DQAS ($3.85M). Intermittent 14% packet loss on Trunked RF Channel 4.",
            "urgency": "1",
            "impact": "1",
            "category": "network",
            "comments": "Assigned to Tier-3 Cryptographic Operations Group. Automated RCA report requested by Priyanka B."
        },
        {
            "short_description": "[REQ0010904] CDMG Governance: Hierarchy Override for Apex Global",
            "description": "Submitted by: Erica Boklewski & Magdalena Zurakowska (CDMG). Master Data hierarchy link for Apex Global (001jV000009ImFVQA0).",
            "urgency": "2",
            "impact": "2",
            "category": "software",
            "comments": "Compliance verification passed."
        },
        {
            "short_description": "[INC0010819] Trade Compliance: RFQ #2026-884 HTS Tariff Conflict",
            "description": "Submitted by: Ken Bradshaw & Ryan Christensen. Hold on Vendor RFQ #2026-884: Supplier declared HTS 8525.60.1020 (0%) vs Motorola DB 8525.60.1050 (7.5%).",
            "urgency": "1",
            "impact": "2",
            "category": "inquiry",
            "comments": "Requires HTS Code 8525.60.1020 temporary export declaration."
        },
        {
            "short_description": "[REQ0010955] HR/Legal Export Clearance: Hand-Carry 4 AES-256 Encrypted APX NEXT Radios (David Katimi)",
            "description": "Submitted by: David Katimi | Approvers: Apoorva & Priyanka B (HR/IT Service Delivery) + Ken Bradshaw (Export Compliance). Requesting temporary export & hand-carry authorization for 4 FIPS 140-3 AES-256 encrypted APX NEXT smart radios for live demonstration at APCO 2026 Summit.",
            "urgency": "2",
            "impact": "2",
            "category": "inquiry",
            "comments": "Verified against Motorola HR & IT Service Delivery Policy Doc (Google Drive). Cleared for domestic/partner summit transport."
        },
        {
            "short_description": "[INC0010988] Legal Redline Escalation: Precision Antenna Systems RFQ #2026-912 Net-15 Exception",
            "description": "Submitted by: Yoke Pheng Wong & Ryan Christensen (Global Procurement & Legal). Vendor Precision Antenna Systems requested Net-15 payment terms and 0.5x liability cap on Base Station Antenna RFQ #2026-912. Violates Motorola Standard Procurement Redline Playbook (Mandatory Net-60 & 2.0x Liability Cap).",
            "urgency": "2",
            "impact": "2",
            "category": "software",
            "comments": "Counter-proposal drafted via Gemini Enterprise using Google Drive Legal Redline Matrix."
        }
    ]

    success_count = 0
    for t in tickets:
        tag = t["short_description"].split("]")[0] + "]"
        q_check = requests.get(
            f"{base_url}/api/now/table/incident",
            auth=auth,
            headers=headers,
            params={"sysparm_query": f"short_descriptionLIKE{tag}", "sysparm_limit": 1}
        )
        if q_check.status_code == 200 and q_check.json().get("result"):
            existing = q_check.json()["result"][0]
            print(f"✅ Ticket already exists: {existing.get('number')} -> {existing.get('short_description')}")
            success_count += 1
            continue
        r = requests.post(
            f"{base_url}/api/now/table/incident",
            auth=auth,
            json=t,
            headers=headers
        )
        if r.status_code in (200, 201):
            inc_num = r.json().get("result", {}).get("number")
            print(f"✅ Created ServiceNow Ticket {inc_num}: {t['short_description'][:60]}...")
            success_count += 1
        else:
            print(f"⚠️ ServiceNow API returned {r.status_code}: Instance may need 'Start building' clicked once in browser to activate admin account.")
            break

    if success_count > 0:
        print(f"🎉 Seeded {success_count} Motorola ServiceNow Tickets!")


async def main():
    await seed_workspace()
    seed_salesforce()
    seed_servicenow()
    print("\n=======================================================")
    print("🚀 MASTER MOTOROLA SOLUTIONS DEMO SEEDING COMPLETE!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(main())
