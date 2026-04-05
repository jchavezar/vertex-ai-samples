"""
Discovery Engine Client with WIF/STS Token Exchange.
Exchanges Microsoft Entra ID JWT for GCP access token via Workforce Identity Federation.
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
    grounding_metadata: Optional[dict] = None


class DiscoveryEngineClient:
    """
    Discovery Engine client with WIF/STS token exchange.

    Flow:
    1. Receive Microsoft Entra ID JWT from Agentspace
    2. Exchange JWT for GCP access token via STS
    3. Call Discovery Engine streamAssist API with dataStoreSpecs
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
        self.project_number = project_number or os.environ.get("PROJECT_NUMBER", "")
        self.location = location
        self.engine_id = engine_id or os.environ.get("ENGINE_ID", "")
        self.data_store_id = data_store_id or os.environ.get("DATA_STORE_ID", "")
        self.wif_pool_id = wif_pool_id or os.environ.get("WIF_POOL_ID", "")
        self.wif_provider_id = wif_provider_id or os.environ.get("WIF_PROVIDER_ID", "")

        self._service_credentials = None

    def _get_service_credentials(self) -> str:
        """Get service account credentials for admin operations."""
        if self._service_credentials is None:
            creds, _ = google.auth.default()
            auth_req = Request()
            creds.refresh(auth_req)
            self._service_credentials = creds.token
        return self._service_credentials

    def exchange_wif_token(self, microsoft_jwt: str) -> str:
        """
        Exchange Microsoft Entra ID JWT for GCP access token via STS.

        Args:
            microsoft_jwt: Microsoft Entra ID JWT (id_token)

        Returns:
            Google Cloud access token
        """
        print(f"[WIF] Pool: {self.wif_pool_id}, Provider: {self.wif_provider_id}", flush=True)

        if not self.wif_pool_id or not self.wif_provider_id:
            print("[WIF] Not configured - using service account", flush=True)
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
            "subjectToken": microsoft_jwt,
            # Use jwt type for Microsoft access tokens (portal sends access_token, not id_token)
            "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt"
        }

        try:
            response = requests.post(sts_url, json=payload, timeout=10)
            print(f"[WIF] STS response status: {response.status_code}", flush=True)

            if response.status_code != 200:
                print(f"[WIF] STS error: {response.text[:500]}", flush=True)
                return self._get_service_credentials()

            token = response.json().get("access_token")
            print(f"[WIF] Exchange SUCCESS, token length: {len(token) if token else 0}", flush=True)
            return token

        except Exception as e:
            print(f"[WIF] Exception: {e}", flush=True)
            return self._get_service_credentials()

    def _get_dynamic_datastores(self) -> List[Dict[str, str]]:
        """
        Dynamically fetch configured datastores from the engine.
        Uses service account credentials (admin operation).
        """
        try:
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
            logger.debug(f"Widget config fetch status: {resp.status_code}")

            if resp.status_code == 200:
                datastore_specs = []
                collections = resp.json().get('collectionComponents', [{}])
                for comp in collections:
                    for ds_comp in comp.get('dataStoreComponents', []):
                        datastore_specs.append({'dataStore': ds_comp['name']})
                        logger.debug(f"Found datastore: {ds_comp['name']}")
                return datastore_specs
            else:
                logger.warning(f"Widget config error: {resp.text[:200]}")

        except Exception as e:
            logger.warning(f"Could not fetch dynamic datastores: {e}")

        return []

    def _extract_sources(self, response_json: Any) -> List[SourceDocument]:
        """
        Extract grounding sources from Discovery Engine response.
        Handles multiple schema formats.
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

                # Schema: textGroundingMetadata (common in streamAssist)
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

                # Schema: groundingMetadata with groundingChunks
                if "groundingMetadata" in obj:
                    gm = obj["groundingMetadata"]
                    chunks = gm.get("groundingChunks", [])
                    for chunk in chunks:
                        ret_ctx = chunk.get("retrievedContext", {})
                        title = ret_ctx.get("title", "Source")
                        url = ret_ctx.get("uri", "#")
                        snippet = ret_ctx.get("text", "")

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

        Args:
            query: User's search query
            user_token: Microsoft Graph access token for ACL-aware search

        Returns:
            SearchResult with synthesized answer and sources
        """
        # Get access token - try WIF exchange first, fallback to service account
        if user_token and len(user_token) > 50:
            print(f"[SEARCH] Attempting WIF exchange (token length: {len(user_token)})", flush=True)
            access_token = self.exchange_wif_token(user_token)
        else:
            print("[SEARCH] No user token - using service account", flush=True)
            access_token = self._get_service_credentials()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_number
        }

        # CRITICAL: Get dataStoreSpecs for SharePoint grounding
        datastore_specs = self._get_dynamic_datastores()
        print(f"[DE] Dynamic datastores found: {len(datastore_specs)}", flush=True)

        # Fallback to configured datastore
        if not datastore_specs and self.data_store_id:
            datastore_specs = [{
                "dataStore": f"projects/{self.project_number}/locations/{self.location}/collections/default_collection/dataStores/{self.data_store_id}"
            }]
            print(f"[DE] Fallback to datastore: {self.data_store_id}", flush=True)

        # Build streamAssist payload
        # CRITICAL: toolsSpec.vertexAiSearchSpec.dataStoreSpecs is REQUIRED for SharePoint grounding
        payload = {
            "query": {"text": query}
        }

        if datastore_specs:
            payload["toolsSpec"] = {
                "vertexAiSearchSpec": {
                    "dataStoreSpecs": datastore_specs
                }
            }
        else:
            logger.warning("No dataStoreSpecs - response will NOT be grounded!")


        # Call streamAssist API
        url = (
            f"https://discoveryengine.googleapis.com/v1alpha/"
            f"projects/{self.project_number}/locations/{self.location}/"
            f"collections/default_collection/engines/{self.engine_id}/"
            f"assistants/default_assistant:streamAssist"
        )

        print(f"[DE] Calling streamAssist: {url}", flush=True)
        print(f"[DE] Payload: {json.dumps(payload)[:300]}", flush=True)

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            print(f"[DE] Response status: {response.status_code}", flush=True)
            response.raise_for_status()

            resp_json = response.json()
            logger.debug(f"Response received (first 500 chars): {json.dumps(resp_json)[:500]}")

            # Extract answer text (skip thinking/thought parts)
            answer_parts = []
            for chunk in resp_json:
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

            # Format answer with sources
            if sources:
                full_answer += "\n\n---\n**Sources:**\n"
                for i, src in enumerate(sources[:5], 1):
                    full_answer += f"{i}. **[{src.title}]({src.url})**\n"
                    if src.snippet:
                        full_answer += f"   > {src.snippet[:150]}...\n\n"

            if not full_answer:
                full_answer = "I couldn't find relevant information for your query. Please try rephrasing."

            return SearchResult(
                answer=full_answer,
                sources=sources,
                grounding_metadata=resp_json
            )

        except requests.exceptions.HTTPError as e:
            logger.error(f"Discovery Engine HTTP error: {e}")
            return SearchResult(answer=f"Search error: {e}", sources=[])

        except Exception as e:
            logger.error(f"Discovery Engine search failed: {e}")
            return SearchResult(answer=f"Search failed: {str(e)}", sources=[])
