import time
import requests
import json

def test_chat_latency(message="hi", model="gemini-2.5-flash"):
    url = "http://localhost:8001/chat"
    payload = {
        "message": message,
        "model": model,
        "session_id": "latency_test_" + str(time.time())
    }
    
    start_time = time.time()
    first_token_time = None
    
    print(f"Sending '{message}' to {model}...")
    try:
        with requests.post(url, json=payload, stream=True, timeout=30) as r:
            if r.status_code != 200:
                print(f"Error: {r.status_code} - {r.text}")
                return
            
            for line in r.iter_lines():
                if line:
                    data = json.loads(line)
                    if data.get("type") == "text" and first_token_time is None:
                        first_token_time = time.time()
                        print(f"Time to first TEXT token: {first_token_time - start_time:.2f}s")
                    
                    # Log other events briefly
                    if not first_token_time:
                        print(f"Received event: {data.get('type')}")
                    
            end_time = time.time()
            print(f"Total time: {end_time - start_time:.2f}s")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Test unauthenticated (if possible) or just authenticated
    # We need a session ID that has a token or we test 'hi' without token logic
    print("--- TEST 1: Simple 'hi' ---")
    test_chat_latency("hi")
    
    time.sleep(1)
    print("\n--- TEST 2: Simple 'hi' with Flash 3 ---")
    test_chat_latency("hi", model="gemini-3-flash-preview")
