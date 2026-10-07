"""Automatically fetch Salesforce Security Token from Gmail inbox, connect to SFDC REST API,
and seed interconnected Enterprise CRM records (Accounts, Contacts, Opportunities, Cases, Tasks)
matching our Gong, Drive, Gmail, and Calendar demo universe.
"""

import asyncio
import json
import os
import re
import requests
import xml.etree.ElementTree as ET
from server import mcp, auth_manager

AUTH_FILE = os.path.expanduser("~/.gemini/sfdc_altostrat_auth.json")


async def fetch_security_token_from_gmail() -> str:
    """Search Gmail for the Salesforce Security Token email and extract the token string."""
    token = auth_manager.get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    q = "from:salesforce.com \"security token\""
    r = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers=headers,
        params={"q": q, "maxResults": 5}
    ).json()

    messages = r.get("messages", [])
    if not messages:
        return ""

    # Check the most recent message
    msg_id = messages[0]["id"]
    msg_detail = requests.get(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}",
        headers=headers
    ).json()

    snippet = msg_detail.get("snippet", "")
    # Also decode body payload if available
    payload = msg_detail.get("payload", {})
    body_data = ""
    if "body" in payload and payload["body"].get("data"):
        import base64
        body_data = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
    elif "parts" in payload:
        import base64
        for p in payload["parts"]:
            if p.get("body", {}).get("data"):
                body_data += base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8", errors="ignore")

    full_text = snippet + "\n" + body_data
    # Look for token pattern: "Security token (case-sensitive): XXXXXXXXXXXXXXXXXXXXXXXX"
    m = re.search(r"token.*?:\s*([A-Za-z0-9]{20,30})", full_text, re.IGNORECASE)
    if m:
        return m.group(1)
    return ""


def sfdc_soap_login(username: str, password: str, security_token: str):
    """Perform SOAP login to Salesforce and return (session_id, instance_url)."""
    url = "https://login.salesforce.com/services/Soap/u/60.0"
    headers = {"Content-Type": "text/xml; charset=UTF-8", "SOAPAction": "login"}
    xml = f"""<?xml version="1.0" encoding="utf-8" ?>
    <env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
      <env:Body>
        <n1:login xmlns:n1="urn:partner.soap.sforce.com">
          <n1:username>{username}</n1:username>
          <n1:password>{password}{security_token}</n1:password>
        </n1:login>
      </env:Body>
    </env:Envelope>"""
    r = requests.post(url, data=xml, headers=headers)
    if r.status_code != 200:
        raise RuntimeError(f"SFDC Login failed ({r.status_code}): {r.text[:400]}")

    root = ET.fromstring(r.text)
    ns = {"partner": "urn:partner.soap.sforce.com"}
    session_id = root.find(".//partner:sessionId", ns).text
    server_url = root.find(".//partner:serverUrl", ns).text
    # Extract base instance URL e.g. https://orgfarm-771334bd2f-dev-ed.develop.my.salesforce.com
    instance_url = "/".join(server_url.split("/")[:3])
    return session_id, instance_url


