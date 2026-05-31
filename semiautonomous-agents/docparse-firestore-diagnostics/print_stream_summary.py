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
        content = res.get('content', {})
        text = content.get('text', '')
        
        objs = json.loads(text)
        print(f"Total objects in stream: {len(objs)}")
        
        for idx, obj in enumerate(objs):
            stream_resp = obj.get("streamAssistResponse", {})
            answer = stream_resp.get("answer", {})
            state = answer.get("state") if answer else None
            replies = answer.get("replies", []) if answer else []
            actions = stream_resp.get("actions")
            action_invocations = stream_resp.get("actionInvocations")
            err = stream_resp.get("error")
            
            print(f"[{idx}] state={state} replies_count={len(replies)} actions={bool(actions)} invocations={bool(action_invocations)} err={bool(err)}")
            if err:
                print(f"  Error: {json.dumps(err, indent=2)}")
            if actions:
                print(f"  Actions: {json.dumps(actions, indent=2)}")
            if action_invocations:
                print(f"  Action Invocations: {json.dumps(action_invocations, indent=2)}")
            if replies:
                for r_idx, rep in enumerate(replies):
                    text_val = rep.get("groundedContent", {}).get("content", {}).get("text", "")
                    print(f"  Reply {r_idx}: {repr(text_val)[:120]}...")
