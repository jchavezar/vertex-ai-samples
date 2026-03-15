import requests
import json
import time

URL = "http://localhost:8008/chat"
TOKEN = "test_token_internal"

def run_ge_stream(prompt):
    print(f"\n--- TESTING GE STREAM ---")
    print(f"Prompt: {prompt}\n")
    
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    payload = {
        "messages": [{"content": prompt, "role": "user"}],
        "model": "gemini-2.5-flash",
        "routerMode": "ge_mcp"
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
                            if data.get("type") == "status":
                                print(f"  [Status]: {data.get('message')}")
                            elif data.get("type") == "telemetry":
                                reasoning = data.get("reasoning", [])
                                for r in reasoning:
                                    if "[Discovery Engine] TOOL RESPONSE" in r:
                                        print(f"  [Trace]: {r}")
                    except json.JSONDecodeError:
                        pass
                elif chunk.startswith("0:"):
                    content = chunk[2:].strip('"').replace('\\n', '\n')
                    print(content, end="", flush=True)
        
        duration = time.time() - start_time
        print(f"\n\nTotal Response Time: {round(duration, 2)}s")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    run_ge_stream("What are the features of Vertex AI?")
