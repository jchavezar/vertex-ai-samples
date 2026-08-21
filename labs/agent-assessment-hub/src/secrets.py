"""Secret Manager integration module.

Provides secure retrieval of API keys and credentials from Google Cloud Secret Manager
with local environment fallback for zero-leak local development.
"""

import os
from typing import Optional
from src.observability import logger

try:
    from google.cloud import secretmanager
    _sm_client = secretmanager.SecretManagerServiceClient()
except Exception:
    _sm_client = None


def get_secret(secret_id: str, project_id: Optional[str] = None, default: Optional[str] = None) -> Optional[str]:
    """Retrieves secret from GCP Secret Manager, falling back to environment variables.

    Args:
        secret_id: Name of secret in Secret Manager or env var.
        project_id: GCP project ID.
        default: Fallback default value.

    Returns:
        Secret string value or default.
    """
    proj = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
    if _sm_client and proj:
        try:
            name = f"projects/{proj}/secrets/{secret_id}/versions/latest"
            response = _sm_client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.warning(f"Could not load secret '{secret_id}' from GCP Secret Manager ({str(e)}). Falling back to env.")

    return os.getenv(secret_id, default)
