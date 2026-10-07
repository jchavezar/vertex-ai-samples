"""Seed an extensive, hyper-realistic Enterprise Demo Universe into admin@jesusarguelles.altostrat.com.

Designed specifically for Gemini Enterprise (GE App) demos showcasing cross-connector
synthesis across:
  - Gong (Simulated Call Transcripts, AI Deal Risk Alerts, Sentiment Briefings)
  - Google Drive (Architecture Whitepapers, Deal Desk Matrices, Executive QBR Decks/Docs)
  - Google Sheets (Enterprise Discount & Migration Credit Approval Matrix)
  - Gmail (Multi-thread CISO escalations, Gong Bot alerts, Deal Desk approvals, Drafts, Labels)
  - Google Calendar (Executive Go/No-Go Reviews, Deal Desk Sign-offs, Emergency Save Calls)
"""

import asyncio
import datetime
import json
import re
from server import mcp


async def call_tool(name: str, args: dict) -> str:
    res = await mcp.call_tool(name, args)
    if hasattr(res, "content") and res.content:
        return res.content[0].text
    return str(res)


def extract_id(text: str) -> str:
    m = re.search(r"ID:\s*`([^`]+)`", text)
    return m.group(1) if m else ""


async def seed_universe():
    print("🚀 Starting Enterprise Demo Universe Seeding for admin@jesusarguelles.altostrat.com...")

    # 1. Find or create root Demo Folder in Google Drive
    find_res = await call_tool("drive_find_folder", {"folder_name": "Gemini Enterprise Executive Demo - Acme & Operations"})
    folder_id = extract_id(find_res)
    if not folder_id:
        create_res = await call_tool("drive_create_folder", {"name": "Gemini Enterprise Executive Demo - Acme & Operations"})
        folder_id = extract_id(create_res)
    print(f"📁 Executive Demo Root Folder ID: {folder_id}")

    # Create dedicated subfolder for Strategic Deal Desk & Gong Intelligence
    find_sub = await call_tool("drive_find_folder", {"folder_name": "Vanguard Global & Gong Deal Intelligence"})
    vanguard_folder_id = extract_id(find_sub)
    if not vanguard_folder_id:
        create_sub = await call_tool("drive_create_folder", {
            "name": "Vanguard Global & Gong Deal Intelligence",
            "parent_id": folder_id
        })
        vanguard_folder_id = extract_id(create_sub)
    print(f"📁 Subfolder 'Vanguard Global & Gong Deal Intelligence' ID: {vanguard_folder_id}")

    # =========================================================================
    # 2. GOOGLE DOCS (Drive Grounding for Gong Transcripts, Whitepapers, QBRs)
    # =========================================================================

    # Doc A: Gong Call Transcript & AI Deal Intelligence (Vanguard Global $2.4M Deal)
    gong_vanguard_title = "[Gong Call Transcript & AI Deal Intelligence] Vanguard Global Financial - Architecture & CISO Security Review"
    gong_vanguard_body = (
        "<h1>Gong Call Intelligence & Verbatim Transcript</h1>"
        "<p><b>Account:</b> Vanguard Global Financial ($2,400,000 ACV - Multi-Year Enterprise AI Platform)<br>"
        "<b>Call Date:</b> September 14, 2026 | <b>Duration:</b> 52 mins | <b>Gong Deal Score:</b> 68/100 (At Risk - Competitor Mentioned)<br>"
        "<b>Participants:</b> Marcus Vance (CISO, Vanguard Global), Elena Rostova (VP Cloud Infrastructure, Vanguard), Jesus Arguelles (Enterprise Account Director)</p>"
        "<h2>1. Executive AI Call Summary (Gong Spotlight)</h2>"
        "<ul>"
        "<li><b>Primary Buying Signal:</b> Vanguard wants to deploy Gemini Enterprise across 14,000 wealth advisors and investment analysts before Q4.</li>"
        "<li><b>Critical Technical Objection #1 (EU Data Residency):</b> CISO Marcus Vance explicitly stated that their European Wealth Division requires strict <b>Frankfurt (europe-west3) data residency</b> for all RAG indexes and embeddings.</li>"
        "<li><b>Critical Technical Objection #2 (Zero Data Retention - ZDR):</b> Vanguard Legal mandates contractual verification that zero customer prompts, financial models, or attachments are cached or used for model training.</li>"
        "<li><b>Competitor Threat (AWS Bedrock / Anthropic):</b> Elena Rostova revealed that AWS offered a <b>$250,000 Migration & Proof-of-Concept Credit</b> if Vanguard signs their Enterprise Addendum by Friday.</li>"
        "</ul>"
        "<h2>2. Key Verbatim Transcript Excerpts</h2>"
        "<p><b>[14:22] Marcus Vance (CISO, Vanguard Global):</b> <i>\"Look, we love the Workspace and Gong native connectors in Gemini Enterprise. Our bankers spend 4 hours a day digging through Drive, Gmail, and call notes. But I cannot sign off on a $2.4M contract unless you prove in writing that our EU wealth client data stays physically pinned to Frankfurt (europe-west3) with customer-managed encryption keys (CMEK) and Zero Data Retention.\"</i></p>"
        "<p><b>[28:45] Elena Rostova (VP Cloud Infrastructure, Vanguard):</b> <i>\"To be completely transparent with you, Jesus, AWS executive leadership offered us a $250,000 migration credit yesterday to offset our switching costs if we standardize on Bedrock. If you can match or beat that migration credit and send us the official EU Sovereign Architecture whitepaper before our 3:30 PM Go/No-Go call today, we will sign with Google.\"</i></p>"
        "<h2>3. Gong Recommended Next Best Actions</h2>"
        "<ol>"
        "<li>Send official <b>Enterprise AI Security, Zero-Data-Retention (ZDR) & EU Frankfurt Sovereign Cloud Architecture</b> policy document.</li>"
        "<li>Request Deal Desk approval for a <b>$280,000 Enterprise Migration Credit</b> (Tier-1 Strategic Exception) to beat AWS's $250K offer.</li>"
        "<li>Update executive reply draft in Gmail and attach CISO compliance matrix before 3:30 PM meeting.</li>"
        "</ol>"
    )
    doc1 = await call_tool("docs_create", {
        "title": gong_vanguard_title,
        "content": gong_vanguard_body,
        "parent_id": vanguard_folder_id
    })
    print(f"📄 Created Gong Transcript Doc:\n{doc1}")

    # Doc B: Official Google Security & EU Frankfurt Sovereign Architecture Whitepaper
    sec_title = "Enterprise AI Security, Zero-Data-Retention (ZDR) & EU Frankfurt Sovereign Cloud Architecture (2026 Approved Policy)"
    sec_body = (
        "<h1>Enterprise Security & Compliance Reference Architecture (2026 Official Standard)</h1>"
        "<p><b>Document ID:</b> SEC-ARCH-2026-V4 | <b>Classification:</b> Customer Shareable (CISO Approved)</p>"
        "<h2>1. Zero Data Retention (ZDR) & No-Training Guarantee</h2>"
        "<p>Under Google Cloud Enterprise Terms of Service (Section 4.2 - Data Privacy & AI Governance):</p>"
        "<ul>"
        "<li><b>Zero Data Retention (ZDR):</b> All prompts, grounding context from Workspace/Drive/Gong, and model completions processed through Gemini Enterprise (Agentspace) and Vertex AI are ephemeral. Zero payload data is written to persistent storage or inspected by human reviewers.</li>"
        "<li><b>Strict Model Isolation:</b> Customer data is <b>NEVER</b> used to train, fine-tune, or improve Google foundation models (including Gemini 3.7 Flash and Gemini 3 Pro).</li>"
        "</ul>"
        "<h2>2. EU Sovereign Data Residency & Frankfurt (europe-west3) Pinning</h2>"
        "<p>For regulated European financial institutions (MiFID II, DORA, BaFin compliance):</p>"
        "<ul>"
        "<li><b>Regional Endpoint Pinning:</b> All Discovery Engine RAG indexes, Vector Search embeddings, and LLM inference endpoints can be strictly pinned to <b>Frankfurt (europe-west3)</b>.</li>"
        "<li><b>CMEK & VPC Service Controls:</b> Supports Customer-Managed Encryption Keys (Cloud KMS in europe-west3) and VPC-SC perimeters preventing data exfiltration outside the European Union.</li>"
        "</ul>"
        "<h2>3. CISO Clause for Contract Addendum</h2>"
        "<p><i>\"Provider guarantees that Customer's European Wealth Division data shall remain exclusively within the Frankfurt (europe-west3) region at rest and in transit, governed by Zero Data Retention (ZDR) and CMEK encryption.\"</i></p>"
    )
    doc2 = await call_tool("docs_create", {
        "title": sec_title,
        "content": sec_body,
        "parent_id": vanguard_folder_id
    })
    print(f"📄 Created Security Architecture Doc:\n{doc2}")

    # Doc C: Gong Executive Sentiment Briefing for NordicBank AB ($1.4M Renewal at Risk)
    nordic_title = "[Gong Executive Briefing] NordicBank AB ($1.4M Renewal) - QBR Sentiment & Churn Prevention Playbook"
    nordic_body = (
        "<h1>Gong Executive Account Health & Sentiment Analysis</h1>"
        "<p><b>Account:</b> NordicBank AB (Stockholm, Sweden) | <b>Contract Value:</b> $1,400,000 ARR (EMEA Region)<br>"
        "<b>Renewal Status:</b> Slipped from Q3 to Q4 (Primary driver of EMEA -8.1% revenue variance)<br>"
        "<b>Gong Sentiment Score:</b> 42/100 (Escalated) | <b>Executive Sponsor:</b> Henrik Lindqvist (CIO, NordicBank)</p>"
        "<h2>1. Root Cause of Q3 Renewal Slippage (From Last 3 Gong Calls)</h2>"
        "<ul>"
        "<li>During the September 8th Payment Gateway latency incident (>2,500ms spike), NordicBank experienced a 14-minute delay in retail FX settlement alerts.</li>"
        "<li>CIO Henrik Lindqvist demanded:"
        "<ol>"
        "<li>Formal confirmation that <b>Mitigation Step 3B (REDIS_MAX_CONNECTIONS=2500 & traffic draining)</b> has been permanently applied to production.</li>"
        "<li>A <b>10% SLA Service Credit ($140,000 value)</b> applied toward their Q4 renewal invoice.</li>"
        "</ol>"
        "</li>"
        "</ul>"
        "<h2>2. Recommended Executive Save Strategy</h2>"
        "<p>Combine proof of technical remediation (from the SRE Payment Gateway Runbook) with a pre-approved 10% SLA renewal credit from the Deal Desk Matrix (Ref #DD-8820) to close the $1.4M renewal this week.</p>"
    )
    doc3 = await call_tool("docs_create", {
        "title": nordic_title,
        "content": nordic_body,
        "parent_id": vanguard_folder_id
    })
    print(f"📄 Created NordicBank Gong Briefing Doc:\n{doc3}")

    # =========================================================================
    # 3. GOOGLE SHEETS (Deal Desk Discount & Migration Credit Approval Matrix)
    # =========================================================================
    sheet_title = "2026 Enterprise Deal Desk - Discount, SLA Credit & Migration Funding Matrix"
    sheet_res = await call_tool("sheets_create", {
        "title": sheet_title,
        "parent_id": vanguard_folder_id
    })
    sheet_id = extract_id(sheet_res)
    print(f"📊 Created Deal Desk Matrix Sheet ID: {sheet_id}")

    matrix_values = [
        ["Deal Tier", "ACV Threshold", "Max Standard Discount", "Max Migration Credit (Competitor Displacement)", "Max SLA Retention Credit", "Approver Required", "Policy Status"],
        ["Tier 1 - Mega Strategic", "$2,000,000+", "18.0%", "$300,000 (Approved for AWS/Anthropic Displacement)", "15.0%", "SVP Global Sales (Auto-Approved via Deal Desk)", "ACTIVE - Q3/Q4 PROMO"],
        ["Tier 2 - Enterprise Growth", "$1,000,000 - $1,999,999", "12.0%", "$150,000", "10.0% ($140K max for NordicBank)", "VP Regional Sales", "ACTIVE"],
        ["Tier 3 - Commercial Mid-Market", "$250,000 - $999,999", "8.0%", "$50,000", "5.0%", "Regional Sales Director", "ACTIVE"],
        ["Account Exception: Vanguard Global", "$2,400,000", "15.0% Approved", "$280,000 Approved (Beats AWS $250K Offer)", "N/A - Net New", "APPROVED - Deal Desk Ref #DD-9941", "READY FOR CISO SIGN-OFF"],
        ["Account Exception: NordicBank AB", "$1,400,000", "10.0% Renewal", "$0", "10.0% ($140,000 Approved SLA Credit)", "APPROVED - Deal Desk Ref #DD-8820", "READY FOR CIO SAVE CALL"]
    ]
    await call_tool("sheets_update", {
        "spreadsheet_id": sheet_id,
        "range": "Sheet1!A1:G6",
        "values": json.dumps(matrix_values)
    })
    print("📊 Populated Deal Desk Approval Matrix rows.")

    # =========================================================================
    # 4. GMAIL LABELS, THREADS, AND DRAFTS (Multi-Thread Realistic Inbox)
    # =========================================================================
    desired_labels = ["GONG-DEAL-RISK", "CISO-SECURITY-REVIEW", "DEAL-DESK-APPROVED", "EMEA-CHURN-RISK"]
    for lbl in desired_labels:
        lbl_res = await call_tool("gmail_create_label", {"name": lbl})
        print(f"🏷️ Label creation result ({lbl}): {lbl_res.splitlines()[0] if lbl_res else ''}")

    # Email 1: Gong Automated Deal Risk Alert (Vanguard Global)
    e1_subj = "[Gong Deal Intelligence Alert] Competitor Mention (AWS $250K Credit) & CISO Security Blockers in Vanguard Global Call"
    e1_body = (
        "Automated Deal Risk Alert from Gong Revenue Intelligence:\n\n"
        "Account: Vanguard Global Financial ($2.4M ACV)\n"
        "Call Analyzed: Architecture & Security Deep Dive (Sep 14, 2026)\n"
        "Gong Risk Rating: HIGH (Competitor Displacement Threat)\n\n"
        "Key Moments Detected in Call Recording:\n"
        "1. [14:22] CISO Marcus Vance: Mandatory requirement for Frankfurt (europe-west3) data residency and Zero Data Retention (ZDR) contractual addendum.\n"
        "2. [28:45] VP Infrastructure Elena Rostova: Disclosed $250,000 migration credit offer from AWS Bedrock if signed by Friday.\n\n"
        "Action Required:\n"
        "Please cross-reference our '2026 Enterprise Deal Desk Matrix' in Google Drive (Ref #DD-9941 authorizes $280,000 migration credit) and send the 'Enterprise AI Security & EU Frankfurt Sovereign Architecture' whitepaper before today's 3:30 PM Go/No-Go meeting."
    )
    msg1 = await call_tool("gmail_send_message", {
        "to": "admin@jesusarguelles.altostrat.com",
        "subject": e1_subj,
        "body": e1_body
    })
    print(f"📧 Sent Email 1 (Gong Alert): {msg1}")

    # Email 2: CISO Marcus Vance Direct Email (Vanguard Global)
    e2_subj = "URGENT: Vanguard Global ($2.4M Agreement) - Final CISO Security & Migration Credit Requirements before 3:30 PM Call"
    e2_body = (
        "Hi Jesus,\n\n"
        "Following up on our Gong recorded architecture session yesterday with Elena and my security engineering team.\n\n"
        "We are ready to move forward with Gemini Enterprise for our 14,000 global wealth advisors, provided you can confirm three items in writing before our 3:30 PM Executive Go/No-Go review today:\n\n"
        "1. EU Data Residency: Can you guarantee that our European Wealth Division RAG indexes and embeddings are strictly pinned to Frankfurt (europe-west3) with CMEK?\n"
        "2. Zero Data Retention (ZDR): Does Google contractually guarantee Zero Data Retention and zero model training on our financial prompts and documents?\n"
        "3. Commercial Parity: As Elena mentioned, AWS offered us a $250,000 migration credit. Can Google Deal Desk match or exceed this funding so I can get CFO sign-off today?\n\n"
        "Best regards,\n"
        "Marcus Vance\n"
        "Chief Information Security Officer (CISO) | Vanguard Global Financial"
    )
    msg2 = await call_tool("gmail_send_message", {
        "to": "admin@jesusarguelles.altostrat.com",
        "subject": e2_subj,
        "body": e2_body
    })
    print(f"📧 Sent Email 2 (CISO Escalation): {msg2}")

    # Email 3: NordicBank CIO Henrik Lindqvist Escalation ($1.4M EMEA Renewal)
    e3_subj = "[URGENT ESCALATION] NordicBank AB ($1.4M Renewal) - Payment Gateway SLA & Q4 Renewal Hold"
    e3_body = (
        "Jesus,\n\n"
        "As discussed on our Gong QBR call, NordicBank AB is holding signature on our $1,400,000 annual renewal (which slipped from Q3 into Q4).\n\n"
        "Before I release the PO this week, our Board requires:\n"
        "1. Engineering verification of the exact root-cause fix applied for the Checkout/Payment Gateway latency spike (>2,500ms). Specifically, confirm whether Mitigation Step 3B (Redis connection pool scaling and traffic draining) was executed.\n"
        "2. Deal Desk confirmation of the 10% SLA Retention Credit ($140,000 value) referenced in Deal Desk Ref #DD-8820.\n\n"
        "If you can reply with both confirmations before our Executive Save Call, we will execute the renewal contract immediately.\n\n"
        "Regards,\n"
        "Henrik Lindqvist\n"
        "Chief Information Officer (CIO) | NordicBank AB"
    )
    msg3 = await call_tool("gmail_send_message", {
        "to": "admin@jesusarguelles.altostrat.com",
        "subject": e3_subj,
        "body": e3_body
    })
    print(f"📧 Sent Email 3 (NordicBank CIO Escalation): {msg3}")

    # Create Pending Draft for Vanguard CISO
    draft_subj = "Re: URGENT: Vanguard Global ($2.4M Agreement) - Final CISO Security & Migration Credit Requirements before 3:30 PM Call"
    draft_body = (
        "Hi Marcus,\n\n"
        "Thank you for the clear summary ahead of our 3:30 PM Go/No-Go call today.\n\n"
        "[PENDING AGENT UPDATE: Insert exact Frankfurt europe-west3 pinning clause, Zero Data Retention section 4.2 guarantee from Drive Security Whitepaper, and confirm the approved $280,000 Migration Credit from Deal Desk Matrix Ref #DD-9941.]\n\n"
        "Best regards,\n"
        "Jesus Arguelles"
    )
    draft_res = await call_tool("gmail_create_draft", {
        "to": "admin@jesusarguelles.altostrat.com",
        "subject": draft_subj,
        "body": draft_body
    })
    print(f"📝 Created CISO Executive Response Draft:\n{draft_res}")

    # =========================================================================
    # 5. GOOGLE CALENDAR EVENTS (Executive Schedule for Today & Tomorrow)
    # =========================================================================
    now = datetime.datetime.now(datetime.timezone.utc)
    today_330pm = now.replace(hour=19, minute=30, second=0, microsecond=0).isoformat()
    today_430pm = now.replace(hour=20, minute=30, second=0, microsecond=0).isoformat()

    today_500pm = now.replace(hour=21, minute=0, second=0, microsecond=0).isoformat()
    today_545pm = now.replace(hour=21, minute=45, second=0, microsecond=0).isoformat()

    ev1 = await call_tool("calendar_create_event", {
        "summary": "Go/No-Go Executive Security & Deal Desk Review: Vanguard Global Financial ($2.4M ACV)",
        "start_time": today_330pm,
        "end_time": today_430pm,
        "description": (
            "Executive sign-off call with CISO Marcus Vance & VP Infrastructure Elena Rostova. "
            "Agenda: Review Frankfurt (europe-west3) Sovereign Architecture, Zero Data Retention (ZDR) contractual guarantee, "
            "and $280,000 Migration Credit (Ref #DD-9941) to displace AWS Bedrock."
        ),
        "location": "Google Meet / Executive Briefing Center"
    })
    print(f"📅 Created Calendar Event 1 (Vanguard Go/No-Go):\n{ev1}")

    ev2 = await call_tool("calendar_create_event", {
        "summary": "Emergency Executive Save Call: NordicBank AB CIO ($1.4M Renewal & SLA Credit)",
        "start_time": today_500pm,
        "end_time": today_545pm,
        "description": (
            "Executive renewal recovery session with CIO Henrik Lindqvist. Present Payment Gateway P1 Runbook "
            "Mitigation Step 3B proof and Deal Desk Ref #DD-8820 ($140,000 SLA Credit) to close slipped Q3 EMEA deal."
        ),
        "location": "Google Meet"
    })
    print(f"📅 Created Calendar Event 2 (NordicBank Save Call):\n{ev2}")

    print("\n✅ Enterprise Demo Universe Seeding Complete!")


if __name__ == "__main__":
    asyncio.run(seed_universe())
