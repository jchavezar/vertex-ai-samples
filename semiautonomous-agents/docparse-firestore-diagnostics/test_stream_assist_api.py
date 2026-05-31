import google.auth
import google.auth.transport.requests
import requests
import json

def test_stream_assist(query_text):
    url = "https://discoveryengine.clients6.google.com/v1alpha/locations/global/widgetStreamAssist?key=AIzaSyD9imQMsvN72Z2__FTNHdWKoyNaq1q2TI4"
    
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://vertexaisearch.cloud.google.com/",
        "Origin": "https://vertexaisearch.cloud.google.com"
    }
    
    payload = {
        "configId": "c8f39af0-eff8-4155-a198-8c0d5d2c438d",
        "additionalParams": {
            "token": "-",
            "origin": "ORIGIN_UNSPECIFIED"
        },
        "streamAssistRequest": {
            "session": "collections/default_collection/engines/docparse_1780161524773/sessions/10997838823481324559",
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
                            "dataStore": "collections/default_collection/dataStores/docparse-firestore-mcp-1780165632_mcp_data"
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
    print(f"Calling clients6 widgetStreamAssist with Query: '{query_text}'")
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
        print("Response received, but no streamAssistResponse.answer.replies content was parsed. Let's inspect raw payload:")
        # Let's perform a non-streaming request to inspect the entire response structure
        r_all = requests.post(url, headers=headers, json=payload)
        try:
            print(json.dumps(r_all.json(), indent=2)[:4000])
        except Exception:
            print(r_all.text[:4000])

if __name__ == "__main__":
    test_stream_assist("what is the metaverse?")
    test_stream_assist("what is the multiverse?")
