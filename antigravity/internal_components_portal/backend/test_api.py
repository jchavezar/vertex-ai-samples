import httpx
import json

def test():
    req = {
        "messages": [
            {"role": "user", "content": "Find the architecture diagram of project anti-gravity inside my google drive."}
        ]
    }
    with httpx.Client(timeout=60.0) as client:
        # It's an SSE endpoint, so we should stream the response
        with client.stream("POST", "http://127.0.0.1:8008/chat", json=req, headers={"Authorization": "fake"}) as response:
            for chunk in response.iter_text():
                print(chunk)

if __name__ == "__main__":
    test()
