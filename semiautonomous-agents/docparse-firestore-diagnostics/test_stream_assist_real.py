import google.auth
import google.auth.transport.requests
import requests
import json

def test_stream_assist_real(query_text):
    creds, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    
    proj_num = "254356041555"
    engine_id = "docparse_1780161524773"
    assistant_id = "default_assistant"
    
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_num
    }
    
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{proj_num}/locations/global/collections/default_collection/engines/{engine_id}/assistants/{assistant_id}:streamAssist"
    
    datastore_id = "docparse-firestore-mcp-1780165632_mcp_data"
    body = {
        "query": {
            "text": query_text
        },
        "toolsSpec": {
            "vertexAiSearchSpec": {
                "dataStoreSpecs": [
                    {
                        "dataStore": f"projects/{proj_num}/locations/global/collections/default_collection/dataStores/{datastore_id}"
                    }
                ]
            }
        }
    }
    
    print(f"\n======================================")
    print(f"Calling v1alpha streamAssist (location 'global') with: '{query_text}'")
    print(f"======================================")
    
    r = requests.post(url, headers=headers, json=body, stream=True)
    print(f"Response Status: {r.status_code}")
    if r.status_code == 200:
        for line in r.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(decoded_line)
    else:
        print(r.text)

if __name__ == "__main__":
    test_stream_assist_real("Please call the list_documents tool to list all distinct documents in the database.")
    test_stream_assist_real("Who is quoted on page 9 of the Accenture report representing Carrefour Group? You MUST call search_docs with page='9' and pdf_name='accenture'.")
