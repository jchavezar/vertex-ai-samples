
import requests
import json
import time

URL = "http://localhost:8005/api/mcp_chat"

test_queries = [
    "Audit the ledger for material transactions (those above $1.5M) and flag any outliers."
]

def test_query(query):
    print(f"\n[TESTING QUERY]: {query}")
    payload = {
        "messages": [{"role": "user", "content": query}],
        "id": f"test-session-{int(time.time())}"
    }
    try:
        response = requests.post(URL, json=payload, timeout=60)
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
