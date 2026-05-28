"""Create the GE Authorization resource with `cloud-platform + drive.readonly` scopes.

GE Custom-A2A only supports server-side OAuth2 (authorization-code). We
register an OAuth2 client requesting two scopes:

  - cloud-platform   -> satisfies GE's pre-forward bearer check.
  - drive.readonly   -> what the agent's Drive tool actually uses.

GE captures the user's access token after consent and forwards it as
`Authorization: Bearer <ya29.user>` to the registered A2A endpoint. Both
scopes are present in the same token, so the agent can call Drive as the
user without any SA impersonation.
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

AUTHZ_ID = os.environ.get("AUTHZ_ID_OVERRIDE", "ge-a2a-auth-oauth")

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/drive.readonly",
]


def bearer() -> str:
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    return creds.token


def _authorization_uri() -> str:
    from urllib.parse import quote
    scope_qs = "+".join(quote(s, safe="") for s in SCOPES)
    return (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        "&access_type=offline"
        "&prompt=consent"
        "&include_granted_scopes=true"
        f"&scope={scope_qs}"
    )


def main() -> None:
    project = os.environ["PROJECT_ID"]
    client_id = os.environ["OAUTH_CLIENT_ID"]
    client_secret = os.environ["OAUTH_CLIENT_SECRET"]

    resource_name = (
        f"projects/{project}/locations/global/authorizations/{AUTHZ_ID}"
    )
    create_url = (
        "https://discoveryengine.googleapis.com/v1alpha/"
        f"projects/{project}/locations/global/authorizations"
        f"?authorizationId={AUTHZ_ID}"
    )

    payload = {
        "name": resource_name,
        "serverSideOauth2": {
            "clientId": client_id,
            "clientSecret": client_secret,
            "authorizationUri": _authorization_uri(),
            "tokenUri": "https://oauth2.googleapis.com/token",
        },
    }

    headers = {
        "Authorization": f"Bearer {bearer()}",
        "X-Goog-User-Project": project,
        "Content-Type": "application/json",
    }
    r = requests.post(create_url, headers=headers, json=payload, timeout=30)
    if r.status_code == 409:
        print("Authorization exists — PATCHing to update scope/auth URI...")
        patch_url = (
            f"https://discoveryengine.googleapis.com/v1alpha/{resource_name}"
            "?updateMask=serverSideOauth2"
        )
        pr = requests.patch(patch_url, headers=headers, json=payload, timeout=30)
        if not pr.ok:
            print(f"PATCH failed status={pr.status_code}\n{pr.text}")
            pr.raise_for_status()
        print("PATCHed:", pr.json().get("name"))
    else:
        if not r.ok:
            print(f"POST failed status={r.status_code}\n{r.text}")
            r.raise_for_status()
        print("Created Authorization:", r.json().get("name"))

    print("\nScopes configured:", " ".join(SCOPES))
    print("AGENT_AUTHORIZATION=" + resource_name)


if __name__ == "__main__":
    main()
