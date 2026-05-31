import json

har_path = "/Users/jesusarguelles/Downloads/vertexaisearch.cloud.google.com-streamassist-5.har"

with open(har_path, 'r') as f:
    data = json.load(f)

entries = data.get('log', {}).get('entries', [])

print(f"Total entries: {len(entries)}")

for i, entry in enumerate(entries):
    req = entry.get('request', {})
    res = entry.get('response', {})
    url = req.get('url', '')
    status = res.get('status')
    
    if "widget" in url or "stream" in url or "assist" in url or "action" in url:
        print(f"[{i}] {req.get('method')} {status} {url}")
        # Let's print request body if exists
        post_data = req.get('postData', {})
        if post_data and post_data.get('text'):
            try:
                post_json = json.loads(post_data['text'])
                print(f"  Request JSON: {json.dumps(post_json, indent=2)[:500]}...")
            except:
                print(f"  Request Raw: {post_data['text'][:200]}...")
        # Let's check response
        content = res.get('content', {})
        if content and content.get('text'):
            print(f"  Response text snippet: {content['text'][:200]}...")

