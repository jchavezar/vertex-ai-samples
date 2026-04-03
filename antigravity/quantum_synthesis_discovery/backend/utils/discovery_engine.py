"""
Discovery Engine Client with WIF/STS Token Exchange.
Direct API integration for SharePoint datastores with proper grounding extraction.
"""
import os
import json
import logging
from typing import Optional, AsyncGenerator, List, Dict, Any
from dataclasses import dataclass
import requests
import google.auth
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


@dataclass
class DataStoreSpec:
    """Discovery Engine datastore specification."""
    data_store: str
    description: str = "Enterprise Datastore"


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
    grounding_metadata: Optional[dict] = None


class DiscoveryEngineClient:
    """
    Direct Discovery Engine API client with WIF/STS token exchange.
    Uses streamAssist API and extracts grounded sources from SharePoint.
    """

    def __init__(
        self,
        project_number: str = None,
        location: str = "global",
        engine_id: str = None,
        data_store_id: str = None,
        wif_pool_id: str = None,
        wif_provider_id: str = None,
    ):
        self.project_number = project_number or os.environ.get("PROJECT_NUMBER", "REDACTED_PROJECT_NUMBER")
        self.location = location
        self.engine_id = engine_id or os.environ.get("DISCOVERY_ENGINE_ID")
        self.data_store_id = data_store_id or os.environ.get("DATA_STORE_ID")
        self.wif_pool_id = wif_pool_id or os.environ.get("WIF_POOL_ID")
        self.wif_provider_id = wif_provider_id or os.environ.get("WIF_PROVIDER_ID")

        self._service_credentials = None

    def _get_service_credentials(self) -> str:
        """Get service account credentials for admin operations."""
        if self._service_credentials is None:
            creds, _ = google.auth.default()
            auth_req = Request()
            creds.refresh(auth_req)
            self._service_credentials = creds.token
        return self._service_credentials

    def exchange_wif_token(self, user_id_token: str) -> str:
        """
        Exchange Entra ID JWT for Google Cloud access token via STS.

        Args:
            user_id_token: Microsoft Entra ID JWT (id_token)

        Returns:
            Google Cloud access token
        """
        print(f"[WIF] Pool: {self.wif_pool_id}, Provider: {self.wif_provider_id}", flush=True)

        if not self.wif_pool_id or not self.wif_provider_id:
            print("[WIF] NOT CONFIGURED - using service account", flush=True)
            return self._get_service_credentials()

        sts_url = "https://sts.googleapis.com/v1/token"
        audience = (
            f"//iam.googleapis.com/locations/global/workforcePools/{self.wif_pool_id}/"
            f"providers/{self.wif_provider_id}"
        )
        print(f"[WIF] Audience: {audience}", flush=True)

        payload = {
            "audience": audience,
            "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
            "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
            "scope": "https://www.googleapis.com/auth/cloud-platform",
            "subjectToken": user_id_token,
            "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt"
        }

        try:
            response = requests.post(sts_url, json=payload, timeout=10)
            print(f"[WIF] STS status: {response.status_code}", flush=True)
            if response.status_code != 200:
                print(f"[WIF] STS ERROR: {response.text[:300]}", flush=True)
                # Fallback to service account
                return self._get_service_credentials()
            token = response.json().get("access_token")
            print(f"[WIF] SUCCESS - token length: {len(token) if token else 0}", flush=True)
            return token
        except Exception as e:
            print(f"[WIF] EXCEPTION: {e}", flush=True)
            return self._get_service_credentials()

    def _get_dynamic_datastores(self) -> List[Dict[str, str]]:
        """Dynamically fetch configured datastores from the engine.

        Uses service account credentials (not user token) since this is an admin operation.
        """
        try:
            # Use service account for admin operations like fetching widget config
            admin_token = self._get_service_credentials()

            url = (
                f"https://discoveryengine.googleapis.com/v1alpha/"
                f"projects/{self.project_number}/locations/{self.location}/"
                f"collections/default_collection/engines/{self.engine_id}/"
                f"widgetConfigs/default_search_widget_config"
            )
            headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json",
                "X-Goog-User-Project": self.project_number
            }
            resp = requests.get(url, headers=headers, timeout=10)
            print(f"[DE] Widget config fetch status: {resp.status_code}", flush=True)
            if resp.status_code == 200:
                datastore_specs = []
                collections = resp.json().get('collectionComponents', [{}])
                for comp in collections:
                    for ds_comp in comp.get('dataStoreComponents', []):
                        datastore_specs.append({'dataStore': ds_comp['name']})
                        print(f"[DE] Found datastore: {ds_comp['name']}", flush=True)
                return datastore_specs
            else:
                print(f"[DE] Widget config error: {resp.text[:200]}", flush=True)
        except Exception as e:
            print(f"[DE] Could not fetch dynamic datastores: {e}", flush=True)
        return []

    def _extract_sources(self, response_json: Any) -> List[SourceDocument]:
        """
        Recursively extract grounding sources from Discovery Engine response.
        Handles multiple schema formats: searchResults, textGroundingMetadata, groundingChunks
        Also handles streamAssistResponse wrapper format.
        """
        sources = []
        seen_keys = set()

        def find_grounding(obj):
            if isinstance(obj, list):
                for item in obj:
                    find_grounding(item)
                return

            if isinstance(obj, dict):
                # Handle streamAssistResponse wrapper
                if "streamAssistResponse" in obj:
                    find_grounding(obj["streamAssistResponse"])
                # Schema 1: searchResults
                if "searchResults" in obj and isinstance(obj.get("searchResults"), list):
                    for res in obj["searchResults"]:
                        doc = res.get("document", res)
                        struct = doc.get("structData", res.get("structData", {}))
                        name = doc.get("name", "")
                        title = struct.get("title") or (name.split('/')[-1] if name else "Document")
                        url = struct.get("url", struct.get("uri", "#"))
                        snippet = struct.get("snippet", struct.get("description", ""))

                        key = f"{title}-{url}"
                        if key not in seen_keys and (title or snippet):
                            seen_keys.add(key)
                            sources.append(SourceDocument(title=title, url=url, snippet=snippet))

                # Schema 2: textGroundingMetadata (common in streamAssist)
                if "textGroundingMetadata" in obj:
                    metadata = obj["textGroundingMetadata"]
                    if "references" in metadata and isinstance(metadata["references"], list):
                        for ref in metadata["references"]:
                            doc_meta = ref.get("documentMetadata", {})
                            title = doc_meta.get("title", "Source Document")
                            url = doc_meta.get("uri", "#")
                            snippet = ref.get("content", "")

                            key = f"{title}-{url}"
                            if key not in seen_keys and snippet:
                                seen_keys.add(key)
                                sources.append(SourceDocument(title=title, url=url, snippet=snippet))

                # Schema 3: groundingMetadata with groundingChunks
                if "groundingMetadata" in obj:
                    gm = obj["groundingMetadata"]
                    chunks = gm.get("groundingChunks", [])
                    for chunk in chunks:
                        ret_ctx = chunk.get("retrievedContext", {})
                        title = chunk.get("title", "Source") # Corrected from chunk.get("title") to ret_ctx.get("title") based on original code line 210
                        url = ret_ctx.get("uri", "#")
                        snippet = ret_ctx.get("text", "")

                        key = f"{title}-{url}"
                        if key not in seen_keys and snippet:
                            seen_keys.add(key)
                            sources.append(SourceDocument(title=title, url=url, snippet=snippet))

                    # Also check groundingSupport
                    supports = gm.get("groundingSupport", [])
                    for support in supports:
                        for chunk_info in support.get("supportChunkInfo", []):
                            chunk_data = chunk_info.get("chunk", {})
                            doc_meta = chunk_data.get("documentMetadata", {})
                            title = doc_meta.get("title", "Source")
                            url = doc_meta.get("uri", "#")
                            snippet = chunk_data.get("chunkContent", "")[:200]

                            key = f"{title}-{url}"
                            if key not in seen_keys and snippet:
                                seen_keys.add(key)
                                sources.append(SourceDocument(title=title, url=url, snippet=snippet))

                # Recurse into nested objects
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        find_grounding(v)

        find_grounding(response_json)
        return sources

    async def search(
        self,
        query: str,
        user_token: Optional[str] = None,
    ) -> SearchResult:
        """
        Search using Discovery Engine streamAssist API.
        Returns synthesized answer with grounded SharePoint sources.

        Args:
            query: User's search query
            user_token: Optional Entra ID token for WIF exchange

        Returns:
            SearchResult with synthesized answer and sources
        """
        # Get access token - exchange JWT via WIF/STS
        if user_token and len(user_token) > 50:
            print(f"[DE-search] Exchanging JWT (length: {len(user_token)})", flush=True)
            access_token = self.exchange_wif_token(user_token)
            print(f"[DE-search] Got token (length: {len(access_token) if access_token else 0})", flush=True)
        else:
            print("[DE-search] No user token - using service account", flush=True)
            access_token = self._get_service_credentials()

        # Build headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_number
        }

        # ALWAYS use dynamic datastore fetching to get SharePoint datastores
        # Uses service account to fetch widget config, then user token for actual search
        datastore_specs = self._get_dynamic_datastores()
        print(f"[DE] Dynamic datastores found: {len(datastore_specs)}", flush=True)
        for ds in datastore_specs:
            print(f"[DE]   - {ds.get('dataStore', 'unknown')}", flush=True)

        # Fallback only if dynamic fetch fails
        if not datastore_specs and self.data_store_id:
            datastore_specs = [{
                "dataStore": f"projects/{self.project_number}/locations/{self.location}/collections/default_collection/dataStores/{self.data_store_id}"
            }]
            print(f"[DE] Fallback to configured datastore: {self.data_store_id}", flush=True)

        # Build streamAssist payload
        # CRITICAL: toolsSpec.vertexAiSearchSpec.dataStoreSpecs is REQUIRED for grounded responses
        # Without dataStoreSpecs: streamAssist returns generic LLM responses (no SharePoint grounding)
        # With dataStoreSpecs: streamAssist searches SharePoint and returns grounded answers with citations
        payload = {
            "query": {"text": query}
        }
        if datastore_specs:
            # This is what triggers grounding on SharePoint documents
            # The response will include textGroundingMetadata with source references
            payload["toolsSpec"] = {
                "vertexAiSearchSpec": {
                    "dataStoreSpecs": datastore_specs
                }
            }
        else:
            print("[DE] WARNING: No dataStoreSpecs - response will NOT be grounded on SharePoint!", flush=True)

        # Call streamAssist API
        url = (
            f"https://discoveryengine.googleapis.com/v1alpha/"
            f"projects/{self.project_number}/locations/{self.location}/"
            f"collections/default_collection/engines/{self.engine_id}/"
            f"assistants/default_assistant:streamAssist"
        )

        logger.info(f"Calling Discovery Engine streamAssist: {url}")

        try:
            # Use requests for direct API call
            # Note: Using requests instead of aiohttp for simplicity as in original code
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            # Parse response - streamAssist returns JSON array
            resp_json = response.json()
            print(f"[DE] RAW RESPONSE (first 2000 chars): {json.dumps(resp_json)[:2000]}", flush=True)

            # Check for grounding metadata
            has_grounding = "textGroundingMetadata" in str(resp_json) or "searchResults" in str(resp_json)
            print(f"[DE] Has grounding data: {has_grounding}", flush=True)

            # Extract answer text (skip thinking/thought parts)
            # Handle both direct and wrapped response formats
            answer_parts = []
            for chunk in resp_json:
                # Handle streamAssistResponse wrapper (actual API format)
                stream_resp = chunk.get("streamAssistResponse", chunk)
                answer = stream_resp.get("answer", {})
                for reply in answer.get("replies", []):
                    grounded = reply.get("groundedContent", {})
                    content = grounded.get("content", {})
                    text = content.get("text", "")
                    is_thought = content.get("thought", False)
                    if text and not is_thought:
                        answer_parts.append(text)

            full_answer = "".join(answer_parts)

            # Extract sources
            sources = self._extract_sources(resp_json)

            # Format answer with sources if found
            if sources:
                full_answer += "\n\n---\n**Sources:**\n"
                for i, src in enumerate(sources[:5], 1):  # Limit to 5 sources
                    full_answer += f"{i}. **[{src.title}]({src.url})**\n"
                    if src.snippet:
                        full_answer += f"   > {src.snippet[:150]}...\n\n"

            if not full_answer:
                full_answer = "I couldn't find relevant information in SharePoint for your query. Please try rephrasing or being more specific."

            return SearchResult(
                answer=full_answer,
                sources=sources,
                grounding_metadata=resp_json
            )

        except requests.exceptions.HTTPError as e:
            logger.error(f"Discovery Engine HTTP error: {e}")
            return SearchResult(
                answer=f"Search error: {e}",
                sources=[]
            )
        except Exception as e:
            logger.error(f"Discovery Engine search failed: {e}")
            return SearchResult(
                answer=f"Search failed: {str(e)}",
                sources=[]
            )

    async def stream_search(
        self,
        query: str,
        user_token: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream search results from Discovery Engine.

        Args:
            query: User's search query
            user_token: Optional Entra ID token for WIF exchange

        Yields:
            Chunks of the synthesized answer
        """
        result = await self.search(query, user_token)

        if result.answer:
            # Yield in chunks for streaming effect
            words = result.answer.split()
            chunk_size = 10
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                yield chunk + " "
