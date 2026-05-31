import json

har_path = "/Users/jesusarguelles/Downloads/vertexaisearch.cloud.google.com-streamassist-3.har"

with open(har_path, 'r') as f:
    data = json.load(f)

entries = data.get('log', {}).get('entries', [])

for i, entry in enumerate(entries):
    req = entry.get('request', {})
    url = req.get('url', '')
    
    if 'widgetStreamAssist' in url:
        print(f"=== ENTRY {i}: widgetStreamAssist Request ===")
        post_data = req.get('postData', {})
        text = post_data.get('text', '')
        if text:
            try:
                js = json.loads(text)
                print(json.dumps(js, indent=2))
            except Exception as e:
                print(text)
        print("-" * 60)
