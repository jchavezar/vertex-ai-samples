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
        print(f"=== ENTRY {i}: widgetSearch ===")
        text = res.get('content', {}).get('text', '')
        try:
            js = json.loads(text)
            print(json.dumps(js, indent=2)[:4000])
        except Exception as e:
            print("Failed to parse JSON:", e)
            print(text[:2000])
            
    if 'widgetStreamAssist' in url:
        print(f"=== ENTRY {i}: widgetStreamAssist ===")
        text = res.get('content', {}).get('text', '')
        try:
            js = json.loads(text)
            # widgetStreamAssist response is a JSON list of streamed chunks (since HAR might contain concatenated JSON objects or list of objects)
            if isinstance(js, list):
                print(f"List with {len(js)} items.")
                for idx, chunk in enumerate(js):
                    print(f"--- Chunk {idx} ---")
                    print(json.dumps(chunk, indent=2)[:1000])
            else:
                print(json.dumps(js, indent=2)[:2000])
        except Exception as e:
            # Let's try newline-delimited or chunked JSON
            print("Failed to parse JSON directly, showing raw snippet:", e)
            print(text[:4000])
