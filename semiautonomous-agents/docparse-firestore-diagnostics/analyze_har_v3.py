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
    
    # Let's inspect any URL with widgetSearch or widgetStreamAssist or errors
    if 'widgetSearch' in url:
        print(f"\n--- Entry {i}: widgetSearch ({url}) ---")
        text = res.get('content', {}).get('text', '')
        try:
            js = json.loads(text)
            # Find any candidateDebugInfos, errors, or searchSpec
            debug_info = js.get('candidateDebugInfos', [])
            print(f"Status: {res.get('status')}")
            print(f"Keys: {list(js.keys())}")
            if 'error' in js:
                print("Error:", js['error'])
            for idx, deb in enumerate(debug_info):
                print(f"Debug Info {idx}: {list(deb.keys())}")
                if 'federatedSearchCandidateDebugInfos' in deb:
                    print("federatedSearchCandidateDebugInfos:", json.dumps(deb['federatedSearchCandidateDebugInfos'], indent=2)[:2000])
        except Exception as e:
            print("Could not parse widgetSearch json:", e)
            
    if 'widgetStreamAssist' in url:
        print(f"\n--- Entry {i}: widgetStreamAssist ({url}) ---")
        text = res.get('content', {}).get('text', '')
        print(f"Status: {res.get('status')}")
        # Look for custom_mcp, search docs, mcp, run.app, etc in stream text
        if 'mcp' in text or 'run.app' in text or 'error' in text or 'unimplemented' in text:
            print("Found mcp/run/error in text:")
            for line in text.splitlines():
                if any(x in line.lower() for x in ['mcp', 'run.app', 'error', 'unimplemented', 'fail']):
                    print("  ", line[:500])
        else:
            print("No error/mcp keywords in text. Preview first 200 chars:")
            print(text[:200])
