"""
Microsoft Graph API Client
Provides authenticated access to Microsoft Graph API endpoints.
"""
import logging
from typing import Optional, Any
import httpx

from auth import get_auth_manager

logger = logging.getLogger("ms365-mcp.graph")

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class GraphAPIError(Exception):
    """Raised when Graph API returns an error."""
    def __init__(self, status_code: int, message: str, error_code: Optional[str] = None):
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(f"Graph API Error ({status_code}): {message}")


class GraphClient:
    """
    Client for Microsoft Graph API with automatic token handling.
    """

    def __init__(self):
        self._client = httpx.Client(timeout=30.0)

    def _get_headers(self) -> dict:
        """Get headers with current access token."""
        auth_manager = get_auth_manager()
        token = auth_manager.get_access_token()

        if not token:
            raise GraphAPIError(401, "Not authenticated. Please run 'login' first.")

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response, raising errors as needed."""
        if response.status_code == 204:
            return {"success": True}

        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text}

        if response.status_code >= 400:
            error = data.get("error", {})
            raise GraphAPIError(
                status_code=response.status_code,
                message=error.get("message", str(data)),
                error_code=error.get("code"),
            )

        return data

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make GET request to Graph API."""
        url = f"{GRAPH_BASE_URL}{endpoint}"
        logger.debug(f"[Graph] GET {endpoint}")

        response = self._client.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(response)

    def post(self, endpoint: str, json_data: Optional[dict] = None) -> dict:
        """Make POST request to Graph API."""
        url = f"{GRAPH_BASE_URL}{endpoint}"
        logger.debug(f"[Graph] POST {endpoint}")

        response = self._client.post(url, headers=self._get_headers(), json=json_data)
        return self._handle_response(response)

    def put(self, endpoint: str, content: bytes, content_type: str = "application/octet-stream") -> dict:
        """Make PUT request for file uploads."""
        url = f"{GRAPH_BASE_URL}{endpoint}"
        logger.debug(f"[Graph] PUT {endpoint}")

        headers = self._get_headers()
        headers["Content-Type"] = content_type

        response = self._client.put(url, headers=headers, content=content)
        return self._handle_response(response)

    def delete(self, endpoint: str) -> dict:
        """Make DELETE request to Graph API."""
        url = f"{GRAPH_BASE_URL}{endpoint}"
        logger.debug(f"[Graph] DELETE {endpoint}")

        response = self._client.delete(url, headers=self._get_headers())
        return self._handle_response(response)

    def patch(self, endpoint: str, json_data: dict) -> dict:
        """Make PATCH request to Graph API."""
        url = f"{GRAPH_BASE_URL}{endpoint}"
        logger.debug(f"[Graph] PATCH {endpoint}")

        response = self._client.patch(url, headers=self._get_headers(), json=json_data)
        return self._handle_response(response)


# Global client instance
_graph_client: Optional[GraphClient] = None


def get_graph_client() -> GraphClient:
    """Get or create the global Graph client."""
    global _graph_client

    if _graph_client is None:
        _graph_client = GraphClient()

    return _graph_client
