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

def get_gcp_token(entra_token: str = None):
    # If Entra ID token is provided, attempt WIF STS exchange directly
    if entra_token and entra_token not in ["null", "undefined", "None"]:
        try:
            sts_url = "https://sts.googleapis.com/v1/token"
            audience = f"//iam.googleapis.com/locations/global/workforcePools/entra-id-oidc-pool-d/providers/entra-id-oidc-pool-provider-de"
            
            payload = {
                "audience": audience,
                "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
                "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
                "scope": "https://www.googleapis.com/auth/cloud-platform",
                "subjectToken": entra_token,
                "subjectTokenType": "urn:ietf:params:oauth:token-type:id_token",
            }
            resp = requests.post(sts_url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("Successfully exchanged Entra ID token for STS token via WIF")
            return resp.json().get("access_token")
        except Exception as e:
            logger.error(f"STS Exchange Failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"STS Error Response: {e.response.text}")
            logger.info("Falling back to default GCP credentials")

    # Fallback to default credentials (will need userPseudoId later)
    try:
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        if not credentials.valid:
            credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        logger.error(f"Failed to get fallback GCP token: {e}")
        return None

async def _contextualize_query(query: str, history: list, adk_events_trace: list = None) -> str:
    """Uses Gemini 2.5 Flash via ADK to rewrite a conversational query into a standalone search query."""
    if not history or len(history) <= 1:
        return query
        
    try:
        from google.adk.agents.llm_agent import LlmAgent
        from google.adk.runners.runner import Runner
        import os
        
        contextualize_agent = LlmAgent(
            name="query_contextualizer",
            model="gemini-2.5-flash",
            instruction="Given a conversation history and a follow-up query, rephrase the follow-up query to be a standalone search query that can be understood without the conversation history. Return ONLY the standalone query, no extra text."
        )
        
        # Build prompt
        prompt = "CONVERSATION HISTORY:\n"
        for msg in history[:-1][-4:]: # Only take last 4 messages for context to keep it fast
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            prompt += f"{role}: {content}\n"
            
        prompt += f"\nFOLLOW-UP QUERY: {query}\n"
        prompt += "STANDALONE SEARCH QUERY (Return ONLY the query, no extra text):"
        
        runner = Runner(agent=contextualize_agent)
        rewritten_text = ""
        
        async for event in runner.run_async(prompt):
            if adk_events_trace is not None:
                edata = event.model_dump(mode='json')
                adk_events_trace.append({"source": "query_contextualizer", "event": edata})
            
            if event.author == "model" and getattr(event, "content", None):
                parts = getattr(event.content, "parts", [])
                for p in parts:
                    if getattr(p, "text", None):
                        rewritten_text += p.text
                        
        rewritten = rewritten_text.strip()
        return rewritten if rewritten else query
    except Exception as e:
        logger.warning(f"Failed to contextualize query: {e}")
        return query

async def stream_ge_search(messages: list, adk_events_trace: list = None, payload: dict = None):
    """
    Calls the Discovery Engine Answer API and yields the result using AIStreamProtocol.
    Includes telemetry data for the Execution Latency dashboard.
    """
    query = messages[-1].get("content", "")
    reasoning_steps = []
    latency_metrics = []
    from utils.auth_context import get_user_token, get_user_id_token
    import jwt
    import time
    
    start_time = time.time()
    user_entra_token = get_user_token()
    user_entra_id_token = get_user_id_token()
    
    # ALWAYS use WIF exchange with the Entra ID token to get a Service Account token
    token = get_gcp_token(user_entra_id_token) 
    reasoning_steps.append("[Discovery Engine] AUTH MODE: 2LO (WIF Service Account using Entra ID)")
    
    if not token:
        yield AIStreamProtocol.text("\n❌ Failed to authenticate with Google Cloud to call Discovery Engine.\n")
        return

    from google.cloud import discoveryengine_v1 as discoveryengine
    
    # 1. Contextualize Query
    contextualize_start = time.time()
    search_query = await _contextualize_query(query, messages, adk_events_trace)
    if search_query != query:
        reasoning_steps.append(f"[Discovery Engine] QUERY REWRITE:\nOriginal: {query}\nRewritten: {search_query}")
        latency_metrics.append({"step": "[Discovery Engine] Contextualization", "duration_s": round(time.time() - contextualize_start, 2)})
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})


    try:
        # 2. Fetch DataStore Specs to enable SharePoint/3p Connector grounding
        # We must use default credentials for this admin metadata, as the WIF user token lacks permissions.
        try:
             admin_creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
             if not admin_creds.valid:
                 admin_creds.refresh(Request())
             admin_token = admin_creds.token
        except Exception as e:
             logger.error(f"Failed to get admin token for widgetConfigs: {e}")
             admin_token = token
             
        ds_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/widgetConfigs/default_search_widget_config"
        ds_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": PROJECT_NUMBER
        }
        
        ds_resp = requests.get(ds_url, headers=ds_headers, timeout=10)
        dataStoreSpecs = []
        if ds_resp.status_code == 200:
             collections = ds_resp.json().get('collectionComponents', [{}])
             dataStoreSpecs = [
                 {'dataStore': r['name']}
                 for r in collections[0].get('dataStoreComponents', [])
             ]

        # ALWAYS use streamAssist to support conversational history and federated connector schemas
        url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/assistants/default_assistant:streamAssist"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": PROJECT_NUMBER
        }
        
        payload = {
            "query": { "text": search_query }
        }
        
        if dataStoreSpecs:
            payload["toolsSpec"] = {
                "vertexAiSearchSpec": {
                    "dataStoreSpecs": dataStoreSpecs
                }
            }

        
        # When using streamAssist with a Service Account (via WIF 2LO), userPseudoId is typically 
        # set differently or not required natively at the root payload for this specific API version.
        # We will log the identity for auditing but remove it from the strict streamAssist payload.
        user_email = "default_user"
        debug_log = [
            f"--- NEW REQUEST ---",
            f"user_entra_id_token present: {bool(user_entra_id_token)}"
        ]
        
        if user_entra_id_token and user_entra_id_token not in ["null", "undefined", "None"]:
            try:
                decoded = jwt.decode(user_entra_id_token, options={"verify_signature": False})
                debug_log.append(f"Decoded JWT keys: {list(decoded.keys())}")
                user_email = decoded.get("preferred_username") or decoded.get("upn") or decoded.get("email") or "default_user"
                debug_log.append(f"Extracted user_email: {user_email}")
            except Exception as e:
                logger.error(f"Failed to decode Entra ID token: {e}")
                debug_log.append(f"Token Decode Exception: {e}")
                
                
        # Write debug log to file
        with open("/tmp/ge_search_debug.log", "a") as f:
            f.write("\n".join(debug_log) + "\n\n")

        payload_str = json.dumps(payload, indent=2)
        api_method = "streamAssist"
        reasoning_steps.append(f"[Discovery Engine] API EVIDENCE: endpoint\nURL: {url}\nClient: REST POST ({api_method})\nPayload:\n{payload_str}")
        reasoning_steps.append(f"[Discovery Engine] TOOL CALL: {api_method}\nQuery: {search_query}")
        
        if adk_events_trace is not None:
            adk_events_trace.append({
                "source": "ge_search_engine",
                "event": {
                    "author": "model",
                    "content": {
                        "parts": [{"text": f"Calling Discovery Engine for: {search_query}"}]
                    }
                }
            })

        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})
        
        yield AIStreamProtocol.data({"type": "status", "message": "🔍 Calling Gemini Enterprise (Discovery Engine)...", "icon": "search", "pulse": True})

        api_start = time.time()
        # Make the streaming request
        response_stream = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
        response_stream.raise_for_status()
        
        is_first_chunk = True
        references = []
        ge_answer_text = ""
        extracted_search_results = []
        
        json_buffer = ""
        bracket_count = 0
        in_string = False
        escape = False

        for chunk in response_stream.iter_content(chunk_size=1024):
            if not chunk: continue
            
            chunk_str = chunk.decode('utf-8')
            for char in chunk_str:
                json_buffer += char
                
                if char == '\\' and not escape:
                    escape = True
                    continue
                    
                if char == '"' and not escape:
                    in_string = not in_string
                elif char == '{' and not in_string:
                    bracket_count += 1
                elif char == '}' and not in_string:
                    bracket_count -= 1
                    
                    if bracket_count == 0 and '{' in json_buffer:
                        # We have a complete JSON object
                        start_idx = json_buffer.find('{')
                        obj_str = json_buffer[start_idx:]
                        
                        try:
                            data = json.loads(obj_str)
                        except json.JSONDecodeError:
                            json_buffer = ""
                            escape = False
                            continue
                            
                        # Reset for next object
                        json_buffer = ""
                        escape = False
                        
                        if "answer" not in data:
                            continue
                            
                        ans = data["answer"]
                        
                        # First chunk telemetry
                        if is_first_chunk:
                            api_duration = time.time() - api_start
                            latency_metrics.append({"step": "[Discovery Engine] API Call", "duration_s": round(api_duration, 2)})
                            reasoning_steps.append(f"[Discovery Engine] TOOL RESPONSE: Stream Connected")
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})
                            is_first_chunk = False

                        def _find_key(obj, key):
                            if isinstance(obj, dict):
                                if key in obj: return obj[key]
                                for k, v in obj.items():
                                    res = _find_key(v, key)
                                    if res is not None: return res
                            elif isinstance(obj, list):
                                for item in obj:
                                    res = _find_key(item, key)
                                    if res is not None: return res
                            return None                        # Check for references recursively in any chunk
                        refs = _find_key(ans, "references")
                        if refs and isinstance(refs, list):
                            for ref in refs:
                                doc_name = ref.get("document", "")
                                meta = ref.get("chunkInfo", {}).get("documentMetadata", {})
                                uri = meta.get("uri", "")
                                title = meta.get("title", "")
                                
                                # Try to enrich from extracted_search_results if missing
                                if (not uri or not title) and doc_name:
                                    for sr in extracted_search_results:
                                        if sr.get("document") == doc_name:
                                            if not title:
                                                title = sr.get("title", "")
                                                if not title and isinstance(sr.get("document"), dict):
                                                    sd = sr["document"].get("structData", {})
                                                    dsd = sr["document"].get("derivedStructData", {})
                                                    if isinstance(sd, dict):
                                                        title = sd.get("title") or sd.get("name") or ""
                                                    if not title and isinstance(dsd, dict):
                                                        title = dsd.get("title") or ""
                                            if not uri:
                                                # Sometimes the top-level has uri/url
                                                uri = sr.get("url") or sr.get("uri") or ""
                                                if not uri and isinstance(sr.get("document"), dict):
                                                    sd = sr["document"].get("structData", {})
                                                    if isinstance(sd, dict):
                                                        uri = sd.get("url") or sd.get("url_for_connector") or ""
                                            break
                                
                                title = title or "Unknown Title"
                                
                                # Plumb it back into the ref so the final text blocks can map it properly
                                if "chunkInfo" not in ref:
                                    ref["chunkInfo"] = {}
                                if "documentMetadata" not in ref["chunkInfo"]:
                                    ref["chunkInfo"]["documentMetadata"] = {}
                                ref["chunkInfo"]["documentMetadata"]["title"] = title
                                ref["chunkInfo"]["documentMetadata"]["uri"] = uri
                                
                                # Deduplicate to avoid repeating the same document
                                if not any(r.get("document") == doc_name for r in references):
                                    references.append(ref)
                                
                                # The user requested snippets and datastore info in Latency Profile
                                content = ref.get("chunkInfo", {}).get("content", "")
                                clean_content = content.replace('\n', ' ')[:250]
                                ref_str = f"[Discovery Engine] DATASOURCE:\nTitle: {title}\nURI: {uri}\nSnippet: {clean_content}..."
                                if ref_str not in reasoning_steps:
                                    reasoning_steps.append(ref_str)
                                    yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})
                            
                        if "steps" in ans:
                            for step in ans["steps"]:
                                state = step.get("state", "")
                                thought = step.get("thought", "")
                                if thought:
                                    step_str = f"[Discovery Engine] THOUGHT: [{state}] {thought}"
                                    if step_str not in reasoning_steps:
                                        reasoning_steps.append(step_str)
                                        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})
                                        
                                desc = step.get("description", "")
                                if desc:
                                    step_str = f"[Discovery Engine] STEP: [{state}] {desc}"
                                    if step_str not in reasoning_steps:
                                        reasoning_steps.append(step_str)
                                        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})
                                        
                                # Extract searchResults for fallback and tracing
                                actions = step.get("actions", [])
                                for action in actions:
                                    obs = action.get("observation", {})
                                    s_results = obs.get("searchResults", [])
                                    if s_results:
                                        action_str = f"[Discovery Engine] DATASOURCE: Retrieved {len(s_results)} documents from enterprise."
                                        if action_str not in reasoning_steps:
                                            reasoning_steps.append(action_str)
                                            for idx, res in enumerate(s_results[:5]): # Log top 5 details
                                                doc_id = res.get("document", "").split('/')[-1][:20]
                                                title = res.get("title", "Unknown Title")
                                                snippet = res.get("snippetInfo", [{}])[0].get("snippet", "")
                                                clean_snippet = snippet.replace('<b>', '').replace('</b>', '').replace('<br>', ' ')[:100]
                                                reasoning_steps.append(f"[Discovery Engine] DATASOURCE: Source {idx+1} | {title} (ID: {doc_id})\nSnippet: {clean_snippet}...")
                                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})
                                            
                                    for res in s_results:
                                        # Deduplicate based on document string
                                        doc_id = res.get("document", "")
                                        if not any(r.get("document") == doc_id for r in extracted_search_results):
                                            extracted_search_results.append(res)

                        # Check for related questions
                        if "relatedQuestions" in ans:
                            rqs = ans["relatedQuestions"]
                            rq_str = "\n".join([f"- {rq}" for rq in rqs])
                            rq_log = f"[Discovery Engine] ANALYSIS: Generated Follow-up Questions:\n{rq_str}"
                            if rq_log not in reasoning_steps:
                                reasoning_steps.append(rq_log)
                                yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})

                        # Stream the answerText or replies fragment if present
                        chunk_text = ""
                        is_thought = False
                        
                        if "replies" in ans and len(ans["replies"]) > 0:
                            reply = ans["replies"][0]
                            content = reply.get("groundedContent", {}).get("content", {})
                            text = content.get("text", "")
                            if not text and "parts" in content and isinstance(content["parts"], list) and len(content["parts"]) > 0:
                                text = content["parts"][0].get("text", "")
                            
                            is_thought = content.get("thought", False)
                                
                            if is_thought:
                                thought_chunk = text
                                if thought_chunk:
                                    # Append to last thought if contiguous to avoid UI fragment spam
                                    if reasoning_steps and reasoning_steps[-1].startswith("[Discovery Engine] THOUGHT:"):
                                        reasoning_steps[-1] += thought_chunk
                                    else:
                                        reasoning_steps.append(f"[Discovery Engine] THOUGHT:\n{thought_chunk}")
                                    yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})
                            else:
                                chunk_text = text or ans.get("answerText", "")
                        elif "answerText" in ans:
                            chunk_text = ans["answerText"]
                            
                        # Universal fallback: if the chunk is explicitly formatted as a thought but missed flags
                        if not is_thought and chunk_text.strip().startswith("**") and chunk_text.strip().endswith("**"):
                            is_thought = True
                            if reasoning_steps and reasoning_steps[-1].startswith("[Discovery Engine] THOUGHT:"):
                                reasoning_steps[-1] += chunk_text
                            else:
                                reasoning_steps.append(f"[Discovery Engine] THOUGHT:\n{chunk_text}")
                            yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})
                            
                        if chunk_text and not is_thought:
                            if not reasoning_steps or "FINAL RESPONSE" not in reasoning_steps[-1]:
                                reasoning_steps.append("[Discovery Engine] FINAL RESPONSE:\n...")
                                yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})
                            
                            ge_answer_text += chunk_text
                            yield AIStreamProtocol.text(chunk_text)
                            
                escape = False
                
        if adk_events_trace is not None:
            adk_events_trace.append({
                "source": "ge_search_engine",
                "event": {
                    "author": "tool",
                    "content": {
                        "parts": [{"text": ge_answer_text}]
                    }
                }
            })

        # Fallback to Classic Search if Answer Generation Failed
        is_fallback = False
        if "could not be generated" in ge_answer_text or "I am sorry" in ge_answer_text or not ge_answer_text:
            is_fallback = True
            logger.info("Quality check failed, trying fallback search...")
            search_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_search:search"
            try:
                search_payload = {
                    "query": query,
                    "pageSize": 5
                }
                if "userPseudoId" in payload:
                    search_payload["userPseudoId"] = payload["userPseudoId"]
                    
                debug_log.append(f"Fallback Search Payload: {json.dumps(search_payload)}")
                with open("/tmp/ge_search_debug.log", "a") as f:
                    f.write("\n".join(debug_log) + "\n\n")

                search_resp = requests.post(search_url, headers=headers, json=search_payload, timeout=30)
                try:
                    search_resp.raise_for_status()
                except Exception as e:
                    with open("/tmp/ge_search_debug.log", "a") as f:
                        f.write(f"Fallback Error Status: {search_resp.status_code}\nFallback Error Body: {search_resp.text}\n\n")
                    raise e
                
                # Parse the JSON stream (we're not streaming it to the user since it's fallback, just collecting the results)
                extracted_search_results = []
                json_buffer = ""
                bracket_count = 0
                in_string = False
                escape = False
                
                for chunk in search_resp.iter_content(chunk_size=1024):
                    if not chunk: continue
                    chunk_str = chunk.decode('utf-8')
                    for char in chunk_str:
                        json_buffer += char
                        if char == '\\' and not escape:
                            escape = True
                            continue
                        if char == '"' and not escape:
                            in_string = not in_string
                        elif char == '{' and not in_string:
                            bracket_count += 1
                        elif char == '}' and not in_string:
                            bracket_count -= 1
                            if bracket_count == 0 and '{' in json_buffer:
                                start_idx = json_buffer.find('{')
                                obj_str = json_buffer[start_idx:]
                                try:
                                    data = json.loads(obj_str)
                                except json.JSONDecodeError:
                                    json_buffer = ""
                                    escape = False
                                    continue
                                json_buffer = ""
                                escape = False
                                
                                if "results" in data:
                                    s_results = data.get("results", [])
                                    for res in s_results:
                                        doc_id = res.get("document", {}).get("name", "")
                                        if not any(r.get("document") == doc_id for r in extracted_search_results):
                                            struct_data = res.get("document", {}).get("structData", {})
                                            derived_struct_data = res.get("document", {}).get("derivedStructData", {})
                                            title = struct_data.get("title") or struct_data.get("name") or derived_struct_data.get("title") or res.get("document", {}).get("name", "Source Material").split('/')[-1]
                                            uri = struct_data.get("url") or struct_data.get("url_for_connector") or ""
                                            snippet_info = res.get("document", {}).get("derivedStructData", {}).get("snippets", [])
                                            if not snippet_info:
                                                snippet_info = res.get("snippetInfo", [{}])
                                            snippet = snippet_info[0].get("snippet") if snippet_info else struct_data.get("snippet") or struct_data.get("description") or ""
                                            if isinstance(title, str) and title:
                                                extracted_search_results.append({
                                                    "title": title,
                                                    "uri": uri,
                                                    "snippetInfo": [{"snippet": snippet}] if snippet else [],
                                                    "document": doc_id
                                                })
                                str_to_eval = "escape = False" 
                                exec(str_to_eval)

            except Exception as e:
                logger.error(f"Fallback search failed: {e}")

        # Stream references at the end
        if references:
            yield AIStreamProtocol.text("\n\n**Sources:**\n")
            for idx, ref in enumerate(references):
                chunk_info = ref.get("chunkInfo", {})
                doc_meta = chunk_info.get("documentMetadata", {})
                title = doc_meta.get("title", "Document")
                uri = doc_meta.get("uri", "")
                if uri:
                    yield AIStreamProtocol.text(f"[{idx+1}] [{title}]({uri})\n")
                else:
                    yield AIStreamProtocol.text(f"[{idx+1}] {title}\n")
                    
        # Always output fallback results if we extracted them
        if extracted_search_results:
            yield AIStreamProtocol.text("\n\n**Fallback Search Results:**\n")
            for sr in extracted_search_results[:5]: # show top 5
                title = sr.get("title", "Document")
                uri = sr.get("uri", "")
                snippets = sr.get("snippetInfo", [])
                snippet_text = snippets[0].get("snippet", "") if snippets else ""
                # Clean snippet HTML highlights if needed
                snippet_text = snippet_text.replace("<b>", "**").replace("</b>", "**")
                
                if uri:
                    yield AIStreamProtocol.text(f"- [{title}]({uri})\n")
                else:
                    yield AIStreamProtocol.text(f"- {title}\n")
                if snippet_text:
                    yield AIStreamProtocol.text(f"  > {snippet_text}\n\n")
                        
        total_time = time.time() - start_time
        latency_metrics.append({"step": "[Total] Router: SEARCH", "duration_s": round(total_time, 2)})
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})

    except requests.exceptions.HTTPError as e:
        err_text = e.response.text
        logger.error(f"GE Search API HTTP Error: {err_text}")
        reasoning_steps.append(f"[Discovery Engine] ERROR: {err_text}")
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})
        yield AIStreamProtocol.text(f"\n❌ GE Search API Error. Check logs.\n")
    except Exception as e:
        logger.error(f"GE Search failed: {e}")
        reasoning_steps.append(f"[Discovery Engine] EXCEPTION: {str(e)}")
        yield AIStreamProtocol.data({"type": "telemetry", "data": latency_metrics, "reasoning": reasoning_steps, "tokens": {"prompt": 0, "candidates": 0, "total": 0}, "adk_events": adk_events_trace})
        yield AIStreamProtocol.text(f"\n❌ GE Search Error: {str(e)}\n")
