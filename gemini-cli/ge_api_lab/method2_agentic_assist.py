import os
import requests
import json
import google.auth
import google.auth.transport.requests

PROJECT_NUMBER = "254356041555"
ENGINE_ID = "agentspace-testing_1748446185255"

def run_agentic_assist(query: str):
    """
    Method 2: Agentic Assistant (Assistants)
    
    This represents the modern agentic loop. It routes user intent through an Assistant,
    which can choose to search the datastore, search the live web, or use tools 
    (like sending an email). It maintains a conversational session and enforces a persona.
    """
    print(f"Executing Agentic Assist Query: {query}")
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    access_token = credentials.token

    # Endpoint: Assistants / streamAssist
    url_stream = f"https://discoveryengine.googleapis.com/v1beta/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"
    
    payload = {
        "query": {"text": query}
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER
    }

    print(f"Calling: {url_stream}")
    with requests.post(url_stream, json=payload, headers=headers, stream=True) as response:
        if response.status_code == 200:
            print("\n=== AGENTIC ASSIST ANSWER ===")
            accumulated_answer = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    
                    # Very simple extraction for streaming chunks in this demo
                    if decoded_line.startswith('"text":'):
                        # Remove trailing comma if present to parse nicely
                        if decoded_line.endswith(','):
                            decoded_line = decoded_line[:-1]
                        
                        try:
                            # Wrap line in JSON object brackets
                            chunk_json = json.loads("{" + decoded_line + "}")
                            text_chunk = chunk_json.get("text", "")
                            
                            # StreamAssist sends chunks; occasionally it resends the full chunk at the very end
                            # Let's avoid printing duplicate massive blocks
                            if len(text_chunk) > len(accumulated_answer) + 50 and accumulated_answer != "":
                                pass
                            else:
                                print(text_chunk, end="", flush=True)
                                accumulated_answer += text_chunk
                        except json.JSONDecodeError:
                            pass
            print("\n\n=== STREAM COMPLETED ===")
        else:
            print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    # Unlike the traditional RAG method, if this query is too vague, the Agent will
    # conversationally ask for clarification instead of failing gracefully.
    run_agentic_assist("Summarize the risk factors for Alphabet Inc based on their 10-K filing.")
