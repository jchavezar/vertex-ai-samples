import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv(override=True)

# Set python path
sys.path.insert(0, os.path.abspath("."))

from backend.main import _sse_stream, _engine

async def main():
    # Let's see if we can do a streaming query
    # We will use the same user_id and session_id from the user's screenshots if possible,
    # or create a temporary one.
    # Note: the user's active session is 4513362259832995840, user is u-vrwxi9mb.
    user_id = "u-vrwxi9mb"
    session_id = "4513362259832995840"
    message = "what was the google revenue?"
    
    print(f"Connecting to engine and streaming query for user={user_id}, session={session_id}")
    try:
        async for chunk in _sse_stream(user_id, session_id, message):
            print("CHUNKS YIELDED:", chunk)
    except Exception as e:
        logging.exception("Exception in _sse_stream generator")

if __name__ == "__main__":
    asyncio.run(main())
