import json

har_path = "/Users/jesusarguelles/Downloads/vertexaisearch.cloud.google.com-streamassist-4.har"

with open(har_path, 'r') as f:
    data = json.load(f)

entries = data.get('log', {}).get('entries', [])

print(f"Total entries: {len(entries)}")

for i, entry in enumerate(entries):
    req = entry.get('request', {})
    res = entry.get('response', {})
    url = req.get('url', '')
    
    if 'widgetStreamAssist' in url:
        print(f"\n--- Entry {i}: widgetStreamAssist ({url}) ---")
        print(f"Status: {res.get('status')}")
        text = res.get('content', {}).get('text', '')
        # Let's print some lines or examine the stream payload
        print("Stream lines:")
        lines = text.splitlines()
        for idx, line in enumerate(lines):
            if any(k in line for k in ["tool", "confirm", "submit", "action", "state", "execute", "agent"]):
                print(f"  [{idx}] {line[:300]}")
            elif idx < 10 or idx > len(lines) - 5:
                print(f"  [{idx}] {line[:120]}")
