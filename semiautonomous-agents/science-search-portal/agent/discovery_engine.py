"""
Discovery Engine Client with WIF/STS Token Exchange.
Exchanges Microsoft Entra ID JWT for GCP access token via Workforce Identity Federation.

Version: 1.2.0
Date: 2026-04-05
Note: Uses WIF_PROVIDER_ID from env (must be entra-provider for api:// audience)
"""
import os
import json
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import requests
import google.auth
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


@dataclass
class SourceDocument:
    """A source document from search results."""
    title: str
    url: str
    snippet: str


@dataclass
class SearchResult:
    """Search result from Discovery Engine."""
    answer: str
    sources: List[SourceDocument]
    raw_response: Optional[Any] = None


class DiscoveryEngineClient:
    """
    Discovery Engine client with WIF/STS token exchange.

    Flow:
    1. Receive Microsoft Entra ID JWT from Agentspace
    2. Exchange JWT for GCP access token via STS
    3. Call Discovery Engine streamAssist API with dataStoreSpecs

    Environment Variables:
    - CLOUD_ML_PROJECT_ID: Agent Engine project ID (auto-set by Agent Engine)
    - PROJECT_NUMBER: GCP project number
    - ENGINE_ID: Discovery Engine ID
    - DATA_STORE_ID: SharePoint datastore ID
    - WIF_POOL_ID: Workforce Identity Federation pool
    - WIF_PROVIDER_ID: WIF provider
    """

    def __init__(
        self,
        project_number: str = None,
        location: str = None,
        engine_id: str = None,
        data_store_id: str = None,
        wif_pool_id: str = None,
        wif_provider_id: str = None,
    ):
        # Agent Engine sets CLOUD_ML_PROJECT_ID at runtime
        self.project_number = (
            project_number or
            os.environ.get("PROJECT_NUMBER") or
            os.environ.get("CLOUD_ML_PROJECT_ID") or
            os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        )
        self.location = location or os.environ.get("LOCATION", "global")
        self.engine_id = engine_id or os.environ.get("ENGINE_ID", "")
        self.data_store_id = data_store_id or os.environ.get("DATA_STORE_ID", "")
        self.wif_pool_id = wif_pool_id or os.environ.get("WIF_POOL_ID", "")
        self.wif_provider_id = wif_provider_id or os.environ.get("WIF_PROVIDER_ID", "")
        self._service_credentials = None

    def _get_service_credentials(self) -> str:
        """Get service account credentials for fallback/admin operations."""
        if self._service_credentials is None:
            creds, project = google.auth.default()
            auth_req = Request()
            creds.refresh(auth_req)
            self._service_credentials = creds.token
            sa_email = getattr(creds, 'service_account_email', 'ADC (user)')
            logger.info(f"[SA] Using credentials: {sa_email}, project: {project}")
        return self._service_credentials

    def exchange_wif_token(self, microsoft_jwt: str) -> str:
        """
        Exchange Microsoft Entra ID JWT for GCP access token via STS.

        Args:
            microsoft_jwt: Microsoft Entra ID JWT (id_token)

        Returns:
            Google Cloud access token
        """
        if not self.wif_pool_id or not self.wif_provider_id:
            logger.warning("WIF not configured - using service account")
            return self._get_service_credentials()

        sts_url = "https://sts.googleapis.com/v1/token"
        audience = (
            f"//iam.googleapis.com/locations/global/workforcePools/{self.wif_pool_id}/"
            f"providers/{self.wif_provider_id}"
        )

        payload = {
            "audience": audience,
            "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
            "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
            "scope": "https://www.googleapis.com/auth/cloud-platform",
            "subjectToken": microsoft_jwt,
            "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt"  # Must be jwt, not id_token
        }

        try:
            logger.info(f"[WIF] Exchanging token with pool={self.wif_pool_id}, provider={self.wif_provider_id}")
            logger.info(f"[WIF] Subject token length: {len(microsoft_jwt)}")
            response = requests.post(sts_url, json=payload, timeout=10)
            logger.info(f"[WIF] STS response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"[WIF] STS error: {response.text[:500]}")
                logger.warning("[WIF] Falling back to service account")
                return self._get_service_credentials()

            resp_data = response.json()
            token = resp_data.get("access_token")
            token_type = resp_data.get("token_type")
            expires_in = resp_data.get("expires_in")
            logger.info(f"[WIF] Exchange SUCCESS - type={token_type}, expires_in={expires_in}, length={len(token) if token else 0}")
            return token

        except Exception as e:
            logger.error(f"[WIF] Exception: {e}")
            import traceback
            traceback.print_exc()
            return self._get_service_credentials()

    # SharePoint federated connector entity types — all data stores derived from
    # the connector. Hardcoded so the GE chat-UI toggle (which is a client-side
    # filter on dataStoreSpecs) cannot strip SharePoint from queries. WIF/ACL
    # enforcement is unaffected — that lives at the engine level, not here.
    _SHAREPOINT_ENTITIES = ["file", "page", "comment", "event", "attachment"]
    _SHAREPOINT_CONNECTOR_PREFIX = "sharepoint-data-def-connector"

    def _get_dynamic_datastores(self) -> List[Dict[str, str]]:
        """Always return the full SharePoint federated connector data-store list.

        Previously this fetched from widget_config, which respects the GE chat-UI
        toggle and silently drops SharePoint when the user disables it. That
        broke per-user search even though WIF authentication and the connector
        bridge were still intact. The toggle is purely client-side; we ignore it.
        Pattern lifted from cortex-retriever/agent/discovery_engine.py.
        """
        # Use `default_collection` in the path — matches the original
        # sharepoint_wif_portal and benchmarks return more grounding refs than
        # the connector-specific collection path.
        return [
            {
                "dataStore": (
                    f"projects/{self.project_number}/locations/{self.location}/"
                    f"collections/default_collection/dataStores/"
                    f"{self._SHAREPOINT_CONNECTOR_PREFIX}_{entity}"
                )
            }
            for entity in self._SHAREPOINT_ENTITIES
        ]

    def _extract_sources(self, response_json: Any) -> List[SourceDocument]:
        """Extract grounding sources from Discovery Engine response."""
        sources = []
        seen_keys = set()

        def find_grounding(obj):
            if isinstance(obj, list):
                for item in obj:
                    find_grounding(item)
                return

            if isinstance(obj, dict):
                # textGroundingMetadata (streamAssist response)
                if "textGroundingMetadata" in obj:
                    for ref in obj["textGroundingMetadata"].get("references", []):
                        doc_meta = ref.get("documentMetadata", {})
                        title = doc_meta.get("title", "Source")
                        url = doc_meta.get("uri", "#")
                        snippet = ref.get("content", "")
                        key = f"{title}-{url}"
                        if key not in seen_keys and snippet:
                            seen_keys.add(key)
                            sources.append(SourceDocument(title=title, url=url, snippet=snippet))

                # groundingMetadata with groundingChunks
                if "groundingMetadata" in obj:
                    for chunk in obj["groundingMetadata"].get("groundingChunks", []):
                        ret_ctx = chunk.get("retrievedContext", {})
                        title = ret_ctx.get("title", "Source")
                        url = ret_ctx.get("uri", "#")
                        snippet = ret_ctx.get("text", "")
                        key = f"{title}-{url}"
                        if key not in seen_keys and snippet:
                            seen_keys.add(key)
                            sources.append(SourceDocument(title=title, url=url, snippet=snippet))

                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        find_grounding(v)

        find_grounding(response_json)
        return sources

    async def search(self, query: str, user_token: Optional[str] = None) -> SearchResult:
        """
        Search using Discovery Engine streamAssist API.

        Args:
            query: User's search query
            user_token: Microsoft JWT for ACL-aware search via WIF

        Returns:
            SearchResult with answer and sources
        """
        # Get access token
        if user_token and len(user_token) > 50:
            access_token = self.exchange_wif_token(user_token)
        else:
            access_token = self._get_service_credentials()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_number
        }

        # Get dataStoreSpecs (CRITICAL for SharePoint grounding)
        datastore_specs = self._get_dynamic_datastores()
        if not datastore_specs and self.data_store_id:
            datastore_specs = [{
                "dataStore": f"projects/{self.project_number}/locations/{self.location}/collections/default_collection/dataStores/{self.data_store_id}"
            }]

        # Build payload — widget shape (parts + assistSkippingMode + toolRegistry).
        # The simpler {query:{text:...}} form silently returns ZERO grounding refs
        # for federated SharePoint per-user queries. Captured from GE console
        # DevTools network trace.
        payload = {
            "query": {"parts": [{"text": query}]},
            "filter": "",
            "fileIds": [],
            "answerGenerationMode": "NORMAL",
            "userMetadata": {"timeZone": "America/New_York"},
            "assistSkippingMode": "REQUEST_ASSIST",
        }
        if datastore_specs:
            payload["toolsSpec"] = {
                "vertexAiSearchSpec": {"dataStoreSpecs": datastore_specs},
                "toolRegistry": "default_tool_registry",
                "imageGenerationSpec": {},
                "videoGenerationSpec": {},
            }

        # Location-aware DE endpoint (us → us-discoveryengine.googleapis.com)
        endpoint = f"{'us-' if self.location == 'us' else ''}discoveryengine.googleapis.com"
        url = (
            f"https://{endpoint}/v1alpha/"
            f"projects/{self.project_number}/locations/{self.location}/"
            f"collections/default_collection/engines/{self.engine_id}/"
            f"assistants/default_assistant:streamAssist"
        )

        try:
            # CRITICAL: Log what identity we're using
            print(f"[DE-IDENTITY] Access token type: {'WIF' if user_token else 'ServiceAccount'}")
            print(f"[DE-IDENTITY] Token length: {len(access_token) if access_token else 0}")
            print(f"[DE-IDENTITY] Project: {self.project_number}, Engine: {self.engine_id}")
            logger.info(f"[DE] Calling streamAssist: {url}")
            logger.info(f"[DE] Payload dataStoreSpecs: {datastore_specs}")
            logger.info(f"[DE] Token length: {len(access_token) if access_token else 0}")

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            logger.info(f"[DE] Response status: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"[DE] Error response: {response.text[:500]}")
                return SearchResult(answer=f"API error: {response.status_code}", sources=[])

            resp_json = response.json()
            logger.info(f"[DE] Response chunks: {len(resp_json) if isinstance(resp_json, list) else 'not a list'}")

            # Extract answer (skip thought parts)
            answer_parts = []
            for i, chunk in enumerate(resp_json):
                stream_resp = chunk.get("streamAssistResponse", chunk)
                replies = stream_resp.get("answer", {}).get("replies", [])
                logger.info(f"[DE] Chunk {i}: {len(replies)} replies")
                for reply in replies:
                    content = reply.get("groundedContent", {}).get("content", {})
                    text = content.get("text", "")
                    is_thought = content.get("thought", False)
                    if text:
                        logger.info(f"[DE] Text found (thought={is_thought}): {text[:100]}...")
                    if text and not is_thought:
                        answer_parts.append(text)

            full_answer = "".join(answer_parts) or "No relevant information found."
            sources = self._extract_sources(resp_json)
            logger.info(f"[DE] Final answer length: {len(full_answer)}, sources: {len(sources)}")

            return SearchResult(answer=full_answer, sources=sources, raw_response=resp_json)

        except Exception as e:
            logger.error(f"Discovery Engine search failed: {e}")
            import traceback
            traceback.print_exc()
            return SearchResult(answer=f"Search error: {str(e)}", sources=[])
