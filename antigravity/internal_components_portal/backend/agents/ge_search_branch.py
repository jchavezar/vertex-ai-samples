import json
import logging
import requests
import google.auth
from google.auth.transport.requests import Request
from utils.protocol import AIStreamProtocol

logger = logging.getLogger(__name__)

PROJECT_NUMBER = "440133963879" # from nexus_search_core
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

    from google.cloud import discoveryengine_v1 as discoveryengine
    import time
    
    try:
        # Set up the client
        client_options = {"api_endpoint": "discoveryengine.googleapis.com"}
        client = discoveryengine.ConversationalSearchServiceClient(client_options=client_options)

        # Build serving config manually to use collections/ engines/ instead of dataStores/
        serving_config = f"projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search"

        request = discoveryengine.AnswerQueryRequest(
            serving_config=serving_config,
            query=discoveryengine.Query(text=query),
            related_questions_spec=discoveryengine.AnswerQueryRequest.RelatedQuestionsSpec(enable=True),
            answer_generation_spec=discoveryengine.AnswerQueryRequest.AnswerGenerationSpec(
                model_spec={"model_version": "stable"},
                include_citations=True,
                ignore_non_answer_seeking_query=False,
                ignore_low_relevant_content=False,
                ignore_adversarial_query=True
            )
        )

        reasoning_steps.append(f"[Discovery Engine] API EVIDENCE: endpoint\nClient: ConversationalSearchServiceClient")
        reasoning_steps.append(f"[Discovery Engine] TOOL CALL: answer_query(stream=True)\nQuery: {query}")
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}})
        
        yield AIStreamProtocol.data({"type": "status", "message": "🔍 Calling Gemini Enterprise (Discovery Engine)...", "icon": "search", "pulse": True})

        api_start = time.time()
        # Make the streaming request
        response_stream = client.stream_answer_query(request=request)
        
        is_first_chunk = True
        references = []
        
        for response in response_stream:
            # First chunk telemetry
            if is_first_chunk:
                api_duration = time.time() - api_start
                latency_metrics.append({"step": "[Discovery Engine] API Call", "duration_s": round(api_duration, 2)})
                reasoning_steps.append(f"[Discovery Engine] TOOL RESPONSE: Stream Connected")
                yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}})
                
                # Check for initial references 
                if response.answer and response.answer.references:
                    references = response.answer.references
                
                is_first_chunk = False

            # Stream the answerText fragment if present
            if response.answer and response.answer.answer_text:
                if "SYNTHESIS" not in reasoning_steps[-1]:
                    reasoning_steps.append("[Discovery Engine] SYNTHESIS:\n...")
                    yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}})
                
                yield AIStreamProtocol.text(response.answer.answer_text)

        # Stream references at the end
        if references:
            yield AIStreamProtocol.text("\n\n**Sources:**\n")
            for ref in references:
                if ref.chunk_info and ref.chunk_info.document_metadata:
                    title = ref.chunk_info.document_metadata.title or "Document"
                    uri = ref.chunk_info.document_metadata.uri or ""
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
