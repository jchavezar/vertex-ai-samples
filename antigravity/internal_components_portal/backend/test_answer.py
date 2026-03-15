import requests
import os
import json

token = os.popen("gcloud auth print-access-token").read().strip()
PROJECT_NUMBER = "165769747209"
LOCATION = "global"
ENGINE_ID = "rag-engine_1731518774094"

url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:answer"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "X-Goog-User-Project": PROJECT_NUMBER
}

payload = {
    "query": { "text": "What are the features of Vertex AI?" },
    "relatedQuestionsSpec": { "enable": True },
    "answerGenerationSpec": {
        "modelSpec": { "modelVersion": "stable" },
        "includeCitations": True,
        "ignoreNonAnswerSeekingQuery": False,
        "ignoreLowRelevantContent": False,
        "ignoreAdversarialQuery": True
    }
}

print("Calling Discovery Engine Answer API...")
resp = requests.post(url, headers=headers, json=payload)
data = resp.json()

print(data.get("answer", {}).get("answerText", "No Answer"))
