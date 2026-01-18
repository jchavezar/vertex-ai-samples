import requests
import json
import time

URL = "http://localhost:8001/chat"
SESSION_ID = "default_chat"

def test_comparison():
    payload = {
        "message": "Generate Price Performance analysis for GOOGL, AMZN",
        "session_id": SESSION_ID,
        "model": "gemini-3-flash-preview"
    }
    
    print(f"Sending message: {payload['message']}")
    response = requests.post(URL, json=payload, stream=True)
    
    for line in response.iter_lines():
        if line:
            event = json.loads(line)
            # print(f"Event: {event['type']}")
            if event['type'] == 'error':
                print(f"!!! ERROR: {event['content']}")
            elif event['type'] == 'text':
                print(f"Assistant: {event['content']}")
            elif event['type'] == 'tool_call':
                print(f"Tool Call: {event['tool']}({json.dumps(event['args'], indent=2)})")
            elif event['type'] == 'tool_result':
                res_preview = str(event['result'])[:200]
                print(f"Tool Result: {event['tool']} (Result snippet: {res_preview}...)")
            elif event.get('sourceAgent'):
                print(f"[{event['sourceAgent']}] {event.get('type')}: {event.get('content') or event.get('tool')}")

if __name__ == "__main__":
    test_comparison()
