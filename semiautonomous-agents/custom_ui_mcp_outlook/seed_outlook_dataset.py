#!/usr/bin/env python3
import asyncio
import os
import sys
import json
import httpx
from pathlib import Path

# Add backend folder to import OutlookClient
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "local-adk-mcp", "backend"))
from outlook_client import OutlookClient

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

# -----------------------------------------------------------------------------
# Test Suite Dataset Definitions (Matching golden_100_suite.json / Google Sheet)
# -----------------------------------------------------------------------------

INBOX_EMAILS = [
    {
        "subject": "RE: Project Falcon Kickoff Notes",
        "sender_name": "Michael Torres",
        "sender_email": "michael.t@contoso.com",
        "received_datetime": "2026-07-23T08:45:00Z",
        "content": "Hi Jesus,\n\nHere are the notes from our Project Falcon Kickoff session earlier today. Please confirm receipt when you get a chance.\n\nBest,\nMichael Torres"
    },
    {
        "subject": "Q3 Budget Review - Action Required",
        "sender_name": "James Wu",
        "sender_email": "james.wu@contoso.com",
        "received_datetime": "2026-07-22T15:15:00Z",
        "content": "Hi Jesus,\n\nPlease review the attached Q3 Budget allocation spreadsheets. Action required: budget approval is required by July 25, 2026.\n\nThanks,\nJames Wu"
    },
    {
        "subject": "Invoice #4521 Payment Confirmation",
        "sender_name": "Linda Park",
        "sender_email": "linda.park@contoso.com",
        "received_datetime": "2026-07-21T09:30:00Z",
        "content": "Hello Jesus,\n\nThis is a payment confirmation for Invoice #4521. The funds have been transferred and cleared.\n\nRegards,\nLinda Park"
    },
    {
        "subject": "Scheduled Maintenance This Weekend",
        "sender_name": "IT Support",
        "sender_email": "it-support@contoso.com",
        "received_datetime": "2026-07-20T11:00:00Z",
        "content": "Team,\n\nPlease be advised that scheduled network maintenance will occur this weekend starting Saturday at midnight.\n\n- IT Support"
    },
    {
        "subject": "Benefits Enrollment Deadline - July 31",
        "sender_name": "HR Operations",
        "sender_email": "hr@contoso.com",
        "received_datetime": "2026-07-16T10:00:00Z",
        "content": "Open Enrollment Reminder:\n\nAccording to company policy, the final deadline to submit all benefit elections for 2026 Open Enrollment is Friday, July 31, 2026.\n\nThank you,\nHR Team"
    }
]

SENT_EMAILS = [
    {
        "subject": "Project Phoenix Launch Plan",
        "recipient_name": "Sarah Chen",
        "recipient_email": "sarah.c@contoso.com",
        "sent_datetime": "2026-07-21T16:00:00Z",
        "content": "Hi Sarah,\n\nSending over the full Project Phoenix Launch Plan as discussed.\n\nBest,\nJesus Chavez"
    }
]

DRAFTS = [
    {
        "subject": "Q3 Strategy Planning",
        "recipient_name": "Self",
        "recipient_email": "admin@sockcop.onmicrosoft.com",
        "modified_datetime": "2026-07-22T14:00:00Z",
        "content": "Q3 Strategy Planning draft points:\n- Expand Graph API evaluation capabilities\n- Deploy tri-modal ADK agents"
    },
    {
        "subject": "RE: Q3 Budget Review",
        "recipient_name": "James Wu",
        "recipient_email": "james.wu@contoso.com",
        "modified_datetime": "2026-07-23T11:00:00Z",
        "content": "Hi James,\n\nAcknowledging your request for the Q3 Budget Review. Working on approval before July 25, 2026."
    },
    {
        "subject": "Project Falcon Status Update",
        "recipient_name": "Falcon Project Team",
        "recipient_email": "team-falcon@contoso.com",
        "modified_datetime": "2026-07-23T12:30:00Z",
        "content": "Team,\n\nQuick milestone update on Project Falcon."
    }
]

CALENDAR_MEETINGS = [
    {
        "subject": "Weekly Team Sync",
        "start": "2026-07-24T10:00:00",
        "end": "2026-07-24T10:30:00",
        "time_zone": "America/New_York",
        "body": "Weekly synchronization on ongoing sprint tasks.",
        "location": "Conference Room B / Teams"
    },
    {
        "subject": "1:1 with Manager",
        "start": "2026-07-24T15:00:00",
        "end": "2026-07-24T15:30:00",
        "time_zone": "America/New_York",
        "body": "Bi-weekly 1:1 check-in.",
        "location": "Manager Office"
    },
    {
        "subject": "Q3 Budget Review Meeting",
        "start": "2026-07-27T14:00:00",
        "end": "2026-07-27T15:00:00",
        "time_zone": "America/New_York",
        "body": "Detailed budget walk-through with James Wu.",
        "location": "Executive Boardroom"
    },
    {
        "subject": "Project Falcon Kickoff",
        "start": "2026-07-29T09:00:00",
        "end": "2026-07-29T10:30:00",
        "time_zone": "America/New_York",
        "body": "Join Microsoft Teams Meeting: https://teams.microsoft.com/l/meetup-join/falcon-kickoff",
        "location": "Microsoft Teams Online Meeting",
        "is_online": True
    },
    {
        "subject": "Client Presentation - Acme Corp",
        "start": "2026-07-30T13:00:00",
        "end": "2026-07-30T14:00:00",
        "time_zone": "America/New_York",
        "body": "Pitch Acme Corp leadership team.",
        "location": "Acme HQ / Virtual"
    },
    {
        "subject": "All Hands Meeting",
        "start": "2026-08-03T11:00:00",
        "end": "2026-08-03T12:00:00",
        "time_zone": "America/New_York",
        "body": "Monthly company All Hands meeting.",
        "location": "Main Auditorium"
    }
]

