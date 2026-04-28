"""
Discovery Engine client with WIF/STS token exchange.

Exchanges Microsoft Entra ID JWT for GCP access token via Workforce Identity
Federation, then calls the streamAssist API with dataStoreSpecs for
ACL-aware SharePoint search.
"""
import os
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import requests
import google.auth
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


@dataclass
class SourceDocument:
    title: str
    url: str
    snippet: str


@dataclass
class SearchResult:
    answer: str
    sources: List[SourceDocument]
    raw_response: Optional[Any] = None


class DiscoveryEngineClient:
    """
    Discovery Engine client for SharePoint federated search.

    Flow:
      1. Receive Microsoft Entra ID JWT from Agentspace session state
      2. Exchange JWT for GCP access token via STS (WIF)
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
        self.project_number = (
            project_number
            or os.environ.get("PROJECT_NUMBER")
            or os.environ.get("CLOUD_ML_PROJECT_ID")
            or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        )
        self.location = location
        self.engine_id = engine_id or os.environ.get("ENGINE_ID", "")
        self.data_store_id = data_store_id or os.environ.get("DATA_STORE_ID", "")
        self.wif_pool_id = wif_pool_id or os.environ.get("WIF_POOL_ID", "")
        self.wif_provider_id = wif_provider_id or os.environ.get("WIF_PROVIDER_ID", "")
        self._service_credentials = None

    def _get_service_credentials(self) -> str:
        if self._service_credentials is None:
            creds, project = google.auth.default()
            creds.refresh(Request())
            self._service_credentials = creds.token
            logger.info(f"Using credentials for project: {project}")
        return self._service_credentials

    def exchange_wif_token(self, microsoft_jwt: str) -> str:
        """Exchange Microsoft Entra ID JWT for GCP access token via STS."""
        if not self.wif_pool_id or not self.wif_provider_id:
            logger.warning("WIF not configured, falling back to service account")
            return self._get_service_credentials()

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
            "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
        }

        try:
            logger.info(f"WIF exchange: pool={self.wif_pool_id}, provider={self.wif_provider_id}")
            response = requests.post("https://sts.googleapis.com/v1/token", json=payload, timeout=10)

            if response.status_code != 200:
                logger.error(f"STS error {response.status_code}: {response.text[:300]}")
                return self._get_service_credentials()

            token = response.json().get("access_token")
            logger.info("WIF token exchange succeeded")
            return token

        except Exception:
            logger.exception("WIF token exchange failed")
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
        bridge were still intact. The toggle is purely client-side; we just
        ignore it.
        """
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
        seen = set()

        def walk(obj):
            if isinstance(obj, list):
                for item in obj:
                    walk(item)
                return
            if not isinstance(obj, dict):
                return

            if "textGroundingMetadata" in obj:
                for ref in obj["textGroundingMetadata"].get("references", []):
                    doc_meta = ref.get("documentMetadata", {})
                    title = doc_meta.get("title", "Source")
                    url = doc_meta.get("uri", "#")
                    snippet = ref.get("content", "")
                    key = f"{title}-{url}"
                    if key not in seen and snippet:
                        seen.add(key)
                        sources.append(SourceDocument(title=title, url=url, snippet=snippet))

            if "groundingMetadata" in obj:
                for chunk in obj["groundingMetadata"].get("groundingChunks", []):
                    ctx = chunk.get("retrievedContext", {})
                    title = ctx.get("title", "Source")
                    url = ctx.get("uri", "#")
                    snippet = ctx.get("text", "")
                    key = f"{title}-{url}"
                    if key not in seen and snippet:
                        seen.add(key)
                        sources.append(SourceDocument(title=title, url=url, snippet=snippet))

            for v in obj.values():
                if isinstance(v, (dict, list)):
                    walk(v)

        walk(response_json)
        return sources

    async def search(self, query: str, user_token: Optional[str] = None) -> SearchResult:
        """
        Search SharePoint via Discovery Engine streamAssist API.

        Args:
            query: Search query
            user_token: Microsoft JWT for ACL-aware search via WIF
        """
        if user_token and len(user_token) > 50:
            access_token = self.exchange_wif_token(user_token)
        else:
            access_token = self._get_service_credentials()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_number,
        }

        datastore_specs = self._get_dynamic_datastores()
        if not datastore_specs and self.data_store_id:
            datastore_specs = [{
                "dataStore": (
                    f"projects/{self.project_number}/locations/{self.location}/"
                    f"collections/default_collection/dataStores/{self.data_store_id}"
                )
            }]

        # Wrap the query so streamAssist's heuristic doesn't classify it as
        # NON_ASSIST_SEEKING_QUERY_IGNORED. Bare keywords ("jennifer") and short
        # questions ("who is X?") get SKIPPED with zero docs returned. The
        # agent's LLM tends to extract single-word keywords for searches, so we
        # rewrap into a full sentence here. Verified against the live API.
        wrapped_query = f"Find information about {query} in SharePoint documents"
        payload = {
            "query": {"parts": [{"text": wrapped_query}]},
            "assistSkippingMode": "REQUEST_ASSIST",
        }
        if datastore_specs:
            payload["toolsSpec"] = {"vertexAiSearchSpec": {"dataStoreSpecs": datastore_specs}}

        url = (
            f"https://discoveryengine.googleapis.com/v1alpha/"
            f"projects/{self.project_number}/locations/{self.location}/"
            f"collections/default_collection/engines/{self.engine_id}/"
            f"assistants/default_assistant:streamAssist"
        )

        logger.info(f"streamAssist URL: {url}")
        logger.info(f"streamAssist Bearer prefix: {access_token[:25]}...")
        import json as _json
        logger.info(f"streamAssist FULL PAYLOAD: {_json.dumps(payload)[:500]}")

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)

            logger.info(f"streamAssist HTTP {response.status_code}, body length: {len(response.text)}")
            logger.info(f"streamAssist response body (first 1000 chars): {response.text[:1000]}")

            if response.status_code != 200:
                logger.error(f"Discovery Engine error {response.status_code}: {response.text[:300]}")
                return SearchResult(answer=f"API error: {response.status_code}", sources=[])

            resp_json = response.json()

            answer_parts = []
            for chunk in resp_json:
                stream_resp = chunk.get("streamAssistResponse", chunk)
                for reply in stream_resp.get("answer", {}).get("replies", []):
                    content = reply.get("groundedContent", {}).get("content", {})
                    text = content.get("text", "")
                    if text and not content.get("thought", False):
                        answer_parts.append(text)

            full_answer = "".join(answer_parts) or "No relevant information found."
            sources = self._extract_sources(resp_json)

            return SearchResult(answer=full_answer, sources=sources, raw_response=resp_json)

        except Exception:
            logger.exception("Discovery Engine search failed")
            return SearchResult(answer="Search error", sources=[])
