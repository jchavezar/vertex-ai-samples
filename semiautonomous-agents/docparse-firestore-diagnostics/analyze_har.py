import json
import os

har_path = "/Users/jesusarguelles/Downloads/vertexaisearch.cloud.google.com-streamassist-2.har"

if not os.path.exists(har_path):
    print(f"Error: File does not exist at {har_path}")
    exit(1)

print(f"Loading HAR file from {har_path}...")
with open(har_path, 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

entries = data.get('log', {}).get('entries', [])
print(f"Total entries found: {len(entries)}")

# Find all entries containing "widgetSearch" or returning 400
failures = []
for entry in entries:
    request = entry.get('request', {})
    response = entry.get('response', {})
    url = request.get('url', '')
    status = response.get('status', 0)
    
    if "widgetSearch" in url or status == 400:
        failures.append(entry)

print(f"Found {len(failures)} matching entries:")
for i, entry in enumerate(failures):
    req = entry.get('request', {})
    resp = entry.get('response', {})
    url = req.get('url', '')
    status = resp.get('status', 0)
    method = req.get('method', '')
    print(f"\n--- Entry {i+1} ---")
    print(f"URL: {url}")
    print(f"Method: {method}")
    print(f"Status: {status}")
    
    # Post Data
    post_data = req.get('postData', {})
    if post_data:
        text = post_data.get('text', '')
        print("Request Payload (truncated):")
        try:
            parsed_payload = json.loads(text)
            print(json.dumps(parsed_payload, indent=2)[:1000])
        except Exception:
            print(text[:1000])
            
    # Response content
    resp_content = resp.get('content', {})
    if resp_content:
        text = resp_content.get('text', '')
        print("Response Content:")
        try:
            parsed_resp = json.loads(text)
            print(json.dumps(parsed_resp, indent=2))
        except Exception:
            print(text[:2000])
