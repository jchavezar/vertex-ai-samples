import asyncio
import logging
import httpx
from mcp.client.streamable_http import streamable_http_client
from mcp.types import JSONRPCRequest, ClientRequest, JSONRPCMessage
from mcp.client.session import ClientSession
import json
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("debug_streamable")

async def main():
    token = "..." 
    # Load token from file
    with open("factset_tokens.json", "r") as f:
        data = json.load(f)
        token = data.get("default_chat", {}).get("token") or data.get("token")

    url = "https://mcp.factset.com/content/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "x-custom-auth": token,
        "Accept": "text/event-stream"
    }

    logger.info("Testing StreamableHTTP directly...")

    try:
        async with httpx.AsyncClient(http2=True, headers=headers, follow_redirects=True, timeout=30.0) as client:
            async with streamable_http_client(url, http_client=client, terminate_on_close=False) as (read_stream, write_stream, get_session_id):
                logger.info(f"Connected. Session ID: {get_session_id()}")
                
                async with ClientSession(read_stream, write_stream) as session:
                    logger.info("Session initialized. Sending Initialize...")
                    await session.initialize()
                    logger.info("Initialized!")
                    
                    result = await session.list_tools()
                    logger.info(f"Tools: {result}")

    except Exception as e:
        logger.error(f"Crashed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
