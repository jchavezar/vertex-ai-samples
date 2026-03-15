import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))
import asyncio

from ge_search_branch import stream_ge_search

import logging
logging.basicConfig(level=logging.INFO)

async def main():
    messages = [
        {"role": "user", "content": "What is the salary of a cfo?"}
    ]
    
    # We pass userPseudoId via a mocked Entra ID token to organicially test the extraction
    from utils.auth_context import set_user_id_token, set_user_token
    import jwt
    mock_token = jwt.encode({"preferred_username": "admin@sockcop.onmicrosoft.com"}, "secret", algorithm="HS256")
    set_user_id_token(mock_token)
    set_user_token(mock_token)
    
    async for chunk in stream_ge_search(messages, []):
        print(chunk)

if __name__ == "__main__":
    asyncio.run(main())
