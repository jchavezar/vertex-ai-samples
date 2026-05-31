import json

har_path = "/Users/jesusarguelles/Downloads/vertexaisearch.cloud.google.com-streamassist-3.har"

with open(har_path, 'r') as f:
    data = json.load(f)

entries = data.get('log', {}).get('entries', [])

for i, entry in enumerate(entries):
    req = entry.get('request', {})
    res = entry.get('response', {})
    url = req.get('url', '')
    
    if 'widgetSearch' in url:
        print(f"\n--- Entry {i}: widgetSearch ({url}) ---")
        text = res.get('content', {}).get('text', '')
        try:
            js = json.loads(text)
            print(json.dumps(js, indent=2))
        except Exception as e:
            print("Failed to parse:", e)
            print(text)
