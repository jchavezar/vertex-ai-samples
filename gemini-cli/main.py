import os
import requests
import google.auth
from google.auth.transport.requests import Request

# Defaults taken from the antigravity/ge_understanding example
DEFAULT_PROJECT_NUMBER = "254356041555"
DEFAULT_ENGINE_ID = "agentspace-testing_1748446185255"

def query_ge_understanding(query: str, project_number: str = DEFAULT_PROJECT_NUMBER, engine_id: str = DEFAULT_ENGINE_ID):
    """Queries the Gemini Enterprise Discovery Engine answer API."""
    try:
        # Get ADC credentials
        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = Request()
        credentials.refresh(auth_req)
        access_token = credentials.token

        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search:answer"
        
        payload = {
            "query": {"text": query},
            "session": "",
            "relatedQuestionsSpec": {"enable": True},
            "answerGenerationSpec": {
                "ignoreAdversarialQuery": True,
                "ignoreNonAnswerSeekingQuery": False,
                "ignoreLowRelevantContent": True,
                "multimodalSpec": {},
                "includeCitations": True,
                "modelSpec": {"modelVersion": "stable"}
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": project_number
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            answer_dict = data.get("answer", {})
            
            # The answer text is usually in answer_dict["answerText"]
            answer_text = answer_dict.get("answerText", "No direct answer returned. The query might not have matched any documents.")
            
            # Print citations if available
            citations = answer_dict.get("citations", [])
            
            return {
                "text": answer_text,
                "citations": citations
            }
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}

    except google.auth.exceptions.DefaultCredentialsError:
        return {"error": "Google Default Credentials not found. Please run 'gcloud auth application-default login' first."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def main():
    print("="*60)
    print("Gemini Enterprise Discovery Engine CLI")
    print(f"Targeting Project Number: {DEFAULT_PROJECT_NUMBER}")
    print(f"Targeting Engine ID:      {DEFAULT_ENGINE_ID}")
    print("="*60)
    print("Type 'exit' or 'quit' to exit.\n")

    while True:
        try:
            user_query = input("Ask a question: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
            
        user_query = user_query.strip()
        if user_query.lower() in ['exit', 'quit']:
            break
            
        if not user_query:
            continue
            
        print("Querying Gemini Enterprise...")
        
        result = query_ge_understanding(user_query)
        
        if "error" in result:
            print(f"\n[ERROR]\n{result['error']}\n")
        else:
            print("\n[ANSWER]")
            print(result["text"])
            
            if result.get("citations"):
                print("\n[CITATIONS]")
                for i, citation in enumerate(result["citations"]):
                    # Handle citation formatting
                    sources = citation.get("sources", [])
                    for source in sources:
                        uri = source.get("uri", "")
                        title = source.get("title", "Unknown Title")
                        print(f"  [{i+1}] {title} ({uri})")
            print("-" * 60 + "\n")

if __name__ == "__main__":
    main()
