import os
import asyncio
import httpx
from dotenv import load_dotenv
import json

load_dotenv(dotenv_path="../.env", override=True)

async def test_query():
    # Fetch token
    url_auth = "http://localhost:8001/api/auth/status"
    async with httpx.AsyncClient() as client:
        r_auth = await client.get(url_auth)
        token = r_auth.json().get("token")
        
        # If not returned, retrieve MS_GRAPH_TOKEN from env
        if not token:
            load_dotenv(override=True)
            load_dotenv("../.env", override=True)
            token = os.getenv("MS_GRAPH_TOKEN")

    if not token:
        print("Error: No access token found.")
        return

    url_search = "http://localhost:8001/api/search"
    payload = {
        "query": "what is my latest unread message?",
        "timezone": "America/New_York"
    }
    headers = {"X-Entra-Id-Token": token}
    
    print("Sending query to local backend search endpoint...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url_search, json=payload, headers=headers)
        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text}")
            return
            
        print("\n--- Stream Response Events ---")
        for line in r.text.split("\n"):
            if line.startswith("data: "):
                data_str = line[6:].strip()
                if not data_str: continue
                try:
                    evt = json.loads(data_str)
                    if evt.get("type") == "text":
                        print(evt.get("text"), end="")
                    elif evt.get("type") == "tool_call":
                        print(f"\n[Tool Call] {evt.get('tool')}")
                    elif evt.get("type") == "tool_response":
                        # Print length of list or preview
                        resp_val = evt.get("response", {})
                        if isinstance(resp_val, dict) and "emails" in resp_val:
                            emails = resp_val["emails"]
                            print(f"\n[Tool Response] Returned {len(emails)} emails:")
                            for idx, email in enumerate(emails[:5]):
                                print(f"  {idx+1}. Subject: {email.get('subject')} | Received: {email.get('receivedDateTime')} | isRead: {email.get('isRead')} | isDraft: {email.get('isDraft')}")
                        else:
                            print(f"\n[Tool Response] {str(resp_val)[:200]}...")
                except Exception as e:
                    pass
        print()

if __name__ == "__main__":
    asyncio.run(test_query())
