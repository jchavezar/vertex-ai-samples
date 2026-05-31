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
        
        # Try parsing as concatenated JSONs or comma separated array of JSONs
        # Many streamAssist responses are returned as a JSON array like [ { ... }, { ... } ]
        # Or just multiple JSON objects separated by commas or newlines.
        
        # Let's clean up and wrap in an array if it's multiple objects
        text = text.strip()
        if text.startswith('['):
            try:
                objs = json.loads(text)
                print(f"Parsed directly as a JSON array. Total elements: {len(objs)}")
            except Exception as e:
                print(f"Failed to parse directly as JSON array: {e}")
                objs = []
        else:
            objs = []
            
        if not objs:
            # Try splitting by "}\n," or ",\n{" or similar to isolate individual JSONs
            # Or parse manually using a JSON decoder
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(text):
                # Skip whitespace/commas
                while pos < len(text) and text[pos] in (' ', '\n', '\r', '\t', ',', '[', ']'):
                    pos += 1
                if pos >= len(text):
                    break
                try:
                    obj, idx = decoder.raw_decode(text[pos:])
                    objs.append(obj)
                    pos += idx
                except Exception as e:
                    print(f"Parsing error at pos {pos}: {e}")
                    break
                    
        print(f"Extracted {len(objs)} objects from StreamAssist response")
        
        # Check tool execution and action confirmation on each object
        for idx, obj in enumerate(objs):
            stream_resp = obj.get("streamAssistResponse", {})
            if not stream_resp:
                continue
                
            answer = stream_resp.get("answer", {})
            state = answer.get("state") if answer else None
            
            # Print if we find actions, tool calls, or exceptions
            actions = stream_resp.get("actions")
            action_invocations = stream_resp.get("actionInvocations")
            
            if actions or action_invocations or state == "SUCCEEDED":
                print(f"\n[Object {idx}] state={state}")
                if actions:
                    print("  ACTIONS:")
                    print(json.dumps(actions, indent=2))
                if action_invocations:
                    print("  ACTION INVOCATIONS:")
                    print(json.dumps(action_invocations, indent=2))
                
                # Check for list of available/called tools in sessionInfo or elsewhere
                invocation_tools = obj.get("invocationTools")
                if invocation_tools:
                    print(f"  Invocation Tools: {invocation_tools}")
                    
                # Let's check grounding/citations
                replies = answer.get("replies", []) if answer else []
                for r_idx, rep in enumerate(replies):
                    grounded_content = rep.get("groundedContent", {})
                    if grounded_content:
                        content_body = grounded_content.get("content", {})
                        text_val = content_body.get("text", "")
                        print(f"  Reply {r_idx} Text: {text_val[:300]}...")
                        # Let's print sources if they exist!
                        sources = grounded_content.get("webSearchQueries") or grounded_content.get("groundingSources")
                        if sources:
                            print(f"  Sources found: {json.dumps(sources, indent=2)}")
