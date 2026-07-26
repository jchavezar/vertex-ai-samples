import os
import asyncio
import httpx
from dotenv import load_dotenv
import sys

# Add local-adk-mcp to python path
sys.path.append("/Users/jesusarguelles/IdeaProjects/vertex-ai-samples/semiautonomous-agents/custom_ui_mcp_outlook/local-adk-mcp")
from backend.outlook_client import OutlookClient

async def dump_unread():
    # Instantiate client and retrieve headers (triggers MSAL refresh)
    client = OutlookClient()
    headers = client._get_headers()
    token = headers.get("Authorization")
    
    if not token:
        print("Error: Failed to obtain access token. Please verify CLIENT_ID/SECRET in .env.")
        return

    # Call Graph API directly for raw inbox data
    graph_url = "https://graph.microsoft.com/v1.0/me/messages"
    params = {
        "$filter": "isRead eq false",
        "$select": "subject,receivedDateTime,isRead,isDraft,parentFolderId",
        "$orderby": "receivedDateTime desc",
        "$top": "15"
    }
    headers_graph = {"Authorization": token}
    
    async with httpx.AsyncClient() as http_client:
        r_graph = await http_client.get(graph_url, params=params, headers=headers_graph)
        if r_graph.status_code != 200:
            print(f"Graph API Error {r_graph.status_code}: {r_graph.text}")
            return
            
        data = r_graph.json()
        print("\n--- Raw Graph API Unread Messages ---")
        for msg in data.get("value", []):
            print(f"Subject: {msg.get('subject')}")
            print(f"  Received: {msg.get('receivedDateTime')}")
            print(f"  isDraft:  {msg.get('isDraft')}")
            print(f"  FolderId: {msg.get('parentFolderId')}")
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(dump_unread())
