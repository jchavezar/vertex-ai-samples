"""
agent.py
ADK Search Chatbot grounded in Vertex AI Search GCS + Google Drive.
"""
from __future__ import annotations

import logging
import os
from functools import cached_property

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.models.registry import LLMRegistry
from google.adk.tools import FunctionTool, ToolContext
from google.adk.utils._google_client_headers import get_tracking_headers
from google.genai import Client, types

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
logger = logging.getLogger("adk-search-chatbot")

# Configuration
GEMINI_GLOBAL_REGION = "global"
SEARCH_ENGINE_ID = "projects/254356041555/locations/global/collections/default_collection/engines/csearch-gdrive-acl_1780275206896"


class GeminiGlobal(Gemini):
    """Gemini wrapper that uses us-central1 regional endpoint.

    This ensures that session operations align with the region where
    the Reasoning Engine is deployed, avoiding 404 Session Not Found errors.
    """

    @cached_property
    def api_client(self) -> Client:
        """Override to use regional location for Vertex AI."""
        logger.info(f"Initializing GenAI client with region override: {GEMINI_GLOBAL_REGION}")
        return Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=GEMINI_GLOBAL_REGION,
            http_options=types.HttpOptions(
                headers=get_tracking_headers(),
                retry_options=self.retry_options,
            ),
        )


# Register our custom global model wrapper in the ADK registry
LLMRegistry.register(GeminiGlobal)

