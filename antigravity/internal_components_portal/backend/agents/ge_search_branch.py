import json
import logging
import requests
import google.auth
from google.auth.transport.requests import Request
from utils.protocol import AIStreamProtocol

logger = logging.getLogger(__name__)

PROJECT_NUMBER = "REDACTED_PROJECT_NUMBER" # from nexus_search_core
LOCATION = "global"
ENGINE_ID = "deloitte-demo"

def get_gcp_token():
    try:
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        if not credentials.valid:
            credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        logger.error(f"Failed to get GCP token: {e}")
        # Return empty or raise, discovery might fail
        return None

async def stream_ge_search(query: str):
    """
    Calls the Discovery Engine Answer API and yields the result using AIStreamProtocol.
    Includes telemetry data for the Execution Latency dashboard.
    """
    reasoning_steps = []
    latency_metrics = []
    import time
    start_time = time.time()

    token = get_gcp_token()
    if not token:
        yield AIStreamProtocol.text("\n❌ Failed to authenticate with Google Cloud to call Discovery Engine.\n")
        return

    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:answer"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER
    }
    
    payload = {
        "query": { "text": query },
        "relatedQuestionsSpec": { "enable": True },
        "answerGenerationSpec": {
            "modelSpec": { "modelVersion": "stable" },
            "includeCitations": True,
            "ignoreNonAnswerSeekingQuery": False,
            "ignoreLowRelevantContent": False,
            "ignoreAdversarialQuery": True
        }
    }
    
    reasoning_steps.append(f"[Discovery Engine] API EVIDENCE: endpoint\nURL: {url}")
    reasoning_steps.append(f"[Discovery Engine] TOOL CALL: servingConfigs/default_search:answer\nARGS: {json.dumps(payload, indent=2)}")
    yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}})
    
    yield AIStreamProtocol.data({"type": "status", "message": "🔍 Calling Gemini Enterprise (Discovery Engine)...", "icon": "search", "pulse": True})
    
    try:
        api_start = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        api_duration = time.time() - api_start
        response.raise_for_status()
        data = response.json()
        
        latency_metrics.append({"step": "[Discovery Engine] API Call", "duration_s": round(api_duration, 2)})
        
        # Show the raw response in reasoning trace
        reasoning_steps.append(f"[Discovery Engine] TOOL RESPONSE: raw_json\nRESULT: {json.dumps(data, indent=2)}")
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}})

        answer_obj = data.get("answer", {})
        answer_text = answer_obj.get("answerText", "No answer found.")
        
        reasoning_steps.append(f"[Discovery Engine] SYNTHESIS:\n{answer_text}")
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}})

        yield AIStreamProtocol.text(answer_text + "\n\n")
        
        # References/citations
        references = answer_obj.get("references", [])
        if references:
            yield AIStreamProtocol.text("\n**Sources:**\n")
            for ref in references:
                chunk_info = ref.get("chunkInfo", {})
                title = chunk_info.get("documentMetadata", {}).get("title", "Document")
                uri = chunk_info.get("documentMetadata", {}).get("uri", "")
                content = chunk_info.get("content", "")[:200] + "..."
                if uri:
                    yield AIStreamProtocol.text(f"- [{title}]({uri})\n")
                else:
                    yield AIStreamProtocol.text(f"- {title}\n")
                    
        total_time = time.time() - start_time
        latency_metrics.append({"step": "[Total] Router: SEARCH", "duration_s": round(total_time, 2)})
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}})

    except requests.exceptions.HTTPError as e:
        err_text = e.response.text
        logger.error(f"GE Search API HTTP Error: {err_text}")
        reasoning_steps.append(f"[Discovery Engine] ERROR: {err_text}")
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}})
        yield AIStreamProtocol.text(f"\n❌ GE Search API Error. Check logs.\n")
    except Exception as e:
        logger.error(f"GE Search failed: {e}")
        reasoning_steps.append(f"[Discovery Engine] EXCEPTION: {str(e)}")
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}})
        yield AIStreamProtocol.text(f"\n❌ GE Search Error: {str(e)}\n")
