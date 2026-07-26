import os
import asyncio
import httpx
from dotenv import load_dotenv
import json

load_dotenv(dotenv_path="../.env", override=True)

class Message(object):
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
    def to_dict(self):
        return {"role": self.role, "content": self.content}

async def run_multi_turn():
    # Fetch token
    url_auth = "http://localhost:8001/api/auth/status"
    async with httpx.AsyncClient() as client:
        r_auth = await client.get(url_auth)
        token = r_auth.json().get("token")
        if not token:
            load_dotenv(override=True)
            load_dotenv("../.env", override=True)
            token = os.getenv("MS_GRAPH_TOKEN")

    if not token:
        print("Error: No access token found.")
        return

    url_chat = "http://localhost:8001/api/chat"
    session_id = "test_session_multi_turn_" + str(int(asyncio.get_event_loop().time()))
    headers = {"X-Entra-Id-Token": token}
    
    history = []

    # Turn 1
    print("\n--- Turn 1: Asking for latest unread email ---")
    payload1 = {
        "message": "what is my latest unread message?",
        "session_id": session_id,
        "history": [h.to_dict() for h in history]
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r1 = await client.post(url_chat, json=payload1, headers=headers)
        res1 = r1.json()
        print(f"Agent Response: {res1.get('response')}")
        print(f"Tools Called: {res1.get('tool_calls')}")
        history.append(Message("user", "what is my latest unread message?"))
        history.append(Message("model", res1.get("response", "")))

    # Turn 2: Ask the exact same query in the same session
    print("\n--- Turn 2: Asking again for latest unread email (same session) ---")
    payload2 = {
        "message": "what is my latest unread message?",
        "session_id": session_id,
        "history": [h.to_dict() for h in history]
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r2 = await client.post(url_chat, json=payload2, headers=headers)
        res2 = r2.json()
        print(f"Agent Response: {res2.get('response')}")
        print(f"Tools Called: {res2.get('tool_calls')}")

if __name__ == "__main__":
    asyncio.run(run_multi_turn())
