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
            with open(f"/Users/jesusarguelles/.gemini/antigravity-cli/brain/13795b1e-7bc1-4f33-a601-7e7f419e67b7/scratch/widgetSearch_{i}.json", "w") as f_out:
                json.dump(js, f_out, indent=2)
            print(f"Saved to scratch/widgetSearch_{i}.json")
        except Exception as e:
            print("Error parsing:", e)
