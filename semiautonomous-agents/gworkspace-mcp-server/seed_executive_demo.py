"""
Finish populating the Google Sheet rows, 3 Gmail threads, 1 Gmail Draft,
and Calendar Event in admin@jesusarguelles.altostrat.com using MCP tools.
"""
import asyncio
import json
from datetime import datetime
from server import mcp, auth_manager

async def call_tool(name: str, args: dict) -> str:
    res = await mcp.call_tool(name, args)
    if hasattr(res, "content") and res.content:
        return res.content[0].text
    return str(res)

async def main():
    print("=== Verifying Authentication ===")
    verify_res = await call_tool("gworkspace_verify_login", {})
    print(verify_res)

    sheet_id = "15LDLrpSwUqJd5rQOgr0djjHs-ai7NlwoyB2lZ7PcClQ"

    print("\n1. Populating Q3 Regional Revenue Google Sheet...")
    rows = [
        ["Region", "Q3 Quota ($M)", "Q3 Actual ($M)", "Variance (%)", "Key Slipped Enterprise Deals", "Primary Deal Blocker"],
        ["North America", "45.0", "47.2", "+4.9%", "None (Acme Corp $500K pending today)", "Acme MSA Redline on Payment Terms"],
        ["EMEA", "32.0", "29.4", "-8.1%", "NordicBank ($1.4M), EuroLogistics ($850K), RhinePharma ($600K)", "GDPR EU-Central Data Residency & Net-60 Hold"],
        ["APAC", "18.5", "18.8", "+1.6%", "Tokyo FinTech ($420K)", "Moved to Q4 Fiscal Budget"],
        ["LATAM", "12.0", "12.5", "+4.2%", "None", "Exceeded target"]
    ]
    write_res = await call_tool("sheets_update", {
        "spreadsheet_id": sheet_id,
        "range": "Q3_Revenue_Summary!A1:F5",
        "values": json.dumps(rows)
    })
    print(write_res)

    print("\n2. Sending 3 Cross-Silo Demo Emails to Gmail Inbox...")
    email1_res = await call_tool("gmail_send_message", {
        "to": "admin@jesusarguelles.altostrat.com",
        "subject": "[URGENT] Acme Corp Renewal - Final Redline Demands before Today's Call",
        "body": (
            "Hi Jesus,\n\n"
            "Ahead of our 2:00 PM Executive Renewal & SLA Finalization meeting today, I just got out of a review with Acme Corp's CFO and General Counsel (Marcus Vance).\n\n"
            "They are ready to sign the $500,000 renewal today, BUT they have issued three non-negotiable redline demands that conflict with our MSA v3 document in Google Drive:\n\n"
            "1. Payment Terms: Acme refuses our standard Net-30 terms. Their procurement policy mandates Net-60 payment terms.\n"
            "2. Limitation of Liability: Acme is demanding we raise the aggregate liability cap from $500,000 (1x ACV) to $2,000,000 USD (4x ACV).\n"
            "3. Data Residency Question: Their CISO asked us to confirm whether their EU subsidiary data will be stored in Frankfurt (eu-central1) or US regions.\n\n"
            "Please review the MSA v3 redline doc in Drive and let me know what compromise we can offer on today's call.\n\n"
            "Best,\n"
            "Marcus Vance | VP Global Procurement, Acme Corp"
        )
    })
    print("Email 1:", email1_res)

    email2_res = await call_tool("gmail_send_message", {
        "to": "admin@jesusarguelles.altostrat.com",
        "subject": "EMEA Sales Weekly Executive Update - Why Q3 Missed Target by 8.1%",
        "body": (
            "Hi Leadership Team,\n\n"
            "As you can see in the 'Q3 2026 Regional Revenue & Enterprise Slippage Tracker' spreadsheet in Google Drive, EMEA closed Q3 at $29.4M against our $32.0M quota (-8.1% variance).\n\n"
            "Here is the exact qualitative breakdown of why our top 3 enterprise deals ($2.85M total) slipped to Q4:\n"
            "- NordicBank ($1.4M ACV): Their Data Protection Officer (DPO) halted signature yesterday because Section 12.1 of our standard MSA restricts data residency to US-East1/US-Central1. They require a binding GDPR Annex guaranteeing Frankfurt (eu-central1) storage.\n"
            "- EuroLogistics ($850K ACV): Procurement froze PO issuance demanding Net-60 payment terms instead of Net-30.\n"
            "- RhinePharma ($600K ACV): Technical sign-off is complete, but CFO signature slipped to October 15 due to Q3 board lock.\n\n"
            "If we approve an EU Data Residency addendum and a Net-45 compromise, we can close both NordicBank and EuroLogistics in the first week of Q4.\n\n"
            "Regards,\n"
            "Elena Rostova | VP EMEA Sales"
        )
    })
    print("Email 2:", email2_res)

    email3_res = await call_tool("gmail_send_message", {
        "to": "admin@jesusarguelles.altostrat.com",
        "subject": "[P1 ESCALATION] Checkout Payment Gateway Latency Spike (>2,500ms) - Action Required",
        "body": (
            "INCIDENT ALERT - SEVERITY P1\n"
            "Service: checkout-token-service-v2 (Primary Region: us-east1)\n\n"
            "Telemetry Summary:\n"
            "- Over the last 45 minutes, p99 latency on checkout-token-service-v2 spiked to 2,540ms (breaching our 99.95% SLA threshold).\n"
            "- Cloud Monitoring shows Redis connection pool saturation at 100% (500/500 active connections) caused by synchronous retry storms from downstream bank throttling.\n\n"
            "Request for Authorization:\n"
            "Per our 'Payment Gateway Microservice - P1 Latency & Failover Runbook' in Google Drive, standard pod restarts will worsen the retry storm. "
            "Please confirm if SRE is authorized to execute Mitigation Step 3B (draining 60% traffic to us-central1 and raising REDIS_MAX_CONNECTIONS to 2,500).\n\n"
            "— SRE Automated War-Room Alert"
        )
    })
    print("Email 3:", email3_res)

    print("\n3. Creating Executive Compromise Draft in Gmail...")
    draft_res = await call_tool("gmail_create_draft", {
        "to": "marcus.vance@acmecorp.example.com",
        "subject": "Re: [URGENT] Acme Corp Renewal - Approved Executive Compromise for 2:00 PM Call",
        "body": (
            "Hi Marcus,\n\n"
            "Ahead of our 2:00 PM call today, I reviewed your redline requests against our MSA v3 in Google Drive with our CFO and Legal team. Here is our approved executive counter-offer to close today:\n\n"
            "1. Payment Terms: Approved compromise at Net-45 (splitting the difference between our standard Net-30 in Section 4.2 and your Net-60 request).\n"
            "2. Liability Cap: Approved increase to $1,000,000 USD (2x ACV) for data/confidentiality claims, up from $500,000 in Section 9.1.\n"
            "3. EU Data Residency: We will attach our GDPR EU-Central1 (Frankfurt) Data Residency Addendum for your European subsidiary.\n\n"
            "Looking forward to finalizing on today's call.\n\n"
            "Best regards,\n"
            "Jesus Chavez"
        )
    })
    print("Draft:", draft_res)

    print("\n4. Creating Executive Calendar Event for Today...")
    now = datetime.utcnow()
    start_dt = now.replace(hour=18, minute=0, second=0, microsecond=0).isoformat() + "Z"
    end_dt = now.replace(hour=19, minute=0, second=0, microsecond=0).isoformat() + "Z"
    cal_res = await call_tool("calendar_create_event", {
        "summary": "Executive Renewal & SLA Finalization: Acme Corp ($500K ACV)",
        "start_time": start_dt,
        "end_time": end_dt,
        "description": (
            "High-stakes renewal negotiation with Marcus Vance (VP Procurement, Acme Corp).\n\n"
            "Required Prep:\n"
            "1. Cross-reference Marcus's latest urgent email in Gmail against 'Acme Corp - Master Services Agreement (MSA v3 Redline - 2026)' in Google Drive.\n"
            "2. Address Net-30 vs Net-60 payment terms, $500K vs $2M liability cap, and US vs EU data residency."
        ),
        "location": "Google Meet / Executive Boardroom"
    })
    print("Calendar Event:", cal_res)

    print("\n=== ALL DEMO ARTIFACTS SEEDED SUCCESSFULLY IN admin@jesusarguelles.altostrat.com ===")

if __name__ == "__main__":
    asyncio.run(main())
