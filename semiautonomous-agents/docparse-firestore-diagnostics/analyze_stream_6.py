import json

har_path = "/Users/jesusarguelles/Downloads/vertexaisearch.cloud.google.com-streamassist-6.har"

with open(har_path, 'r') as f:
    data = json.load(f)

entries = data.get('log', {}).get('entries', [])

for i, entry in enumerate(entries):
    req = entry.get('request', {})
    res = entry.get('response', {})
    url = req.get('url', '')
    
    if "widgetStreamAssist" in url and req.get('method') == "POST":
        print(f"\n--- Entry {i}: POST {url} ---")
        content = res.get('content', {})
        text = content.get('text', '')
        
        # StreamAssist responds with JSON lines or concatenated JSON objects
        # Let's break it down by lines or find JSON blocks
        lines = text.strip().split('\n')
        print(f"Total lines in response: {len(lines)}")
        
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                stream_resp = obj.get("streamAssistResponse", {})
                
                # Check for answer state, actions, errors, tool calls
                answer = stream_resp.get("answer", {})
                if answer:
                    state = answer.get("state")
                    replies = answer.get("replies", [])
                    print(f"  [Line {idx}] state={state}")
                    for rep in replies:
                        grounded_content = rep.get("groundedContent", {})
                        content_body = grounded_content.get("content", {})
                        text_val = content_body.get("text", "")
                        if text_val:
                            print(f"    Text: {text_val[:200]}...")
                            
                # Check for actions/tools executed
                actions = stream_resp.get("actions", [])
                if actions:
                    print(f"  [Line {idx}] ACTIONS FOUND:")
                    print(json.dumps(actions, indent=2))
                    
                # Check for actionInvocation or errors
                action_invocations = stream_resp.get("actionInvocations", [])
                if action_invocations:
                    print(f"  [Line {idx}] ACTION INVOCATIONS:")
                    print(json.dumps(action_invocations, indent=2))
                    
                # Check for errors in sessionInfo or general
                err = stream_resp.get("error", {})
                if err:
                    print(f"  [Line {idx}] ERROR DETECTED: {json.dumps(err, indent=2)}")
                    
            except Exception as e:
                # Could be multiple JSONs on same line or partial
                print(f"  [Line {idx}] Failed to parse: {line[:200]}... Error: {e}")
