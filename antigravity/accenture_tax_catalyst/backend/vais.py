import os
import time
import httpx
import google.auth
import logging
from google.auth.transport.requests import Request
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Configuration detection
# We try to get from environment first
PROJECT_ID = os.getenv("VAIS_PROJECT_ID")
LOCATION = os.getenv("VAIS_LOCATION", "global")
COLLECTION = os.getenv("VAIS_COLLECTION", "default_collection")
ENGINE = os.getenv("VAIS_ENGINE", "accenture")
SERVING_CONFIG = os.getenv("VAIS_SERVING_CONFIG", "default_search")

class VertexSearchClient:
    def __init__(self):
        try:
            self.credentials, self.project = google.auth.default()
            global PROJECT_ID
            if not PROJECT_ID:
                PROJECT_ID = self.project
                logger.info(f"[VAIS] Using project from ADC: {PROJECT_ID}")
        except Exception as e:
            logger.error(f"[VAIS] Failed to initialize Google Auth: {e}")
            self.credentials = None
            self.project = None
            
        self._token = None
        self._token_expiry = 0
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_token(self) -> str:
        if not self.credentials:
            raise Exception("Google credentials not initialized")
            
        now = time.time()
        if not self._token or not self.credentials.valid or now > self._token_expiry:
            logger.info("[VAIS] Refreshing Google Auth Token...")
            import anyio
            await anyio.to_thread.run_sync(self.credentials.refresh, Request())
            self._token = self.credentials.token
            self._token_expiry = now + 3000 # 50 min buffer
        return self._token

    async def search(self, query: str, page_size: int = 10, offset: int = 0) -> Dict[str, Any]:
        token = await self.get_token()
        
        # Use globally detected or provided PROJECT_ID
        api_url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION}/engines/{ENGINE}/servingConfigs/{SERVING_CONFIG}:search"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "pageSize": page_size,
            "offset": offset,
            "queryExpansionSpec": {"condition": "AUTO"},
            "spellCorrectionSpec": {"mode": "AUTO"},
            "contentSearchSpec": {
                "snippetSpec": {"returnSnippet": True}
            },
            "userInfo": {"timeZone": "UTC"}
        }

        try:
            response = await self._client.post(api_url, headers=headers, json=payload)
            if response.status_code != 200:
                logger.error(f"[VAIS] Search Failed with status {response.status_code}: {response.text}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.exception(f"[VAIS] Search Exception: {e}")
            raise

# Singleton instance
vais_client = VertexSearchClient()
