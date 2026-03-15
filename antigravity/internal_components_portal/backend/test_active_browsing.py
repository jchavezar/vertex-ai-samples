import requests
import json
import time

URL = "http://localhost:8008/chat"
TOKEN = "test_token_internal"

def run_active_browsing(prompt):
    print(f"\n--- TESTING ACTIVE BROWSING ---")
    print(f"Prompt: {prompt}\n")
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    payload = {
        "messages": [{"content": prompt, "role": "user"}],
        "model": "gemini-2.5-flash",
        "routerMode": "all_mcp"
    }
    
    try:
        start_time = time.time()
        response = requests.post(URL, headers=headers, json=payload, stream=True, timeout=60)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                chunk = line.decode('utf-8')
                if chunk.startswith("2:"):
                    data_str = chunk[2:]
                    try:
                        data_list = json.loads(data_str)
                        for data in data_list:
                            if data.get("type") == "public_insight":
                                content = data.get("data", "")
                                if content:
                                    print(f"[Active Browsing Insight Updated]:\n{content}\n")
                            elif data.get("type") == "telemetry":
                                reasoning = data.get("reasoning", [])
                                for r in reasoning:
                                    if "[Public Web] TOOL:" in r or "[Public Web] ARGS:" in r or "[Public Web] RESPONSE:" in r:
                                        print(f"  [Active Browsing Trace]: {r.replace('\n', ' ')}")
                            elif data.get("type") == "status":
                                print(f"  [Status]: {data.get('message')}")
                    except json.JSONDecodeError:
                        pass
        
        duration = time.time() - start_time
        print(f"\nTotal Response Time: {round(duration, 2)}s")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    run_active_browsing("What are the latest news about Alphabet's earnings?")
