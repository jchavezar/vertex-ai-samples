import asyncio
import json
import os
import datetime
from dotenv import load_dotenv
import httpx

load_dotenv()

# We pull MS_GRAPH_TOKEN dynamically from server or env
TOKEN = os.getenv("MS_GRAPH_TOKEN")

async def fetch_raw_graph_data():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json",
        "Prefer": 'outlook.timezone="America/New_York"',
    }
    
    async with httpx.AsyncClient() as client:
        # 1. Fetch Profile
        res_profile = await client.get("https://graph.microsoft.com/v1.0/me", headers=headers)
        profile = res_profile.json() if res_profile.status_code == 200 else {}
        
        # 2. Fetch Messages
        res_msgs = await client.get("https://graph.microsoft.com/v1.0/me/messages?$top=20&$select=id,subject,from,receivedDateTime,bodyPreview,webLink", headers=headers)
        msgs = res_msgs.json().get("value", []) if res_msgs.status_code == 200 else []
        
        # 3. Fetch Events (Next 30 days)
        now = datetime.datetime.now(datetime.timezone.utc)
        future = now + datetime.timedelta(days=30)
        events_url = f"https://graph.microsoft.com/v1.0/me/calendar/calendarView?startDateTime={now.strftime('%Y-%m-%dT%H:%M:%SZ')}&endDateTime={future.strftime('%Y-%m-%dT%H:%M:%SZ')}&$top=20"
        res_events = await client.get(events_url, headers=headers)
        events = res_events.json().get("value", []) if res_events.status_code == 200 else []

    return profile, msgs, events

async def main():
    profile, msgs, events = await fetch_raw_graph_data()
    print(f"Direct Graph API Extraction:")
    print(f"- User Profile: {profile.get('displayName')} ({profile.get('userPrincipalName')})")
    print(f"- Messages Extracted: {len(msgs)}")
    print(f"- Calendar Events Extracted: {len(events)}")
    
    raw_data = {
        "profile": profile,
        "messages": msgs,
        "events": events
    }
    
    with open("raw_graph_data.json", "w") as f:
        json.dump(raw_data, f, indent=2)
        
    print("Saved raw Microsoft Graph data to raw_graph_data.json")

if __name__ == "__main__":
    asyncio.run(main())
