import json

har_path = "/Users/jesusarguelles/Downloads/vertexaisearch.cloud.google.com-streamassist-6.har"

with open(har_path, 'r') as f:
    data = json.load(f)

entries = data.get('log', {}).get('entries', [])

print(f"Total entries: {len(entries)}")

for i, entry in enumerate(entries):
    req = entry.get('request', {})
    res = entry.get('response', {})
    url = req.get('url', '')
    status = res.get('status')
    
    if "widget" in url or "stream" in url or "assist" in url or "action" in url or "complete" in url:
        print(f"\n[{i}] {req.get('method')} {status} {url}")
        
        # Check request body
        post_data = req.get('postData', {})
        if post_data and post_data.get('text'):
            try:
                post_json = json.loads(post_data['text'])
                print(f"  Request JSON: {json.dumps(post_json, indent=2)[:800]}...")
            except:
                print(f"  Request Raw: {post_data['text'][:300]}...")
                
        # Check response content
        content = res.get('content', {})
        if content and content.get('text'):
            print(f"  Response text length: {len(content['text'])}")
            print(f"  Response text snippet: {content['text'][:1000]}...")
