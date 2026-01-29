import requests
import json

def test_search_routing():
    url = "http://localhost:8001/chat"
    
    # 1. Test General Search (Should go to research_specialist)
    print("\n--- TESTING GENERAL SEARCH ROUTING ---")
    payload = {
        "messages": [{"role": "user", "content": "Who won the Super Bowl last year?"}],
        "sessionId": "test_routing_session",
        "model": "gemini-2.5-flash"
    }
    response = requests.post(url, json=payload, stream=True)
    print(f"Status Code: {response.status_code}")
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))

    # 2. Test News Dashboard (Should handle missing ticker)
    print("\n--- TESTING NEWS DASHBOARD (NO TICKER) ---")
    payload = {
        "messages": [{"role": "user", "content": "show me the latest market news"}],
        "sessionId": "test_news_session",
        "model": "gemini-2.5-flash"
    }
    response = requests.post(url, json=payload, stream=True)
    print(f"Status Code: {response.status_code}")
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))

if __name__ == "__main__":
    test_search_routing()
