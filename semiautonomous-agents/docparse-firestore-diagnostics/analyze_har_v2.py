import json

har_path = "/Users/jesusarguelles/Downloads/vertexaisearch.cloud.google.com-streamassist-3.har"

with open(har_path, 'r') as f:
    data = json.load(f)

entries = data.get('log', {}).get('entries', [])
print(f"Total entries: {len(entries)}")

for i, entry in enumerate(entries):
    req = entry.get('request', {})
    res = entry.get('response', {})
    url = req.get('url', '')
    status = res.get('status', 0)
    
    # Let's filter for streamassist, widget, search, or anything else interesting
    if any(k in url for k in ['streamassist', 'widget', 'search', 'converse', 'assist', 'docparse']):
        print(f"[{i}] URL: {url} | Status: {status}")
        # If response content text exists, print a snippet
        content = res.get('content', {})
        text = content.get('text', '')
        if text:
            print(f"  Response text snippet: {text[:500]}")
            # If it's json, try to parse and pretty-print if small or print keys
            try:
                js = json.loads(text)
                if isinstance(js, dict):
                    print(f"  Response JSON keys: {list(js.keys())}")
                elif isinstance(js, list):
                    print(f"  Response JSON list len: {len(js)}")
            except:
                pass
        print("-" * 40)
