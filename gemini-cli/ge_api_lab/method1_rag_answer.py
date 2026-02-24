import os
import requests
import google.auth
import google.auth.transport.requests

PROJECT_NUMBER = "254356041555"
ENGINE_ID = "agentspace-testing_1748446185255"

def run_legacy_rag_answer(query: str):
    print(f"Executing Legacy RAG Query: {query}")
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    access_token = credentials.token

    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/global/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:answer"
    
    payload = {
        "query": {"text": query},
        "relatedQuestionsSpec": {"enable": True},
        "answerGenerationSpec": {
            "ignoreAdversarialQuery": True,
            "ignoreNonAnswerSeekingQuery": False,
            "ignoreLowRelevantContent": False, 
            "includeCitations": True,
            "modelSpec": {"modelVersion": "stable"}
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER
    }

    print(f"Calling: {url}")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("\n=== LEGACY RAG ANSWER ===")
        print(data.get("answer", {}).get("answerText", "No answer found."))
        print("\n=== RAW RESPONSE DUMP ===")
        print("Keys:", data.keys())
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    run_legacy_rag_answer("What is the main topic of the documents?")
