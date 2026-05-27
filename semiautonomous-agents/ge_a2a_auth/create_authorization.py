"""Create the GE Authorization resource for the OAuth2-cloud-platform bridge.

This is the centerpiece of `ge_a2a_auth`. GE's Custom-A2A registration only
supports server-side OAuth2 authorization-code flow. We exploit that: the
OAuth2 client is granted the `cloud-platform` scope, so the access token GE
captures for the user is ALSO valid against the Vertex AI Agent Runtime A2A
endpoint. GE forwards it as `Authorization: Bearer <ya29.user_token>` and AE
accepts it natively.

Net effect: a user logs in once via the GE UI, and GE talks to the Agent
Runtime-hosted A2A agent as that user — no service account, no IAP, no
extra middleware.
"""

from __future__ import annotations

import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from google.auth import default
from google.auth.transport.requests import Request

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

AUTHZ_ID = "ge-a2a-auth-oauth"


def bearer() -> str:
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    return creds.token


def main() -> None:
    project = os.environ["PROJECT_ID"]
    client_id = os.environ["OAUTH_CLIENT_ID"]
    client_secret = os.environ["OAUTH_CLIENT_SECRET"]

    url = (
        "https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{project}/locations/global/authorizations"
        f"?authorizationId={AUTHZ_ID}"
    )

    payload = {
        "name": (
            f"projects/{project}/locations/global/authorizations/{AUTHZ_ID}"
        ),
        "serverSideOauth2": {
            "clientId": client_id,
            "clientSecret": client_secret,
            "authorizationUri": (
                "https://accounts.google.com/o/oauth2/v2/auth"
                "?response_type=code"
                "&access_type=offline"
                "&prompt=consent"
                "&include_granted_scopes=true"
                "&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform"
            ),
            "tokenUri": "https://oauth2.googleapis.com/token",
        },
    }

    headers = {
        "Authorization": f"Bearer {bearer()}",
        "X-Goog-User-Project": project,
        "Content-Type": "application/json",
    }
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    if r.status_code == 409:
        print("Authorization already exists — that's fine.")
    else:
        r.raise_for_status()
        print("✓ Created Authorization:", r.json().get("name"))

    print(
        "\nAGENT_AUTHORIZATION="
        f"projects/{project}/locations/global/authorizations/{AUTHZ_ID}"
    )


if __name__ == "__main__":
    main()
