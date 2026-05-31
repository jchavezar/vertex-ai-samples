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
    method = req.get('method')
    print(f"[{i:2d}] {method:4s} {status} {url[:100]} (Size: {res.get('content', {}).get('size')} bytes)")


