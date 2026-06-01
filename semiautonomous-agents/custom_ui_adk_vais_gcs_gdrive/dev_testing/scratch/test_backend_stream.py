import requests
import json

backend_url = "http://localhost:8088"

# 1. Create session
session_payload = {
    "message": "",
    "access_token": "dummy_token",
    "user_id": "test_user_backend_test",
}

print("Creating session...")
res = requests.post(f"{backend_url}/api/session", json=session_payload)
print("Session response:", res.status_code, res.text)
if res.status_code != 200:
    exit(1)

session_id = res.json()["session_id"]
print("Session ID:", session_id)

# 2. Chat stream
chat_payload = {
    "message": "Hi, who are you?",
    "access_token": "dummy_token",
    "user_id": "test_user_backend_test",
    "session_id": session_id,
    "thinking_level": "HIGH"
}

print("Streaming chat response...")
# Use stream=True to read chunks
res_chat = requests.post(f"{backend_url}/api/chat", json=chat_payload, stream=True)
print("Chat status:", res_chat.status_code)

for chunk in res_chat.iter_content(chunk_size=1024):
    if chunk:
        print(chunk.decode("utf-8"), end="")
