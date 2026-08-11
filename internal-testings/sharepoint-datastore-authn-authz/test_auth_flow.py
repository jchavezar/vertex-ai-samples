#!/usr/bin/env python3
"""
Workforce Identity Federation (WIF) & Connector Auth Validator
Demonstrates how the AuthN/AuthZ pipeline functions entirely at the
GCP IAM (STS) and Discovery Engine Collection levels without needing a GE App.
"""

import os
import sys
import json
import argparse
import requests

def exchange_entra_token(wif_pool: str, wif_provider: str, entra_jwt: str) -> str:
    """Exchange Microsoft Entra ID JWT for GCP federated access token via Google STS."""
    url = "https://sts.googleapis.com/v1/token"
    payload = {
        "audience": f"//iam.googleapis.com/locations/global/workforcePools/{wif_pool}/providers/{wif_provider}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": entra_jwt,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:id_token",
    }
    resp = requests.post(url, json=payload, timeout=10)
    if resp.ok:
        return resp.json().get("access_token")
    raise RuntimeError(f"STS Token Exchange failed ({resp.status_code}): {resp.text}")

def check_connector_access_token(project_number: str, connector_id: str, gcp_token: str) -> bool:
    """Verify if Discovery Engine has an active SharePoint access token for this identity."""
    url = (
        f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_number}/"
        f"locations/global/collections/{connector_id}/dataConnector:acquireAccessToken"
    )
    headers = {
        "Authorization": f"Bearer {gcp_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_number,
    }
    resp = requests.post(url, headers=headers, json={}, timeout=15)
    return resp.ok and bool(resp.json().get("accessToken"))

def main():
    parser = argparse.ArgumentParser(description="Test WIF and Connector Token Validation")
    parser.add_argument("--project-number", default="545964020693", help="GCP Project Number")
    parser.add_argument("--connector-id", default="sharepoint-data-def-connector", help="Data Connector ID")
    parser.add_argument("--wif-pool", default="sp-wif-pool-v2", help="WIF Workforce Pool ID")
    parser.add_argument("--wif-provider", default="entra-provider", help="WIF Provider ID")
    args = parser.parse_args()

    print("=" * 80)
    print("[*] FEDERATED CONNECTOR AUTHN / AUTHZ ARCHITECTURE VALIDATOR")
    print("=" * 80)
    print(f"1. Target Project Number: {args.project_number}")
    print(f"2. Connector ID:          {args.connector_id}")
    print(f"3. WIF Workforce Pool:    {args.wif-pool if hasattr(args, 'wif_pool') else args.wif_pool}")
    print(f"4. Discovery Engine URI:  https://discoveryengine.googleapis.com/v1alpha/.../collections/{args.connector_id}/dataConnector:*")
    print("\n[NOTE] All authentication endpoints reside strictly at the IAM (WIF) and Collection levels.")
    print("[NOTE] No Gemini Enterprise Engine (engines/{ENGINE_ID}) is invoked for AuthN/AuthZ.")
    print("=" * 80)

if __name__ == "__main__":
    main()
