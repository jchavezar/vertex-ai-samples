
import requests
import json
import time

URL = "http://localhost:8001/api/mcp_chat"

test_queries = [
    'EXECUTE PROTOCOL: { "jurisdiction_name": "Cayman Islands" }'
]

def test_query(query):
    print(f"\n[TESTING RAW PROTOCOL]: {query}")
    start_time = time.time()
    payload = {
        "messages": [{"role": "user", "content": query}],
        "id": f"test-raw-{int(time.time())}"
    }
    try:
        response = requests.post(URL, json=payload, timeout=60)
        end_time = time.time()
        print(f"[TIME TAKEN]: {end_time - start_time:.2f} seconds")
        if response.status_code == 200:
            print("[RESPONSE RECEIVED]:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"[ERROR]: Status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[EXCEPTION]: {e}")

if __name__ == "__main__":
    for q in test_queries:
        test_query(q)
