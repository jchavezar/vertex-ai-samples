#!/usr/bin/env python3
import asyncio
import os
import sys
import json
import httpx
import datetime

# Add local-adk-mcp/backend to import OutlookClient
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "local-adk-mcp", "backend"))
from outlook_client import OutlookClient

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

async def seed_dataset():
    print("🚀 Initializing Microsoft Graph Connection for Sandbox Seeding...")
    client = OutlookClient()
    headers = client._get_headers()
    
    async with httpx.AsyncClient(timeout=30.0) as http:
        # Check profile
        resp = await http.get(f"{GRAPH_BASE}/me", headers=headers)
        if resp.status_code != 200:
            print(f"❌ Graph API Auth failed: Status {resp.status_code} - {resp.text}")
            return
        profile = resp.json()
        print(f"✅ Authenticated as: {profile.get('displayName')} ({profile.get('userPrincipalName')})")
        print("=" * 80)

        # Dynamic Dates
        now = datetime.datetime.now(datetime.timezone.utc)
        today_date = now.strftime('%Y-%m-%d')
        yesterday_date = (now - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        tomorrow_date = (now + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Last Friday
        days_since_friday = (now.weekday() - 4) % 7
        if days_since_friday == 0:
            days_since_friday = 7
        last_friday_date = (now - datetime.timedelta(days=days_since_friday)).strftime('%Y-%m-%d')
        
        # Next Monday
        days_to_monday = (0 - now.weekday()) % 7
        if days_to_monday == 0:
            days_to_monday = 7
        next_monday_date = (now + datetime.timedelta(days=days_to_monday)).strftime('%Y-%m-%d')
        
        # Next Wednesday
        days_to_wednesday = (2 - now.weekday()) % 7
        if days_to_wednesday == 0:
            days_to_wednesday = 7
        next_wednesday_date = (now + datetime.timedelta(days=days_to_wednesday)).strftime('%Y-%m-%d')

        inbox_emails = [
            {
                "subject": "Project Updates",
                "sender_name": "Adele Vance",
                "sender_email": "adelev@M365x214355.onmicrosoft.com",
                "received_datetime": f"{today_date}T10:00:00Z",
                "content": "Hi Jesus, here are the project updates for this week. Best, Adele"
            },
            {
                "subject": "Invoice #98765",
                "sender_name": "Northwind Traders",
                "sender_email": "invoices@northwind.com",
                "received_datetime": f"{yesterday_date}T15:00:00Z",
                "content": "Hello Jesus, please find attached Invoice #98765 for your review."
            },
            {
                "subject": "Quarterly Review",
                "sender_name": "Joni Sherman",
                "sender_email": "jonis@M365x214355.onmicrosoft.com",
                "received_datetime": f"{today_date}T09:30:00Z",
                "content": "Please perform the following tasks: 1. Update the Excel charts, 2. Confirm the guest list for the keynote, and 3. Finalize the slide deck by Friday."
            },
            {
                "subject": "Security Alert",
                "sender_name": "IT Support",
                "sender_email": "support@M365x214355.onmicrosoft.com",
                "received_datetime": f"{today_date}T08:00:00Z",
                "content": "We detected a suspicious login attempt from a Linux/Chrome device located in Dublin. Please verify."
            },
            {
                "subject": "Project Phoenix Launch Date",
                "sender_name": "Alex Wilber",
                "sender_email": "alexw@M365x214355.onmicrosoft.com",
                "received_datetime": f"{yesterday_date}T09:00:00Z",
                "content": "The launch date is set for October 12th."
            },
            {
                "subject": "RE: Project Phoenix Launch Date",
                "sender_name": "Megan Bowen",
                "sender_email": "meganb@M365x214355.onmicrosoft.com",
                "received_datetime": f"{yesterday_date}T10:30:00Z",
                "content": "Actually, the launch has been pushed to October 19th due to testing delays."
            }
        ]

        sent_emails = [
            {
                "subject": "Project Alpha Budget Approval",
                "recipient_name": "Megan Bowen",
                "recipient_email": "meganb@M365x214355.onmicrosoft.com",
                "sent_datetime": f"{yesterday_date}T16:30:00Z",
                "content": "Hi Megan, the Project Alpha Budget Approval is ready."
            },
            {
                "subject": "Project Code Update",
                "recipient_name": "Lee Gu",
                "recipient_email": "leeg@M365x214355.onmicrosoft.com",
                "sent_datetime": f"{yesterday_date}T11:00:00Z",
                "content": "The project code is PX-200"
            },
            {
                "subject": "Project Phoenix Launch Plan",
                "recipient_name": "Sarah Chen",
                "recipient_email": "sarah.c@contoso.com",
                "sent_datetime": f"{yesterday_date}T14:00:00Z",
                "content": "Plan sent."
            },
            {
                "subject": "Project Beta Updates",
                "recipient_name": "Isaiah Langer",
                "recipient_email": "isaiahl@M365x214355.onmicrosoft.com",
                "sent_datetime": f"{last_friday_date}T15:00:00Z",
                "content": "Phase 1 completion"
            },
            {
                "subject": "Weekly Status Update",
                "recipient_name": "All Staff",
                "recipient_email": "all@M365x214355.onmicrosoft.com",
                "sent_datetime": f"{today_date}T17:00:00Z",
                "content": "Weekly Status Update content."
            }
        ]

        draft_emails = [
            {
                "subject": "Project Beta Updates",
                "recipient_name": "Isaiah Langer",
                "recipient_email": "isaiahl@M365x214355.onmicrosoft.com",
                "content": "excellent progress on Phase 1"
            },
            {
                "subject": "Joni Sherman Draft Review",
                "recipient_name": "Joni Sherman",
                "recipient_email": "jonis@M365x214355.onmicrosoft.com",
                "content": "proposed budget amount is $50,000"
            },
            {
                "subject": "RE: Project Code Update",
                "recipient_name": "Lee Gu",
                "recipient_email": "leeg@M365x214355.onmicrosoft.com",
                "content": "The new code has been updated to PX-205."
            },
            {
                "subject": "Annual Board Meeting",
                "recipient_name": "Board Members",
                "recipient_email": "board@M365x214355.onmicrosoft.com",
                "content": "draft content for Annual Board Meeting"
            }
        ]

        calendar_meetings = [
            {
                "subject": "Weekly Leadership Sync",
                "start": f"{today_date}T10:00:00",
                "end": f"{today_date}T11:00:00",
                "time_zone": "America/New_York",
                "body": "Weekly Leadership Sync Teams Join Link: https://teams.microsoft.com/l/meetup-join/weekly-sync-123",
                "location": "Teams Online",
                "is_online": True
            },
            {
                "subject": "Client Lunch: Globex",
                "start": f"{today_date}T12:30:00",
                "end": f"{today_date}T13:30:00",
                "time_zone": "America/New_York",
                "body": "Client Lunch: Globex",
                "location": "Globex Cafe"
            },
            {
                "subject": "Morning Stand-up",
                "start": f"{tomorrow_date}T09:00:00",
                "end": f"{tomorrow_date}T09:30:00",
                "time_zone": "America/New_York",
                "body": "Morning Stand-up",
                "location": "Stand-up room"
            },
            {
                "subject": "Team Retro",
                "start": f"{tomorrow_date}T15:00:00",
                "end": f"{tomorrow_date}T16:00:00",
                "time_zone": "America/New_York",
                "body": "Team Retro",
                "location": "Retro Room"
            },
            {
                "subject": "Q3 Planning Kickoff",
                "start": f"{(now - datetime.timedelta(days=7)).strftime('%Y-%m-%d')}T14:00:00",
                "end": f"{(now - datetime.timedelta(days=7)).strftime('%Y-%m-%d')}T15:00:00",
                "time_zone": "America/New_York",
                "body": "Q3 Planning Kickoff at 2:00 PM",
                "location": "Room 200"
            },
            {
                "subject": "Product Demo",
                "start": f"{next_wednesday_date}T14:00:00",
                "end": f"{next_wednesday_date}T15:00:00",
                "time_zone": "America/New_York",
                "body": "Product Demo",
                "location": "Virtual / Demo Room"
            },
            {
                "subject": "Budget Approval Meeting",
                "start": f"{next_monday_date}T09:00:00",
                "end": f"{next_monday_date}T10:00:00",
                "time_zone": "America/New_York",
                "body": "Budget Approval Meeting from 9:00 AM to 10:00 AM",
                "location": "Boardroom A"
            }
        ]

        # 1. Seed Inbox
        print("📥 Seeding Inbox...")
        for mail in inbox_emails:
            payload = {
                "subject": mail["subject"],
                "body": {"contentType": "Text", "content": mail["content"]},
                "from": {"emailAddress": {"name": mail["sender_name"], "address": mail["sender_email"]}},
                "sender": {"emailAddress": {"name": mail["sender_name"], "address": mail["sender_email"]}},
                "receivedDateTime": mail["received_datetime"],
                "isRead": False,
                "isDraft": False
            }
            res = await http.post(f"{GRAPH_BASE}/me/mailFolders/inbox/messages", headers=headers, json=payload)
            print(f"   ✔ Inbox: \"{mail['subject']}\" ({res.status_code})")

        # 2. Seed Sent Items
        print("\n📤 Seeding Sent Items...")
        for mail in sent_emails:
            payload = {
                "subject": mail["subject"],
                "body": {"contentType": "Text", "content": mail["content"]},
                "toRecipients": [{"emailAddress": {"name": mail["recipient_name"], "address": mail["recipient_email"]}}],
                "sentDateTime": mail["sent_datetime"],
                "isDraft": False,
                "isRead": True
            }
            res = await http.post(f"{GRAPH_BASE}/me/mailFolders/sentitems/messages", headers=headers, json=payload)
            print(f"   ✔ Sent: \"{mail['subject']}\" ({res.status_code})")

        # 3. Seed Drafts
        print("\n📝 Seeding Drafts...")
        for draft in draft_emails:
            payload = {
                "subject": draft["subject"],
                "body": {"contentType": "Text", "content": draft["content"]},
                "toRecipients": [{"emailAddress": {"name": draft["recipient_name"], "address": draft["recipient_email"]}}],
                "isDraft": True
            }
            res = await http.post(f"{GRAPH_BASE}/me/mailFolders/drafts/messages", headers=headers, json=payload)
            print(f"   ✔ Draft: \"{draft['subject']}\" ({res.status_code})")

        # 4. Seed Calendar Meetings
        print("\n📅 Seeding Calendar Events...")
        for evt in calendar_meetings:
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
            print(f"   ✔ Meeting: \"{evt['subject']}\" ({res.status_code})")

    print("\n🎉 SEEDING COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(seed_dataset())