async def seed_dataset():
    print("🚀 Initializing Microsoft Graph Connection...")
    client = OutlookClient()
    headers = client._get_headers()
    
    async with httpx.AsyncClient(timeout=30.0) as http:
        # Check profile first
        resp = await http.get(f"{GRAPH_BASE}/me", headers=headers)
        if resp.status_code != 200:
            print(f"❌ Graph API Auth failed: Status {resp.status_code} - {resp.text}")
            return
        profile = resp.json()
        print(f"✅ Authenticated as: {profile.get('displayName')} ({profile.get('userPrincipalName')})")
        print("=" * 80)

        # 1. Seed Inbox Emails
        print("📥 Seeding Inbox Messages...")
        for mail in INBOX_EMAILS:
            payload = {
                "subject": mail["subject"],
                "body": {"contentType": "Text", "content": mail["content"]},
                "from": {"emailAddress": {"name": mail["sender_name"], "address": mail["sender_email"]}},
                "sender": {"emailAddress": {"name": mail["sender_name"], "address": mail["sender_email"]}},
                "receivedDateTime": mail["received_datetime"],
                "isRead": False
            }
            res = await http.post(f"{GRAPH_BASE}/me/mailFolders/inbox/messages", headers=headers, json=payload)
            if res.status_code in [200, 201]:
                print(f"   ✔ Seeded Inbox: \"{mail['subject']}\" from {mail['sender_name']}")
            else:
                # Fallback to general me/messages
                res2 = await http.post(f"{GRAPH_BASE}/me/messages", headers=headers, json=payload)
                print(f"   status ({res.status_code} / {res2.status_code}): {mail['subject']}")

        # 2. Seed Sent Items
        print("\n📤 Seeding Sent Messages...")
        for mail in SENT_EMAILS:
            payload = {
                "subject": mail["subject"],
                "body": {"contentType": "Text", "content": mail["content"]},
                "toRecipients": [{"emailAddress": {"name": mail["recipient_name"], "address": mail["recipient_email"]}}],
                "sentDateTime": mail["sent_datetime"],
                "isDraft": False,
                "isRead": True
            }
            res = await http.post(f"{GRAPH_BASE}/me/mailFolders/sentitems/messages", headers=headers, json=payload)
            if res.status_code in [200, 201]:
                print(f"   ✔ Seeded Sent: \"{mail['subject']}\" to {mail['recipient_name']}")
            else:
                print(f"   status ({res.status_code}): {mail['subject']}")

        # 3. Seed Drafts
        print("\n📝 Seeding Draft Messages...")
        for draft in DRAFTS:
            payload = {
                "subject": draft["subject"],
                "body": {"contentType": "Text", "content": draft["content"]},
                "toRecipients": [{"emailAddress": {"name": draft["recipient_name"], "address": draft["recipient_email"]}}],
                "isDraft": True
            }
            res = await http.post(f"{GRAPH_BASE}/me/mailFolders/drafts/messages", headers=headers, json=payload)
            if res.status_code in [200, 201]:
                print(f"   ✔ Seeded Draft: \"{draft['subject']}\"")
            else:
                print(f"   status ({res.status_code}): {draft['subject']}")

        # 4. Seed Calendar Meetings
        print("\n📅 Seeding Calendar Events...")
        for evt in CALENDAR_MEETINGS:
            payload = {
                "subject": evt["subject"],
                "body": {"contentType": "Text", "content": evt["body"]},
                "start": {"dateTime": evt["start"], "timeZone": evt["time_zone"]},
                "end": {"dateTime": evt["end"], "timeZone": evt["time_zone"]},
                "location": {"displayName": evt["location"]}
            }
            if evt.get("is_online"):
                payload["isOnlineMeeting"] = True
                payload["onlineMeetingProvider"] = "teamsForBusiness"

            res = await http.post(f"{GRAPH_BASE}/me/events", headers=headers, json=payload)
            if res.status_code in [200, 201]:
                print(f"   ✔ Seeded Meeting: \"{evt['subject']}\" ({evt['start'][:10]})")
            else:
                print(f"   status ({res.status_code}): {evt['subject']} -> {res.text[:120]}")

    print("\n🎉 ALL SEEDING OPERATIONS COMPLETED! Your Outlook mailbox is now matched to the test suite.")

if __name__ == "__main__":
    asyncio.run(seed_dataset())
