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
            debug_info = js.get('searchResponse', {}).get('debugInfo', {})
            print("EVALUATION METADATA KEYS:", list(debug_info.get('evaluationMetadata', {}).keys()))
            # Print any message containing "unimplemented", "error", "fail", "custom_mcp", etc.
            debug_str = json.dumps(debug_info, indent=2)
            for line in debug_str.splitlines():
                if any(x in line.lower() for x in ["unimplemented", "error", "fail", "connector", "mcp", "unsupported", "invalid"]):
                    print(line)
        except Exception as e:
            print("Error parsing JSON:", e)
