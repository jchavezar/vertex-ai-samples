import google.auth
import google.auth.transport.requests
import requests
import json

def test_stream_assist_oauth(query_text):
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    engine_id = "docparse_1780161524773"
    datastore_id = "docparse-firestore-mcp-1780165632_mcp_data"
    
    # Let's call the widgetStreamAssist endpoint using clients6 but with our OAuth Bearer Token!
    url = "https://discoveryengine.clients6.google.com/v1alpha/locations/global/widgetStreamAssist"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    payload = {
        "configId": "c8f39af0-eff8-4155-a198-8c0d5d2c438d",
        "additionalParams": {
            "token": "-",
            "origin": "ORIGIN_UNSPECIFIED"
        },
        "streamAssistRequest": {
            "session": f"collections/default_collection/engines/{engine_id}/sessions/session-{int(google.auth.transport.requests.Request().session is not None)}",
            "query": {
                "parts": [
                    {
                        "text": query_text
                    }
                ]
            },
            "filter": "",
            "fileIds": [],
            "answerGenerationMode": "NORMAL",
            "agentsSpec": {},
            "toolsSpec": {
                "vertexAiSearchSpec": {
                    "dataStoreSpecs": [
                        {
                            "dataStore": f"collections/default_collection/dataStores/{datastore_id}"
                        }
                    ]
                },
                "toolRegistry": "default_tool_registry",
                "imageGenerationSpec": {},
                "videoGenerationSpec": {}
            },
            "languageCode": "en-US",
            "userMetadata": {
                "timeZone": "America/New_York"
            },
            "assistSkippingMode": "REQUEST_ASSIST"
        }
    }
    
    print(f"\n======================================")
    print(f"Calling clients6 widgetStreamAssist with OAuth for Query: '{query_text}'")
    print(f"======================================")
    
    r = requests.post(url, headers=headers, json=payload, stream=True)
    print(f"Response Status: {r.status_code}")
    if r.status_code != 200:
        print(r.text)
        return
        
    full_text = []
    for line in r.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            try:
                # Handle leading stream-format comma/bracket
                clean_line = decoded_line.lstrip("[, \n\r")
                if clean_line.endswith("]"):
                    clean_line = clean_line.rstrip("]")
                if not clean_line:
                    continue
                data = json.loads(clean_line)
                
                # Parse grounded content text parts
                replies = data.get("streamAssistResponse", {}).get("answer", {}).get("replies", [])
                for reply in replies:
                    text_part = reply.get("groundedContent", {}).get("content", {}).get("text", "")
                    if text_part:
                        full_text.append(text_part)
            except Exception as e:
                pass
                
    if full_text:
        print("".join(full_text))
    else:
        print("Response received, but no streamAssistResponse.answer.replies content was parsed. Raw response:")
        r_all = requests.post(url, headers=headers, json=payload)
        print(r_all.text[:4000])

if __name__ == "__main__":
    test_stream_assist_oauth("what is the metaverse?")
    test_stream_assist_oauth("what is the multiverse?")
