import requests

url = "http://127.0.0.1:8001/api/chat"
resp = requests.post(url, json={
    "message": "Generate a beautiful coastal sunset video. 5 seconds.",
    "session_id": "vid_session_1"
})
print("STATUS:", resp.status_code)
if resp.status_code == 200:
    data = resp.json()
    print("RESPONSE TEXT:", data.get("response"))
    print("VIDEO LENGTH:", len(data.get("video_base64", "")) if data.get("video_base64") else "None")
else:
    print(resp.text)
