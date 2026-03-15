import asyncio, httpx, json, jwt

async def main():
    try:
        # Mock token to simulate being signed in
        mock_token = jwt.encode({"preferred_username": "admin@CONTOSO.onmicrosoft.com"}, "secret", algorithm="HS256")
        
        async with httpx.AsyncClient() as client:
            r = await client.post('http://localhost:8008/chat', json={
                'messages': [{'role': 'user', 'content': 'what is the salary of a cfo?'}],
                'mode': 'ge_mcp_router'
            }, headers={
                'Authorization': f'Bearer {mock_token}'
            }, timeout=30)
            
            async for line in r.aiter_lines():
                if line:
                    print(line)
    except Exception as e:
        print('HTTP Error:', e)
asyncio.run(main())
