import os
import time
import httpx
import google.auth
import json
from google.auth.transport.requests import Request
from typing import Dict, Any, Optional

# Configuration
PROJECT_ID = os.getenv("VAIS_PROJECT_ID", "254356041555")
LOCATION = os.getenv("VAIS_LOCATION", "global")
COLLECTION = os.getenv("VAIS_COLLECTION", "default_collection")
ENGINE = os.getenv("VAIS_ENGINE", "factset")
SERVING_CONFIG = os.getenv("VAIS_SERVING_CONFIG", "default_search")

VAIS_API_URL = f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION}/engines/{ENGINE}/servingConfigs/{SERVING_CONFIG}:search"

class VertexSearchClient:
    def __init__(self):
        self.credentials, self.project = google.auth.default()
        self._token = None
        self._token_expiry = 0
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_token(self) -> str:
        now = time.time()
        if not self._token or not self.credentials.valid or now > self._token_expiry:
            print("[VAIS] Refreshing Google Auth Token (Async Thread)...")
            t0 = time.time()
            import anyio
            await anyio.to_thread.run_sync(self.credentials.refresh, Request())
            self._token = self.credentials.token
            self._token_expiry = now + 3000 # 50 min buffer
            print(f"[VAIS] Token refresh took {time.time() - t0:.4f}s")
        return self._token

    async def search(self, query: str, page_size: int = 10, offset: int = 0) -> Dict[str, Any]:
        token = await self.get_token()
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
            "userInfo": {"timeZone": "UTC"}
        }

        t0 = time.time()
        try:
            response = await self._client.post(VAIS_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            print(f"[VAIS] Search for '{query}' took {time.time() - t0:.4f}s")
            return response.json()
        except Exception as e:
            print(f"[VAIS] Search Failed after {time.time() - t0:.4f}s: {e}")
            raise

# Singleton instance
vais_client = VertexSearchClient()