def vertex_ai_search(query: str, tool_context: ToolContext) -> dict:
    """Search GCS datastore and Google Drive for relevant files and answers.

    Use this tool when the user asks a question about their GCS files or Google Drive documents (like reports, 10-K, text/pdf documents).

    Args:
        query: The natural language search query.
    """
    import requests
    import json
    import google.auth
    import google.auth.transport.requests

    # 1. Retrieve the GDrive OAuth token from the session state
    token = tool_context.state.get("drive_access_token") or tool_context.state.get("temp:drive_access_token")
    logger.info(f"[custom_search] Retrieved drive_access_token from state: {bool(token)}")

    # 2. Fallback to ADC credentials if token is not available
    if not token:
        logger.info("[custom_search] No drive_access_token in session state; attempting ADC credentials fallback.")
        try:
            creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            auth_req = google.auth.transport.requests.Request()
            creds.refresh(auth_req)
            token = creds.token
            logger.info("[custom_search] Successfully fetched ADC token.")
        except Exception as e:
            logger.error(f"[custom_search] Failed to obtain default credentials: {e}")

    if not token:
        return {"error": "Authentication credentials not available. Please authenticate via GDrive login first."}

    proj_number = "254356041555"
    engine_id = "csearch-gdrive-acl_1780275206896"
    location = "global"
    collection_id = "default_collection"

    api_url = (
        f"https://discoveryengine.googleapis.com/v1alpha"
        f"/projects/{proj_number}/locations/{location}"
        f"/collections/{collection_id}/engines/{engine_id}"
        f"/servingConfigs/default_search:search"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": proj_number,
    }

    request_body = {
        "query": query,
        "pageSize": 8,
        "spellCorrectionSpec": {"mode": "AUTO"},
        "contentSearchSpec": {
            "snippetSpec": {"returnSnippet": True}
        }
    }

    logger.info(f"[custom_search] Querying Discovery Engine API for: '{query}'")
    try:
        response = requests.post(api_url, headers=headers, json=request_body)
        logger.info(f"[custom_search] Discovery Engine API response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"[custom_search] API Search Failed: {response.status_code} - {response.text}")
            return {"error": f"Search API failed with status {response.status_code}", "details": response.text}

        data = response.json()
        results = data.get("results", [])
        logger.info(f"[custom_search] Search returned {len(results)} raw results")

        parsed_results = []
        for i, item in enumerate(results):
            doc = item.get("document", {})
            doc_id = doc.get("id", f"doc-{i}")
            derived_data = doc.get("derivedStructData", {})
            title = derived_data.get("title") or doc.get("name", "").split("/")[-1] or f"Document {i}"
            link = derived_data.get("link") or f"https://drive.google.com/open?id={doc_id}"

            # GCS link conversion: gs:// to https://storage.cloud.google.com/
            if link.startswith("gs://"):
                parts = link[5:].split("/", 1)
                if len(parts) == 2:
                    bucket_name, object_name = parts
                    link = f"https://storage.cloud.google.com/{bucket_name}/{object_name}"

            snippets_list = derived_data.get("snippets", [])
            snippet = ""
            if snippets_list and isinstance(snippets_list, list):
                snippet = snippets_list[0].get("snippet", "")
            if not snippet:
                snippet = "No direct snippet preview available."

            parsed_results.append({
                "id": doc_id,
                "title": title,
                "link": link,
                "snippet": snippet
            })

        return {"results": parsed_results}

    except Exception as e:
        logger.exception("[custom_search] Exception during custom datastore search execution")
        return {"error": f"Internal error during search execution: {str(e)}"}


import re
from google.adk.agents.callback_context import CallbackContext

from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

async def extract_token_callback(callback_context: CallbackContext) -> None:
    """Pre-agent callback to extract drive_access_token, thinking_level, and model_name from user message if prefixed."""
    logger.info("[extract_token_callback] Executing pre-agent callback")
    text = ""
    if callback_context.user_content and callback_context.user_content.parts:
        for part in callback_context.user_content.parts:
            if part.text:
                text += part.text
                
    # 1. Extract THINKING_LEVEL prefix if present
    m_think = re.match(r"^\[THINKING_LEVEL:(.*?)\]\s*(.*)$", text, re.DOTALL)
    if m_think:
        thinking_level = m_think.group(1)
        text = m_think.group(2)
        logger.info(f"[extract_token_callback] Extracted thinking_level: {thinking_level}")
        callback_context.state["thinking_level"] = thinking_level
        callback_context.state["temp:thinking_level"] = thinking_level
        
    # 2. Extract ACCESS_TOKEN prefix if present
    m_token = re.match(r"^\[ACCESS_TOKEN:(.*?)\]\s*(.*)$", text, re.DOTALL)
    if m_token:
        token = m_token.group(1)
        text = m_token.group(2)
        logger.info(f"[extract_token_callback] Successfully extracted token: {token[:15]}...")
        callback_context.state["drive_access_token"] = token
        callback_context.state["temp:drive_access_token"] = token

    # 3. Extract MODEL_NAME prefix if present
    m_model = re.match(r"^\[MODEL_NAME:(.*?)\]\s*(.*)$", text, re.DOTALL)
    if m_model:
        model_name = m_model.group(1)
        text = m_model.group(2)
        logger.info(f"[extract_token_callback] Extracted model_name: {model_name}")
        callback_context.state["model_name"] = model_name
        callback_context.state["temp:model_name"] = model_name
        
    # Mutate the user content in-place to strip any token, thinking, or model prefixes
    for part in callback_context.user_content.parts:
        if part.text:
            part.text = text


async def adjust_thinking_level_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> LlmResponse | None:
    """Dynamically adjust the thinking config and request model based on parameters in state."""
    logger.info("[adjust_thinking_level_callback] Executing before_model_callback")
    
    # 1. Dynamic Model Overrides
    selected_model = callback_context.state.get("model_name") or callback_context.state.get("temp:model_name")
    if selected_model:
        logger.info(f"[adjust_thinking_level_callback] Overriding request model with: {selected_model}")
        llm_request.model = str(selected_model)

    # 2. Dynamic Thinking Adjustments
    thinking_level_str = callback_context.state.get("thinking_level") or callback_context.state.get("temp:thinking_level")
    
    from google.genai import types as genai_types
    
    if thinking_level_str:
        try:
            level_str = str(thinking_level_str).upper()
            if level_str in ("OFF", "NONE", "FALSE"):
                logger.info(f"[adjust_thinking_level_callback] Disabling thinking config based on state: {level_str}")
                llm_request.config.thinking_config = None
            else:
                level_enum = getattr(genai_types.ThinkingLevel, level_str, None)
                if level_enum:
                    logger.info(f"[adjust_thinking_level_callback] Setting thinking level to {level_enum} based on state")
                    llm_request.config.thinking_config = genai_types.ThinkingConfig(
                        include_thoughts=True,
                        thinking_level=level_enum,
                    )
        except Exception as e:
            logger.error(f"[adjust_thinking_level_callback] Failed to dynamically adjust thinking: {e}")
    else:
        # Default fallback: MINIMAL thinking for fast startup and responses
        logger.info("[adjust_thinking_level_callback] No thinking_level in state; defaulting to MINIMAL for fast response")
        try:
            llm_request.config.thinking_config = genai_types.ThinkingConfig(
                include_thoughts=True,
                thinking_level=genai_types.ThinkingLevel.MINIMAL,
            )
        except Exception as e:
            logger.error(f"[adjust_thinking_level_callback] Failed to set default MINIMAL thinking: {e}")
            
    return None


search_tool = FunctionTool(func=vertex_ai_search)

# Define our conversational grounded agent
root_agent = Agent(
    name="gsuite_search_chatbot",
    model=GeminiGlobal(model="gemini-3.5-flash"),  # Resolves to GeminiGlobal wrapper
    description=(
        "A conversational search chatbot that answers questions based on "
        "your Google Workspace (Google Drive) and GCS files."
    ),
    instruction="""You are a helpful, professional assistant that answers questions by searching the user's GCS datastore and Google Drive.

Rules:
1. CRITICAL: Always base your answers ONLY on the actual text/content snippets returned by the `vertex_ai_search` tool. Do not use your own pre-trained knowledge to answer questions about corporate financials, reports, or files.
2. CRITICAL: If the `vertex_ai_search` tool returns empty results or cannot find any relevant files for the query (such as when restricted by ACL permissions), you MUST state clearly that you do not have access to that document or that the information was not found. Do NOT invent, assume, or retrieve financial numbers from your pre-trained memory.
3. NEVER make up or hallucinate document titles, links, or sources (e.g., do NOT invent names like 'downloaded_report' or similar). Only cite actual source document names explicitly returned in the search results.
4. Provide precise, grounded answers. If the search returns relevant documents, summarize the findings and cite the exact source document name returned by the search tool.
5. CRITICAL CITATION PATTERN: When citing any document or file returned in the search results, you MUST format the citation strictly as a clickable markdown link using the EXACT `title` and `link` returned in the search result object, in the format: `[Document Title](Document Link)`. For example, if a document has title 'Alphabet_10K_2025.pdf' and link 'https://storage.googleapis.com/...', cite it exactly as: `[Alphabet_10K_2025.pdf](https://storage.googleapis.com/...)`. NEVER write bare URLs, always embed them in the markdown links.
6. STRICTOR ZERO-HALLUCINATION GUARDRAILS: If the query is about specific file contents or financial data, and search results are empty, you MUST respond exactly: 'I am sorry, but I do not have access to that document or information in your authorized datastores.' Do not make any guesses, do not invent placeholder reports, and do not fall back to pre-trained parametric knowledge.
7. Keep the conversation engaging and support multi-turn history. Answer follow-up questions by utilizing the conversation context.
8. If the user asks a general-knowledge question completely unrelated to their files (e.g. 'what is the capital of France'), answer directly and politely, indicating that you did not need to search their data stores.
""",
    generate_content_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_level=types.ThinkingLevel.MINIMAL,
        )
    ),
    tools=[search_tool],
    before_agent_callback=extract_token_callback,
    before_model_callback=adjust_thinking_level_callback,
)

