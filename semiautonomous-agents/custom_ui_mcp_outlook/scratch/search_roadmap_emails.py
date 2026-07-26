import os
import asyncio
import httpx
from dotenv import load_dotenv
import sys

sys.path.append("/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/custom_ui_mcp_outlook/local-adk-mcp")
from backend.outlook_client import OutlookClient

async def search_roadmap():
    client = OutlookClient()
    headers = client._get_headers()
    token = headers.get("Authorization")
    
    if not token:
        print("Error: No token.")
        return

    graph_url = "https://graph.microsoft.com/v1.0/me/messages"
    params = {
        "$search": '"Roadmap Deck Review"',
        "$select": "subject,receivedDateTime,isRead,isDraft,parentFolderId",
        "$top": "20"
    }
    headers_graph = {"Authorization": token}
    
    async with httpx.AsyncClient() as http_client:
        r_graph = await http_client.get(graph_url, params=params, headers=headers_graph)
        if r_graph.status_code != 200:
            print(f"Error {r_graph.status_code}: {r_graph.text}")
            return
            
        data = r_graph.json()
        print("\n--- Emails matching 'Roadmap Deck Review' ---")
        for msg in data.get("value", []):
            print(f"Subject: {msg.get('subject')}")
            print(f"  Received: {msg.get('receivedDateTime')}")
            print(f"  isRead:   {msg.get('isRead')}")
            print(f"  isDraft:  {msg.get('isDraft')}")
            print(f"  FolderId: {msg.get('parentFolderId')}")
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(search_roadmap())
