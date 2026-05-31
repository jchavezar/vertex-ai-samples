import json

har_path = "/Users/jesusarguelles/Downloads/vertexaisearch.cloud.google.com-streamassist-5.har"

with open(har_path, 'r') as f:
    data = json.load(f)

entries = data.get('log', {}).get('entries', [])

for i, entry in enumerate(entries):
    req = entry.get('request', {})
    url = req.get('url', '')
    if "widgetStreamAssist" in url:
        print(f"--- ENTRY {i} ---")
        post_data = req.get('postData', {})
        if post_data and post_data.get('text'):
            post_json = json.loads(post_data['text'])
            print(json.dumps(post_json, indent=2))