def seed_sfdc_records(session_id: str, instance_url: str):
    """Create Accounts, Contacts, Opportunities, Cases, and Tasks in Salesforce."""
    headers = {
        "Authorization": f"Bearer {session_id}",
        "Content-Type": "application/json"
    }
    base = f"{instance_url}/services/data/v60.0/sobjects"

    print(f"🌐 Connected to Salesforce Instance: {instance_url}")

    # 1. Create 3 Strategic Accounts
    accounts = [
        {
            "Name": "Vanguard Global Financial",
            "Type": "Enterprise Customer",
            "Industry": "Financial Services",
            "AnnualRevenue": 4800000000,
            "NumberOfEmployees": 14000,
            "BillingCity": "Frankfurt",
            "BillingCountry": "Germany",
            "Description": "Global wealth management firm deploying Gemini Enterprise across 14,000 advisors. Requires Frankfurt (europe-west3) data residency & Zero Data Retention (ZDR). AWS Bedrock competing with $250K credit."
        },
        {
            "Name": "NordicBank AB",
            "Type": "Customer - Direct",
            "Industry": "Banking",
            "AnnualRevenue": 1900000000,
            "NumberOfEmployees": 6200,
            "BillingCity": "Stockholm",
            "BillingCountry": "Sweden",
            "Description": "$1.4M ARR EMEA banking customer. Q3 renewal slipped to Q4 following Checkout Payment Gateway P1 latency spike (>2,500ms). Requires proof of Mitigation Step 3B and 10% SLA Retention Credit ($140K)."
        },
        {
            "Name": "Acme Corp",
            "Type": "Customer - Direct",
            "Industry": "Manufacturing & Logistics",
            "AnnualRevenue": 850000000,
            "NumberOfEmployees": 3400,
            "BillingCity": "New York",
            "BillingCountry": "United States",
            "Description": "$500K ACV renewal negotiating Net-45 compromise payment terms and $1M liability cap redline."
        }
    ]

    account_ids = {}
    for acc in accounts:
        r = requests.post(f"{base}/Account", headers=headers, json=acc)
        if r.status_code in (200, 201):
            aid = r.json()["id"]
            account_ids[acc["Name"]] = aid
            print(f"🏢 Created Account '{acc['Name']}' -> ID: {aid}")
        else:
            print(f"⚠️ Account '{acc['Name']}' response: {r.text}")

    # 2. Create Executive Contacts matching Gmail & Gong Participants
    contacts = [
        {
            "FirstName": "Marcus",
            "LastName": "Vance",
            "Title": "Chief Information Security Officer (CISO)",
            "Email": "marcus.vance@vanguardglobal.example.com",
            "Phone": "+49 69 9102 4400",
            "AccountId": account_ids.get("Vanguard Global Financial"),
            "Description": "Primary security decision maker on $2.4M deal. Demanded Frankfurt europe-west3 pinning & ZDR contractual addendum."
        },
        {
            "FirstName": "Elena",
            "LastName": "Rostova",
            "Title": "VP Cloud Infrastructure",
            "Email": "elena.rostova@vanguardglobal.example.com",
            "Phone": "+49 69 9102 4412",
            "AccountId": account_ids.get("Vanguard Global Financial"),
            "Description": "Disclosed AWS Bedrock $250,000 migration credit offer during Gong architecture call."
        },
        {
            "FirstName": "Henrik",
            "LastName": "Lindqvist",
            "Title": "Chief Information Officer (CIO)",
            "Email": "henrik.lindqvist@nordicbank.example.com",
            "Phone": "+46 8 506 200 00",
            "AccountId": account_ids.get("NordicBank AB"),
            "Description": "Executive sponsor holding $1.4M renewal PO until SRE Mitigation Step 3B proof and $140K SLA credit are confirmed."
        }
    ]

    for c in contacts:
        if c.get("AccountId"):
            r = requests.post(f"{base}/Contact", headers=headers, json=c)
            if r.status_code in (200, 201):
                print(f"👤 Created Contact '{c['FirstName']} {c['LastName']}' -> ID: {r.json()['id']}")

    # 3. Create 3 High-Stakes Opportunities
    opportunities = [
        {
            "Name": "Vanguard Global - Gemini Enterprise AI Platform (14,000 Seats)",
            "AccountId": account_ids.get("Vanguard Global Financial"),
            "StageName": "Negotiation/Review",
            "Amount": 2400000,
            "CloseDate": "2026-09-25",
            "Probability": 75,
            "NextStep": "Deliver EU Frankfurt ZDR Whitepaper & $280K Deal Desk Migration Credit (Ref #DD-9941) on 3:30 PM Go/No-Go Call",
            "Description": "Multi-year Enterprise AI platform expansion. Competitor AWS Bedrock offered $250K credit. Deal Desk approved $280K credit (Ref #DD-9941) to displace AWS."
        },
        {
            "Name": "NordicBank AB - FY26 Annual Enterprise Renewal ($1.4M ARR)",
            "AccountId": account_ids.get("NordicBank AB"),
            "StageName": "Proposal/Price Quote",
            "Amount": 1400000,
            "CloseDate": "2026-10-05",
            "Probability": 60,
            "NextStep": "Present Payment Gateway P1 Mitigation Step 3B proof + 10% ($140K) SLA Credit (Ref #DD-8820) on 5:00 PM CIO Save Call",
            "Description": "Slipped from Q3 EMEA forecast (-8.1% regional variance). CIO Henrik Lindqvist ready to sign upon SLA credit and SRE runbook verification."
        },
        {
            "Name": "Acme Corp - Enterprise Renewal & SLA Expansion",
            "AccountId": account_ids.get("Acme Corp"),
            "StageName": "Negotiation/Review",
            "Amount": 500000,
            "CloseDate": "2026-09-18",
            "Probability": 85,
            "NextStep": "Finalize Net-45 payment terms & $1M liability cap compromise on 2:00 PM executive call",
            "Description": "Renewal of core platform. Approved Net-45 payment terms and $1M liability cap compromise in MSA v3."
        }
    ]

    for opp in opportunities:
        if opp.get("AccountId"):
            r = requests.post(f"{base}/Opportunity", headers=headers, json=opp)
            if r.status_code in (200, 201):
                print(f"💰 Created Opportunity '{opp['Name']}' (${opp['Amount']:,}) -> ID: {r.json()['id']}")

    # 4. Create Support Cases (Linking SRE Incident to Customer CRM Account)
    cases = [
        {
            "Subject": "[P1 ESCALATION] Payment Gateway Latency Spike (>2,500ms) Impacting Retail FX Alerts",
            "AccountId": account_ids.get("NordicBank AB"),
            "Priority": "High",
            "Status": "Working",
            "Origin": "Web",
            "Description": "Root Cause: Redis Cluster Connection Pool Exhaustion (500/500 active connections) in us-east1. Remediation: Mitigation Step 3B executed (traffic drained to us-central1, REDIS_MAX_CONNECTIONS increased to 2,500). Linked to Deal Desk SLA Credit Ref #DD-8820 ($140,000)."
        },
        {
            "Subject": "CISO Security Architecture & Frankfurt (europe-west3) Sovereign Cloud Review",
            "AccountId": account_ids.get("Vanguard Global Financial"),
            "Priority": "High",
            "Status": "Working",
            "Origin": "Email",
            "Description": "CISO Marcus Vance requested contractual proof of Zero Data Retention (ZDR Section 4.2) and Frankfurt regional pinning. Reference document: SEC-ARCH-2026-V4 in Google Drive."
        }
    ]

    for cs in cases:
        if cs.get("AccountId"):
            r = requests.post(f"{base}/Case", headers=headers, json=cs)
            if r.status_code in (200, 201):
                print(f"🚨 Created Case '{cs['Subject']}' -> ID: {r.json()['id']}")

    print("\n🎉 ALL SALESFORCE ENTERPRISE DEMO RECORDS SEEDED SUCCESSFULLY!")


async def main():
    with open(AUTH_FILE) as f:
        auth = json.load(f)

    token = auth.get("security_token")
    if not token:
        print("🔍 Searching Gmail for Salesforce Security Token...")
        token = await fetch_security_token_from_gmail()
        if token:
            print(f"✅ Found Security Token in Gmail: {token[:4]}...{token[-4:]}")
            auth["security_token"] = token
            with open(AUTH_FILE, "w") as f:
                json.dump(auth, f, indent=2)
        else:
            print("⏳ Security Token email not yet in inbox. Please click 'Reset Security Token' in Salesforce Settings.")
            return

    if auth.get("session_id"):
        print("🔑 Using active Salesforce Session ID from config...")
        seed_sfdc_records(auth["session_id"], auth["instance_url"])
        return

    session_id, instance_url = sfdc_soap_login(auth["username"], auth["password"], token)
    seed_sfdc_records(session_id, instance_url)


if __name__ == "__main__":
    asyncio.run(main())
